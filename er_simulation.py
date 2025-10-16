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
# ROOM NAVIGATION + INVENTORY
# --------------------------------------
rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
st.sidebar.header("🏥 Navigation")
if st.session_state.room not in rooms:
    st.session_state.room = "ER"
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
# DIAGNOSTIC SYSTEM
# --------------------------------------
def perform_diagnostics(patient):
    st.subheader("🧪 Order Diagnostic Tests")

    test_type = st.radio("Select Test Type:", ["Imaging", "Lab Test"])
    if test_type == "Imaging":
        imaging_types = ["X-Ray", "CT Scan", "MRI", "Ultrasound"]
        body_parts = ["Chest", "Abdomen", "Head/Brain", "Limb", "Neck", "Pelvis"]
        chosen_imaging = st.selectbox("Select Imaging Type:", imaging_types)
        chosen_body_part = st.selectbox("Select Body Part:", body_parts)
        if st.button("📸 Perform Imaging"):
            result = f"{chosen_imaging} of {chosen_body_part} performed."
            dx = patient["diagnosis"]
            if (dx == "Pneumonia" and chosen_imaging == "X-Ray" and chosen_body_part == "Chest") or \
               (dx == "Stroke" and chosen_imaging == "CT Scan" and chosen_body_part == "Head/Brain") or \
               (dx == "Appendicitis" and chosen_imaging == "Ultrasound" and chosen_body_part == "Abdomen"):
                result += " Findings consistent with suspected diagnosis."
                st.session_state.score += 10
            else:
                result += " No significant findings."
            st.session_state.test_results = result
            st.session_state.treatment_history.append(result)
            st.success(result)

    elif test_type == "Lab Test":
        lab_tests = ["CBC", "Urinalysis", "Biopsy", "Endoscopy", "EKG", "EEG"]
        chosen_test = st.selectbox("Select Diagnostic Test:", lab_tests)
        if st.button("🧬 Perform Test"):
            result = f"{chosen_test} completed."
            dx = patient["diagnosis"]
            if (dx == "Heart attack" and chosen_test == "EKG") or \
               (dx == "Seizure" and chosen_test == "EEG") or \
               (dx == "Pneumonia" and chosen_test == "CBC"):
                result += " Results confirm clinical suspicion."
                st.session_state.score += 10
            else:
                result += " Results inconclusive."
            st.session_state.test_results = result
            st.session_state.treatment_history.append(result)
            st.success(result)

# --------------------------------------
# MAIN INTERFACE
# --------------------------------------
left, right = st.columns([2, 1])

with left:
    st.header("🏥 Main Actions")

    # ER ROOM
    if st.session_state.room == "ER":
        # Show introduction and difficulty only in ER
        st.subheader("👋 Welcome to the ER")
        st.write(f"**Difficulty Level:** {difficulty}")
        st.write("---")

        if st.button("🚨 Receive Next Patient"):
            st.session_state.patient = random.choice(patients)
            st.session_state.treatment_history = []
            st.session_state.test_results = None

        if st.session_state.patient:
            p = st.session_state.patient
            st.write(f"### 🧍 Patient: {p['name']} (Age {p['age']})")
            st.write(f"**Symptoms:** {p['symptoms']}")
            st.write("---")

            # Pre-fill based on patient diagnosis
            default_history = {
                "Heart attack": {
                    "chronic_conditions": ["Heart Disease", "Hypertension"],
                    "allergies": "None",
                    "medications": "Aspirin, Statins",
                    "family_history": "Father had heart disease"
                },
                "Pneumonia": {
                    "chronic_conditions": ["Asthma"],
                    "allergies": "Penicillin",
                    "medications": "Albuterol",
                    "family_history": "No significant history"
                },
                "Stroke": {
                    "chronic_conditions": ["Hypertension", "Diabetes"],
                    "allergies": "None",
                    "medications": "Blood thinners",
                    "family_history": "Mother had stroke"
                },
                "Appendicitis": {
                    "chronic_conditions": [],
                    "allergies": "None",
                    "medications": "None",
                    "family_history": "No significant history"
                },
                "Seizure": {
                    "chronic_conditions": ["Seizure Disorder"],
                    "allergies": "None",
                    "medications": "Diazepam",
                    "family_history": "Brother has epilepsy"
                },
                "Anaphylaxis": {
                    "chronic_conditions": ["Asthma"],
                    "allergies": "Peanuts",
                    "medications": "Inhaler",
                    "family_history": "No significant history"
                },
                "Diabetic Crisis": {
                    "chronic_conditions": ["Diabetes"],
                    "allergies": "None",
                    "medications": "Insulin",
                    "family_history": "Mother has diabetes"
                }
            }

            history = default_history.get(p["diagnosis"], {
                "chronic_conditions": [],
                "allergies": "",
                "medications": "",
                "family_history": ""
            })

            st.write(f"**Chronic Conditions:** {', '.join(history['chronic_conditions']) if history['chronic_conditions'] else 'None'}")
            st.write(f"**Allergies:** {history['allergies'] if history['allergies'] else 'None'}")
            st.write(f"**Current Medications:** {history['medications'] if history['medications'] else 'None'}")
            st.write(f"**Family History:** {history['family_history'] if history['family_history'] else 'None'}")

            # -------------------------
            # Medical History Questionnaire
            # -------------------------
            st.subheader("📝 Medical History")
            with st.form("medical_history_form"):
                chronic_conditions = st.multiselect(
                    "Select chronic conditions the patient has:",
                    ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Kidney Disease", "Liver Disease", "Seizure Disorder", "Other"]
                )
                allergies_input = st.text_input("List any known allergies (comma separated):")
                medications_taken = st.text_area("Current medications the patient is taking:")
                family_history_input = st.text_area("Relevant family medical history:")

                submitted = st.form_submit_button("Save Medical History")
                if submitted:
                    st.session_state.treatment_history.append(
                        f"Medical history recorded: Chronic conditions={chronic_conditions}, Allergies={allergies_input}, Medications={medications_taken}, Family history={family_history_input}"
                    )
                    st.success("✅ Medical history saved.")

            # Allow diagnostics for doctor/nurse/radiologist
            if role in ["Doctor", "Nurse", "Radiologist"]:
                perform_diagnostics(p)

    # SUPPLY ROOM
    elif st.session_state.room == "Supply Room":
        st.subheader("🧰 Hospital Supply Room")
        for item, desc in hospital_supplies.items():
            if st.button(f"Collect {item}"):
                if item not in st.session_state.inventory:
                    st.session_state.inventory.append(item)
                    st.success(f"✅ {item} added to inventory.")
                else:
                    st.info(f"ℹ️ You already have {item}.")
            with st.expander(item):
                st.caption(desc)

    # MEDSTATION
    elif st.session_state.room == "Medstation":
        st.subheader("💉 Emergency Medstation")
        st.write("Dispense emergency and critical-care medications.")
        for med, desc in medstation_meds.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                with st.expander(med):
                    st.caption(desc)
            with col2:
                if st.button(f"Dispense {med}", key=f"dispense_{med}"):
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)
                        st.success(f"✅ {med} added to your inventory.")
                    else:
                        st.info(f"ℹ️ You already have {med}.")

    # PHARMACY
    elif st.session_state.room == "Pharmacy":
        st.subheader("🏪 Hospital Pharmacy")
        st.write("Access long-term and prescription medications for patients.")
        for med, desc in pharmacy_meds.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                with st.expander(med):
                    st.caption(desc)
            with col2:
                if st.button(f"Dispense {med}", key=f"pharmacy_{med}"):
                    if role == "Pharmacist":
                        st.session_state.score += 5
                        st.success(f"💊 Correctly dispensed {med}. +5 points!")
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)
                        st.info(f"{med} added to your inventory.")
                    else:
                        st.warning(f"You already have {med}.")

    # RADIOLOGY LAB
    elif st.session_state.room == "Radiology Lab":
        st.subheader("🩻 Radiology Lab")
        if role not in ["Radiologist", "Doctor", "Nurse"]:
            st.warning("Only medical staff can perform imaging tests.")
        elif st.session_state.patient:
            perform_diagnostics(st.session_state.patient)
        else:
            st.info("No patient available for imaging tests. Return to ER to receive one.")

    # OPERATING ROOM
    elif st.session_state.room == "Operating Room":
        st.subheader("🔪 Operating Room")
        if role != "Surgeon":
            st.warning("Only Surgeons can perform operations.")
        elif st.button("Start Surgery"):
            steps = [
                "Sterilize area",
                "Administer anesthesia",
                "Make incision",
                "Repair or remove organ",
                "Close incision"
            ]
            for step in steps:
                st.write(f"✅ {step}")
            st.success("Surgery completed successfully!")
            st.session_state.score += 15

# -----------------------
# RIGHT SIDE: VITALS & LOG
# -----------------------
with right:
    st.header("🩺 Patient Vitals & Logs")

    if st.session_state.patient:
        p = st.session_state.patient
        st.subheader(f"{p['name']} - Vitals")
        for k, v in p['vitals'].items():
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










