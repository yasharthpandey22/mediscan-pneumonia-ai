import os
import sys
import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from auth import (
    init_db,
    authenticate_user,
    register_user,
    save_patient_record,
    get_patient_history
)
from modules.xray_engine import analyze_chest_xray, DISEASE_PROFILES
from modules.blood_engine import (
    parse_blood_report,
    evaluate_parameters,
    diagnose_blood_report,
    BLOOD_PRESETS,
    REFERENCE_RANGES
)
from modules.report_generator import generate_medical_report_text

# Page setup
st.set_page_config(
    page_title="MediScan AI • Multi-Modal Clinical Diagnosis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom CSS for modern medical styling
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #0c131f;
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headers and typography */
    h1, h2, h3, h4 {
        color: #f8fafc;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Header Card */
    .med-header-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .med-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    .badge-normal { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
    .badge-warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #f59e0b; }
    .badge-danger { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
    .badge-info { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid #3b82f6; }
    
    /* Diagnostic Result Cards */
    .diag-box {
        background: #1e293b;
        border-left: 6px solid #0ea5e9;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .metric-chip {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 16px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Tab styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        padding: 8px 20px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_data" not in st.session_state:
    st.session_state["user_data"] = None
if "xray_result" not in st.session_state:
    st.session_state["xray_result"] = None
if "blood_result" not in st.session_state:
    st.session_state["blood_result"] = None

# Sidebar branding & Patient info
with st.sidebar:
    st.markdown("### 🩺 MediScan AI Portal")
    st.caption("AI-Powered Clinical Multimodal Diagnosis")
    st.markdown("---")
    
    if st.session_state["logged_in"]:
        user = st.session_state["user_data"]
        st.markdown(f"#### 👤 Patient Profile")
        st.write(f"**Name:** {user.get('name')}")
        st.write(f"**Patient ID:** `{user.get('patient_id')}`")
        st.write(f"**Age / Sex:** {user.get('age')} yrs / {user.get('gender')}")
        st.write(f"**Blood Group:** `{user.get('blood_group')}`")
        st.write(f"**Known Allergies:** {user.get('allergies', 'None')}")
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            st.session_state["logged_in"] = False
            st.session_state["user_data"] = None
            st.session_state["xray_result"] = None
            st.session_state["blood_result"] = None
            st.rerun()
    else:
        st.info("👋 Please sign in to access your patient diagnostic portal.")
        st.markdown("---")
        st.caption("⚡ **Fast Demo Testing**")
        if st.button("🔑 Quick Login as John Doe", use_container_width=True):
            success, user = authenticate_user("john.doe@example.com", "Password123!")
            if success:
                st.session_state["logged_in"] = True
                st.session_state["user_data"] = user
                st.rerun()
        if st.button("🔑 Quick Login as Sarah Connor", use_container_width=True):
            success, user = authenticate_user("sarah.connor@example.com", "Demo1234!")
            if success:
                st.session_state["logged_in"] = True
                st.session_state["user_data"] = user
                st.rerun()

# -------------------------------------------------------------
# AUTHENTICATION SCREEN (If not logged in)
# -------------------------------------------------------------
if not st.session_state["logged_in"]:
    st.markdown("""
    <div class="med-header-card">
        <div style="display:flex; align-items:center; gap: 16px;">
            <div style="font-size: 3rem;">🩺</div>
            <div>
                <h1 style="margin:0; color:#38bdf8;">MediScan AI Diagnostic System</h1>
                <p style="margin:4px 0 0 0; color:#94a3b8; font-size:1.05rem;">
                    Advanced Automated Disease Screening & Triage for Chest Radiographs & Blood Reports
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_auth_left, col_auth_right = st.columns([1.1, 0.9], gap="large")
    
    with col_auth_left:
        st.markdown("### 🔐 Patient Authentication Window")
        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 New Patient Registration"])
        
        with auth_tab1:
            st.markdown("Enter your registered patient credentials to enter your medical portal:")
            with st.form("login_form"):
                email_input = st.text_input("Patient Email Address", value="john.doe@example.com")
                pwd_input = st.text_input("Password", type="password", value="Password123!")
                submit_login = st.form_submit_button("Sign In to Portal", use_container_width=True, type="primary")
                
                if submit_login:
                    if not email_input or not pwd_input:
                        st.error("Please enter both email and password.")
                    else:
                        success, user = authenticate_user(email_input, pwd_input)
                        if success:
                            st.session_state["logged_in"] = True
                            st.session_state["user_data"] = user
                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password. Please verify credentials or use demo button.")
                            
        with auth_tab2:
            st.markdown("Register a new patient profile:")
            with st.form("reg_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Alex Morgan")
                reg_email = st.text_input("Email Address", placeholder="e.g. alex.m@example.com")
                reg_pwd = st.text_input("Password", type="password", placeholder="Choose a secure password")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    reg_age = st.number_input("Age", min_value=1, max_value=120, value=30)
                with col_r2:
                    reg_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                with col_r3:
                    reg_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    
                reg_phone = st.text_input("Phone Number", placeholder="+1 (555) 000-0000")
                reg_allergies = st.text_input("Known Drug Allergies / Medical Conditions", placeholder="e.g. None, Penicillin, Asthma")
                
                submit_reg = st.form_submit_button("Register Patient Profile", use_container_width=True, type="primary")
                if submit_reg:
                    if not reg_name or not reg_email or not reg_pwd:
                        st.error("Name, email, and password are required fields.")
                    else:
                        ok, msg = register_user(reg_name, reg_email, reg_pwd, reg_age, reg_gender, reg_blood, reg_phone, reg_allergies)
                        if ok:
                            st.success(msg)
                            st.info("You can now sign in using the 'Sign In' tab.")
                        else:
                            st.error(msg)
                            
    with col_auth_right:
        st.markdown("### 🌟 System Capabilities")
        st.markdown("""
        <div style="background:#0f172a; border: 1px solid #334155; border-radius:12px; padding:20px;">
            <div style="margin-bottom:16px;">
                <h4 style="color:#38bdf8; margin:0 0 4px 0;">🩻 Chest X-Ray Pneumonia AI Analysis</h4>
                <p style="font-size:0.9rem; color:#cbd5e1; margin:0;">
                    Automated pulmonary screening for <strong>Normal vs. Pneumonia</strong> (differentiating Bacterial Lobar Consolidation and Viral Interstitial Infiltrates) with Class Activation localization heatmaps.
                </p>
            </div>
            <div style="margin-bottom:16px;">
                <h4 style="color:#ec4899; margin:0 0 4px 0;">🩸 Complete Blood Report Parser</h4>
                <p style="font-size:0.9rem; color:#cbd5e1; margin:0;">
                    Multiphasic screening across <strong>Complete Blood Count (CBC), Metabolic, Liver Enzymes, Renal Biomarkers, and Glycemic Indices</strong> for early pathological intervention.
                </p>
            </div>
            <div>
                <h4 style="color:#10b981; margin:0 0 4px 0;">📄 Clinical Summary Export</h4>
                <p style="font-size:0.9rem; color:#cbd5e1; margin:0;">
                    Structured, physician-ready diagnostic reports with clinical recommendations, severity staging, and longitudinal patient record tracking.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### ⚡ Quick Demo Accounts")
        st.markdown("""
        - **Account 1:** `john.doe@example.com` / `Password123!`
        - **Account 2:** `sarah.connor@example.com` / `Demo1234!`
        *(Or click the quick login buttons on the left sidebar)*
        """)

# -------------------------------------------------------------
# MAIN APPLICATION INTERFACE (When Logged In)
# -------------------------------------------------------------
else:
    user = st.session_state["user_data"]
    
    # Top banner
    st.markdown(f"""
    <div class="med-header-card">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap: 14px;">
                <div style="font-size: 2.4rem;">🩺</div>
                <div>
                    <h2 style="margin:0; color:#38bdf8;">MediScan AI Diagnostic Portal</h2>
                    <p style="margin:2px 0 0 0; color:#94a3b8; font-size:0.95rem;">
                        Patient: <strong style="color:#f8fafc;">{user.get('name')}</strong> (ID: <code style="color:#38bdf8;">{user.get('patient_id')}</code>)
                    </p>
                </div>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <span class="med-badge badge-info">Age: {user.get('age')}</span>
                <span class="med-badge badge-info">{user.get('gender')}</span>
                <span class="med-badge badge-normal">Blood: {user.get('blood_group')}</span>
                <span class="med-badge badge-warning">Allergies: {user.get('allergies', 'None')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Navigation Tabs
    main_tab_xray, main_tab_blood, main_tab_history, main_tab_info = st.tabs([
        "🩻 Chest X-Ray Diagnostic Engine",
        "🩸 Blood Report Analyzer",
        "📋 Patient Medical History",
        "ℹ️ Clinical Guidance & Safety"
    ])

    # =========================================================================
    # TAB 1: CHEST X-RAY PNEUMONIA ANALYSIS
    # =========================================================================
    with main_tab_xray:
        st.markdown("### 🩻 Chest Radiograph (X-Ray) Pneumonia Diagnostic Engine")
        st.caption("Upload a posteroanterior (PA) or anteroposterior (AP) chest radiograph to evaluate for pneumonia (Normal vs. Pneumonia):")

        xray_input_mode = st.radio(
            "Select X-Ray Input Source:",
            ["📁 Upload My Own Chest X-Ray", "🔬 Select Pre-loaded Clinical Case Sample"],
            horizontal=True
        )

        selected_xray_image = None
        sample_xray_desc = ""

        if xray_input_mode == "📁 Upload My Own Chest X-Ray":
            uploaded_file = st.file_uploader("Upload Chest X-Ray Image (JPG, PNG, JPEG)", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                try:
                    selected_xray_image = Image.open(uploaded_file)
                except Exception as e:
                    st.error(f"Error reading image: {e}")
        else:
            sample_dir = os.path.join(current_dir, "sample_data")
            sample_options = {
                "Case 1: Normal Healthy Lung Fields (No Pneumonia)": ("xray_normal.png", "Clear radiolucent pulmonary lung fields without focal consolidation or alveolar infiltrates."),
                "Case 2: Bacterial Lobar Pneumonia (Dense Consolidation)": ("xray_bacterial_pneumonia.png", "Dense focal alveolar consolidation in the right lower lobe with exudates."),
                "Case 3: Viral Interstitial Pneumonia (Bilateral Infiltrates)": ("xray_viral_pneumonia.png", "Bilateral diffuse interstitial reticulonodular opacities with peribronchial thickening.")
            }
            sample_choice = st.selectbox("Select a Sample Clinical Case:", list(sample_options.keys()))
            filename, sample_xray_desc = sample_options[sample_choice]
            sample_path = os.path.join(sample_dir, filename)
            if os.path.exists(sample_path):
                selected_xray_image = Image.open(sample_path)
                st.caption(f"ℹ️ **Case Description:** {sample_xray_desc}")
            else:
                st.warning("Sample image not found on disk. Please upload an image.")

        if selected_xray_image is not None:
            col_x1, col_x2 = st.columns([1, 1], gap="medium")
            with col_x1:
                st.markdown("#### 📷 Input Radiograph")
                st.image(selected_xray_image, caption="Submitted Radiograph", use_container_width=True)

            with col_x2:
                st.markdown("#### ⚙️ Diagnostics Execution")
                st.write("Ready to analyze pulmonary parenchymal opacity, focal consolidation, and bilateral aeration.")
                
                run_xray_btn = st.button("🚀 Analyze for Pneumonia", type="primary", use_container_width=True)
                if run_xray_btn:
                    with st.spinner("Analyzing pulmonary parenchyma, focal consolidation, and opacification..."):
                        xray_result = analyze_chest_xray(selected_xray_image)
                        st.session_state["xray_result"] = xray_result
                        st.success("Pneumonia Screening Complete!")

            # Display Results if Available
            if st.session_state["xray_result"] is not None:
                res = st.session_state["xray_result"]
                primary_diag = res["primary_disease"]
                binary_verdict = res.get("binary_verdict", "NORMAL")
                conf = res["confidence"] * 100
                p_prob = res.get("pneumonia_probability", 0.0) * 100
                n_prob = res.get("normal_probability", 0.0) * 100
                profile = res["profile"]
                metrics = res["metrics"]

                st.markdown("---")
                st.markdown("### 📊 Diagnostic Findings & Pneumonia Evaluation")

                # Verdict Banner
                is_pneumonia = (primary_diag != "Normal")
                severity_class = "badge-normal" if not is_pneumonia else ("badge-danger" if "Bacterial" in primary_diag else "badge-warning")
                
                st.markdown(f"""
                <div class="diag-box" style="border-left-color: {profile['color']};">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <span class="med-badge {severity_class}" style="font-size:0.95rem; padding:6px 16px;">
                                {binary_verdict}
                            </span>
                            <h3 style="margin:8px 0 2px 0; color:{profile['color']};">Subtype: {profile['title']}</h3>
                        </div>
                        <div style="text-align:right;">
                            <span class="med-badge {severity_class}">{profile['severity']} Severity</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:24px; margin:14px 0 10px 0; flex-wrap:wrap;">
                        <span style="font-size:1.05rem; color:#f1f5f9;">
                            <strong>Pneumonia Risk:</strong> <span style="color:#{'ef4444' if p_prob > 50 else '34d399'}; font-weight:700;">{p_prob:.1f}%</span>
                        </span>
                        <span style="font-size:1.05rem; color:#f1f5f9;">
                            <strong>Clear / Normal Probability:</strong> <span style="color:#{'34d399' if n_prob > 50 else '94a3b8'}; font-weight:700;">{n_prob:.1f}%</span>
                        </span>
                        <span style="font-size:1.05rem; color:#f1f5f9;">
                            <strong>Subtype Confidence:</strong> <span style="color:#38bdf8; font-weight:700;">{conf:.1f}%</span>
                        </span>
                    </div>
                    <p style="color:#cbd5e1; font-size:0.95rem; margin:0;">
                        {profile['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Quantitative Metric Cards
                c_m1, c_m2, c_m3, c_m4 = st.columns(4)
                with c_m1:
                    st.markdown(f"""
                    <div class="metric-chip">
                        <div class="metric-value">{metrics.get('lung_opacity_density', 'N/A')}</div>
                        <div class="metric-label">Parenchymal Opacity</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_m2:
                    st.markdown(f"""
                    <div class="metric-chip">
                        <div class="metric-value">{metrics.get('focal_consolidation_pct', 'N/A')}%</div>
                        <div class="metric-label">Focal Consolidation</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_m3:
                    st.markdown(f"""
                    <div class="metric-chip">
                        <div class="metric-value">{metrics.get('asymmetry_index', 'N/A')}%</div>
                        <div class="metric-label">Hemithorax Asymmetry</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_m4:
                    st.markdown(f"""
                    <div class="metric-chip">
                        <div class="metric-value">{metrics.get('consolidation_ratio', 'N/A')}</div>
                        <div class="metric-label">Consolidation Ratio</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Visualization: Original vs Heatmap & Differential Probabilities
                col_viz_left, col_viz_right = st.columns([1, 1], gap="medium")
                with col_viz_left:
                    st.markdown("#### 🎯 Pathology Localization (Grad-CAM Heatmap)")
                    st.image(res["heatmap"], caption="Hotspots indicate region of focal consolidation or architectural distortion", use_container_width=True)

                with col_viz_right:
                    st.markdown("#### 📈 Multi-Disease Probability Distribution")
                    df_probs = pd.DataFrame(res["ranking"], columns=["Condition", "Probability"])
                    df_probs["Percentage"] = df_probs["Probability"] * 100
                    df_probs = df_probs.sort_values(by="Percentage", ascending=True)

                    fig = px.bar(
                        df_probs,
                        x="Percentage",
                        y="Condition",
                        orientation="h",
                        color="Percentage",
                        color_continuous_scale="Viridis",
                        text=df_probs["Percentage"].apply(lambda v: f"{v:.1f}%")
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94a3b8"),
                        xaxis=dict(title="Probability (%)", range=[0, 100], gridcolor="#334155"),
                        yaxis=dict(title=""),
                        height=340,
                        margin=dict(l=0, r=20, t=20, b=20),
                        coloraxis_showscale=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Clinical Findings & Actions
                col_act1, col_act2 = st.columns(2, gap="medium")
                with col_act1:
                    st.markdown("#### 📋 Radiographic Findings Identified")
                    for finding in profile["findings"]:
                        st.markdown(f"- 🔎 **{finding}**")

                with col_act2:
                    st.markdown("#### 🩺 Recommended Clinical Action Plan")
                    for rec in profile["recommendations"]:
                        st.markdown(f"- 💊 {rec}")

                # Download & Record Saving
                st.markdown("---")
                col_save1, col_save2 = st.columns([1, 1])
                with col_save1:
                    report_txt = generate_medical_report_text(user, "CHEST_XRAY", res)
                    st.download_button(
                        label="📥 Download Official Radiography Report (.txt)",
                        data=report_txt,
                        file_name=f"XRAY_Report_{user['patient_id']}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_save2:
                    if st.button("💾 Save Diagnosis to Patient History", use_container_width=True):
                        record = {
                            "type": "Chest X-Ray",
                            "primary_disease": primary_diag,
                            "confidence": f"{conf:.1f}%",
                            "severity": profile["severity"],
                            "summary": profile["description"]
                        }
                        save_patient_record(user["patient_id"], record)
                        st.success("✅ Consultation record saved to your profile history!")

    # =========================================================================
    # TAB 2: BLOOD REPORT ANALYZER
    # =========================================================================
    with main_tab_blood:
        st.markdown("### 🩸 Complete Blood Count (CBC) & Metabolic Panel Analyzer")
        st.caption("Upload a lab test file (CSV), select a clinical test case preset, or enter parameter values manually:")

        blood_mode = st.radio(
            "Select Blood Report Input Method:",
            ["🔬 Clinical Preset Scenarios (Instant Load)", "📂 Upload CSV Lab Report", "✍️ Interactive Parameter Editor"],
            horizontal=True
        )

        active_blood_data = None

        if blood_mode == "🔬 Clinical Preset Scenarios (Instant Load)":
            selected_preset_key = st.selectbox("Select Patient Clinical Condition Preset:", list(BLOOD_PRESETS.keys()))
            active_blood_data = BLOOD_PRESETS[selected_preset_key].copy()
            st.info(f"Loaded clinical profile: **{selected_preset_key}**")

        elif blood_mode == "📂 Upload CSV Lab Report":
            uploaded_csv = st.file_uploader("Upload Blood Test CSV (Columns: Parameter, Value)", type=["csv"])
            if uploaded_csv is not None:
                active_blood_data = parse_blood_report(uploaded_csv)
                st.success("CSV file successfully parsed!")
            else:
                st.caption("Need sample data? You can download sample CSVs from the `sample_data` folder or choose presets above.")
                active_blood_data = BLOOD_PRESETS["Healthy Normal Profile"].copy()

        else: # Interactive Editor
            st.markdown("#### 🎛️ Adjust Lab Values Manually:")
            active_blood_data = BLOOD_PRESETS["Healthy Normal Profile"].copy()
            
            e_col1, e_col2, e_col3, e_col4 = st.columns(4)
            with e_col1:
                st.markdown("**🔴 RBC Profile**")
                active_blood_data["Hemoglobin"] = st.number_input("Hemoglobin (g/dL)", value=13.5, step=0.1)
                active_blood_data["RBC_Count"] = st.number_input("RBC Count (M/mcL)", value=4.7, step=0.1)
                active_blood_data["Hematocrit"] = st.number_input("Hematocrit (%)", value=41.0, step=0.5)
                active_blood_data["MCV"] = st.number_input("MCV (fL)", value=88.0, step=1.0)
            with e_col2:
                st.markdown("**⚪ WBC & Differential**")
                active_blood_data["WBC"] = st.number_input("WBC Count (/mcL)", value=7200, step=100)
                active_blood_data["Neutrophils"] = st.number_input("Neutrophils (%)", value=60.0, step=1.0)
                active_blood_data["Lymphocytes"] = st.number_input("Lymphocytes (%)", value=30.0, step=1.0)
                active_blood_data["Platelets"] = st.number_input("Platelets (/mcL)", value=250000, step=5000)
            with e_col3:
                st.markdown("**🍬 Glycemic & Renal**")
                active_blood_data["Fasting_Glucose"] = st.number_input("Fasting Glucose (mg/dL)", value=92.0, step=1.0)
                active_blood_data["HbA1c"] = st.number_input("HbA1c (%)", value=5.3, step=0.1)
                active_blood_data["Creatinine"] = st.number_input("Creatinine (mg/dL)", value=0.9, step=0.1)
                active_blood_data["BUN"] = st.number_input("BUN (mg/dL)", value=14.0, step=1.0)
            with e_col4:
                st.markdown("**🧪 Hepatic & Inflammation**")
                active_blood_data["Bilirubin_Total"] = st.number_input("Bilirubin (mg/dL)", value=0.8, step=0.1)
                active_blood_data["ALT_SGPT"] = st.number_input("ALT / SGPT (U/L)", value=25.0, step=1.0)
                active_blood_data["AST_SGOT"] = st.number_input("AST / SGOT (U/L)", value=22.0, step=1.0)
                active_blood_data["CRP"] = st.number_input("CRP (mg/L)", value=1.2, step=0.5)

        st.markdown("---")
        run_blood_btn = st.button("🚀 Analyze Laboratory Blood Report", type="primary", use_container_width=True)

        if run_blood_btn and active_blood_data:
            with st.spinner("Evaluating multiphasic biomarkers against diagnostic clinical criteria..."):
                blood_res = diagnose_blood_report(active_blood_data)
                st.session_state["blood_result"] = blood_res
                st.success("Blood Analysis Complete!")

        # Display Blood Results
        if st.session_state["blood_result"] is not None:
            b_res = st.session_state["blood_result"]
            primary_b = b_res["primary_diagnosis"]
            conf_b = primary_b["confidence"] * 100
            sev_b = primary_b.get("severity", "Normal")

            b_badge_class = "badge-normal" if sev_b == "Normal" else ("badge-danger" if "High" in sev_b or "Severe" in sev_b else "badge-warning")

            st.markdown(f"""
            <div class="diag-box" style="border-left-color: {primary_b.get('color', '#0ea5e9')};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:{primary_b.get('color', '#38bdf8')};">Primary Diagnosis: {primary_b['condition']}</h3>
                    <span class="med-badge {b_badge_class}">{sev_b} Severity</span>
                </div>
                <p style="font-size:1.1rem; margin:8px 0; color:#f1f5f9;">
                    <strong>Confidence:</strong> <span style="color:#38bdf8; font-weight:700;">{conf_b:.1f}%</span> | 
                    <strong>Physiological System:</strong> <span style="color:#a78bfa;">{primary_b.get('system')}</span> |
                    <strong>Abnormal Biomarkers:</strong> <span style="color:#f87171; font-weight:700;">{b_res['total_abnormal']}</span>
                </p>
                <p style="color:#cbd5e1; font-size:0.95rem; margin:0;">
                    {primary_b['summary']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Recommendations
            col_b_act1, col_b_act2 = st.columns([1.2, 0.8], gap="medium")
            with col_b_act1:
                st.markdown("#### 🩺 Clinical Actions & Medical Management")
                for act in primary_b.get("action_items", []):
                    st.markdown(f"- 💊 {act}")

            with col_b_act2:
                # Mini Gauge Chart for confidence
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = conf_b,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Confidence Level (%)", 'font': {'color': '#94a3b8', 'size': 14}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickcolor': "#94a3b8"},
                        'bar': {'color': primary_b.get('color', '#38bdf8')},
                        'bgcolor': "#1e293b",
                        'borderwidth': 1,
                        'bordercolor': "#334155"
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#f8fafc"),
                    height=240,
                    margin=dict(l=20, r=20, t=30, b=10)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            # Parameters Detailed Breakdown Table
            st.markdown("#### 🧪 Evaluated Biomarkers & Reference Comparison")
            
            eval_list = b_res["evaluated_parameters"]
            df_eval = pd.DataFrame(eval_list)
            
            # Format DataFrame display
            df_display = df_eval[["param", "category", "value", "unit", "min", "max", "status"]].copy()
            df_display.columns = ["Biomarker", "Category", "Result Value", "Unit", "Min Ref", "Max Ref", "Clinical Status"]
            
            # Custom styled dataframe table
            def color_status(val):
                if val == "Normal":
                    return "color: #34d399; font-weight: bold;"
                elif "Critical" in val or "High" in val:
                    return "color: #f87171; font-weight: bold;"
                elif "Low" in val:
                    return "color: #60a5fa; font-weight: bold;"
                return ""

            st.dataframe(
                df_display.style.map(color_status, subset=["Clinical Status"]),
                use_container_width=True,
                height=350
            )

            # Download & Record Saving
            st.markdown("---")
            col_b_save1, col_b_save2 = st.columns([1, 1])
            with col_b_save1:
                b_report_txt = generate_medical_report_text(user, "BLOOD_REPORT", b_res)
                st.download_button(
                    label="📥 Download Laboratory Diagnostic Report (.txt)",
                    data=b_report_txt,
                    file_name=f"Blood_Report_{user['patient_id']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_b_save2:
                if st.button("💾 Save Blood Diagnostic to History", use_container_width=True):
                    record = {
                        "type": "Blood Report",
                        "primary_disease": primary_b["condition"],
                        "confidence": f"{conf_b:.1f}%",
                        "severity": sev_b,
                        "summary": primary_b["summary"]
                    }
                    save_patient_record(user["patient_id"], record)
                    st.success("✅ Blood diagnostic record archived to your profile history!")

    # =========================================================================
    # TAB 3: PATIENT MEDICAL HISTORY
    # =========================================================================
    with main_tab_history:
        st.markdown(f"### 📋 Diagnostic History for {user['name']}")
        st.caption(f"Patient ID: `{user['patient_id']}` | Records are stored securely.")

        history = get_patient_history(user["patient_id"])
        if not history:
            st.info("ℹ️ No previous diagnoses recorded yet. Run an X-ray or Blood analysis to archive records.")
        else:
            for idx, item in enumerate(history):
                badge_type = "badge-danger" if "High" in item.get("severity", "") or "Severe" in item.get("severity", "") else "badge-normal"
                st.markdown(f"""
                <div style="background:#1e293b; border: 1px solid #334155; border-radius:12px; padding:16px 20px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <div>
                            <span style="font-size:0.8rem; color:#94a3b8;">📅 {item.get('timestamp')}</span>
                            <h4 style="margin:4px 0; color:#38bdf8;">{item.get('type')}: {item.get('primary_disease')}</h4>
                        </div>
                        <div>
                            <span class="med-badge {badge_type}">{item.get('severity')}</span>
                            <span class="med-badge badge-info">Confidence: {item.get('confidence')}</span>
                        </div>
                    </div>
                    <p style="margin:8px 0 0 0; color:#cbd5e1; font-size:0.9rem;">
                        {item.get('summary')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 4: CLINICAL GUIDANCE & SAFETY
    # =========================================================================
    with main_tab_info:
        st.markdown("### ℹ️ Clinical Decision Support System Notice")
        st.markdown("""
        #### 🩺 Diagnostic Modalities & Algorithms
        1. **Chest Radiography (CXR) Engine:**
           - Analyzes posteroanterior and anteroposterior digital thoracic radiographs.
           - Employs spatial lung zone partitioning (upper, mid, lower zones) and optical density profiling.
           - Generates **Grad-CAM style Class Activation localization heatmaps** highlighting regions of consolidation, infiltration, or cavitary distortion.
        2. **Multiphasic Laboratory Blood Engine:**
           - Interrogates Complete Blood Count (CBC with differential) alongside metabolic, renal, and hepatic panels.
           - Maps pathological clusters including microcytic anemia, acute bacterial neutrophilia, viral bone-marrow suppression (e.g. Dengue), diabetic hyperglycemia, and azotemia.

        #### ⚠️ Medical & Legal Disclaimer
        > **ATTENTION:** This software application is engineered as an **Artificial Intelligence Clinical Decision Support (CDSS) and triage aid**. It is **not** an FDA/CE-cleared primary diagnostic device and should **never** supersede the professional judgment, clinical evaluation, or official diagnosis of a licensed physician, radiologist, or clinical pathologist.
        >
        > In case of acute chest pain, hemoptysis, severe respiratory distress, or severe hemorrhage, **seek emergency medical assistance immediately**.
        """)
