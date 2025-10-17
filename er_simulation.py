import streamlit as st

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

# Room List
rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

# --------------------------------------
# UI Layout with 3 Columns
# --------------------------------------
col1, col2, col3 = st.columns([1, 3, 1])  # Left (1), Center (3), Right (1)

# --------------------------------------
# Left Column (Game Settings, Room Navigation, Inventory)
# --------------------------------------
with col1:
    st.title("AI Emergency Room Simulation")
    
    # Difficulty and Role Select
    st.subheader("Game Settings")
    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty_selectbox")
    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role_radio")
    
    # Room Navigation
    st.write("---")
    room_selection = st.radio("Move to another room:", rooms, index=rooms.index(st.session_state.room), key="room_navigation")
    st.session_state.room = room_selection  # Update the room when a new room is selected
    
    # Inventory display
    st.write("---")
    st.subheader("📦 Current Inventory")
    if st.session_state.inventory:
        for item in st.session_state.inventory:
            st.write(f"- {item}")
    else:
        st.info("Inventory is empty.")

    if st.button("🗑️ Clear Inventory", key="clear_inventory"):
        st.session_state.inventory = []
        st.warning("Inventory cleared.")

# --------------------------------------
# Center Column (Main Content for Rooms)
# --------------------------------------
with col2:
    if st.session_state.room == "ER":
        st.header("Emergency Room")
        # Show the role-specific details and patient data
        if st.session_state.patient:
            patient = st.session_state.patient
            st.subheader(f"Patient: {patient['name']}")
            st.write(f"**Age**: {patient['age']}")
            st.write(f"**Symptoms**: {patient['symptoms']}")
            st.write(f"**Diagnosis**: {patient['diagnosis']}")
            st.write("---")
            # Patient Treatment History
            st.subheader("Treatment History")
            if st.session_state.treatment_history:
                for treatment in st.session_state.treatment_history:
                    st.write(treatment)
            else:
                st.write("No treatments administered yet.")
        else:
            st.info("No active patient. Please assign a patient.")
        
        # Button for assigning the next patient
        if st.button("👩‍⚕️ Next Patient", on_click=lambda: next_patient()):
            st.session_state.score += 10  # Add points for assigning a new patient

    elif st.session_state.room == "Supply Room":
        st.header("Supply Room")
        st.write("Here you can manage medical supplies.")
        st.write("Add supplies to your inventory.")
        if st.button("Add Oxygen Mask", on_click=lambda: add_to_inventory("Oxygen Mask")):
            st.session_state.inventory.append("Oxygen Mask")
            st.success("Oxygen Mask added to inventory.")
        if st.button("Add Intubation Kit", on_click=lambda: add_to_inventory("Intubation Kit")):
            st.session_state.inventory.append("Intubation Kit")
            st.success("Intubation Kit added to inventory.")
        # You can add more supplies here with similar buttons.

    elif st.session_state.room == "Medstation":
        st.header("Medstation")
        st.write("Here you can add medications.")
        if st.button("Add Aspirin", on_click=lambda: add_to_inventory("Aspirin")):
            st.session_state.inventory.append("Aspirin")
            st.success("Aspirin added to inventory.")
        if st.button("Add Epinephrine", on_click=lambda: add_to_inventory("Epinephrine")):
            st.session_state.inventory.append("Epinephrine")
            st.success("Epinephrine added to inventory.")
        # You can add more medications here with similar buttons.

    elif st.session_state.room == "Operating Room":
        st.header("Operating Room")
        st.write("Here, you can perform surgeries and other complex procedures.")
        # Example surgery buttons
        if st.button("Start Surgery", on_click=lambda: start_surgery()):
            st.success("Surgery started!")

    elif st.session_state.room == "Radiology Lab":
        st.header("Radiology Lab")
        st.write("Here, you can perform imaging tests.")
        if st.button("Take X-ray", on_click=lambda: take_xray()):
            st.success("X-ray completed!")

    elif st.session_state.room == "Pharmacy":
        st.header("Pharmacy")
        st.write("Here you can dispense medications.")
        if st.button("Dispense Painkillers", on_click=lambda: dispense_painkillers()):
            st.success("Painkillers dispensed.")

# --------------------------------------
# Right Column (Vitals, Logs, and Score)
# --------------------------------------
with col3:
    if st.session_state.patient:
        patient = st.session_state.patient
        st.subheader("Patient Vitals")
        st.write(f"**Blood Pressure**: {patient['vitals']['BP']}")
        st.write(f"**Heart Rate**: {patient['vitals']['HR']}")
        st.write(f"**Oxygen Saturation**: {patient['vitals']['O2']}")
    else:
        st.info("No active patient.")
    
    st.write("---")
    st.subheader("📝 Action Log")
    for line in reversed(st.session_state.treatment_history[-10:]):
        st.write(line)

    st.write("---")
    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)

# --------------------------------------
# Helper Functions
# --------------------------------------
def next_patient():
    # Replace the current patient with a new one
    patient_list = [
        {"name": "John Doe", "age": 45, "symptoms": "severe chest pain", "diagnosis": "Heart Attack", "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"}},
        {"name": "Sarah Li", "age": 29, "symptoms": "high fever", "diagnosis": "Pneumonia", "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"}},
        {"name": "James Lee", "age": 61, "symptoms": "difficulty breathing", "diagnosis": "COPD", "vitals": {"BP": "130/85", "HR": 110, "O2": "80%"}},
        # Add more patients as needed
    ]
    
    # Randomly select a new patient
    selected_patient = patient_list[1]  # For simplicity, we'll select a patient (can be randomized)
    st.session_state.patient = selected_patient
    st.session_state.treatment_history.append(f"Assigned new patient: {selected_patient['name']}")

def add_to_inventory(item):
    # Helper function to add items to the inventory
    st.session_state.inventory.append(item)

def start_surgery():
    # Simulate surgery action
    st.session_state.treatment_history.append("Surgery started in Operating Room.")

def take_xray():
    # Simulate X-ray procedure
    st.session_state.treatment_history.append("X-ray taken in Radiology Lab.")

def dispense_painkillers():
    # Simulate dispensing painkillers
    st.session_state.treatment_history.append("Painkillers dispensed in Pharmacy.")
