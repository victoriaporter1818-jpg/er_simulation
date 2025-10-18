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
# CSS FOR LAYOUT SPACING
# --------------------------------------
st.markdown("""
<style>
/* Align center column flush to sidebar, add small gaps between columns */
main[data-testid="stAppViewContainer"] {
    padding-left: 0rem !important;
    margin-left: 0rem !important;
}
.block-container {
    padding-left: 0rem !important;
    margin-left: 0rem !important;
    width: 100% !important;
}
div[data-testid="stHorizontalBlock"] {
    gap: 1.5rem !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
    margin-left: 0rem !important;
    padding-left: 0.5rem !important;
    padding-right: 1.5rem !important;
    width: 100% !important;
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
if "test_results" not in st.session_state:
    st.session_state.test_results = None
if "next_patient_button_clicked" not in st.session_state:
    st.session_state.next_patient_button_clicked = False

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"},
     "diagnosis": "Heart attack",
     "medical_history": {"Allergies": "None", "Past Surgeries": "None", "Current Medications": "None", "Chronic Conditions": "None"}},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"},
     "diagnosis": "Pneumonia",
     "medical_history": {"Allergies": "Penicillin", "Past Surgeries": "Appendectomy", "Current Medications": "Ibuprofen", "Chronic Conditions": "Asthma"}},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"},
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
    st.session_state.score += 10

# --------------------------------------
# SUPPLIES & MEDS
# --------------------------------------
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

medstation_meds = {
    "Acetaminophen": "Used for fever and mild pain relief.",
    "Morphine": "Strong opioid used for severe pain management.",
    "Motrin (Ibuprofen)": "NSAID used to reduce inflammation and pain.",
    "Ondansetron": "Used to treat nausea and vomiting.",
    "Phenytoin": "Anticonvulsant used to control seizures.",
    "Epinephrine": "Used in cases of anaphylaxis or severe allergic reactions.",
    "Glucose": "Used to treat hypoglycemia (low blood sugar).",
    "Hydralazine": "Used to lower blood pressure in hypertensive emergencies.",
    "Midodrine": "Used to raise blood pressure in patients with hypotension.",
    "Heparin": "Anticoagulant used to prevent blood clots.",
    "Lasix (Furosemide)": "Diuretic used to treat fluid overload and hypertension.",
    "Naloxone": "Used to reverse opioid overdose."
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

            # 🧰 USE SUPPLIES SECTION WITH SMART SCORING
if st.session_state.inventory:
    st.subheader("🧰 Use Supplies")
    selected_item = st.selectbox("Select an item to use from inventory:", st.session_state.inventory)

    if st.button("Use Selected Item"):
        p = st.session_state.patient
        diagnosis = p["diagnosis"]
        correct_uses = {
            "Heart attack": ["Defibrillator and Pads", "Oxygen Mask", "IV Kit", "Aspirin"],
            "Pneumonia": ["Oxygen Mask", "Thermometer", "IV Kit"],
            "Stroke": ["Oxygen Mask", "IV Kit", "Glucometer", "Blood Pressure Cuff"]
        }

        # Check if the selected supply matches the condition
        if selected_item in correct_uses.get(diagnosis, []):
            st.session_state.score += 5
            feedback = f"✅ Correct use! {selected_item} was appropriate for {diagnosis}. (+5 points)"
        else:
            feedback = f"⚠️ {selected_item} had limited effect for {diagnosis}."

        st.session_state.treatment_history.append(f"Used {selected_item} on {p['name']}. {feedback}")
        st.session_state.inventory.remove(selected_item)
        st.success(feedback)
        st.toast(feedback, icon="💉")
        st.rerun()
else:
    st.info("No available supplies in your inventory to use.")

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
        st.subheader("🩺 Patient Vitals")
        for k, v in p["vitals"].items():
            st.write(f"**{k}:** {v}")
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
