import streamlit as st
import random

# Make full use of the browser width
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",  # <-- This makes it span the full screen width
    initial_sidebar_state="expanded"
)

# Optional: Light CSS to remove padding and align content neatly
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------
# SESSION STATE INITIALIZATION (Top of file)
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
if "next_patient_button_clicked" not in st.session_state:
    st.session_state.next_patient_button_clicked = False

# --------------------------------------
# EXAMPLE PATIENT DATA
# --------------------------------------

patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"}, "diagnosis": "Heart attack",
     "medical_history": {"Allergies": "None", "Past Surgeries": "None", "Current Medications": "None", "Chronic Conditions": "None"}},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"}, "diagnosis": "Pneumonia",
     "medical_history": {"Allergies": "Penicillin", "Past Surgeries": "Appendectomy", "Current Medications": "Ibuprofen", "Chronic Conditions": "Asthma"}},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"}, "diagnosis": "Stroke",
     "medical_history": {"Allergies": "None", "Past Surgeries": "Knee Replacement", "Current Medications": "Aspirin", "Chronic Conditions": "Hypertension"}},
]

# --------------------------------------
# FUNCTION DEFINITIONS
# --------------------------------------

def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []
    st.session_state.score += 10

def perform_diagnostics(patient):
    pass

# --------------------------------------
# SUPPLY ROOM ITEMS WITH DESCRIPTIONS
# --------------------------------------

emergency_supplies = {
    "Defibrillator and Pads": "Used to deliver electric shocks to the heart in case of cardiac arrest.",
    "Oxygen Mask": "Used to deliver oxygen to patients who are experiencing breathing difficulties.",
    "Intubation Kit": "Contains tools required to insert a breathing tube into the airway of a patient.",
    "IV Kit": "Includes intravenous catheter, tape, and other supplies needed to administer IV fluids or medications.",
    "Saline": "Used for irrigation of wounds or to administer hydration through an IV line.",
    "Catheter Kit": "Contains the necessary instruments to insert a urinary catheter into a patient.",
    "Bed Pan": "Used for bedridden patients to urinate or defecate in a safe and hygienic manner.",
    "Tourniquet": "A device used to stop blood flow to a limb in cases of severe bleeding.",
    "Sutures": "Used to close wounds or surgical incisions.",
    "Cervical Collar": "A device used to immobilize a patient's neck to prevent further injury in case of trauma.",
    "Arm Splint": "A rigid device used to immobilize broken or injured limbs.",
    "Test Swabs": "Used for taking samples of bodily fluids, commonly for testing infections.",
    "Glucometer": "A device used to measure blood glucose levels.",
    "Thermometer": "A device used to measure a patient's body temperature."
}

# --------------------------------------
# MAIN LAYOUT: THREE COLUMNS
# --------------------------------------

left_col, main_col, right_col = st.columns([1, 3, 1.2])

# ---------- LEFT COLUMN ----------
with left_col:
    st.header("🏥 Emergency Room Simulation")

    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    st.write(f"Selected Difficulty: {difficulty}")

    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")
    st.write(f"Selected Role: {role}")

    rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
    st.session_state.room = st.radio("Select a Room", rooms, index=rooms.index(st.session_state.room))

    st.write("---")
    st.subheader("📦 Current Inventory")
    if st.session_state.inventory:
        for item in st.session_state.inventory:
            st.write(f"- {item}")
    else:
        st.info("Inventory is empty.")

    if st.button("🗑️ Clear Inventory"):
        st.session_state.inventory = []
        st.warning("Inventory cleared.")

# ---------- MAIN COLUMN ----------
with main_col:
    if st.session_state.room == "ER":
        st.header("🏥 Emergency Room")

        if st.button("Next Patient"):
            st.session_state.next_patient_button_clicked = True

        if st.session_state.get("next_patient_button_clicked", False):
            assign_patient()
            st.session_state.next_patient_button_clicked = False

        if st.session_state.patient:
            patient = st.session_state.patient
            st.subheader("Patient Information")
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Age:** {patient['age']}")
            st.write(f"**Symptoms:** {patient['symptoms']}")

            st.subheader("📜 Medical History Form")
            for key, value in patient['medical_history'].items():
                st.write(f"**{key}:** {value}")
        else:
            st.info("No active patient.")

        elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")
        for item, description in emergency_supplies.items():
            st.subheader(item)
            st.write(description)
elif st.session_state.room == "Supply Room":
    st.header("🛒 Supply Room")
    for item, description in emergency_supplies.items():
        st.subheader(item)
        st.write(description)
        if st.button(f"Add {item} to Inventory", key=f"add_{item}"):
            if item not in st.session_state.inventory:
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")
                st.rerun()  # ✅ Immediately refresh the sidebar to show update
            else:
                st.warning(f"{item} is already in the inventory.")

else:
    st.header(f"🚪 {st.session_state.room}")
    st.info("Room functionality coming soon!")

# ---------- RIGHT COLUMN ----------
with right_col:
    st.subheader("👩‍⚕️ Patient Data")

    if st.session_state.patient:
        patient = st.session_state.patient
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Symptoms:** {patient['symptoms']}")

        st.subheader("🩺 Patient Vitals")
        vitals = patient['vitals']
        st.write(f"**Blood Pressure (BP):** {vitals['BP']}")
        st.write(f"**Heart Rate (HR):** {vitals['HR']}")
        st.write(f"**Oxygen Saturation (O2):** {vitals['O2']}")

        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for treatment in st.session_state.treatment_history:
                st.write(treatment)
        else:
            st.write("No treatments administered yet.")
        st.write("---")
    else:
        st.info("No active patient.")

    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)
