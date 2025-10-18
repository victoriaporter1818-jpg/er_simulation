import streamlit as st
import random

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style for simulated modal (Transfer Patient Summary)
st.markdown("""
<style>
div[data-testid="stExpander"] {
    background-color: #f9f9f9;
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------
# SESSION STATE INITIALIZATION
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
if "next_patient_button_clicked" not in st.session_state:
    st.session_state.next_patient_button_clicked = False

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%", "Temp": "37.0°C"},
     "diagnosis": "Heart attack",
     "medical_history": {"Allergies": "None", "Past Surgeries": "None", "Current Medications": "None", "Chronic Conditions": "None"}},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%", "Temp": "39.2°C"},
     "diagnosis": "Pneumonia",
     "medical_history": {"Allergies": "Penicillin", "Past Surgeries": "Appendectomy", "Current Medications": "Ibuprofen", "Chronic Conditions": "Asthma"}},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%", "Temp": "36.8°C"},
     "diagnosis": "Stroke",
     "medical_history": {"Allergies": "None", "Past Surgeries": "Knee Replacement", "Current Medications": "Aspirin", "Chronic Conditions": "Hypertension"}}
]

# --------------------------------------
# FUNCTIONS
# --------------------------------------
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []
    st.session_state.score = 0

# --------------------------------------
# MEDSTATION MEDICATIONS
# --------------------------------------
medstation_meds = {
    "Acetaminophen": "Used for mild pain and fever reduction.",
    "Morphine": "Strong painkiller for severe pain.",
    "Motrin": "Used for fever and inflammation.",
    "Ondansetron": "Prevents nausea and vomiting.",
    "Phenytoin": "Used for seizure control.",
    "Epinephrine": "Used for anaphylaxis or cardiac arrest.",
    "Glucose": "Used for low blood sugar emergencies.",
    "Hydralazine": "Used to treat high blood pressure.",
    "Midodrine": "Used for low blood pressure.",
    "Heparin": "Blood thinner to prevent clots.",
    "Lasix": "Used to remove excess fluid in heart failure.",
    "Naloxone": "Reverses opioid overdose effects."
}

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 Emergency Room Simulation")

    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    st.write(f"Selected Difficulty: {difficulty}")

    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist"], key="role")
    st.write(f"Selected Role: {role}")

    rooms = ["ER", "Supply Room", "Medstation"]
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
        st.rerun()

# --------------------------------------
# MAIN LAYOUT
# --------------------------------------
col1, col2, col3 = st.columns([0.3, 3.4, 1.3])

# ---- CENTER COLUMN ----
with col2:
    if st.session_state.room == "ER":
        st.header("🏥 Emergency Room")

        if st.button("Next Patient"):
            st.session_state.next_patient_button_clicked = True

        if st.session_state.get("next_patient_button_clicked", False):
            assign_patient()
            st.session_state.next_patient_button_clicked = False

        if st.session_state.patient:
            p = st.session_state.patient
            st.subheader("Patient Information")
            st.write(f"**Name:** {p['name']}")
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Symptoms:** {p['symptoms']}")

            st.subheader("📜 Medical History Form")
            for k, v in p["medical_history"].items():
                st.write(f"**{k}:** {v}")

            # ---------------- USE SUPPLIES ----------------
            if st.session_state.inventory:
                st.subheader("🧰 Use Supplies")
                selected_item = st.selectbox("Select an item to use from inventory:", st.session_state.inventory)
                if st.button("Use Selected Item"):
                    diagnosis = p["diagnosis"]
                    correct_uses = {
                        "Heart attack": ["Defibrillator and Pads", "Oxygen Mask", "IV Kit", "Aspirin"],
                        "Pneumonia": ["Oxygen Mask", "Thermometer", "IV Kit"],
                        "Stroke": ["Oxygen Mask", "IV Kit", "Glucometer", "Blood Pressure Cuff"]
                    }
                    if selected_item in correct_uses.get(diagnosis, []):
                        st.session_state.score += 5
                        feedback = f"✅ Correct use! {selected_item} was appropriate. (+5 points)"
                    else:
                        feedback = f"⚠️ {selected_item} had limited effect."
                    st.session_state.treatment_history.append(f"Used {selected_item} on {p['name']}. {feedback}")
                    st.session_state.inventory.remove(selected_item)
                    st.success(feedback)
                    st.toast(feedback, icon="💉")
                    st.rerun()
            else:
                st.info("No available supplies in your inventory to use.")

            # ---------------- GIVE MEDICATION ----------------
            meds_in_inventory = [m for m in st.session_state.inventory if m.lower() in [
                "acetaminophen", "morphine", "motrin", "ondansetron", "phenytoin",
                "epinephrine", "glucose", "hydralazine", "midodrine", "heparin", "lasix", "naloxone"
            ]]

            if meds_in_inventory:
                st.subheader("💊 Give Medication")
                selected_med = st.selectbox("Select a medication to administer:", meds_in_inventory)

                if st.button("Give Medication"):
                    diagnosis = p["diagnosis"]
                    correct_meds = {
                        "Heart attack": ["Morphine", "Heparin", "Oxygen Mask"],
                        "Pneumonia": ["Motrin", "Acetaminophen", "Oxygen Mask"],
                        "Stroke": ["Heparin", "Glucose"]
                    }

                    if selected_med in correct_meds.get(diagnosis, []):
                        st.session_state.score += 10
                        feedback = f"💊 Correct treatment! {selected_med} helped improve the patient's condition. (+10 points)"
                    else:
                        feedback = f"⚠️ {selected_med} was not very effective for this condition."

                    st.session_state.treatment_history.append(f"Gave {selected_med} to {p['name']}. {feedback}")
                    st.session_state.inventory.remove(selected_med)
                    st.success(feedback)
                    st.toast(feedback, icon="💊")
                    st.rerun()
            else:
                st.info("No medications available in your inventory.")

            # ---------------- TRANSFER PATIENT ----------------
            st.subheader("🏥 Transfer Patient")
            transfer_option = st.selectbox(
                "Select Transfer Destination:",
                ["-- Select --", "Discharge", "Send to Surgery", "Send to ICU"],
                key="transfer_destination"
            )

            if st.button("Confirm Transfer", key="confirm_transfer"):
                with st.expander("🏁 Patient Transfer Summary", expanded=True):
                    total_score = max(0, min(100, int(st.session_state.score)))
                    effectiveness = total_score
                    diagnostic_accuracy = random.randint(60, 100)
                    resource_efficiency = random.randint(50, 95)

                    if total_score >= 85:
                        outcome, color = "🏆 Excellent", "#2ecc71"
                    elif total_score >= 70:
                        outcome, color = "🙂 Good", "#27ae60"
                    elif total_score >= 50:
                        outcome, color = "⚠️ Fair", "#f1c40f"
                    else:
                        outcome, color = "💀 Poor", "#e74c3c"

                    st.markdown(
                        f"<h3 style='text-align:center;color:{color};margin-bottom:0;'>"
                        f"{outcome} — Score: {total_score}/100"
                        f"</h3>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"Transfer decision: **{transfer_option}**")

                    st.write("**Treatment Effectiveness**")
                    st.progress(effectiveness / 100)
                    st.write("**Diagnostic Accuracy**")
                    st.progress(diagnostic_accuracy / 100)
                    st.write("**Resource Management**")
                    st.progress(resource_efficiency / 100)

                    st.write("---")

                    correct_acts = sum("✅" in line for line in st.session_state.treatment_history)
                    limited_acts = sum("limited effect" in line.lower() or "not very effective" in line.lower()
                                       for line in st.session_state.treatment_history)

                    st.markdown("**Action Summary**")
                    st.write(f"- ✅ Effective actions: **{correct_acts}**")
                    st.write(f"- ⚠️ Limited/ineffective actions: **{limited_acts}**")

                    feedback_pool = [
                        "Great clinical judgment and timely interventions!",
                        "Diagnostics were appropriate; consider earlier imaging next time.",
                        "Supplies were used efficiently; watch for redundant meds.",
                        "Good stabilization—optimize sequence of care for better outcomes.",
                        "Consider reassessing vitals before transfer to ensure stability."
                    ]
                    st.write("---")
                    st.markdown(f"**Feedback:** {random.choice(feedback_pool)}")

                    st.write("---")
                    if st.button("🆕 Start New Case", key="start_new_case"):
                        st.session_state.patient = None
                        st.session_state.treatment_history = []
                        st.session_state.score = 0
                        st.rerun()
        else:
            st.info("No active patient.")

    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")
        # (Supply Room contents retained...)

    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")
        # (Medstation contents retained...)

# ---- RIGHT COLUMN ----
with col3:
    st.subheader("👩‍⚕️ Patient Data")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Age:** {p['age']}")
        st.write(f"**Symptoms:** {p['symptoms']}")

        if "vitals" in p and p["vitals"]:
            vitals = p["vitals"]
            st.subheader("🩺 Patient Vitals")
            st.write(f"**BP:** {vitals.get('BP', 'N/A')}")
            st.write(f"**HR:** {vitals.get('HR', 'N/A')}")
            st.write(f"**O2:** {vitals.get('O2', 'N/A')}")
            st.write(f"**Temp:** {vitals.get('Temp', 'N/A')}")
        else:
            st.warning("⚠️ No vitals available for this patient.")

        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for t in st.session_state.treatment_history:
                st.write(t)
        else:
            st.write("No treatments administered yet.")
    else:
        st.info("No active patient.")

    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)
