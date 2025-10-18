import streamlit as st
import random

# --------------------------------------
# SUPPLY ROOM ITEMS WITH DESCRIPTIONS
# --------------------------------------

# Define the emergency supplies with their descriptions
emergency_supplies = {
    "Defibrillator and Pads": "Used to deliver electric shocks to the heart in case of cardiac arrest.",
    "Oxygen Mask": "Used to deliver oxygen to patients who are experiencing breathing difficulties.",
    "Intubation Kit": "Contains tools required to insert a breathing tube into the airway of a patient.",
    "IV Kit": "Includes intravenous catheter, tape, and other supplies needed to administer IV fluids or medications.",
    "Saline and Other IV Fluids": "Used to hydrate patients or deliver medications through an IV line.",
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
# LEFT PANEL (Difficulty & Role Select)
# --------------------------------------

with st.sidebar:
    st.header("🏥 Emergency Room Simulation")
    
    # Difficulty and Role selection moved to the left column
    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    st.write(f"Selected Difficulty: {difficulty}")
    
    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")
    st.write(f"Selected Role: {role}")
    
    # Room Navigation
    st.sidebar.header("Move to Another Room")
    rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
    st.session_state.room = st.sidebar.radio("Select a Room", rooms, index=rooms.index(st.session_state.room))

    # Inventory
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

# --------------------------------------
# MAIN CONTENT AREA (CENTRAL COLUMN)
# --------------------------------------

with st.container():
    col1, col2 = st.columns([2, 1])

    # Main Column (center content)
    with col1:
        if st.session_state.room == "Supply Room":
            st.header("🛒 Supply Room")
            
            # Show all items in the Supply Room with descriptions and an "Add to Inventory" button
            for item, description in emergency_supplies.items():
                st.subheader(item)
                st.write(description)
                if st.button(f"Add {item} to Inventory", key=f"add_{item}"):
                    if item not in st.session_state.inventory:
                        st.session_state.inventory.append(item)
                        st.success(f"{item} added to inventory.")
                    else:
                        st.warning(f"{item} is already in the inventory.")
        
        elif st.session_state.room == "ER":
            st.header("🏥 Emergency Room")
            
            # Show the Next Patient button and patient details in the center column only
            if st.button("Next Patient", key="next_patient_button"):  # Unique key added here
                assign_patient()

            # Display patient data in the center column only
            if st.session_state.patient:
                patient = st.session_state.patient
                st.subheader("Patient Information")
                st.write(f"**Name:** {patient['name']}")
                st.write(f"**Age:** {patient['age']}")
                st.write(f"**Symptoms:** {patient['symptoms']}")
                
                # Patient-specific Medical History Form (ONLY in the center column)
                st.subheader("📜 Medical History Form")
                medical_history = patient['medical_history']
                for key, value in medical_history.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.info("No active patient.")

# --------------------------------------
# RIGHT COLUMN (Patient Data & Logs)
# --------------------------------------

with col2:
    # Show Patient Data in the Right Column
    if st.session_state.patient:
        patient = st.session_state.patient
        st.header("👨‍⚕️ Patient Data")

        # Display Patient Information
        st.subheader("Patient Information")
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Symptoms:** {patient['symptoms']}")

        # Display Patient Vitals
        st.subheader("Vitals")
        if "vitals" in patient:
            st.write(f"**Blood Pressure:** {patient['vitals']['BP']}")
            st.write(f"**Heart Rate:** {patient['vitals']['HR']}")
            st.write(f"**Oxygen Saturation:** {patient['vitals']['O2']}")
        else:
            st.warning("Vitals data not available for this patient.")

        # Display Treatment History (for context)
        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for treatment in st.session_state.treatment_history:
                st.write(treatment)
        else:
            st.write("No treatments administered yet.")

        # Display Score (for context)
        st.subheader("🏆 Score")
        st.metric("Total Score", st.session_state.score)
    else:
        st.info("No active patient.")

# --------------------------------------
# INITIALIZATION (Session State)
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
# Example Patient Data (with Medical History)
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
    # Add more patients as needed
]

# --------------------------------------
# Logic to Assign New Patient
# --------------------------------------
def assign_patient():
    # Randomly select a patient and reset their medical history
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []  # Clear previous treatment history when new patient is assigned
    st.session_state.score += 10

    # Perform Diagnostics (just a placeholder function here)
    perform_diagnostics(patient)

# Display Assign Button
if st.session_state.room == "ER":
    st.button("Next Patient", on_click=lambda: assign_patient())
``
