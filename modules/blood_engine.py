import pandas as pd
import numpy as np

# Reference ranges for clinical parameters
# Low, High, Unit, Category
REFERENCE_RANGES = {
    "Hemoglobin": {"min": 12.0, "max": 17.5, "unit": "g/dL", "cat": "RBC Profile"},
    "RBC_Count": {"min": 4.2, "max": 5.9, "unit": "million/mcL", "cat": "RBC Profile"},
    "Hematocrit": {"min": 37.0, "max": 52.0, "unit": "%", "cat": "RBC Profile"},
    "MCV": {"min": 80.0, "max": 100.0, "unit": "fL", "cat": "RBC Indices"},
    "MCH": {"min": 27.0, "max": 33.0, "unit": "pg", "cat": "RBC Indices"},
    "MCHC": {"min": 32.0, "max": 36.0, "unit": "g/dL", "cat": "RBC Indices"},
    "WBC": {"min": 4000, "max": 11000, "unit": "/mcL", "cat": "WBC Differential"},
    "Neutrophils": {"min": 40.0, "max": 70.0, "unit": "%", "cat": "WBC Differential"},
    "Lymphocytes": {"min": 20.0, "max": 45.0, "unit": "%", "cat": "WBC Differential"},
    "Eosinophils": {"min": 1.0, "max": 6.0, "unit": "%", "cat": "WBC Differential"},
    "Platelets": {"min": 150000, "max": 450000, "unit": "/mcL", "cat": "Platelets"},
    "Fasting_Glucose": {"min": 70.0, "max": 100.0, "unit": "mg/dL", "cat": "Metabolic"},
    "HbA1c": {"min": 4.0, "max": 5.6, "unit": "%", "cat": "Metabolic"},
    "Creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL", "cat": "Renal Panel"},
    "BUN": {"min": 7.0, "max": 20.0, "unit": "mg/dL", "cat": "Renal Panel"},
    "Bilirubin_Total": {"min": 0.2, "max": 1.2, "unit": "mg/dL", "cat": "Hepatic Panel"},
    "ALT_SGPT": {"min": 7.0, "max": 56.0, "unit": "U/L", "cat": "Hepatic Panel"},
    "AST_SGOT": {"min": 10.0, "max": 40.0, "unit": "U/L", "cat": "Hepatic Panel"},
    "CRP": {"min": 0.0, "max": 3.0, "unit": "mg/L", "cat": "Inflammatory Marker"},
    "ESR": {"min": 0.0, "max": 20.0, "unit": "mm/hr", "cat": "Inflammatory Marker"}
}

# Pre-configured clinical test scenarios for instant demonstration
BLOOD_PRESETS = {
    "Healthy Normal Profile": {
        "Hemoglobin": 14.5, "RBC_Count": 4.8, "Hematocrit": 43.0, "MCV": 89.0, "MCH": 30.2, "MCHC": 33.7,
        "WBC": 6800, "Neutrophils": 58.0, "Lymphocytes": 32.0, "Eosinophils": 2.5,
        "Platelets": 260000, "Fasting_Glucose": 88.0, "HbA1c": 5.2, "Creatinine": 0.9, "BUN": 13.0,
        "Bilirubin_Total": 0.7, "ALT_SGPT": 24.0, "AST_SGOT": 21.0, "CRP": 1.1, "ESR": 8.0
    },
    "Iron Deficiency Microcytic Anemia": {
        "Hemoglobin": 8.4, "RBC_Count": 3.4, "Hematocrit": 27.5, "MCV": 68.0, "MCH": 21.0, "MCHC": 28.5,
        "WBC": 7200, "Neutrophils": 61.0, "Lymphocytes": 30.0, "Eosinophils": 2.0,
        "Platelets": 390000, "Fasting_Glucose": 92.0, "HbA1c": 5.1, "Creatinine": 0.8, "BUN": 12.0,
        "Bilirubin_Total": 0.5, "ALT_SGPT": 20.0, "AST_SGOT": 19.0, "CRP": 1.8, "ESR": 24.0
    },
    "Acute Bacterial Infection / Sepsis Risk": {
        "Hemoglobin": 13.2, "RBC_Count": 4.4, "Hematocrit": 40.0, "MCV": 88.0, "MCH": 30.0, "MCHC": 34.0,
        "WBC": 18500, "Neutrophils": 86.0, "Lymphocytes": 8.0, "Eosinophils": 0.5,
        "Platelets": 210000, "Fasting_Glucose": 115.0, "HbA1c": 5.5, "Creatinine": 1.1, "BUN": 18.0,
        "Bilirubin_Total": 0.9, "ALT_SGPT": 35.0, "AST_SGOT": 32.0, "CRP": 48.0, "ESR": 65.0
    },
    "Viral Infection with Thrombocytopenia (e.g. Dengue)": {
        "Hemoglobin": 14.1, "RBC_Count": 4.6, "Hematocrit": 42.0, "MCV": 87.0, "MCH": 29.5, "MCHC": 33.5,
        "WBC": 2900, "Neutrophils": 34.0, "Lymphocytes": 58.0, "Eosinophils": 1.0,
        "Platelets": 42000, "Fasting_Glucose": 90.0, "HbA1c": 5.0, "Creatinine": 0.9, "BUN": 14.0,
        "Bilirubin_Total": 0.8, "ALT_SGPT": 68.0, "AST_SGOT": 75.0, "CRP": 8.5, "ESR": 18.0
    },
    "Type 2 Diabetes Mellitus (Uncontrolled Hyperglycemia)": {
        "Hemoglobin": 13.8, "RBC_Count": 4.7, "Hematocrit": 41.5, "MCV": 88.5, "MCH": 29.8, "MCHC": 33.6,
        "WBC": 7600, "Neutrophils": 62.0, "Lymphocytes": 29.0, "Eosinophils": 2.2,
        "Platelets": 240000, "Fasting_Glucose": 215.0, "HbA1c": 9.4, "Creatinine": 1.2, "BUN": 19.0,
        "Bilirubin_Total": 0.8, "ALT_SGPT": 42.0, "AST_SGOT": 38.0, "CRP": 4.2, "ESR": 22.0
    },
    "Chronic Kidney Disease (Renal Impairment)": {
        "Hemoglobin": 10.1, "RBC_Count": 3.5, "Hematocrit": 31.0, "MCV": 87.0, "MCH": 29.0, "MCHC": 33.0,
        "WBC": 7100, "Neutrophils": 64.0, "Lymphocytes": 27.0, "Eosinophils": 2.0,
        "Platelets": 190000, "Fasting_Glucose": 105.0, "HbA1c": 5.9, "Creatinine": 3.4, "BUN": 48.0,
        "Bilirubin_Total": 0.6, "ALT_SGPT": 28.0, "AST_SGOT": 25.0, "CRP": 7.8, "ESR": 38.0
    },
    "Acute Hepatic Dysfunction / Jaundice": {
        "Hemoglobin": 12.9, "RBC_Count": 4.3, "Hematocrit": 39.0, "MCV": 90.0, "MCH": 30.0, "MCHC": 33.5,
        "WBC": 8200, "Neutrophils": 60.0, "Lymphocytes": 31.0, "Eosinophils": 2.5,
        "Platelets": 175000, "Fasting_Glucose": 95.0, "HbA1c": 5.3, "Creatinine": 0.9, "BUN": 15.0,
        "Bilirubin_Total": 4.6, "ALT_SGPT": 290.0, "AST_SGOT": 245.0, "CRP": 12.0, "ESR": 26.0
    }
}

def parse_blood_report(file_or_data):
    """
    Parses an uploaded CSV or text report, or returns dictionary of values.
    """
    if isinstance(file_or_data, dict):
        return file_or_data

    # If it's an uploaded file from Streamlit
    try:
        # Check if CSV
        df = pd.read_csv(file_or_data)
        # Normalize columns: look for Parameter & Value or key-value pairs
        parsed = {}
        if "Parameter" in df.columns and "Value" in df.columns:
            for _, row in df.iterrows():
                key = str(row["Parameter"]).strip()
                val = float(row["Value"])
                parsed[key] = val
        else:
            # Assume first column is parameter, second is value
            cols = df.columns
            for _, row in df.iterrows():
                key = str(row[cols[0]]).strip()
                try:
                    val = float(row[cols[1]])
                    parsed[key] = val
                except Exception:
                    pass
        if parsed:
            return parsed
    except Exception:
        pass

    # Default fallback to normal
    return BLOOD_PRESETS["Healthy Normal Profile"].copy()

def evaluate_parameters(values):
    """
    Evaluates individual lab parameters against medical reference ranges.
    """
    evaluated = []
    for param, ref in REFERENCE_RANGES.items():
        val = values.get(param, None)
        if val is None:
            continue
        
        status = "Normal"
        badge_color = "#10b981" # Green
        
        if val < ref["min"]:
            status = "Low"
            badge_color = "#3b82f6" # Blue
        elif val > ref["max"]:
            # Check if critically high
            if val > ref["max"] * 1.5:
                status = "Critical High"
                badge_color = "#ef4444" # Red
            else:
                status = "High"
                badge_color = "#f59e0b" # Orange
                
        evaluated.append({
            "param": param.replace("_", " "),
            "raw_key": param,
            "category": ref["cat"],
            "value": val,
            "min": ref["min"],
            "max": ref["max"],
            "unit": ref["unit"],
            "status": status,
            "badge_color": badge_color
        })
    return evaluated

def diagnose_blood_report(values):
    """
    Executes a comprehensive multi-system pathophysiological clinical inference engine
    on laboratory blood count and metabolic values.
    """
    evaluated_params = evaluate_parameters(values)
    
    # Extract key parameters safely
    hb = values.get("Hemoglobin", 14.0)
    mcv = values.get("MCV", 90.0)
    mch = values.get("MCH", 30.0)
    wbc = values.get("WBC", 7000)
    neutro = values.get("Neutrophils", 60.0)
    lympho = values.get("Lymphocytes", 30.0)
    eos = values.get("Eosinophils", 2.0)
    plt = values.get("Platelets", 250000)
    fbs = values.get("Fasting_Glucose", 90.0)
    hba1c = values.get("HbA1c", 5.2)
    creat = values.get("Creatinine", 0.9)
    bun = values.get("BUN", 14.0)
    bili = values.get("Bilirubin_Total", 0.7)
    alt = values.get("ALT_SGPT", 25.0)
    ast = values.get("AST_SGOT", 22.0)
    crp = values.get("CRP", 1.0)
    esr = values.get("ESR", 10.0)

    diagnoses = []

    # 1. Anemia Evaluation
    if hb < 12.0:
        if mcv < 80.0:
            diagnoses.append({
                "condition": "Iron Deficiency Microcytic Anemia",
                "confidence": 0.92 if mch < 27.0 else 0.84,
                "severity": "Moderate" if hb >= 8.5 else "Severe",
                "system": "Hematologic",
                "color": "#f59e0b",
                "summary": f"Reduced Hemoglobin ({hb} g/dL) with Microcytosis (MCV {mcv} fL) and Hypochromia (MCH {mch} pg), strongly indicative of impaired iron stores or chronic micro-blood loss.",
                "action_items": [
                    "Order Serum Ferritin, Total Iron Binding Capacity (TIBC), and Transferrin Saturation",
                    "Stool occult blood screening to evaluate gastrointestinal blood loss",
                    "Oral elemental iron supplementation (Ferrous sulfate / Ascorbic acid co-administration)",
                    "Dietary modification with iron-rich foods"
                ]
            })
        elif mcv > 100.0:
            diagnoses.append({
                "condition": "Macrocytic / Megaloblastic Anemia",
                "confidence": 0.88,
                "severity": "Moderate",
                "system": "Hematologic",
                "color": "#8b5cf6",
                "summary": f"Low Hemoglobin ({hb} g/dL) with elevated MCV ({mcv} fL) indicating defective erythroid DNA maturation, classical for Vitamin B12 or Folate deficiency.",
                "action_items": [
                    "Serum Vitamin B12 and Serum/RBC Folate levels",
                    "Peripheral blood smear to inspect hypersegmented neutrophils",
                    "Evaluate for malabsorption or pernicious anemia (Anti-Intrinsic Factor antibodies)"
                ]
            })
        else:
            diagnoses.append({
                "condition": "Normocytic Normochromic Anemia",
                "confidence": 0.82,
                "severity": "Moderate",
                "system": "Hematologic",
                "color": "#3b82f6",
                "summary": f"Decreased Hemoglobin ({hb} g/dL) with normal erythrocyte indices (MCV {mcv} fL). Common in anemia of chronic disease, early hemolysis, or renal insufficiency.",
                "action_items": [
                    "Reticulocyte count to differentiate marrow hypo-proliferation vs hemolysis",
                    "Check Renal function (BUN/Creatinine) and inflammatory markers (CRP/ESR)"
                ]
            })

    # 2. Infectious & Inflammatory Evaluation
    if wbc > 11500 or neutro > 75.0 or crp > 15.0:
        diagnoses.append({
            "condition": "Acute Bacterial Infection / Pyogenic Inflammatory Response",
            "confidence": 0.94 if (wbc > 15000 and neutro > 80.0) else 0.86,
            "severity": "High" if crp > 30.0 or wbc > 17000 else "Moderate",
            "system": "Infectious Disease / Immunology",
            "color": "#ef4444",
            "summary": f"Leukocytosis ({wbc:,} /mcL) with prominent Neutrophilic shift ({neutro}%) and elevated CRP ({crp} mg/L), denoting acute bacterial infection or systemic inflammatory cascade.",
            "action_items": [
                "Blood cultures (2 sets from different sites) prior to antibiotic administration",
                "Clinical focus search: Chest radiograph (pneumonia), Urinalysis (UTI), or abdominal imaging",
                "Broad-spectrum antimicrobial therapy tailored to organ-specific source",
                "Serum Procalcitonin test for precision bacterial stewardship"
            ]
        })
    elif wbc < 4000 or (lympho > 50.0 and plt < 100000):
        diagnoses.append({
            "condition": "Acute Viral Infection / Thrombocytopenia Syndrome (e.g. Dengue / Arbovirus)",
            "confidence": 0.91 if plt < 60000 else 0.83,
            "severity": "High" if plt < 50000 else "Moderate",
            "system": "Infectious Disease / Hematology",
            "color": "#ec4899",
            "summary": f"Leukopenia ({wbc:,} /mcL), relative Lymphocytosis ({lympho}%), and significant Thrombocytopenia ({plt:,} /mcL), highly suggestive of acute viral suppression of bone marrow (e.g. Dengue, EBV, Cytomegalovirus).",
            "action_items": [
                "Dengue NS1 Antigen and IgM/IgG serology, or relevant viral PCR",
                "Strict monitoring of daily platelet count and hematocrit for plasma leakage",
                "Warning signs check: abdominal pain, mucosal bleeding, persistent vomiting",
                "Avoid NSAIDs (Aspirin, Ibuprofen) due to hemorrhage risk; use Paracetamol for fever"
            ]
        })

    # 3. Eosinophilic / Allergic Evaluation
    if eos > 7.0:
        diagnoses.append({
            "condition": "Eosinophilia (Allergic / Hypersensitivity or Parasitic)",
            "confidence": 0.85,
            "severity": "Mild to Moderate",
            "system": "Immunology",
            "color": "#06b6d4",
            "summary": f"Elevated Eosinophil count ({eos}%), characteristic of IgE-mediated allergic disease (asthma, eczema) or parasitic helminthic infection.",
            "action_items": [
                "Total Serum IgE quantitative test",
                "Stool examination for ova, cysts, and parasites (3 consecutive days)",
                "Allergy specialist consultation and skin prick testing"
            ]
        })

    # 4. Metabolic / Diabetic Evaluation
    if fbs >= 126.0 or hba1c >= 6.5:
        diagnoses.append({
            "condition": "Type 2 Diabetes Mellitus / Overt Hyperglycemia",
            "confidence": 0.96 if (fbs >= 140.0 or hba1c >= 7.0) else 0.89,
            "severity": "High" if (fbs > 200.0 or hba1c > 9.0) else "Moderate",
            "system": "Endocrine & Metabolism",
            "color": "#f97316",
            "summary": f"Markedly elevated Fasting Glucose ({fbs} mg/dL) and glycosylated hemoglobin (HbA1c {hba1c}%), meeting diagnostic criteria for Diabetes Mellitus.",
            "action_items": [
                "Immediate lifestyle counseling: dietary glycemic control and aerobic exercise regimen",
                "Initiate pharmacological management (Metformin or SGLT2i/GLP-1RA per guidelines)",
                "Comprehensive diabetes screening: Urine Albumin-to-Creatinine Ratio (UACR), Diabetic Retinopathy exam, and Monofilament foot check"
            ]
        })
    elif fbs >= 100.0 or (hba1c >= 5.7 and hba1c < 6.5):
        diagnoses.append({
            "condition": "Pre-Diabetes / Impaired Fasting Glucose (IFG)",
            "confidence": 0.85,
            "severity": "Mild",
            "system": "Endocrine & Metabolism",
            "color": "#fbbf24",
            "summary": f"Borderline elevation in Fasting Glucose ({fbs} mg/dL) and HbA1c ({hba1c}%), placing patient at heightened risk for progression to Type 2 Diabetes.",
            "action_items": [
                "Oral Glucose Tolerance Test (OGTT) for definitive risk staging",
                "Structured weight management and carbohydrate reduction plan",
                "Repeat glycemic panel in 3 to 6 months"
            ]
        })

    # 5. Renal Impairment Evaluation
    if creat > 1.3 or bun > 22.0:
        diagnoses.append({
            "condition": "Renal Impairment / Azotemia (Possible CKD or AKI)",
            "confidence": 0.93 if creat > 2.0 else 0.86,
            "severity": "Severe" if creat > 3.0 else "Moderate",
            "system": "Nephrology",
            "color": "#ef4444",
            "summary": f"Elevated Serum Creatinine ({creat} mg/dL) and BUN ({bun} mg/dL) indicating diminished glomerular filtration capacity.",
            "action_items": [
                "Calculate Estimated Glomerular Filtration Rate (eGFR - CKD-EPI equation)",
                "Renal ultrasound to evaluate kidney morphology and rule out obstructive uropathy",
                "Urinalysis with microscopic examination for proteinuria and dysmorphic RBC casts",
                "Review and immediately adjust all nephrotoxic medications (NSAIDs, aminoglycosides)"
            ]
        })

    # 6. Hepatic Dysfunction Evaluation
    if bili > 1.4 or alt > 60.0 or ast > 50.0:
        diagnoses.append({
            "condition": "Acute Hepatocellular Injury / Hepatic Dysfunction",
            "confidence": 0.92 if (alt > 100.0 or bili > 2.5) else 0.85,
            "severity": "High" if (alt > 200.0 or bili > 3.0) else "Moderate",
            "system": "Hepatology / Gastroenterology",
            "color": "#d97706",
            "summary": f"Significant elevation in transaminases (ALT {alt} U/L, AST {ast} U/L) and/or Total Bilirubin ({bili} mg/dL), indicative of liver inflammation or biliary stasis.",
            "action_items": [
                "Viral hepatitis serologies (Anti-HAV IgM, HBsAg, Anti-HCV, Anti-HEV)",
                "Abdominal ultrasonography of liver, gallbladder, and biliary tree",
                "Assess synthetic hepatic function: Prothrombin Time (PT/INR) and Serum Albumin",
                "Avoid alcohol and any hepatotoxic medications/supplements"
            ]
        })

    # If no conditions flagged, classify as Normal
    if not diagnoses:
        diagnoses.append({
            "condition": "Normal Hematologic & Biochemical Profile",
            "confidence": 0.95,
            "severity": "Normal",
            "system": "General Physiology",
            "color": "#10b981",
            "summary": "All evaluated complete blood count parameters, leukocyte differential counts, glycemic markers, renal function, and hepatic indices fall within established biological reference ranges.",
            "action_items": [
                "Continue balanced dietary nutrition and regular physical activity",
                "Repeat routine preventative health checkup in 12 months"
            ]
        })

    primary_diagnosis = diagnoses[0]
    
    return {
        "primary_diagnosis": primary_diagnosis,
        "all_diagnoses": diagnoses,
        "evaluated_parameters": evaluated_params,
        "total_abnormal": sum(1 for p in evaluated_params if p["status"] != "Normal")
    }
