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

# Medications and Supplies for each room
hospital_supplies = {
    "ER": ["Role Select", "Generate New Patient", "Patient Information", "Patient Medical History"],
    "Supply Room": ["Bandages", "Gauze", "Needles", "Sterile Kits", "IV Lines"],
    "Medstation": ["Aspirin", "Nitroglycerin", "tPA (Clot Buster)", "Insulin", "Morphine"],
    "Operating Room": ["Scalpel", "Sutures", "Surgical Gloves", "Surgical Drapes"],
    "Radiology Lab": ["X-Ray Machine", "CT Scanner", "MRI Scanner", "Ultrasound Machine"],
    "Pharmacy": ["Antibiotics", "Painkillers", "Blood Pressure Meds", "Antihistamines"]
}

# Main layout with 2 columns
col1, col2 = st.columns([3, 1])

# Left Column - Difficulty, Role, and Room Navigation
with col1:
    st.title("AI Emergency Room Simulation")

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
        for item in hospital_supplies["Supply Room"]:
            st.write(f"- {item}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")

    # Medstation specific content
    elif st.session_state.room == "Medstation":
        st.subheader("Medstation")
        for item in hospital_supplies["Medstation"]:
            st.write(f"- {item}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")

    # Operating Room specific content
    elif st.session_state.room == "Operating Room":
        st.subheader("Operating Room")
        for item in hospital_supplies["Operating Room"]:
            st.write(f"- {item}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")
        if st.button("Perform Surgery"):
            st.session_state.score += 20
            st.success("Surgery performed successfully.")

    # Radiology Lab specific content
    elif st.session_state.room == "Radiology Lab":
        st.subheader("Radiology Lab")
        for item in hospital_supplies["Radiology Lab"]:
            st.write(f"- {item}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")
        if st.button("Order X-Ray"):
            st.session_state.score += 15
            st.success("X-Ray ordered successfully.")

    # Pharmacy specific content
    elif st.session_state.room == "Pharmacy":
        st.subheader("Pharmacy")
        for item in hospital_supplies["Pharmacy"]:
            st.write(f"- {item}")
            if st.button(f"Add {item} to Inventory"):
                st.session_state.inventory.append(item)
                st.success(f"{item} added to inventory.")
        if st.button("Fill Prescription for Antibiotics"):
            st.session_state.inventory.append("Antibiotics")
            st.success("Antibiotics prescription filled.")

# Right Column - Vitals, Action Log, and Score
with col2:
    if st.session_state.patient:
        patient = st.session_state.patient
        st.subheader("Patient Vitals")
        for k, v in patient["vitals"].items():
            st.write(f"**{k}:** {v}")
        
        # Action Log: Show recent treatment actions
        st.subheader("📝 Action Log")
        for line in reversed(st.session_state.treatment_history[-10:]):
            st.write(line)
        
        # Display score
        st.subheader("🏆 Score")
        st.metric("Total Score", st.session_state.score)
    else:
        st.info("No active patient.")


