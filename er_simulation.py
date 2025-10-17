import streamlit as st
import random

# Set up Streamlit page
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

# Initialize session state variables if not already present
if "patient" not in st.session_state:
    st.session_state.patient = None
if "treatment_history" not in st.session_state:
    st.session_state.treatment_history = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "room" not in st.session_state:
    st.session_state.room = "ER"

# Patient database
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath", "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"}, "diagnosis": "Heart attack"},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen", "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"}, "diagnosis": "Pneumonia"},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech", "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"}, "diagnosis": "Stroke"},
    {"name": "Emma Brown", "age": 8, "symptoms": "abdominal pain and vomiting for 12 hours", "vitals": {"BP": "100/65", "HR": 110, "O2": "98%"}, "diagnosis": "Appendicitis"},
]

# Difficulty and Role Selection
difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")

# Assign patient logic
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history.append(f"Assigned patient: {patient['name']}")
    st.session_state.score += 10

# Room navigation logic
rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
room = st.sidebar.radio("Move to another room:", rooms, index=rooms.index(st.session_state.room))
st.session_state.room = room

# Inventory display
st.sidebar.write("---")
st.sidebar.subheader("📦 Current Inventory")
if st.session_state.inventory:
    for item in st.session_state.inventory:
        st.sidebar.write(f"- {item}")
else:
    st.sidebar.info("Inventory is empty.")

if st.sidebar.button("🗑️ Clear Inventory"):
    st.session_state.inventory = []
    st.sidebar.warning("Inventory cleared.")

# Medications and Supplies for each room with descriptions
hospital_supplies = {
    "ER": {
        "Role Select": "Choose your role in the ER (Doctor, Nurse, etc.).",
        "Generate New Patient": "Create a new patient for diagnosis and treatment.",
        "Patient Information": "View the patient's personal information and diagnosis.",
        "Patient Medical History": "View the patient's medical history and treatment log."
    },
    "Supply Room": {
        "Bandages": "Used for dressing wounds and cuts.",
        "Gauze": "Used for cleaning and dressing wounds.",
        "Needles": "Used for injections or IVs.",
        "Sterile Kits": "Used for performing procedures in a sterile environment.",
        "IV Lines": "Used for administering fluids and medications."
    },
    "Medstation": {
        "Aspirin": "Used for pain relief and heart attacks.",
        "Nitroglycerin": "Used for chest pain and heart attack treatment.",
        "tPA (Clot Buster)": "Used to dissolve blood clots in stroke patients.",
        "Insulin": "Used for diabetic patients to regulate blood sugar.",
        "Morphine": "Used for severe pain relief."
    },
    "Operating Room": {
        "Scalpel": "A small, sharp knife used in surgeries.",
        "Sutures": "Used to stitch wounds or surgical incisions.",
        "Surgical Gloves": "Used to maintain a sterile field during surgeries.",
        "Surgical Drapes": "Used to cover and maintain sterile areas during surgery."
    },
    "Radiology Lab": {
        "X-Ray Machine": "Used to capture images of bones and organs.",
        "CT Scanner": "Used to create detailed cross-sectional images of the body.",
        "MRI Scanner": "Used for imaging soft tissues like the brain and muscles.",
        "Ultrasound Machine": "Used for imaging organs and tissues using sound waves."
    },
    "Pharmacy": {
        "Antibiotics": "Used to treat bacterial infections.",
        "Painkillers": "Used for managing mild to severe pain.",
        "Blood Pressure Meds": "Used to control high blood pressure.",
        "Antihistamines": "Used to treat allergic reactions."
    }
}

# Main layout with 3 columns
col1, col2, col3 = st.columns([1, 3, 1])

# Left Column - Difficulty, Role, Room Navigation, and Inventory
with col1:
    st.title("AI Emergency Room Simulation")
    
    # Difficulty and Role Select
    st.subheader("Game Settings")
    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")
    
    # Room Navigation
    st.write("---")
    st.radio("Move to another room:", rooms, index=rooms.index(st.session_state.room))
    
    # Inventory display
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

# Center Column - Main Content of the Current Room
with col2:
    # ER specific content
    if st.session_state.room == "ER":
        st.subheader("ER - Emergency Room")
        if st.session_state.patient:
            patient = st.session_state.patient
            st.subheader(f"Patient: {patient['name']} - {patient['age']} years old")
            st.write(f"**Symptoms:** {patient['symptoms']}")
            st.write(f"**Diagnosis:** {patient['diagnosis']}")
            st.write(f"**Vitals:** {patient['vitals']}")
            st.subheader("Patient Medical History")
            for history in st.session_state.treatment_history:
                st.write(history)
        else:
            st.info("No patient assigned yet.")
        if st.button("🚑 Generate New Patient", on_click=assign_patient):
            pass

    # Supply Room specific content
    elif st.session_state.room == "Supply Room":
        st.subheader("Supply Room")
        for item, description in hospital_supplies["Supply Room"].items():
            st.write(f"**{item}:** {description}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")

    # Medstation specific content
    elif st.session_state.room == "Medstation":
        st.subheader("Medstation")
        for item, description in hospital_supplies["Medstation"].items():
            st.write(f"**{item}:** {description}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")

    # Operating Room specific content
    elif st.session_state.room == "Operating Room":
        st.subheader("Operating Room")
        for item, description in hospital_supplies["Operating Room"].items():
            st.write(f"**{item}:** {description}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")
        if st.button("Perform Surgery"):
            st.session_state.score += 20
            st.success("Surgery performed successfully.")

    # Radiology Lab specific content
    elif st.session_state.room == "Radiology Lab":
        st.subheader("Radiology Lab")
        for item, description in hospital_supplies["Radiology Lab"].items():
            st.write(f"**{item}:** {description}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f
