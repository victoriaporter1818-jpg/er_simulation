import streamlit as st
import random

# --------------------------------------
# STREAMLIT SETUP
# --------------------------------------
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

st.title("🏥 AI Emergency Room Simulation - Hospital Expansion")
st.subheader("Choose your role, diagnose patients, perform procedures, and manage care.")
st.write("---")

# --------------------------------------
# DIFFICULTY LEVEL
# --------------------------------------
difficulty = st.radio("Select Difficulty Level:", ["Beginner", "Intermediate", "Expert"])
difficulty_multiplier = {"Beginner": 1, "Intermediate": 1.5, "Expert": 2}[difficulty]
st.write("---")

# --------------------------------------
# ROLE SELECTION
# --------------------------------------
roles = ["-- Choose --", "Nurse", "Doctor", "Surgeon", "Radiologist", "Pharmacist"]
role = st.selectbox("Select your role:", roles)

role_descriptions = {
    "Nurse": "🩺 You’re on triage duty. Take vitals, record patient history, and provide initial care.",
    "Doctor": "⚕️ Diagnose patients, order tests, and prescribe medications.",
    "Surgeon": "🔪 Perform critical surgical procedures in the OR.",
    "Radiologist": "🩻 Perform and interpret diagnostic imaging such as CT, MRI, and X-rays.",
    "Pharmacist": "💊 Verify prescriptions and dispense correct medications to patients."
}

if role == "-- Choose --":
    st.info("👋 Welcome! Please select a role to begin your shift.")
else:
    st.success(role_descriptions[role])

st.write("---")

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
}

hospital_meds = {
    "Aspirin": "Used for heart attacks and stroke prevention.",
    "Nitroglycerin": "Used for chest pain and heart attacks.",
    "Antibiotics": "Treat bacterial infections.",
    "tPA (Clot Buster)": "Used for ischemic strokes.",
    "Diazepam": "Used for seizure control.",
    "Epinephrine": "Used for anaphylaxis or cardiac arrest.",
    "Insulin": "Used for diabetic emergencies.",
    "Morphine": "Strong opioid pain medication.",
}

# --------------------------------------
# ROOM NAVIGATION + INVENTORY
# --------------------------------------
rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy", "Nursing Station"]

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
            result = f"{chosen_imaging} of {chosen_body_part} performed. "
            dx = patient["diagnosis"]
            if (dx == "Pneumonia" and chosen_imaging == "X-Ray" and chosen_body_part == "Chest") or \
               (dx == "Stroke" and chosen_imaging == "CT Scan" and chosen_body_part == "Head/Brain") or \
               (dx == "Appendicitis" and chosen_imaging == "Ultrasound" and chosen_body_part == "Abdomen"):
                result += "Findings consistent with suspected diagnosis."
                st.session_state.score += 10
            else:
                result += "No significant findings."
            st.session_state.test_results = result
            st.session_state.treatment_history.append(result)
            st.success(result)

    elif test_type == "Lab Test":
        lab_tests = ["CBC", "Urinalysis", "Biopsy", "Endoscopy", "EKG", "EEG"]
        chosen_test = st.selectbox("Select Diagnostic Test:", lab_tests)
        if st.button("🧬 Perform Test"):
            result = f"{chosen_test} completed. "
            dx = patient["diagnosis"]
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
    st.header("🏥 Main Actions")

    if st.session_state.room == "ER":
        if st.button("🚨 Receive Next Patient"):
            st.session_state.patient = random.choice(patients)
            st.session_state.treatment_history = []
            st.session_state.test_results = None

        if st.session_state.patient:
            p = st.session_state.patient
            st.write(f"### 🧍 Patient: {p['name']} (Age {p['age']})")
            st.write(f"**Symptoms:** {p['symptoms']}")
            st.write("---")
            if role in ["Doctor", "Radiologist"]:
                perform_diagnostics(p)

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




