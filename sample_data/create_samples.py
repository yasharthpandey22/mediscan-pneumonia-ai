import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

SAMPLE_DIR = os.path.dirname(__file__)

def generate_base_chest_xray(width=512, height=512):
    """Generates an anatomically plausible synthetic chest radiograph baseline."""
    # Dark thoracic background
    img_array = np.zeros((height, width), dtype=np.float32)
    
    y, x = np.ogrid[:height, :width]
    cx, cy = width / 2.0, height / 2.0
    
    # Outer ribcage boundary (oval)
    thoracic_mask = ((x - cx)**2 / (width * 0.44)**2 + (y - cy)**2 / (height * 0.46)**2) <= 1.0
    img_array[thoracic_mask] = 40.0
    
    # Soft tissue shoulders and neck (superior brightness)
    neck = np.exp(-((x - cx)**2) / (2 * (width * 0.15)**2)) * np.exp(-y / (height * 0.25))
    img_array += neck * 140.0
    
    # Lateral chest walls (soft tissue)
    lateral_dist = np.abs(x - cx) / (width * 0.5)
    img_array += np.clip((lateral_dist - 0.75) * 400.0, 0, 120)
    
    # Lung Fields (Dark radiolucent bilaterally)
    # Right lung (viewer's left)
    r_cx, r_cy = width * 0.32, height * 0.48
    r_lung = ((x - r_cx)**2 / (width * 0.16)**2 + (y - r_cy)**2 / (height * 0.32)**2) <= 1.0
    
    # Left lung (viewer's right)
    l_cx, l_cy = width * 0.68, height * 0.48
    l_lung = ((x - l_cx)**2 / (width * 0.16)**2 + (y - l_cy)**2 / (height * 0.32)**2) <= 1.0
    
    img_array[r_lung] = 25.0
    img_array[l_lung] = 25.0
    
    # Diaphragm domes (curved lower boundary)
    r_diaphragm = np.exp(-((x - r_cx)**2) / (2 * (width * 0.18)**2)) * np.exp(-((y - height * 0.82)**2) / (2 * (height * 0.08)**2))
    l_diaphragm = np.exp(-((x - l_cx)**2) / (2 * (width * 0.18)**2)) * np.exp(-((y - height * 0.84)**2) / (2 * (height * 0.08)**2))
    img_array += (r_diaphragm + l_diaphragm) * 160.0
    
    # Subdiaphragmatic abdomen (dense/bright)
    abdomen_mask = (y > height * 0.85) & np.ones((height, width), dtype=bool)
    img_array[abdomen_mask] = 130.0
    
    # Spine (vertical central radiopaque column)
    spine = np.exp(-((x - cx)**2) / (2 * (width * 0.04)**2)) * 75.0
    img_array += spine
    
    # Rib shadows (horizontal curved lines)
    for i in range(8):
        rib_y = height * (0.22 + i * 0.075)
        rib_curve = np.exp(-((y - rib_y - 0.0003 * (x - cx)**2)**2) / (2 * 4.0**2))
        img_array += rib_curve * 35.0
        
    # Clavicles
    clav_r = np.exp(-((y - height * 0.20 + 0.12 * (x - cx))**2) / (2 * 5.0**2)) * (x < cx)
    clav_l = np.exp(-((y - height * 0.20 - 0.12 * (x - cx))**2) / (2 * 5.0**2)) * (x >= cx)
    img_array += (clav_r + clav_l) * 90.0
    
    # Normal Cardiac Silhouette (offset toward patient's left / viewer's right)
    c_mask = ((x - (cx + width * 0.05))**2 / (width * 0.15)**2 + (y - (cy + height * 0.14))**2 / (height * 0.18)**2) <= 1.0
    img_array[c_mask] += 95.0
    
    # Add subtle radiologic noise texture
    noise = np.random.normal(0, 3.5, (height, width))
    img_array += noise
    
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_array)
    return img.filter(ImageFilter.GaussianBlur(1.2))

def create_sample_xrays():
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    
    # 1. Normal
    normal_img = generate_base_chest_xray()
    normal_img.save(os.path.join(SAMPLE_DIR, "xray_normal.png"))
    
    # 2. Bacterial Pneumonia (Dense consolidation in Right Lower Lobe - viewer's left)
    pneumonia_np = np.array(generate_base_chest_xray(), dtype=np.float32)
    y, x = np.ogrid[:512, :512]
    # Dense opacity in right lower/mid zone
    consolidation = np.exp(-((x - 170)**2 / (2 * 45**2) + (y - 340)**2 / (2 * 50**2))) * 165.0
    pneumonia_np += consolidation
    pneumonia_img = Image.fromarray(np.clip(pneumonia_np, 0, 255).astype(np.uint8))
    pneumonia_img.save(os.path.join(SAMPLE_DIR, "xray_bacterial_pneumonia.png"))
    
    # 3. COVID-19 (Bilateral peripheral lower ground glass opacities)
    covid_np = np.array(generate_base_chest_xray(), dtype=np.float32)
    ggo_right = np.exp(-((x - 110)**2 / (2 * 35**2) + (y - 350)**2 / (2 * 60**2))) * 110.0
    ggo_left = np.exp(-((x - 400)**2 / (2 * 35**2) + (y - 350)**2 / (2 * 60**2))) * 110.0
    covid_np += (ggo_right + ggo_left)
    covid_img = Image.fromarray(np.clip(covid_np, 0, 255).astype(np.uint8))
    covid_img.save(os.path.join(SAMPLE_DIR, "xray_covid19.png"))
    
    # 4. Tuberculosis (Right upper lobe apical cavity and nodular opacity)
    tb_np = np.array(generate_base_chest_xray(), dtype=np.float32)
    apical_lesion = np.exp(-((x - 165)**2 / (2 * 35**2) + (y - 135)**2 / (2 * 35**2))) * 145.0
    # Radiolucent central cavity
    cavity = np.exp(-((x - 165)**2 / (2 * 12**2) + (y - 135)**2 / (2 * 12**2))) * 90.0
    tb_np += (apical_lesion - cavity)
    tb_img = Image.fromarray(np.clip(tb_np, 0, 255).astype(np.uint8))
    tb_img.save(os.path.join(SAMPLE_DIR, "xray_tuberculosis.png"))
    
    # 5. Cardiomegaly (Significantly enlarged cardiac shadow CTR > 0.60)
    cardio_np = np.array(generate_base_chest_xray(), dtype=np.float32)
    # Huge heart extending across lower thorax
    huge_heart = np.exp(-((x - 290)**2 / (2 * 120**2) + (y - 330)**2 / (2 * 80**2))) * 150.0
    cardio_np += huge_heart
    cardio_img = Image.fromarray(np.clip(cardio_np, 0, 255).astype(np.uint8))
    cardio_img.save(os.path.join(SAMPLE_DIR, "xray_cardiomegaly.png"))
    
    print("Sample X-rays generated successfully!")

def create_sample_blood_csvs():
    from modules.blood_engine import BLOOD_PRESETS
    for name, data in BLOOD_PRESETS.items():
        filename = "blood_" + name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace(".", "") + ".csv"
        rows = [{"Parameter": k, "Value": v} for k, v in data.items()]
        df = pd.DataFrame(rows)
        df.to_csv(os.path.join(SAMPLE_DIR, filename), index=False)
    print("Sample Blood CSVs generated successfully!")

if __name__ == "__main__":
    create_sample_xrays()
    create_sample_blood_csvs()
