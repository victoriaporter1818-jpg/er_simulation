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
# CSS for Layout Alignment
# --------------------------------------
st.markdown("""
<style>
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
    gap: 1rem !important; /* Small gap between columns */
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
    padding-left: 1rem !important; /* Add left margin to center content */
    padding-right: 1rem !important; /* ✅ Adds small gap on the right side */
    justify-content: flex-start !important;
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
# SUPPLY ROOM ITEMS
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
        st.experimental_rerun()  # ✅ Immediately refreshes UI

# --------------------------------------
# MAIN LAYOUT
# --------------------------------------
col1, col2, col3 = st.columns([0.3, 3.4, 1.3])

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
        else:
            st.info("No active patient.")

    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")

        color_map = {
            "Airway & Breathing": "#d0f0fd",
            "Circulation & IV": "#d0ffd0",
            "Diagnostics": "#fff6d0",
            "Immobilization": "#ffe0d0",
            "General Care": "#e0d0ff"
        }

        categorized_supplies = {
            "Airway & Breathing": {
                "Oxygen Mask": "Used to deliver oxygen to patients with breathing difficulties.",
                "Intubation Kit": "Contains tools required to insert a breathing tube into the airway.",
                "Defibrillator and Pads": "Delivers electric shocks to the heart in case of cardiac arrest."
            },
            "Circulation & IV": {
                "IV Kit": "Includes catheter and supplies for IV fluids or medications.",
                "Saline and Other IV Fluids": "Used to hydrate or deliver IV medications.",
                "Tourniquet": "Stops blood flow to a limb in severe bleeding."
            },
            "Diagnostics": {
                "Test Swabs": "Used to take samples of bodily fluids for infection testing.",
                "Glucometer": "Measures blood glucose levels.",
                "Thermometer": "Measures body temperature."
            },
            "Immobilization": {
                "Cervical Collar": "Immobilizes the neck to prevent further injury.",
                "Arm Splint": "Used to immobilize broken or injured limbs."
            },
            "General Care": {
                "Catheter Kit": "Used for urinary drainage in immobile patients.",
                "Bed Pan": "For bedridden patients to use safely.",
                "Sutures": "Used to close wounds or surgical incisions."
            }
        }

        for category, supplies in categorized_supplies.items():
            st.markdown(f"<h4 style='background-color:{color_map[category]};padding:6px;border-radius:8px;'>{category}</h4>", unsafe_allow_html=True)
            items = list(supplies.items())
            for i in range(0, len(items), 2):
                colA, colB = st.columns(2)
                for col, (item, description) in zip((colA, colB), items[i:i+2]):
                    with col.expander(item):
                        st.write(description)
                        if st.button(f"Add {item} to Inventory", key=f"add_{item}"):
                            if item not in st.session_state.inventory:
                                st.session_state.inventory.append(item)
                                st.success(f"{item} added to inventory.")
                                st.toast(f"✅ {item} added to inventory!", icon="📦")
                                st.rerun()
                            else:
                                st.warning(f"{item} is already in the inventory.")
                                st.toast(f"⚠️ {item} already in inventory.", icon="⚠️")

    elif st.session_state.room == "Medstation":
        st.header("💉 Medstation")

        med_color_map = {
            "Pain & Fever Relief": "#fddede",
            "Seizure & Neurological": "#e0d0ff",
            "Cardiac & Emergency": "#d0f0fd",
            "Blood Pressure & Circulation": "#d0ffd0",
            "Fluid & Metabolic": "#fff6d0"
        }

        categorized_meds = {
            "Pain & Fever Relief": {
                "Acetaminophen": "Used to relieve mild to moderate pain and reduce fever.",
                "Morphine": "A potent opioid for severe pain management.",
                "Motrin (Ibuprofen)": "An NSAID that reduces pain, inflammation, and fever."
            },
            "Seizure & Neurological": {
                "Phenytoin": "Used to control seizures and prevent epileptic episodes.",
                "Naloxone": "Reverses the effects of opioid overdose quickly and safely."
            },
            "Cardiac & Emergency": {
                "Epinephrine": "Used for anaphylaxis or cardiac arrest; increases heart rate and blood pressure.",
                "Heparin": "Prevents and treats blood clots and deep vein thrombosis.",
                "Lasix (Furosemide)": "A diuretic that removes excess fluid in heart failure or pulmonary edema."
            },
            "Blood Pressure & Circulation": {
                "Hydralazine": "A vasodilator used to lower blood pressure during hypertensive crises.",
                "Midodrine": "Raises blood pressure by constricting blood vessels."
            },
            "Fluid & Metabolic": {
                "Glucose": "Quickly raises blood sugar in hypoglycemic emergencies.",
                "Ondansetron": "Prevents nausea and vomiting post-operation or during chemotherapy."
            }
        }

        for category, meds in categorized_meds.items():
            st.markdown(
                f"<h4 style='background-color:{med_color_map[category]};padding:6px;border-radius:8px;margin-top:10px;'>{category}</h4>",
                unsafe_allow_html=True
            )
            items = list(meds.items())
            for i in range(0, len(items), 2):
                colA, colB = st.columns(2)
                for col, (med, desc) in zip((colA, colB), items[i:i+2]):
                    with col.expander(med):
                        st.write(desc)
                        if st.button(f"Add {med} to Inventory", key=f"add_{med}"):
                            if med not in st.session_state.inventory:
                                st.session_state.inventory.append(med)
                                st.success(f"{med} added to inventory.")
                                st.toast(f"✅ {med} added to inventory!", icon="💊")
                                st.rerun()
                            else:
                                st.warning(f"{med} is already in the inventory.")
                                st.toast(f"⚠️ {med} already in inventory.", icon="⚠️")

# ---- RIGHT COLUMN ----
with col3:
    st.subheader("👩‍⚕️ Patient Data")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Age:** {p['age']}")
        st.write(f"**Symptoms:** {p['symptoms']}")
        vitals = p["vitals"]
        st.subheader("🩺 Patient Vitals")
        st.write(f"**BP:** {vitals['BP']}")
        st.write(f"**HR:** {vitals['HR']}")
        st.write(f"**O2:** {vitals['O2']}")
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
