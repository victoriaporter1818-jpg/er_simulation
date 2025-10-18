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

st.markdown("""
<style>
/* Completely remove Streamlit’s built-in horizontal padding */
.block-container {
    padding-left: 0rem !important;
    margin-left: 0rem !important;
    width: 100% !important;
}

/* Remove invisible padding between sidebar and main body */
section.main > div {
    padding-left: 0rem !important;
    margin-left: 0rem !important;
}

/* Force the internal main content wrapper to hug the sidebar */
main[data-testid="stAppViewContainer"] > div:first-child {
    padding-left: 0rem !important;
    margin-left: 0rem !important;
}

/* Remove column spacing entirely */
div[data-testid="stHorizontalBlock"] {
    gap: 0rem !important;
}

/* Force the center column content to the far left */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
    margin-left: 0rem !important;
    padding-left: 0rem !important;
    width: 100% !important;
    justify-content: flex-start !important;
    align-items: flex-start !important;
}

/* Keep text and widgets aligned to left */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) * {
    text-align: left !important;
    margin-left: 0 !important;
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

# --------------------------------------
# MAIN LAYOUT
# --------------------------------------
col1, col2, col3 = st.columns([0.5, 3.0, 1.2])

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

    # Define color categories for different types of supplies
    color_map = {
        "Airway & Breathing": "#d0f0fd",   # light blue
        "Circulation & IV": "#d0ffd0",     # light green
        "Diagnostics": "#fff6d0",          # light yellow
        "Immobilization": "#ffe0d0",       # light peach
        "General Care": "#e0d0ff"          # light lavender
    }

    # Assign categories to each item
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

    # Two-column grid layout
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
