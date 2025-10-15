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
        comp_chance += 0.12
        success_modifier = 20
        msg = "Patient taken to cath lab for angioplasty."
    elif action == "Appendectomy":
        if role != "Surgeon":
            return "Only Surgeons may operate (appendectomy)."
        comp_chance += 0.15
        success_modifier = 25
        msg = "Appendectomy performed."
    elif action == "tPA":
        # stroke thrombolysis risk/benefit
        comp_chance += 0.10
        success_modifier = 18
        msg = "tPA administered for stroke (if eligible)."
    elif action == "Chest x-ray":
        msg = "Chest x-ray obtained: helps confirm pneumonia."
    else:
        msg = f"Performed {action}."
    # result roll
    roll = random.random()
    if roll < comp_chance:
        # complication
        s["stability"] -= random.randint(10, 25)
        log_action(f"Procedure '{action}' had a complication. Stability decreased.")
        outcome_text = f"Procedure had a complication. Patient stability decreased."
    else:
        s["stability"] += success_modifier
        s["treated"] = True
        outcome_text = f"Procedure succeeded; patient improved."
        log_action(f"Procedure '{action}' succeeded. Stability improved by {success_modifier}.")
    # clamp
    s["stability"] = max(0, min(100, s["stability"]))
    return msg + " " + outcome_text + f" (took {time_cost} minutes)."

# ---------- UI layout ----------
left, mid, right = st.columns([1, 2, 1])

# Left column: Controls
with left:
    st.header("Controls")
    if st.button("🚨 Receive Next Patient"):
        spawn_patient()

    st.write("**Move between rooms:**")
    room = st.selectbox("Go to:", ["ER Room", "Supply Room", "Medstation", "Operating Room", "Nursing Station"], index=["ER Room", "Supply Room", "Medstation", "Operating Room", "Nursing Station"].index(st.session_state.room) if st.session_state.room in ["ER Room", "Supply Room", "Medstation", "Operating Room", "Nursing Station"] else 0)
    if room != st.session_state.room:
        st.session_state.room = room
        log_action(f"Moved to {room}.")

    st.write("---")
    st.write("**Inventory**")
    for item, qty in st.session_state.inventory.items():
        st.write(f"{item}: {qty}")

    st.write("---")
    st.write("**Quick actions**")
    if st.button("Advance time by 5 min"):
        update_patient_over_time(minutes=5)
        log_action("Advanced time by 5 minutes.")
    if st.button("Advance time by 15 min"):
        update_patient_over_time(minutes=15)
        log_action("Advanced time by 15 minutes.")

# Middle column: Patient and main workflow
with mid:
    st.header("Patient & Workflow")

    if st.session_state.patient is None:
        st.info("No active patient. Click 'Receive Next Patient' to get a new case.")
    else:
        p = st.session_state.patient
        s = st.session_state.patient_state
        st.subheader(f"🧍 Patient: {p['name']} (Age {p['age']})")
        st.markdown(f"**Symptoms:** {p['symptoms']}")
        st.markdown(f"**Priority:** {p.get('priority', 'N/A')}")
        st.markdown(f"**Stability:** {s['stability']:.1f}/100")
        st.markdown(f"**Pain:** {s['pain']}/10")
        st.markdown(f"**Arrival:** {s['arrival_time']}m ago")

        st.write("**Vitals:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"BP: {p['vitals']['BP_systolic']}/{p['vitals']['BP_diastolic']}")
            st.write(f"HR: {p['vitals']['HR']} bpm")
        with col2:
            st.write(f"O2: {p['vitals']['O2']}%")
            st.write(f"Temp: {p['vitals']['Temp']} °C")
        with col3:
            st.write(f"Diagnosis (hidden until doctor confirms)")

        st.write("---")
        st.subheader("Role-specific actions")
        if st.session_state.room == "ER Room":
            if role == "Nurse":
                if st.button("Take Vitals / Reassess"):
                    # small random variation
                    p["vitals"]["HR"] += random.randint(-3, 3)
                    p["vitals"]["O2"] = max(60, p["vitals"]["O2"] + random.randint(-1, 2))
                    update_patient_over_time(minutes=2)
                    log_action("Nurse took vitals and reassessed patient.")
                # administer item selection
                item_choice = st.selectbox("Use item from inventory:", ["-- choose --"] + [k for k in st.session_state.inventory.keys()])
                if item_choice != "-- choose --":
                    if st.button("Apply item"):
                        msg = apply_item(item_choice)
                        st.info(msg)
            elif role == "Doctor":
                # Diagnostics: view labs / confirm diagnosis
                if st.button("View Vitals (read-only)"):
                    st.write(p["vitals"])
                # diagnostic choice
                diag_choices = ["Heart attack", "Pneumonia", "Stroke", "Appendicitis", "Other"]
                diag_pick = st.selectbox("Suspected diagnosis:", diag_choices)
                if st.button("Confirm diagnosis and recommend treatment"):
                    update_patient_over_time(minutes=3)
                    if diag_pick == p["diagnosis"]:
                        st.success("✅ Correct diagnosis.")
                        log_action("Doctor correctly diagnosed the patient.")
                        # propose treatment choices
                        for t in p["treatment"]:
                            st.write(f"- {t}")
                        st.session_state.patient_state["treated"] = True
                        st.session_state.score += 10
                    else:
                        st.error(f"❌ Incorrect. True diagnosis: {p['diagnosis']}.")
                        log_action("Doctor made incorrect diagnosis.")
                        st.session_state.score -= 5
                # order procedure
                proc = st.selectbox("Order procedure:", ["-- choose --", "CT scan", "Chest x-ray", "tPA", "Cath lab (angioplasty)"])
                if proc != "-- choose --" and st.button("Perform/Order procedure"):
                    result = perform_procedure(proc if proc != "Cath lab (angioplasty)" else "Cath lab (angioplasty)")
                    st.info(result)
            elif role == "Surgeon":
                st.write("Surgeons can move to the OR for operations.")
                if st.button("Move patient to OR"):
                    st.session_state.room = "Operating Room"
                    log_action("Patient moved to Operating Room.")
        elif st.session_state.room == "Supply Room":
            st.subheader("Supply Room — Collect items")
            # show available items with stock (infinite or limited)
            supply_options = ["IV", "Bandage", "Ice Pack", "Oxygen Mask"]
            for it in supply_options:
                col_a, col_b = st.columns([3,1])
                with col_a:
                    st.write(it)
                with col_b:
                    if st.button(f"Take 1 x {it}", key=f"take_{it}"):
                        st.session_state.inventory[it] = st.session_state.inventory.get(it, 0) + 1
                        log_action(f"Picked up 1 x {it} in Supply Room.")
                        st.success(f"{it} added to inventory.")
        elif st.session_state.room == "Medstation":
            st.subheader("Medstation — Get medications")
            meds = ["Aspirin", "Antibiotics"]
            for med in meds:
                col_a, col_b = st.columns([3,1])
                with col_a:
                    st.write(med)
                with col_b:
                    if st.button(f"Dispense 1 x {med}", key=f"med_{med}"):
                        st.session_state.inventory[med] = st.session_state.inventory.get(med, 0) + 1
                        log_action(f"Dispensed 1 x {med} from Medstation.")
                        st.success(f"{med} added to inventory.")
        elif st.session_state.room == "Operating Room":
            st.subheader("Operating Room")
            if role == "Surgeon":
                if st.button("Perform Appendectomy / Major Surgery"):
                    # pick suitable procedure from patient
                    op_name = "Appendectomy" if "Appendicitis" in p["diagnosis"] else "Major surgery"
                    result = perform_procedure(op_name)
                    st.info(result)
            else:
                st.info("Only surgeons may perform operations here.")
        elif st.session_state.room == "Nursing Station":
            st.subheader("Nursing Station")
            if st.button("Write patient notes / update chart"):
                log_action("Nurse charted notes in patient chart.")
                st.success("Chart updated.")
        # After actions, check patient outcome
        outcome = check_patient_outcome()
        if outcome == "deceased":
            st.error("❌ The patient has deteriorated and expired.")
            log_action("Patient died.")
            st.session_state.patient = None
            st.session_state.patient_state = {}
        elif outcome == "discharged_stable":
            st.success("✅ Patient stabilized and discharged.")
            log_action("Patient stabilized and discharged.")
            st.session_state.score += 20
            st.session_state.patient = None
            st.session_state.patient_state = {}

# Right column: Info and history
with right:
    st.header("Current Room")
    st.info(st.session_state.room)

    st.write("---")
 # Right column: Info and history
with right:
    st.header("Current Room")
    st.info(st.session_state.room)

    st.write("---")
    st.header("Action Log")
    if st.session_state.history:
        for line in st.session_state.history[:15]:
            st.write(line)
    else:
        st.write("No actions yet.")

    st.write("---")
    st.header("Performance")
    st.write(f"Score: {st.session_state.score}")

    st.write("---")
    st.header("Quick patient snapshot")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"Name: {p['name']}")
        st.write(f"Symptoms: {p['symptoms']}")
        st.write("Diagnosis (hidden until doctor confirms)")
    else:
        st.write("No active patient.")

