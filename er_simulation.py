import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="ER Simulation", layout="wide")

# -------------------------
# INITIAL SESSION STATE SETUP
# -------------------------
if "room" not in st.session_state:
    st.session_state.room = "ER"
if "role" not in st.session_state:
    st.session_state.role = None
if "patient" not in st.session_state:
    st.session_state.patient = None
if "treatment_history" not in st.session_state:
    st.session_state.treatment_history = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "test_results" not in st.session_state:
    st.session_state.test_results = ""

# -------------------------
# SAMPLE IMAGING DATABASE
# -------------------------
sample_imaging = {
    "X-Ray": {
        "Chest": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Chest_Xray_PA_3-8-2010.png",
        "Abdomen": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Abdominal_X-ray.jpg"
    },
    "CT Scan": {
        "Head/Brain": "https://upload.wikimedia.org/wikipedia/commons/3/3c/CT_scan_head.png"
    },
    "MRI": {
        "Head/Brain": "https://upload.wikimedia.org/wikipedia/commons/4/42/MRI_brain.png"
    },
    "Ultrasound": {
        "Abdomen": "https://upload.wikimedia.org/wikipedia/commons/6/63/Ultrasound_abdomen.jpg"
    }
}

# -------------------------
# PATIENT DATABASE
# -------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": ["Chest pain", "Shortness of breath"],
        "diagnosis": "Heart attack",
        "imaging": {"EKG": "ST elevation in anterior leads."},
        "labs": {"Troponin": [0.03, 0.2, 1.5, 3.0, 5.0]},
    },
    {
        "name": "Sarah Lee",
        "age": 32,
        "symptoms": ["Fever", "Cough", "Fatigue"],
        "diagnosis": "Pneumonia",
        "imaging": {"Chest X-Ray": "Left lower lobe consolidation with air bronchograms."},
        "labs": {"WBC": [12, 14, 13, 11, 9]},
    },
    {
        "name": "Michael Chen",
        "age": 64,
        "symptoms": ["Slurred speech", "Right-sided weakness"],
        "diagnosis": "Stroke",
        "imaging": {"CT Brain": "Acute left MCA infarct with loss of grey-white differentiation."},
        "labs": {"INR": [1.0, 1.1, 1.1, 1.0, 1.0]},
    },
    {
        "name": "Emma Davis",
        "age": 22,
        "symptoms": ["Abdominal pain", "Nausea", "Fever"],
        "diagnosis": "Appendicitis",
        "imaging": {"Ultrasound Abdomen": "Non-compressible appendix 9mm with surrounding inflammation."},
        "labs": {"WBC": [11, 13, 15, 14, 12]},
    }
]

# -------------------------
# GENERATE LAB TRENDS
# -------------------------
def generate_lab_trends(patient):
    # Returns a dataframe for plotting trends (if available)
    if "WBC" in patient.get("labs", {}):
        df = pd.DataFrame({"WBC": patient["labs"]["WBC"]}, index=["T0", "T1", "T2", "T3", "T4"])
        return df
    if "Troponin" in patient.get("labs", {}):
        df = pd.DataFrame({"Troponin": patient["labs"]["Troponin"]}, index=["T0", "T1", "T2", "T3", "T4"])
        return df
    if "INR" in patient.get("labs", {}):
        df = pd.DataFrame({"INR": patient["labs"]["INR"]}, index=["T0", "T1", "T2", "T3", "T4"])
        return df
    return None

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
st.sidebar.title("Navigation")

rooms = ["ER", "Radiology", "Pharmacy", "Operating Room", "Medstation"]
# Ensure current room is valid
if st.session_state.room not in rooms:
    st.session_state.room = "ER"

st.session_state.room = st.sidebar.radio("Move to another room:", rooms, index=rooms.index(st.session_state.room))

# Role selection in sidebar (keeps role available globally)
st.sidebar.write("---")
st.sidebar.subheader("👥 Role Selection")
role_choice = st.sidebar.selectbox("Choose your role:", ["-- Choose --", "Doctor", "Nurse", "Surgeon", "Radiologist", "Pharmacist"], index=0)
if role_choice != "-- Choose --":
    st.session_state.role = role_choice

# Difficulty (kept in sidebar to persist)
st.sidebar.write("---")
st.sidebar.subheader("⚙️ Difficulty")
difficulty = st.sidebar.radio("Difficulty level:", ["Beginner", "Intermediate", "Expert"], index=1)
difficulty_multiplier = {"Beginner": 1, "Intermediate": 1.5, "Expert": 2}[difficulty]

st.sidebar.write("---")
st.sidebar.subheader("📦 Current Inventory")
if "inventory" not in st.session_state or not st.session_state.inventory:
    st.sidebar.info("Inventory is empty.")
else:
    for it in st.session_state.inventory:
        st.sidebar.write(f"- {it}")

if st.sidebar.button("🗑️ Clear Inventory"):
    st.session_state.inventory = []
    st.sidebar.warning("Inventory cleared.")

# -------------------------
# MAIN ROOM LOGIC
# -------------------------
left, right = st.columns([2, 1])

with left:
    st.header("🏥 Main Actions")

    if st.session_state.room == "ER":
        st.subheader("Emergency Room")
        st.write(f"**Difficulty:** {difficulty}")
        st.write("---")

        # Patient selection only visible in ER
if st.session_state.room == "ER":
    st.subheader("🚨 Emergency Room")
    st.subheader("🧍 Patient Info")

        # ER ROOM
    if st.session_state.room == "ER":
            st.subheader("🚨 Emergency Room")

    # Generate a new patient when the button is pressed
    if st.button("🆕 Generate New Patient"):
        st.session_state.patient = random.choice(patients)
        st.session_state.treatment_history = []
        st.session_state.test_results = None
        st.success(f"New patient arrived: {st.session_state.patient['name']}!")

    # If a patient is currently active, display their details
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"### 🧍 Patient: {p['name']} (Age {p['age']})")
        st.write(f"**Symptoms:** {p['symptoms']}")
        st.write("---")

        # Allow diagnostics for doctors and radiologists
        if role in ["Doctor", "Radiologist", "Nurse"]:
            perform_diagnostics(p)

        st.session_state.patient = next((p for p in patients if p["name"] == patient_name), None)

        if st.session_state.patient:
            p = st.session_state.patient
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Symptoms:** {', '.join(p['symptoms'])}")
            st.write("---")

            # Show pre-filled history summary (non-editable)
            st.subheader("📝 Pre-filled Medical History (by diagnosis)")
            default_hist = {
                "Heart attack": {"chronic_conditions": ["Heart Disease", "Hypertension"], "allergies": "None", "medications": "Aspirin, Statins", "family_history": "Father had heart disease"},
                "Pneumonia": {"chronic_conditions": ["Asthma"], "allergies": "Penicillin", "medications": "Albuterol", "family_history": "No significant history"},
                "Stroke": {"chronic_conditions": ["Hypertension", "Diabetes"], "allergies": "None", "medications": "Blood thinners", "family_history": "Mother had stroke"},
                "Appendicitis": {"chronic_conditions": [], "allergies": "None", "medications": "None", "family_history": "No significant history"},
            }
            hist = default_hist.get(p["diagnosis"], {"chronic_conditions": [], "allergies": "", "medications": "", "family_history": ""})
            st.write(f"**Chronic Conditions:** {', '.join(hist['chronic_conditions']) if hist['chronic_conditions'] else 'None'}")
            st.write(f"**Allergies:** {hist['allergies'] if hist['allergies'] else 'None'}")
            st.write(f"**Current Medications:** {hist['medications'] if hist['medications'] else 'None'}")
            st.write(f"**Family History:** {hist['family_history'] if hist['family_history'] else 'None'}")
            st.write("---")

            # Editable medical history form (unique key per patient)
            form_key = f"medical_history_form_{p['name'].replace(' ', '_')}"
            with st.form(form_key):
                chronic_conditions = st.multiselect(
                    "Select chronic conditions the patient has:",
                    ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Kidney Disease", "Liver Disease", "Seizure Disorder", "High Cholesterol", "Obesity", "Sleep Apnea", "Other"],
                    default=hist["chronic_conditions"]
                )
                allergies_input = st.text_input("List any known allergies (comma separated):", value=hist["allergies"])
                medications_taken = st.text_area("Current medications the patient is taking:", value=hist["medications"])
                family_history_input = st.text_area("Relevant family medical history:", value=hist["family_history"])
                submitted = st.form_submit_button("Save Medical History")
                if submitted:
                    st.session_state.treatment_history.append(
                        f"Medical history saved for {p['name']}: Chronic conditions={chronic_conditions}, Allergies={allergies_input}, Meds={medications_taken}, Family history={family_history_input}"
                    )
                    st.success("✅ Medical history saved.")

            st.write("---")

            # Diagnostics (allowed for Doctor, Nurse, Radiologist)
            if st.session_state.role in ["Doctor", "Nurse", "Radiologist"]:
                st.subheader("🔬 Diagnostics (Order tests)")
                # perform_diagnostics defined inline here so it can access local variables
                def perform_diagnostics(patient_local):
                    test_type = st.radio("Select Test Type:", ["Imaging", "Lab Test"], key=f"test_type_{patient_local['name']}")
                    if test_type == "Imaging":
                        imaging_types = ["X-Ray", "CT Scan", "MRI", "Ultrasound"]
                        body_parts = ["Chest", "Abdomen", "Head/Brain"]
                        chosen_imaging = st.selectbox("Select Imaging Type:", imaging_types, key=f"imaging_type_{patient_local['name']}")
                        chosen_body_part = st.selectbox("Select Body Part:", body_parts, key=f"imaging_part_{patient_local['name']}")
                        if st.button("📸 Perform Imaging", key=f"imaging_btn_{patient_local['name']}"):
                            dx = patient_local["diagnosis"]
                            key = f"{chosen_imaging} {chosen_body_part}"
                            # look up a patient-specific imaging description (if present)
                            # patient imaging keys may be like "Chest X-Ray" or "CT Brain" or "EKG"
                            # try several key forms to match stored imaging entries
                            findings = (
                                patient_local.get("imaging", {}).get(f"{chosen_imaging} {chosen_body_part}") or
                                patient_local.get("imaging", {}).get(f"{chosen_imaging}") or
                                patient_local.get("imaging", {}).get(f"{chosen_body_part}") or
                                None
                            )
                            if findings:
                                result_text = f"{key} performed. **Findings:** {findings}"
                                st.session_state.score += int(10 * difficulty_multiplier)
                            else:
                                result_text = f"{key} performed. No acute abnormalities detected."
                            st.session_state.test_results = result_text
                            st.session_state.treatment_history.append(result_text)
                            st.success(result_text)
                            # display sample image if available
                            img_url = sample_imaging.get(chosen_imaging, {}).get(chosen_body_part)
                            if img_url:
                                st.image(img_url, caption=f"{chosen_imaging} of {chosen_body_part}")

                    elif test_type == "Lab Test":
                        lab_tests = ["CBC", "Urinalysis", "Biopsy", "Endoscopy", "EKG", "EEG"]
                        chosen_test = st.selectbox("Select Diagnostic Test:", lab_tests, key=f"lab_select_{patient_local['name']}")
                        if st.button("🧬 Perform Test", key=f"lab_btn_{patient_local['name']}"):
                            result_text = f"{chosen_test} performed. Results: "
                            # patient-specific logic for CBC/WBC or Troponin/EKG
                            if chosen_test == "CBC" and "WBC" in patient_local.get("labs", {}):
                                result_text += "WBC trend displayed."
                                df = generate_lab_trends(patient_local)
                                if df is not None:
                                    st.line_chart(df)
                                st.session_state.score += int(10 * difficulty_multiplier)
                            elif chosen_test == "EKG" and "Troponin" in patient_local.get("labs", {}):
                                result_text += "EKG shows ischemic changes; troponin rising."
                                df = generate_lab_trends(patient_local)
                                if df is not None:
                                    st.line_chart(df)
                                st.session_state.score += int(10 * difficulty_multiplier)
                            else:
                                result_text += "Inconclusive or not applicable."
                            st.session_state.test_results = result_text
                            st.session_state.treatment_history.append(result_text)
                            st.success(result_text)

                perform_diagnostics(p)
            else:
                st.info("Role must be Doctor, Nurse, or Radiologist to order diagnostics.")

    else:
        st.info("Switch to the ER room to see patient actions.")

    # Additional rooms handled below (left column)
    if st.session_state.room == "Triage":
        st.subheader("Triage")
        st.write("Triage area for nurse-led assessments and vital checks.")

    elif st.session_state.room == "Medstation":
        st.subheader("Medstation")
        st.write("Access emergency meds (Medstation).")

    elif st.session_state.room == "Pharmacy":
        st.subheader("Pharmacy")
        st.write("Dispense long-term and outpatient meds here.")

    elif st.session_state.room == "Operating Room":
        st.subheader("Operating Room")
        if st.session_state.role != "Surgeon":
            st.warning("Only Surgeons can perform operations.")
        else:
            if st.button("Start Surgery"):
                steps = ["Sterilize area", "Administer anesthesia", "Make incision", "Repair/Remove organ", "Close incision"]
                for s in steps:
                    st.write(f"✅ {s}")
                st.success("Surgery completed successfully!")
                st.session_state.score += int(15 * difficulty_multiplier)

    elif st.session_state.room == "Radiology":
        st.subheader("Radiology")
        st.write("Radiology works with imaging results ordered from ER.")

with right:
    st.header("🩺 Patient Vitals & Logs")

    if st.session_state.patient:
        p = st.session_state.patient
        st.subheader(f"{p['name']} - Vitals")
        # Static vitals for now (could be dynamic later)
        vitals = p.get("vitals", {"BP": "120/80", "HR": 80, "O2": "98%"})
        for k, v in vitals.items():
            st.write(f"**{k}:** {v}")
    else:
        st.info("No active patient selected.")

    if st.session_state.test_results:
        st.write("---")
        st.subheader("🧠 Test Results")
        st.info(st.session_state.test_results)

    st.write("---")
    st.subheader("📋 Action Log")
    for line in reversed(st.session_state.treatment_history[-10:]):
        st.write(line)

    st.write("---")
    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)
















