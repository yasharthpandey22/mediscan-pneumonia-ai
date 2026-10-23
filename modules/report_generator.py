import datetime

def generate_medical_report_text(patient, diagnosis_type, result_data):
    """
    Generates a formal clinical consultation report in text format suitable for download.
    """
    now_str = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    report = []
    report.append("=" * 72)
    report.append("          AI CLINICAL DECISION SUPPORT & DIAGNOSTIC REPORT          ")
    report.append("=" * 72)
    report.append(f"Report Generated: {now_str}")
    report.append("-" * 72)
    report.append("PATIENT DEMOGRAPHICS & CLINICAL PROFILE:")
    report.append(f"  • Patient Name:     {patient.get('name', 'N/A')}")
    report.append(f"  • Patient ID:       {patient.get('patient_id', 'N/A')}")
    report.append(f"  • Age / Gender:     {patient.get('age', 'N/A')} yrs / {patient.get('gender', 'N/A')}")
    report.append(f"  • Blood Group:      {patient.get('blood_group', 'N/A')}")
    report.append(f"  • Known Allergies:  {patient.get('allergies', 'None documented')}")
    report.append("-" * 72)
    
    if diagnosis_type == "CHEST_XRAY":
        report.append("DIAGNOSTIC MODALITY: DIGITAL CHEST RADIOGRAPHY (PNEUMONIA SCREENING)")
        report.append("-" * 72)
        primary = result_data["primary_disease"]
        binary_status = result_data.get("binary_verdict", "NORMAL")
        conf = result_data["confidence"] * 100
        profile = result_data["profile"]
        
        report.append(f"TRIAGE STATUS:                    {binary_status}")
        report.append(f"RADIOLOGICAL IMPRESSION:          {primary.upper()}")
        report.append(f"CONFIDENCE SCORE:                 {conf:.1f}%")
        report.append(f"PNEUMONIA PROBABILITY:            {result_data.get('pneumonia_probability', 0)*100:.1f}%")
        report.append(f"NORMAL PROBABILITY:               {result_data.get('normal_probability', 0)*100:.1f}%")
        report.append(f"PATHOLOGY SEVERITY:               {profile['severity']}")
        report.append("\nCLINICAL SUMMARY:")
        report.append(f"  {profile['description']}")
        
        report.append("\nKEY RADIOLOGICAL FINDINGS:")
        for f in profile["findings"]:
            report.append(f"  [✓] {f}")
            
        report.append("\nQUANTITATIVE THORACIC METRICS:")
        metrics = result_data.get("metrics", {})
        report.append(f"  • Lung Parenchymal Opacity Density: {metrics.get('lung_opacity_density', 'N/A')}")
        report.append(f"  • Hemithorax Asymmetry Index:       {metrics.get('asymmetry_index', 'N/A')}%")
        report.append(f"  • Focal Consolidation Density:      {metrics.get('focal_consolidation_pct', 'N/A')}%")
        report.append(f"  • Consolidation Ratio:              {metrics.get('consolidation_ratio', 'N/A')}")
        
        report.append("\nDIFFERENTIAL PROBABILITY SPECTRUM:")
        for d, p in result_data.get("ranking", []):
            report.append(f"  • {d:35s} : {p*100:5.1f}%")
            
        report.append("\nRECOMMENDED CLINICAL ACTION PLAN:")
        for rec in profile["recommendations"]:
            report.append(f"  → {rec}")

    elif diagnosis_type == "BLOOD_REPORT":
        report.append("DIAGNOSTIC MODALITY: COMPLETE HEMATOLOGY & METABOLIC BIOCHEMISTRY")
        report.append("-" * 72)
        primary = result_data["primary_diagnosis"]
        conf = primary.get("confidence", 0) * 100
        
        report.append(f"PRIMARY CLINICAL DIAGNOSIS:  {primary['condition'].upper()}")
        report.append(f"CONFIDENCE LEVEL:            {conf:.1f}%")
        report.append(f"CLINICAL SEVERITY:           {primary.get('severity', 'Moderate')}")
        report.append(f"PHYSIOLOGICAL SYSTEM:        {primary.get('system', 'Hematologic')}")
        report.append("\nPATHOPHYSIOLOGICAL EVALUATION:")
        report.append(f"  {primary['summary']}")
        
        report.append("\nRECOMMENDED INTERVENTIONS & FOLLOW-UP:")
        for act in primary.get("action_items", []):
            report.append(f"  → {act}")
            
        report.append("\nCRITICAL & ABNORMAL PARAMETERS FLAGGED:")
        abnormal = [p for p in result_data.get("evaluated_parameters", []) if p["status"] != "Normal"]
        if abnormal:
            for p in abnormal:
                report.append(f"  • {p['param']:20s}: {p['value']} {p['unit']:12s} [{p['status']}] (Normal: {p['min']}-{p['max']})")
        else:
            report.append("  All evaluated parameters within baseline physiological boundaries.")
            
    report.append("\n" + "=" * 72)
    report.append("IMPORTANT REGULATORY & MEDICAL DISCLAIMER:")
    report.append("This report is generated using an artificial intelligence clinical support")
    report.append("algorithm for preliminary triage and patient guidance only. It is NOT a")
    report.append("substitute for official medical diagnosis, pathological biopsy, or clinical")
    report.append("judgment of a licensed healthcare practitioner. In case of acute shortness")
    report.append("of breath, severe chest pain, or high fever, seek emergency medical attention.")
    report.append("=" * 72)
    
    return "\n".join(report)
