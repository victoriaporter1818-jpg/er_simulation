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
if "test_results" not in st.session_state:
    st.session_state.test_results = None
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
     "medical_history": {"Allergies": "None", "Past Surgeries": "Knee Replacement", "Current Medications": "Aspirin", "Chronic Conditions": "Hypertension"}},
]

# --------------------------------------
# FUNCTIONS
# --------------------------------------
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []
    st.session_state.score = 0  # reset score per patient

# --------------------------------------
# SUPPLY ROOM ITEMS
# --------------------------------------
emergency_supplies = {
    "Defibrillator and Pads": "Used to deliver electric shocks to the heart in case of cardiac arrest.",
    "Oxygen Mask": "Used to deliver oxygen to patients who are experiencing breathing difficulties.",
    "IV Kit": "Includes intravenous catheter, tape, and other supplies needed to administer IV fluids or medications.",
    "Tourniquet": "Stops blood flow to a limb in cases of severe bleeding.",
    "Glucometer": "Measures blood glucose levels.",
    "Thermometer": "Measures body temperature."
}

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

    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")
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

            # USE SUPPLIES
            if st.session_state.inventory:
                st.subheader("🧰 Use Supplies")
                selected_item = st.selectbox("Select an item to use from inventory:", st.session_state.inventory)
                if st.button("Use Selected Item"):
                    st.session_state.inventory.remove(selected_item)
                    st.session_state.treatment_history.append(f"Used {selected_item} on {p['name']}. ✅ Correct use!")
                    st.session_state.score += 5
                    st.success(f"✅ {selected_item} used successfully.")
                    st.rerun()
            else:
                st.info("No available supplies in your inventory to use.")

            # GIVE MEDICATIONS
            if st.session_state.inventory:
                meds_in_inv = [item for item in st.session_state.inventory if item in medstation_meds]
                if meds_in_inv:
                    st.subheader("💊 Give Medication")
                    selected_med = st.selectbox("Select a medication to give:", meds_in_inv)
                    if st.button("Administer Medication"):
                        st.session_state.inventory.remove(selected_med)
                        st.session_state.treatment_history.append(f"Gave {selected_med} to {p['name']}. ✅ Correct medication given.")
                        st.session_state.score += 10
                        st.success(f"✅ {selected_med} administered successfully.")
                        st.rerun()
                else:
                    st.info("No medications in your inventory.")
            else:
                st.info("Collect medications from the Medstation first.")

            # TRANSFER PATIENT SECTION
            st.subheader("🏥 Transfer Patient")
            transfer_option = st.selectbox("Select Transfer Destination:", ["-- Select --", "Discharge", "Send to Surgery", "Send to ICU"])
            if st.button("Confirm Transfer"):
                with st.modal("🏁 Patient Transfer Summary"):
                    total_score = min(st.session_state.score, 100)
                    effectiveness = total_score
                    diagnostic_accuracy = random.randint(60, 100)
                    resource_efficiency = random.randint(50, 95)

                    outcome = "🏆 Excellent" if total_score >= 85 else ("🙂 Good" if total_score >= 70 else ("⚠️ Fair" if total_score >= 50 else "💀 Poor"))
                    color = "#2ecc71" if total_score >= 85 else ("#f1c40f" if total_score >= 50 else "#e74c3c")

                    st.markdown(f"<h3 style='text-align:center;color:{color};'>{outcome} - Score: {total_score}/100</h3>", unsafe_allow_html=True)
                    st.progress(effectiveness / 100)
                    st.write(f"**Treatment Effectiveness:** {effectiveness}%")
                    st.progress(diagnostic_accuracy / 100)
                    st.write(f"**Diagnostic Accuracy:** {diagnostic_accuracy}%")
                    st.progress(resource_efficiency / 100)
                    st.write(f"**Resource Management:** {resource_efficiency}%")

                    st.write("---")
                    st.markdown(f"**Feedback:** {random.choice(['Great clinical judgment!', 'Efficient case handling!', 'Consider reviewing diagnostic steps earlier.', 'Supplies and meds used effectively!'])}")

                    if st.button("🆕 Start New Case"):
                        st.session_state.patient = None
                        st.session_state.treatment_history = []
                        st.session_state.score = 0
                        st.rerun()

        else:
            st.info("No active patient.")

    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")
        for item, desc in emergency_supplies.items():
            with st.expander(item):
                st.write(desc)
                if st.button(f"Add {item} to Inventory", key=f"supply_{item}"):
                    if item not in st.session_state.inventory:
                        st.session_state.inventory.append(item)
                        st.success(f"{item} added to inventory.")
                        st.toast(f"✅ {item} added!", icon="📦")
                        st.rerun()
                    else:
                        st.warning(f"{item} already in inventory.")

    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")
        for med, desc in medstation_meds.items():
            with st.expander(med):
                st.write(desc)
                if st.button(f"Add {med} to Inventory", key=f"med_{med}"):
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)
                        st.success(f"{med} added to inventory.")
                        st.toast(f"💊 {med} collected!", icon="💊")
                        st.rerun()
                    else:
                        st.warning(f"{med} already in inventory.")

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
