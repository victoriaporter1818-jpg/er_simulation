# --------------------------------------
# FUNCTION TO ASSIGN A NEW PATIENT
# --------------------------------------

def assign_patient():
    # Reset treatment history and patient data
    st.session_state.treatment_history = []  # Clear the treatment history
    
    # Randomly select a new patient from the database
    patient = random.choice(patients)
    st.session_state.patient = patient
    
    # Log the new patient assignment
    st.session_state.treatment_history.append(f"Assigned patient: {patient['name']}")
    
    # Optionally, increase the score when a new patient is assigned
    st.session_state.score += 10

# --------------------------------------
# MAIN CODE
# --------------------------------------

# Create 3 columns layout: Left for navigation, center for content, right for patient data
col1, col2, col3 = st.columns([2, 4, 1])

# --------------------------------------
# LEFT COLUMN (Controls)
# --------------------------------------
with col1:
    # Difficulty Selection
    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    
    # Role Selection
    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")

    # Room Navigation
    st.sidebar.header("🏥 Navigation")
    rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
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
# CENTER COLUMN (Main Content - Room Specific)
# --------------------------------------
with col2:
    if st.session_state.room == "ER":
        # ER Room: Display Patient Information and Next Patient Button
        if st.session_state.patient:
            patient = st.session_state.patient
            st.header(f"👩‍⚕️ Patient: {patient['name']}")
            
            # Display Patient Information
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Age:** {patient['age']}")
            st.write(f"**Symptoms:** {patient['symptoms']}")
            
            # Display Patient Medical History
            st.subheader("📜 Medical History Form")
            medical_history = patient['medical_history']
            for key, value in medical_history.items():
                st.write(f"**{key}:** {value}")

        # Button to assign a new patient
        st.button("Next Patient", on_click=assign_patient)

# --------------------------------------
# RIGHT COLUMN (Patient Data & Treatment History)
# --------------------------------------
with col3:
    if st.session_state.patient:
        patient = st.session_state.patient
        st.header("👨‍⚕️ Patient Data")

        # Display Patient Vitals
        st.subheader("Vitals")
        if "vitals" in patient:
            st.write(f"**Blood Pressure:** {patient['vitals']['BP']}")
            st.write(f"**Heart Rate:** {patient['vitals']['HR']}")
            st.write(f"**Oxygen Saturation:** {patient['vitals']['O2']}")
        else:
            st.warning("Vitals data not available for this patient.")

        # Display Treatment History (now reset every time a new patient is generated)
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
