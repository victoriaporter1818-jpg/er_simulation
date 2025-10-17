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

    # Check for imaging tests
    if test_type == "Imaging":
        imaging_types = ["X-Ray", "CT Scan", "MRI", "Ultrasound"]
        body_parts = ["Chest", "Abdomen", "Head/Brain", "Limb"]
        chosen_imaging = st.selectbox("Select Imaging Type:", imaging_types)
        chosen_body_part = st.selectbox("Select Body Part:", body_parts)

        if st.button("📸 Perform Imaging", key=f"imaging_{chosen_imaging}_{chosen_body_part}"):
            dx = patient["diagnosis"]
            result = f"{chosen_imaging} of {chosen_body_part} performed. "

            # Check if the diagnosis matches the selected imaging test
            if (dx == "Pneumonia" and chosen_imaging == "X-Ray" and chosen_body_part == "Chest"):
                result += "Findings consistent with suspected diagnosis."
                st.session_state.score += 10
                image_url = diagnostic_images["X-Ray"]["Chest"]
                st.image(image_url, caption="Chest X-Ray - Pneumonia", use_container_width=True)
            elif (dx == "Heart attack" and chosen_imaging == "CT Scan" and chosen_body_part == "Chest"):
                result += "Findings consistent with suspected diagnosis."
                st.session_state.score += 10
                image_url = diagnostic_images["CT Scan"]["Chest"]
                st.image(image_url, caption="CT Scan - Heart Attack", use_container_width=True)
            else:
                result += "No findings relevant to diagnosis."
                st.session_state.score -= 5

            st.session_state.test_results = result
            st.success(result)

    # Check for lab tests
    elif test_type == "Lab Test":
        lab_tests = ["Blood Test", "ECG", "EEG"]
        chosen_lab_test = st.selectbox("Select Lab Test:", lab_tests)

        if st.button("🧬 Perform Lab Test", key=f"lab_{chosen_lab_test}"):
            dx = patient["diagnosis"]
            result = f"{chosen_lab_test} ordered. "
            
            if chosen_lab_test == "Blood Test":
                result += "Results pending."
                st.session_state.score += 5
            elif chosen_lab_test == "ECG":
                result += "ECG results show arrhythmia."
                st.session_state.score += 10
                image_url = diagnostic_images["ECG"]["12-lead"]
                st.image(image_url, caption="ECG - Arrhythmia", use_container_width=True)
            elif chosen_lab_test == "EEG":
                result += "EEG results show abnormal brain activity."
                st.session_state.score += 5
                image_url = diagnostic_images["EEG"]["Brain"]
                st.image(image_url, caption="EEG - Abnormal Activity", use_container_width=True)
            
            st.session_state.test_results = result
            st.success(result)

# --------------------------------------
# LEFT PANEL (Patient Interaction)
# --------------------------------------
with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("👩‍⚕️ Patient Details")
        if st.session_state.patient:
            p = st.session_state.patient
            st.write(f"**Name:** {p['name']}")
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Symptoms:** {p['symptoms']}")
            st.write(f"**Diagnosis:** {p['diagnosis']}")
            st.write("---")
        else:
            st.info("No active patient.")

        # Action buttons
        st.write("---")
        if st.session_state.room == "ER":
            st.button("🚑 Assign Patient", on_click=lambda: assign_patient())

    with col2:
        if st.session_state.room == "ER":
            # Action buttons for ER room
            pass

# --------------------------------------
# RIGHT PANEL (Vitals & Logs)
# --------------------------------------
with st.container():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("🩺 Patient Vitals & Logs")
        if st.session_state.patient:
            p = st.session_state.patient
            st.subheader(f"{p['name']} - Vitals")

            # Ensure vitals data exists before trying to display it
            if "vitals" in p:
                for k, v in p["vitals"].items():
                    st.write(f"**{k}:** {v}")
            else:
                st.warning("Vitals data not available for this patient.")
        else:
            st.info("No active patient.")

    with col2:
        st.subheader("📝 Action Log")
        for line in reversed(st.session_state.treatment_history[-10:]):
            st.write(line)

    st.write("---")
    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)

# --------------------------------------
# Patient Assign Logic
# --------------------------------------
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history.append(f"Assigned patient: {patient['name']}")
    st.session_state.score += 10

    # Perform Diagnostics
    perform_diagnostics(patient)










































