import streamlit as st
import random

# --------------------------------------
# STREAMLIT SETUP
# --------------------------------------
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

st.title("🏥 AI Emergency Room Simulation")
st.subheader("Choose your role, treat patients, and manage emergency situations.")
st.write("---")

# --------------------------------------
# ROLE SELECTION
# --------------------------------------
role = st.selectbox("Select your role:", ["-- Choose --", "Nurse", "Doctor", "Surgeon"])

if role == "-- Choose --":
    st.info("👋 Welcome! Please select a role to begin your shift.")
elif role == "Nurse":
    st.success("🩺 You’re on triage duty. Take vitals, record patient history, and provide initial care.")
elif role == "Doctor":
    st.success("⚕️ You’ll diagnose and determine treatment plans for your patients.")
elif role == "Surgeon":
    st.success("🔪 You handle critical surgical procedures in the OR.")
st.write("---")

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
if "treatment_feedback" not in st.session_state:
    st.session_state.treatment_feedback = None
if "treatment_history" not in st.session_state:
    st.session_state.treatment_history = []

# --------------------------------------
# PATIENT GENERATOR
# --------------------------------------
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"}, "diagnosis": "Heart attack"},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"}, "diagnosis": "Pneumonia"},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"}, "diagnosis": "Stroke"},
    {"name": "Emma Brown", "age": 8, "symptoms": "abdominal pain and vomiting for 12 hours",
     "vitals": {"BP": "100/65", "HR": 110, "O2": "98%"}, "diagnosis": "Appendicitis"},
    {"name": "Maya Thompson", "age": 34, "symptoms": "convulsions and unresponsiveness",
     "vitals": {"BP": "130/85", "HR": 112, "O2": "94%"}, "diagnosis": "Seizure"},
    {"name": "Jacob Rivera", "age": 50, "symptoms": "swelling and trouble breathing after eating peanuts",
     "vitals": {"BP": "80/50", "HR": 140, "O2": "82%"}, "diagnosis": "Anaphylaxis"},
    {"name": "Helen Carter", "age": 67, "symptoms": "confusion, sweating, and low blood sugar",
     "vitals": {"BP": "120/80", "HR": 105, "O2": "96%"}, "diagnosis": "Diabetic Crisis"},
]

# --------------------------------------
# ROOM CONTENTS: SUPPLIES & MEDS
# --------------------------------------
hospital_supplies = {
    "IV Fluids (Saline)": "Used to maintain hydration and administer medications.",
    "Intubation Kit": "Used for airway management in critical patients.",
    "Blood Test Kit": "Used to collect and test blood samples.",
    "Swab Kit": "Used for infection testing or viral samples.",
    "Bandages": "Used to dress wounds or stop bleeding.",
    "Ice Pack": "Used to reduce inflammation or pain.",
    "Oxygen Mask": "Used to deliver oxygen to patients.",
    "Bed Pan": "Used for bedridden patients needing toileting assistance.",
    "Vomit Bag": "Used for patients experiencing nausea or vomiting.",
    "Heated Blanket": "Used to prevent hypothermia or comfort shivering patients.",
    "Syringe Pack": "Used for injections or drawing samples.",
    "Defibrillator Pads": "Used to deliver electric shocks during cardiac arrest.",
    "Gloves & PPE": "Personal protective equipment for infection control."
}

hospital_meds = {
    "Ibuprofen": "Pain relief and anti-inflammatory.",
    "Acetaminophen": "Fever reducer and mild pain reliever.",
    "Morphine": "Strong opioid pain medication.",
    "Epinephrine": "Used for anaphylaxis, cardiac arrest, or asthma attacks.",
    "Diazepam": "Used for seizure control or anxiety.",
    "Lorazepam": "Used for seizures or sedation.",
    "Insulin": "Lowers blood sugar in diabetic emergencies.",
    "Nitroglycerin": "Used for chest pain and heart attacks.",
    "Aspirin": "For heart attacks and stroke prevention.",
    "Antibiotics": "Treat bacterial infections.",
    "tPA (Clot Buster)": "Used for ischemic strokes.",
    "Albuterol": "Relieves bronchospasm in asthma.",
    "Ondansetron": "Treats nausea and vomiting.",
    "Ketamine": "Used for sedation and pain management.",
    "Erythropoietin": "Used for anemia management."
}

# --------------------------------------
# SIDEBAR: NAVIGATION + INVENTORY
# --------------------------------------
st.sidebar.header("🏥 Navigation")
st.session_state.room = st.sidebar.radio(
    "Move to another room:",
    ["ER", "Supply Room", "Medstation", "Operating Room", "Nursing Station"],
    index=["ER", "Supply Room", "Medstation", "Operating Room", "Nursing Station"].index(st.session_state.room)
)

# --------------------------------------
# TREATMENT PROTOCOLS
# --------------------------------------
treatment_protocols = {
    "Heart attack": {"correct": ["Aspirin", "Nitroglycerin", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": ["Bandages", "Heated Blanket"], "harmful": ["Insulin", "tPA (Clot Buster)"]},
    "Pneumonia": {"correct": ["Antibiotics", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": ["Acetaminophen", "Ibuprofen"], "harmful": ["Epinephrine", "Nitroglycerin"]},
    "Stroke": {"correct": ["tPA (Clot Buster)", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": ["Heated Blanket"], "harmful": ["Morphine", "Nitroglycerin"]},
    "Appendicitis": {"correct": ["IV Fluids (Saline)", "Antibiotics", "Intubation Kit"], "neutral": ["Heated Blanket"], "harmful": ["Aspirin", "Ibuprofen"]},
    "Seizure": {"correct": ["Diazepam", "Lorazepam", "Oxygen Mask"], "neutral": ["Heated Blanket"], "harmful": ["Morphine", "Nitroglycerin"]},
    "Anaphylaxis": {"correct": ["Epinephrine", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": ["Heated Blanket"], "harmful": ["Morphine", "Nitroglycerin"]},
    "Diabetic Crisis": {"correct": ["Insulin", "IV Fluids (Saline)"], "neutral": ["Heated Blanket"], "harmful": ["Aspirin", "Morphine"]},
}

# --------------------------------------
# MAIN LAYOUT: LEFT (actions) / RIGHT (vitals & logs)
# --------------------------------------
left, right = st.columns([2, 1])

# -------------------
# LEFT: ROOM INTERACTIONS
# -------------------
with left:
    st.header("🏥 Main Actions")
    
    if st.session_state.room == "Supply Room":
        for item, desc in hospital_supplies.items():
            if st.button(f"Collect {item}"):
                if item not in st.session_state.inventory:
                    st.session_state.inventory.append(item)
                    st.success(f"✅ {item} added to inventory.")
                else:
                    st.info(f"ℹ️ You already have {item}.")
            with st.expander(item):
                st.caption(desc)

    elif st.session_state.room == "Medstation":
        for med, desc in hospital_meds.items():
            if st.button(f"Dispense {med}"):
                if med not in st.session_state.inventory:
                    st.session_state.inventory.append(med)
                    st.success(f"💉 {med} added to inventory.")
                else:
                    st.info(f"ℹ️ You already have {med}.")
            with st.expander(med):
                st.caption(desc)

    elif st.session_state.room == "ER":
        if st.button("🚨 Receive Next Patient"):
            st.session_state.patient = random.choice(patients)
            st.session_state.treatment_feedback = None
            st.session_state.treatment_history = []

        if st.session_state.patient:
            p = st.session_state.patient
            st.write(f"### 🧍 Patient: {p['name']} (Age {p['age']})")
            st.write(f"**Symptoms:** {p['symptoms']}")

            # Treatment selection
            if st.session_state.inventory:
                selected_item = st.selectbox("Select an item from your inventory to use:", st.session_state.inventory)
                if st.button("🩹 Use Selected Item"):
                    diagnosis = p["diagnosis"]
                    protocol = treatment_protocols.get(diagnosis, {})
                    correct, neutral, harmful = protocol.get("correct", []), protocol.get("neutral", []), protocol.get("harmful", [])

                    if selected_item in correct:
                        st.session_state.score += 10
                        feedback = f"✅ You used {selected_item}. Correct treatment!"
                        color = "success"
                    elif selected_item in neutral:
                        feedback = f"😐 {selected_item} had little effect."
                        color = "info"
                    elif selected_item in harmful:
                        st.session_state.score -= 10
                        feedback = f"❌ {selected_item} was harmful!"
                        color = "error"
                    else:
                        st.session_state.score -= 2
                        feedback = f"⚠️ {selected_item} had no effect."
                        color = "warning"

                    st.session_state.treatment_feedback = (feedback, color)
                    st.session_state.treatment_history.append(f"{selected_item} → {feedback.split('.')[0]}")

    elif st.session_state.room == "Operating Room":
        st.header("🔪 Operating Room")
        st.info("Perform advanced surgical procedures here (future feature).")

    elif st.session_state.room == "Nursing Station":
        st.header("🗒️ Nursing Station")
        st.write("Review patient charts, update notes, and plan ongoing care.")

# -------------------
# RIGHT: PATIENT VITALS + ACTION LOG
# -------------------
with right:
    st.header("🩺 Patient Vitals & Action Log")

    if st.session_state.patient:
        p = st.session_state.patient
        st.subheader(f"{p['name']} - Vitals")
        for k, v in p['vitals'].items():
            st.write(f"**{k}:** {v}")
    else:
        st.info("No active patient.")

    st.write("---")
    st.subheader("📋 Action Log")
    if st.session_state.treatment_history:
        for line in reversed(st.session_state.treatment_history[-15:]):
            st.write(line)
    else:
        st.info("No actions taken yet.")

    st.write("---")
    st.subheader("🏆 Score")
    st.write(st.session_state.score)

