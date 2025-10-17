import streamlit as st
import random

# Streamlit setup
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

# Initial session state
if "patient" not in st.session_state:
    st.session_state.patient = None
if "treatment_history" not in st.session_state:
    st.session_state.treatment_history = []
if "score" not in st.session_state:
    st.session_state.score = 0

# Patient database
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath", "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"}, "diagnosis": "Heart attack"},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen", "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"}, "diagnosis": "Pneumonia"},
    # Add more patients as necessary
]

# Action to assign patient
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history.append(f"Assigned patient: {patient['name']}")
    st.session_state.score += 10

# Difficulty and Role selection
difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")

# Layout
col1, col2 = st.columns([3, 1])

# Left column: Main content
with col1:
    st.title("AI Emergency Room Simulation")

    # Show patient info if available
    if st.session_state.patient:
        patient = st.session_state.patient
        st.subheader(f"Patient: {patient['name']} - {patient['age']} years old")
        st.write(f"Symptoms: {patient['symptoms']}")
        st.write(f"Diagnosis: {patient['diagnosis']}")
        
        # Show Treatment History
        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for treatment in st.session_state.treatment_history:
                st.write(treatment)
        else:
            st.write("No treatments administered yet.")
    else:
        st.info("No patient selected.")

    # Button to assign a patient (for ER room)
    if st.button("🚑 Assign Patient", on_click=assign_patient):
        pass

# Right column: Patient vitals and action logs
with col2:
    if st.session_state.patient:
        patient = st.session_state.patient
        st.subheader("Patient Vitals")
        if "vitals" in patient:
            for k, v in patient["vitals"].items():
                st.write(f"**{k}:** {v}")
        else:
            st.warning("Vitals data not available.")

        # Action Log: Show last 10 treatment actions
        st.subheader("📝 Action Log")
        for line in reversed(st.session_state.treatment_history[-10:]):
            st.write(line)

        # Display score
        st.write("---")
        st.subheader("🏆 Score")
        st.metric("Total Score", st.session_state.score)
    else:
        st.info("No active patient.")

# --------------------------------------
# Patient Assign Logic
# --------------------------------------











































