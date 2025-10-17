import streamlit as st
import random

# --------------------------------------
# STREAMLIT SETUP
# --------------------------------------
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

# --------------------------------------
# INITIAL SESSION STATE
# --------------------------------------
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "room" not in st.session_state:
    st.session_state.room = "ER"
if "score" not in st.session_state:
    st.session_state.score = 0
if "patient" not in st.session_state:
    st.session_state.patient = None
if "treatment_history" not in st.session_state:
    st.session_state.treatment_history = []
if "test_results" not in st.session_state:
    st.session_state.test_results = None

# --------------------------------------
# PATIENT DATABASE
# --------------------------------------
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"}, "diagnosis": "Heart attack"},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"}, "diagnosis": "Pneumonia"},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"}, "diagnosis": "Stroke"},
    {"name": "Emma Brown", "age": 8, "symptoms": "abdominal pain and vomiting for 12 hours",
     "vitals": {"BP": "100/65", "HR": 110, "O2": "98%"}, "diagnosis": "Appendicitis"},
    {"name": "Maya Thompson", "age": 34, "symptoms": "convulsions and unresponsiveness",
     "vitals": {"BP": "130/85", "HR": 112, "O2": "94%"}, "diagnosis": "Seizure"},
    {"name": "Jacob Rivera", "age": 50, "symptoms": "swelling and trouble breathing after eating peanuts",
     "vitals": {"BP": "80/50", "HR": 140, "O2": "82%"}, "diagnosis": "Anaphylaxis"},
    {"name": "Helen Carter", "age": 67, "symptoms": "confusion, sweating, and low blood sugar",
     "vitals": {"BP": "120/80", "HR": 105, "O2": "96%"}, "diagnosis": "Diabetic Crisis"},
]

# --------------------------------------
# SUPPLIES & MEDS
# --------------------------------------
hospital_supplies = {
    "IV Fluids (Saline)": "Used to maintain hydration and administer medications.",
    "Intubation Kit": "Used for airway management in critical patients.",
    "Oxygen Mask": "Used to deliver oxygen to patients.",
    "Blood Test Kit": "Used to collect and test blood samples.",
    "Swab Kit": "Used for infection or viral samples.",
    "Defibrillator Pads": "Used to deliver electric shocks during cardiac arrest.",
    "Heated Blanket": "Used to maintain body temperature in hypothermic or post-op patients."
}

medstation_meds = {
    "Aspirin": "Used for heart attacks and stroke prevention.",
    "Nitroglycerin": "Used for chest pain and heart attacks.",
    "tPA (Clot Buster)": "Used for ischemic strokes.",
    "Epinephrine": "Used for anaphylaxis or cardiac arrest.",
    "Insulin": "Used for diabetic emergencies.",
    "Morphine": "Strong opioid pain medication.",
    "Diazepam": "Used for seizure control.",
    "IV Antibiotics": "Used for emergency infection treatment (broad-spectrum).",
}

pharmacy_meds = {
    "Oral Antibiotics": "Treat common bacterial infections (e.g., amoxicillin, doxycycline).",
    "Antifungals": "Treat fungal infections (e.g., fluconazole, clotrimazole).",
    "Inhalers": "Used for asthma and COPD symptom relief.",
    "Antidepressants": "Used to treat mood disorders (SSRIs, SNRIs, etc.).",
    "Cholesterol Meds (Statins)": "Lower LDL cholesterol and prevent heart disease.",
    "Blood Thinners (Warfarin, Heparin)": "Prevent blood clots and strokes.",
    "Antihypertensives": "Used to control high blood pressure.",
    "Steroids": "Used to reduce inflammation (e.g., prednisone)."
}

# --------------------------------------
# ROOM NAVIGATION
# --------------------------------------
rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
st.sidebar.header("🏥 Navigation")
st.session_state.room = st.sidebar.radio("Move to another room:", rooms, index=rooms.index(st.session_state.room))

st.sidebar.write("---")
st.sidebar.subheader("📦 Current Inventory")
if st.session_state.inventory:
    for i in st.session_state.inventory:
        st.sidebar.write(f"- {i}")
else:
    st.sidebar.info("Inventory is empty.")

if st.sidebar.button("🗑️ Clear Inventory"):
    st.session_state.inventory = []
    st.sidebar.warning("Inventory cleared.")

# --------------------------------------
# DIAGNOSTIC SYSTEM (Updated with Detailed Test Images)
# --------------------------------------
diagnostic_images = {
    "X-Ray": {
        "Chest": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Chest_Xray_PA_3-8-2010.png",
        "Abdomen": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Abdomen_X-ray.jpg",
        "Head/Brain": "https://upload.wikimedia.org/wikipedia/commons/e/e8/CT_head.jpg",
        "Limb": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Hand_xray.jpg"
    },
    "CT Scan": {
        "Head/Brain": "https://upload.wikimedia.org/wikipedia/commons/5/59/CT_of_brain_showing_infarction_of_right_MCA_territory.jpg",
        "Chest": "https://upload.wikimedia.org/wikipedia/commons/4/44/CT_Thorax.jpg",
        "Abdomen": "https://upload.wikimedia.org/wikipedia/commons/9/9b/CT_Abdomen.png"
    },
    "MRI": {
        "Head/Brain": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Brain_MRI.jpg",
        "Spine": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Spine_MRI.jpg"
    },
    "Ultrasound": {
        "Abdomen": "https://upload.wikimedia.org/wikipedia/commons/0/00/Normal_liver_ultrasound.jpg",
        "Pelvis": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Pelvic_ultrasound.jpg"
    },
    "Blood Test": {
        "CBC": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Complete_blood_count_report.JPG",
        "Blood Chemistry": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Blood_biochemistry_report_example.jpg"
    },
    "ECG": {
        "12-lead": "https://upload.wikimedia.org/wikipedia/commons/9/99/12_lead_ECG_with_ST_elevation_myocardial_infarction_inferior_leads.png"
    },
    "EEG": {
        "Brain": "https://upload.wikimedia.org/wikipedia/commons/4/4f/EEG_recording.png"
    }
}

def perform_diagnostics(patient):
    st.subheader("🧪 Order Diagnostic Tests")
    test_type = st.radio("Select Test Type:", ["Imaging", "Lab Test"])
    if test_type == "Imaging":
        imaging_types = ["X-Ray", "CT Scan", "MRI", "Ultrasound"]
        body_parts = ["Chest", "Abdomen", "Head/Brain", "Limb"]
        chosen_imaging = st.selectbox("Select Imaging Type:", imaging_types)
        chosen_body_part = st.selectbox("Select Body Part:", body_parts)
        if st.button("📸 Perform Imaging", key=f"imaging_{chosen_imaging}_{chosen_body_part}"):
            dx = patient["diagnosis"]
            result = f"{chosen_imaging} of {chosen_body_part} performed. "
            # patient-specific interpretation
            if (dx == "Pneumonia" and chosen_imaging == "X-Ray" and chosen_body_part == "Chest") or \
               (dx == "Stroke" and chosen_imaging == "CT Scan" and chosen_body_part == "Head/Brain") or \
               (dx == "Appendicitis" and chosen_imaging == "Ultrasound" and chosen_body_part == "Abdomen") or \
               (dx == "Heart attack" and chosen_imaging == "X-Ray" and chosen_body_part == "Chest"):
                result += "Findings consistent with suspected diagnosis."
                st.session_state.score += 10
            else:
                result += "No significant findings."
            st.session_state.test_results = result
            st.session_state.treatment_history.append(result)
            st.success(result)
            # ✅ Display diagnostic image (robust version)
if chosen_imaging in diagnostic_images and chosen_body_part in diagnostic_images[chosen_imaging]:
    image_url = diagnostic_images[chosen_imaging][chosen_body_part]
    st.image(
        image_url,
        caption=f"{chosen_imaging} - {chosen_body_part} (Sample Result)",
        use_container_width=True
    )
else:
    st.warning("No image available for this selection.")

    else:
        lab_tests = ["CBC", "Urinalysis", "Biopsy", "Endoscopy", "EKG", "EEG"]
        chosen_test = st.selectbox("Select Lab Test:", lab_tests)
        if st.button("🧬 Perform Test", key=f"lab_{chosen_test}"):
            dx = patient["diagnosis"]
            result = f"{chosen_test} completed. "
            if (dx == "Heart attack" and chosen_test == "EKG") or \
               (dx == "Seizure" and chosen_test == "EEG") or \
               (dx == "Pneumonia" and chosen_test == "CBC"):
                result += "Results confirm clinical suspicion."
                st.session_state.score += 10
            else:
                result += "Results inconclusive."
            st.session_state.test_results = result
            st.session_state.treatment_history.append(result)
            st.success(result)

# --------------------------------------
# MAIN INTERFACE
# --------------------------------------
left, right = st.columns([2, 1])

with left:
    # --------------------------------------
# ER ROOM
# --------------------------------------
    if st.session_state.room == "ER":
        st.subheader("🚨 Emergency Room")

    # Initialize role in session state if not set
    if "role" not in st.session_state:
        st.session_state.role = "-- Choose --"

    # Role selection
    roles = ["-- Choose --", "Nurse", "Doctor", "Surgeon", "Radiologist", "Pharmacist"]
    st.session_state.role = st.selectbox("Select your role:", roles)

    # Show role description if selected
    if st.session_state.role != "-- Choose --":
        role_descriptions = {
            "Nurse": "🩺 You’re on duty. Take vitals, record patient history, and provide care.",
            "Doctor": "⚕️ Diagnose patients, order tests, and prescribe medications.",
            "Surgeon": "🔪 Perform critical surgical procedures in the OR.",
            "Radiologist": "🩻 Perform and interpret diagnostic imaging.",
            "Pharmacist": "💊 Verify prescriptions and dispense medications."
        }
        st.success(role_descriptions[st.session_state.role])

    st.write("---")

    # Generate new patient button
    if st.button("🚑 Generate New Patient"):
        st.session_state.patient = random.choice(patients)
        st.session_state.treatment_history = []
        st.session_state.test_results = None

    # Display patient info
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"### 🧍 Patient: {p['name']} (Age {p['age']})")
        st.write(f"**Symptoms:** {p['symptoms']}")
        st.write("---")

    # Show vitals
        st.subheader("🩺 Patient Vitals")
        for k, v in p["vitals"].items():
            st.write(f"**{k}:** {v}")

    # Show medical history questionnaire
        st.subheader("📝 Medical History")
        with st.form("medical_history_form"):
            chronic_conditions = st.multiselect(
                "Select chronic conditions the patient has:",
                ["Diabetes", "Hypertension", "Asthma", "Heart Disease",
                 "Kidney Disease", "Liver Disease", "Seizure Disorder", "Other"]
            )
            allergies = st.text_input("List any known allergies (comma separated):")
            medications_taken = st.text_area("Current medications the patient is taking:")
            family_history = st.text_area("Relevant family medical history:")

            submitted = st.form_submit_button("Save Medical History")
            if submitted:
                st.session_state.treatment_history.append(
                    f"Medical history recorded: Chronic conditions={chronic_conditions}, "
                    f"Allergies={allergies}, Medications={medications_taken}, "
                    f"Family history={family_history}"
                )
                st.success("✅ Medical history saved.")

        # Allow diagnostics for Doctors, Radiologists, and Nurses
        if st.session_state.role in ["Doctor", "Radiologist", "Nurse"]:
            perform_diagnostics(p)

    # -----------------------------
    # Supply Room
    # -----------------------------
    elif st.session_state.room == "Supply Room":
        st.subheader("🧰 Hospital Supply Room")
        for item, desc in hospital_supplies.items():
            if st.button(f"Collect {item}", key=f"supply_{item}"):
                if item not in st.session_state.inventory:
                    st.session_state.inventory.append(item)
                    st.success(f"✅ {item} added to inventory.")
                else:
                    st.info(f"ℹ️ Already have {item}.")
            with st.expander(item):
                st.caption(desc)

    # -----------------------------
    # Medstation
    # -----------------------------
    elif st.session_state.room == "Medstation":
        st.subheader("💉 Emergency Medstation")
        for med, desc in medstation_meds.items():
            col1, col2 = st.columns([3,1])
            with col1:
                with st.expander(med):
                    st.caption(desc)
            with col2:
                if st.button(f"Dispense {med}", key=f"med_{med}"):
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)
                        st.success(f"✅ {med} added to inventory.")
                    else:
                        st.info(f"ℹ️ Already have {med}.")

    # -----------------------------
    # Pharmacy
    # -----------------------------
    elif st.session_state.room == "Pharmacy":
        st.subheader("🏪 Hospital Pharmacy")
        for med, desc in pharmacy_meds.items():
            col1, col2 = st.columns([3,1])
            with col1:
                with st.expander(med):
                    st.caption(desc)
            with col2:
                if st.button(f"Dispense {med}", key=f"pharm_{med}"):
                    if st.session_state.role == "Pharmacist":
                        st.session_state.score += 5
                        st.success(f"💊 Correctly dispensed {med}. +5 points!")
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)
                        st.info(f"{med} added to inventory.")
                    else:
                        st.warning(f"ℹ️ Already have {med}.")

    # -----------------------------
    # Radiology Lab
    # -----------------------------
    elif st.session_state.room == "Radiology Lab":
        st.subheader("🩻 Radiology Lab")
        if st.session_state.role != "Radiologist":
            st.warning("Only Radiologists can perform imaging tests.")
        elif st.session_state.patient:
            perform_diagnostics(st.session_state.patient)
        else:
            st.info("No patient available. Generate a patient in the ER first.")

    # -----------------------------
    # Operating Room
    # -----------------------------
    elif st.session_state.room == "Operating Room":
        st.subheader("🔪 Operating Room")
        if st.session_state.role != "Surgeon":
            st.warning("Only Surgeons can perform operations.")
        elif st.button("Start Surgery"):
            steps = ["Sterilize area", "Administer anesthesia", "Make incision", "Repair/Remove organ", "Close incision"]
            for step in steps:
                st.write(f"✅ {step}")
            st.success("Surgery completed successfully!")
            st.session_state.score += 15

# --------------------------------------
# RIGHT PANEL
# --------------------------------------
with right:
    st.header("🩺 Patient Vitals & Logs")
    if st.session_state.patient:
        p = st.session_state.patient
        st.subheader(f"{p['name']} - Vitals")
        for k, v in p["vitals"].items():
            st.write(f"**{k}:** {v}")
    else:
        st.info("No active patient.")

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








































