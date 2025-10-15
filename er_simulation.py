import streamlit as st
import random

# --------------------------------------
# STREAMLIT SETUP
# --------------------------------------
st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

st.title("🏥 AI Emergency Room Simulation - Hospital Expansion")
st.subheader("Choose your role, diagnose patients, perform procedures, and manage care.")
st.write("---")

# --------------------------------------
# DIFFICULTY LEVEL
# --------------------------------------
difficulty = st.radio("Select Difficulty Level:", ["Beginner", "Intermediate", "Expert"])
difficulty_multiplier = {"Beginner": 1, "Intermediate": 1.5, "Expert": 2}[difficulty]
st.write("---")

# --------------------------------------
# ROLE SELECTION
# --------------------------------------
roles = [
"-- Choose --",
"Nurse",
"Doctor",
"Surgeon",
"Radiologist",
"Pharmacist"
]
role = st.selectbox("Select your role:", roles)

role_descriptions = {
"Nurse": "🩺 You’re on triage duty. Take vitals, record patient history, and provide initial care.",
"Doctor": "⚕️ Diagnose patients, order tests, and prescribe medications.",
"Surgeon": "🔪 Perform critical surgical procedures in the OR.",
"Radiologist": "🩻 Perform and interpret diagnostic imaging such as CT, MRI, and X-rays.",
"Pharmacist": "💊 Verify prescriptions and dispense correct medications to patients."
}

if role == "-- Choose --":
  st.info("👋 Welcome! Please select a role to begin your shift.")
else:
  st.success(role_descriptions[role])

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
if "treatment_history" not in st.session_state:
  st.session_state.treatment_history = []
if "test_results" not in st.session_state:
  st.session_state.test_results = None

# --------------------------------------
# PATIENT DATABASE
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
# SUPPLIES & MEDS
# --------------------------------------
hospital_supplies = {
"IV Fluids (Saline)": "Used to maintain hydration and administer medications.",
"Intubation Kit": "Used for airway management in critical patients.",
"Oxygen Mask": "Used to deliver oxygen to patients.",
"Blood Test Kit": "Used to collect and test blood samples.",
"Swab Kit": "Used for infection or viral samples.",
"Defibrillator Pads": "Used to deliver electric shocks during cardiac arrest.",
}

hospital_meds = {
"Aspirin": "Used for heart attacks and stroke prevention.",
"Nitroglycerin": "Used for chest pain and heart attacks.",
"Antibiotics": "Treat bacterial infections.",
"tPA (Clot Buster)": "Used for ischemic strokes.",
"Diazepam": "Used for seizure control.",
"Epinephrine": "Used for anaphylaxis or cardiac arrest.",
"Insulin": "Used for diabetic emergencies.",
"Morphine": "Strong opioid pain medication.",
}

# --------------------------------------
# ROOM NAVIGATION
# --------------------------------------
rooms = [
"ER",
"Supply Room",
"Medstation",
"Operating Room",
"Radiology Lab",
"Pharmacy",
"Nursing Station",
]
st.sidebar.header("🏥 Navigation")
st.session_state.room = st.sidebar.radio("Move to another room:", rooms, index=rooms.index(st.session_state.room))

# --------------------------------------
# TREATMENT PROTOCOLS
# --------------------------------------
treatment_protocols = {
"Heart attack": {"correct": ["Aspirin", "Nitroglycerin", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": [], "harmful": ["Insulin", "tPA (Clot Buster)"]},
"Pneumonia": {"correct": ["Antibiotics", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": [], "harmful": ["Epinephrine", "Nitroglycerin"]},
"Stroke": {"correct": ["tPA (Clot Buster)", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": [], "harmful": ["Morphine", "Nitroglycerin"]},
"Appendicitis": {"correct": ["IV Fluids (Saline)", "Antibiotics", "Intubation Kit"], "neutral": [], "harmful": ["Aspirin", "Ibuprofen"]},
"Seizure": {"correct": ["Diazepam", "Oxygen Mask"], "neutral": [], "harmful": ["Morphine", "Nitroglycerin"]},
"Anaphylaxis": {"correct": ["Epinephrine", "Oxygen Mask", "IV Fluids (Saline)"], "neutral": [], "harmful": ["Morphine", "Nitroglycerin"]},
"Diabetic Crisis": {"correct": ["Insulin", "IV Fluids (Saline)"], "neutral": [], "harmful": ["Aspirin", "Morphine"]},
}

# --------------------------------------
# MAIN INTERFACE
# --------------------------------------
left, right = st.columns([2, 1])

# -----------------------
# LEFT SIDE: MAIN ACTIONS
# -----------------------
with left:
st.header("🏥 Main Actions")

# SUPPLY ROOM
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

# MEDSTATION / PHARMACY
elif st.session_state.room in ["Medstation", "Pharmacy"]:
  st.subheader("💊 Medication Handling")
for med, desc in hospital_meds.items():
if st.button(f"Dispense {med}"):
if role == "Pharmacist":
  st.session_state.score += 5
  st.success(f"💊 You dispensed {med} correctly to the patient.")
if med not in st.session_state.inventory:
  st.session_state.inventory.append(med)
  st.info(f"{med} added to your inventory.")
with st.expander(med):
  st.caption(desc)

# RADIOLOGY LAB
elif st.session_state.room == "Radiology Lab":
if role != "Radiologist":
  st.warning("Only Radiologists can perform imaging tests.")
else:
  st.subheader("🩻 Imaging Options")
  imaging_tests = {
"CT Scan": "Shows internal bleeding or stroke clots.",
"MRI": "Reveals detailed brain or tissue abnormalities.",
"X-Ray": "Displays fractures or pneumonia.",
"Ultrasound": "Detects fluid, gallstones, or pregnancy complications."
}
test_choice = st.selectbox("Select Imaging Test", list(imaging_tests.keys()))
if st.button("📸 Perform Imaging"):
  result = imaging_tests[test_choice]
  st.session_state.test_results = result
  st.success(f"✅ Imaging complete: {result}")
  st.session_state.score += 10

# ER ROOM
elif st.session_state.room == "ER":
if st.button("🚨 Receive Next Patient"):
  st.session_state.patient = random.choice(patients)
  st.session_state.treatment_history = []
  st.session_state.test_results = None

if st.session_state.patient:
  p = st.session_state.patient
  st.write(f"### 🧍 Patient: {p['name']} (Age {p['age']})")
  st.write(f"**Symptoms:** {p['symptoms']}")
  st.write("---")

# Diagnostic test (Doctor access)
if role in ["Doctor", "Radiologist"]:
if st.button("🧪 Request Diagnostic Imaging"):
  imaging = {
"Heart attack": "CT Scan shows cardiac blockage.",
"Pneumonia": "X-Ray reveals lung infiltrates.",
"Stroke": "CT Scan shows ischemic area.",
"Appendicitis": "Ultrasound reveals swollen appendix.",
}
st.info(imaging.get(p["diagnosis"], "No abnormal findings."))

# Treatment selection
if st.session_state.inventory:
  selected_item = st.selectbox("Select an item from inventory:", st.session_state.inventory)
if st.button("🩹 Use Selected Item"):
  dx = p["diagnosis"]
  protocol = treatment_protocols.get(dx, {})
  correct, neutral, harmful = protocol.get("correct", []), protocol.get("neutral", []), protocol.get("harmful", [])

if selected_item in correct:
  st.session_state.score += int(10 * difficulty_multiplier)
  fb = f"✅ You used {selected_item}. Correct treatment!"
elif selected_item in neutral:
  fb = f"😐 {selected_item} had little effect."
elif selected_item in harmful:
  st.session_state.score -= int(10 * difficulty_multiplier)
  fb = f"❌ {selected_item} was harmful!"
else:
  st.session_state.score -= 2
  fb = f"⚠️ {selected_item} had no effect."

  st.session_state.treatment_history.append(fb)
  st.info(fb)

if st.button("🏁 Finish Treatment"):
if st.session_state.score >= 20:
  st.success(f"🎉 Great job! {p['name']} stabilized and is recovering.")
elif st.session_state.score >= 10:
  st.info(f"😐 {p['name']} is stable but needs monitoring.")
else:
  st.error(f"💀 {p['name']} deteriorated. Review treatment choices.")

# OPERATING ROOM
elif st.session_state.room == "Operating Room":
if role != "Surgeon":
  st.warning("Only Surgeons can perform operations.")
else:
if st.button("Start Surgery"):
  steps = ["Sterilize area", "Administer anesthesia", "Make incision", "Repair or remove organ", "Close incision"]
for step in steps:
  st.write(f"✅ {step}")
  st.success("Surgery completed successfully!")
  st.session_state.score += 15

# NURSING STATION
elif st.session_state.room == "Nursing Station":
  st.header("🗒️ Nursing Station")
  st.write("Review charts, update notes, and manage ongoing patient care.")
  st.session_state.score += 2

# -----------------------
# RIGHT SIDE: VITALS & LOG
# -----------------------
with right:
  st.header("🩺 Patient Vitals & Logs")

if st.session_state.patient:
  p = st.session_state.patient
  st.subheader(f"{p['name']} - Vitals")
for k, v in p['vitals'].items():
  st.write(f"**{k}:** {v}")
else:
  st.info("No active patient.")

if st.session_state.test_results:
  st.write("---")
  st.subheader("🧠 Test Results")
  st.info(st.session_state.test_results)

  st.write("---")
  st.subheader("📋 Action Log")
for line in reversed(st.session_state.treatment_history[-10:]):
  st.write(line)

st.write("---")
st.subheader("🏆 Score")
st.metric("Total Score", st.session_state.score)

