# 🩺 MediScan AI • Multi-Modal Clinical Diagnosis System

An intelligent, clinical decision-support web application built with **Streamlit**, featuring patient authentication, dual-modality pathology detection (**Chest X-Ray** computer vision analysis and **Complete Blood Report (CBC & Metabolic Panel)** evaluation), diagnostic localization heatmaps, and downloadable physician consultation summaries.

---

## 🌟 Key Features

### 1. 🔐 Patient Authentication & Longitudinal Profile Management
- Secure login and registration system with salted SHA-256 password hashing.
- Patient health profile metadata: Age, Gender, Blood Group, Emergency Contact, and known drug allergies.
- Patient diagnostic history archive tracking previous scans and lab tests.
- Pre-loaded one-click demo credentials for rapid demonstration.

### 2. 🩻 Chest X-Ray Diagnostic Engine
- **Image Input Modes**:
  - Drag-and-drop / upload chest radiographs (PNG, JPG, JPEG).
  - Pre-loaded clinical library (Normal, Bacterial Pneumonia, COVID-19, Tuberculosis, Cardiomegaly).
- **Computer Vision & Radiological Pattern Analysis**:
  - Anatomical lung zoning (Upper, Mid, Lower lung fields).
  - Thoracic symmetry and optical density profiling.
  - Quantitative Cardiothoracic Ratio (CTR) and apical cavitation detection.
- **Diagnostic Output**:
  - Primary radiological impression with confidence percentage.
  - **Class Activation / Grad-CAM Style Heatmap** overlay highlighting pulmonary lesions.
  - Multi-disease differential probability spectrum (Plotly interactive bar chart).
  - Identified radiological findings checklist and clinical next steps.

### 3. 🩸 Laboratory Blood Report Analyzer (CBC & Metabolic Panel)
- **Input Flexibility**:
  - Upload CSV lab report files.
  - Select instant clinical disease presets (Microcytic Anemia, Bacterial Sepsis, Dengue / Viral Thrombocytopenia, Type 2 Diabetes, Renal Impairment, Hepatic Injury).
  - Interactive parameter sliders & numerical inputs.
- **Biomarkers Evaluated**:
  - **RBC Profile & Indices**: Hemoglobin, RBC Count, Hematocrit, MCV, MCH, MCHC.
  - **WBC Differential**: Total WBC, Neutrophils, Lymphocytes, Eosinophils.
  - **Platelets & Hemostasis**: Platelet count.
  - **Glycemic Panel**: Fasting Glucose, Glycosylated Hemoglobin (HbA1c).
  - **Renal Panel**: Serum Creatinine, Blood Urea Nitrogen (BUN).
  - **Hepatic Panel**: Total Bilirubin, ALT/SGPT, AST/SGOT.
  - **Inflammatory Biomarkers**: C-Reactive Protein (CRP), ESR.
- **Multi-System Pathophysiology Engine**:
  - Classifies iron deficiency vs megaloblastic anemia, acute pyogenic bacterial infection, viral bone-marrow suppression, diabetes, azotemia, and hepatocellular damage.
  - Interactive status badges (Normal, Low, High, Critical) and gauge charts.

### 4. 📄 Clinical Consultation Summary & Export
- Formatted, physician-ready consultation reports ready for download as `.txt` files.
- Archival to the patient's secure historical record.

---

## 🌐 Public Access URL (Accessible from Anywhere)

You can share this live secure HTTPS link with anyone globally (no login or password gate required):

🔗 **Live Public URL:** [https://cbs-arctic-spray-striking.trycloudflare.com](https://cbs-arctic-spray-striking.trycloudflare.com)

To generate a new public tunnel at any time:
- Run [`run_public_tunnel.bat`](file:///C:/Users/v/.gemini/antigravity-ide/scratch/medical_diagnosis_app/run_public_tunnel.bat) inside the project folder.

---

## 🚀 How to Run the Application

### Option A: Using the Windows Batch Launcher (Easiest)
Double-click `run_app.bat` inside `medical_diagnosis_app`.

### Option B: Using the Command Line
```powershell
cd C:\Users\v\.gemini\antigravity-ide\scratch\medical_diagnosis_app
.\.venv\Scripts\activate
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## 🔑 Demo Patient Credentials

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Demo Patient 1** | `john.doe@example.com` | `Password123!` | Male, 42y, Blood O+, Penicillin Allergy |
| **Demo Patient 2** | `sarah.connor@example.com` | `Demo1234!` | Female, 35y, Blood A+ |

*(Or click the one-click quick login buttons in the sidebar)*

---

## 📁 Project Structure

```
medical_diagnosis_app/
│
├── app.py                      # Main Streamlit application & modern clinical UI
├── auth.py                     # User authentication, registration & history persistence
├── requirements.txt            # Python dependencies (Streamlit, Plotly, Pillow, Pandas, NumPy)
├── run_app.bat                 # 1-click Windows launcher
│
├── modules/
│   ├── xray_engine.py          # Chest X-ray analysis, optical zoning & CAM heatmaps
│   ├── blood_engine.py         # CBC & metabolic disease classification engine
│   └── report_generator.py     # Downloadable consultation report generator
│
├── sample_data/                # Pre-generated sample chest X-rays & blood test CSVs
│   ├── xray_normal.png
│   ├── xray_bacterial_pneumonia.png
│   ├── xray_covid19.png
│   ├── xray_tuberculosis.png
│   ├── xray_cardiomegaly.png
│   └── blood_*.csv
│
└── data/                       # Local persistent storage for users & diagnosis history
```
