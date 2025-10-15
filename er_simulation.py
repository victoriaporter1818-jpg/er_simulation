# Full enhanced Streamlit app: room navigation, inventory, patient progression, treatment workflow

import streamlit as st
import random
import time

st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

st.title("🏥 AI Emergency Room Simulation")
st.subheader("Choose your role and interact with dynamic patient cases.")

# ---------- Role selection ----------
role = st.selectbox("Select your role:", ["-- Choose --", "Nurse", "Doctor", "Surgeon"])

if role == "-- Choose --":
    st.info("👋 Welcome! Please select a role to begin your shift.")
elif role == "Nurse":
    st.success("🩺 You’re on triage duty. Take vitals, record patient history, and administer meds.")
elif role == "Doctor":
    st.success("⚕️ You’ll be diagnosing and performing minor procedures like biopsies or intubation.")
elif role == "Surgeon":
    st.success("🔪 You’re scheduled for major procedures, including transplants and trauma surgeries.")

st.write("---")

# ---------- Patients ----------
PATIENT_POOL = [
    {
        "id": 1,
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "vitals": {"BP_systolic": 90, "BP_diastolic": 60, "HR": 120, "O2": 85, "Temp": 36.8},
        "diagnosis": "Heart attack",
        "treatment": ["Aspirin", "Oxygen", "Cath lab (angioplasty)"],
        "priority": 1
    },
    {
        "id": 2,
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "vitals": {"BP_systolic": 110, "BP_diastolic": 70, "HR": 95, "O2": 88, "Temp": 39.2},
        "diagnosis": "Pneumonia",
        "treatment": ["IV antibiotics", "Oxygen", "Chest x-ray"],
        "priority": 2
    },
    {
        "id": 3,
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "vitals": {"BP_systolic": 150, "BP_diastolic": 90, "HR": 82, "O2": 97, "Temp": 36.9},
        "diagnosis": "Stroke",
        "treatment": ["CT scan", "tPA (if eligible)", "Stroke team"],
        "priority": 1
    },
    {
        "id": 4,
        "name": "Emma Brown",
        "age": 8,
        "symptoms": "abdominal pain and vomiting for 12 hours",
        "vitals": {"BP_systolic": 100, "BP_diastolic": 65, "HR": 110, "O2": 98, "Temp": 37.0},
        "diagnosis": "Appendicitis",
        "treatment": ["NPO", "IV fluids", "Emergency appendectomy"],
        "priority": 2
    }
]

# ---------- Session state initialization ----------
if "inventory" not in st.session_state:
    st.session_state.inventory = {"IV": 0, "Bandage": 0, "Ice Pack": 0, "Aspirin": 0, "Antibiotics": 0, "Oxygen Mask": 0}

if "patient" not in st.session_state:
    st.session_state.patient = None

if "time_elapsed" not in st.session_state:
    st.session_state.time_elapsed = 0  # minutes since patient arrival in simulation

if "score" not in st.session_state:
    st.session_state.score = 0

if "history" not in st.session_state:
    st.session_state.history = []  # action log lines

if "room" not in st.session_state:
    st.session_state.room = "ER Room"

if "patient_state" not in st.session_state:
    # will hold patient dynamics: stability (0-100), pain, need flags
    st.session_state.patient_state = {}

# ---------- Helper functions ----------
def log_action(text):
    timestamp = f"{st.session_state.time_elapsed}m"
    st.session_state.history.insert(0, f"[{timestamp}] {text}")
    # limit history length
    if len(st.session_state.history) > 100:
        st.session_state.history = st.session_state.history[:100]

def spawn_patient():
    p = random.choice(PATIENT_POOL).copy()
    # deep-ish copy for vitals
    p["vitals"] = p["vitals"].copy()
    st.session_state.patient = p
    # initialize dynamic state
    st.session_state.patient_state = {
        "stability": 60 + random.randint(-10, 10),  # 0-100 where lower -> critical
        "pain": random.randint(1, 10),
        "bleeding": 0,   # 0 none, 1 minor, 2 major
        "infection_risk": 0,
        "treated": False,
        "arrival_time": st.session_state.time_elapsed
    }
    log_action(f"Patient arrived: {p['name']} ({p['symptoms']})")

def update_patient_over_time(minutes=1):
    """Advance patient internal clock and degrade/improve based on state."""
    for _ in range(minutes):
        st.session_state.time_elapsed += 1
        s = st.session_state.patient_state
        if not s:
            continue
        # baseline deterioration for unstable patients
        instability = max(0, 50 - s["stability"])  # the lower the stability, the higher instability
        deterioration = 0
        # random events: slow deterioration, faster if untreated or severe vitals
        deterioration += 0.5 + (instability * 0.02)
        # if bleeding or high pain increases deterioration
        deterioration += s["bleeding"] * 0.5
        deterioration += (s["pain"] / 20.0)
        # apply deterioration
        s["stability"] -= deterioration
        # infection risk increases slowly if untreated infection-prone cases
        if st.session_state.patient and "Pneumonia" in st.session_state.patient["diagnosis"]:
            s["infection_risk"] += 0.3
        # cap values
        s["stability"] = max(0, min(100, s["stability"]))
        s["infection_risk"] = min(100, s["infection_risk"])

def check_patient_outcome():
    s = st.session_state.patient_state
    if not s:
        return None
    if s["stability"] <= 0:
        return "deceased"
    if s["stability"] >= 100 and s["treated"]:
        return "discharged_stable"
    return None

def apply_item(item):
    """Use an inventory item on patient; return message"""
    if st.session_state.inventory.get(item, 0) <= 0:
        return f"You do not have any {item} in inventory."
    # consume
    st.session_state.inventory[item] -= 1
    s = st.session_state.patient_state
    msg = ""
    if item == "IV":
        s["stability"] += 8
        s["pain"] -= 1
        msg = "Started IV fluids: modest stabilization."
    elif item == "Bandage":
        if s["bleeding"] > 0:
            s["bleeding"] -= 1
            s["stability"] += 6
            msg = "Applied bandage to control bleeding."
        else:
            msg = "Applied bandage; no active bleeding but wound covered."
    elif item == "Ice Pack":
        s["pain"] = max(0, s["pain"] - 2)
        msg = "Ice pack applied: pain reduced."
    elif item == "Aspirin":
        # effective for heart attack scenario (simplified)
        if st.session_state.patient and "Heart attack" in st.session_state.patient["diagnosis"]:
            s["stability"] += 12
            msg = "Administered aspirin — patient shows improvement."
        else:
            s["stability"] += 3
            msg = "Administered aspirin."
    elif item == "Antibiotics":
        if st.session_state.patient and "Pneumonia" in st.session_state.patient["diagnosis"]:
            s["stability"] += 15
            s["infection_risk"] = max(0, s["infection_risk"] - 20)
            msg = "Antibiotics given — infection controlled."
        else:
            s["stability"] += 2
            msg = "Antibiotics given (empiric)."
    elif item == "Oxygen Mask":
        s["stability"] += 10
        st.session_state.patient["vitals"]["O2"] = min(100, st.session_state.patient["vitals"]["O2"] + 6)
        msg = "Oxygen provided — O2 improved."
    # bounds
    s["stability"] = min(100, s["stability"])
    s["pain"] = max(0, s["pain"])
    log_action(f"Used {item} on patient: {msg}")
    return msg

def perform_procedure(action):
    """Procedures like CT scan, surgery, cath lab, etc."""
    p = st.session_state.patient
    s = st.session_state.patient_state
    if not p or not s:
        return "No patient to treat."
    # cost: performing procedures consumes time and has chance for complications
    time_cost = random.randint(5, 20)
    update_patient_over_time(minutes=time_cost)
    comp_chance = 0.08  # baseline complication
    success_modifier = 0
    msg = ""
    if action == "CT scan":
        msg = "Performed CT scan: imaging completed. Useful for stroke/appendicitis."
        success_modifier = 0
    elif action == "Cath lab (angioplasty)":
        if role != "Surgeon" and role != "Doctor":
            return "Only Doctors or Surgeons can call the cath lab / perform interventional procedures."
        comp_chance +=_
