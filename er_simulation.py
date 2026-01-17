import streamlit as st
import random
import time
import math
import pandas as pd
import altair as alt

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=2000, key="ecg_refresh")

# --------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------
defaults = {
    "inventory": [],
    "room": "ER",
    "score": 0,
    "patient": None,
    "treatment_history": [],
    "diagnostic_history": [],
    "last_update": time.time(),
    "patient_status": "Stable",
    "case_start_time": None,
    "mistakes": 0,
    "paused": False,
    "case_complete": False,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "entered_diagnosis" not in st.session_state:
    st.session_state.entered_diagnosis = ""

if "handoff_decision" not in st.session_state:
    st.session_state.handoff_decision = None

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "diagnosis": "Heart attack",
        "vitals": {
            "BP": "90/60",
            "HR": 120,
            "O2": "85%",
            "RR": 28,
            "Temp": 37.0,
        },
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "diagnosis": "Pneumonia",
        "vitals": {
            "BP": "110/70",
            "HR": 95,
            "O2": "88%",
            "RR": 26,
            "Temp": 39.2,
        },
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "diagnosis": "Stroke",
        "vitals": {
            "BP": "150/90",
            "HR": 82,
            "O2": "97%",
            "RR": 18,
            "Temp": 36.8,
        },
    },
]

# --------------------------------------
# DIAGNOSTIC RESULTS
# --------------------------------------
diagnostic_results = {
    "Heart attack": {
        "X-Ray": "Chest X-ray shows mild pulmonary congestion.",
        "CT Scan": "CT chest shows coronary artery calcifications.",
        "MRI": "MRI reveals myocardial ischemia.",
        "Ultrasound": "Echocardiogram shows reduced left ventricular function.",
        "CBC": "CBC within normal limits.",
        "Blood Test": "Troponin markedly elevated — myocardial infarction confirmed.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated for acute coronary syndrome.",
    },
    "Pneumonia": {
        "X-Ray": "Chest X-ray shows right lower lobe infiltrates.",
        "CT Scan": "CT chest shows consolidation consistent with pneumonia.",
        "MRI": "MRI not typically indicated for pneumonia.",
        "Ultrasound": "Lung ultrasound shows B-lines and consolidation.",
        "CBC": "Elevated white blood cell count — infection likely.",
        "Blood Test": "Inflammatory markers elevated.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated — infection suspected.",
    },
    "Stroke": {
        "X-Ray": "Chest X-ray unremarkable.",
        "CT Scan": "CT head shows acute ischemic changes.",
        "MRI": "MRI brain confirms ischemic stroke.",
        "Ultrasound": "Carotid ultrasound shows reduced flow.",
        "CBC": "CBC within normal limits.",
        "Blood Test": "Glucose mildly elevated.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated for acute stroke.",
    },
}

# --------------------------------------
# ECG GENERATOR
# --------------------------------------
def generate_ecg(diagnosis, hr, length=120):
    ecg = []
    beat_interval = max(6, int(60 / max(hr, 40)))

    for i in range(length):
        baseline = random.uniform(-0.05, 0.05)

        if i % beat_interval == 0:
            spike = random.uniform(2.5, 4.0)

            if diagnosis == "Heart attack":
                spike *= random.uniform(0.6, 1.6)
                baseline += random.uniform(-0.6, 0.6)
            elif diagnosis == "Pneumonia":
                spike *= 0.9
            elif diagnosis == "Stroke":
                spike *= 1.1

            ecg.append(spike + baseline)
        else:
            decay = math.exp(-(i % beat_interval) / 2)
            ecg.append(decay * random.uniform(0.1, 0.4) + baseline)

    return ecg

# --------------------------------------
# CORE FUNCTIONS
# --------------------------------------
def assign_patient():
    st.session_state.patient = random.choice(patients)
    st.session_state.inventory.clear()
    st.session_state.score = 0
    st.session_state.treatment_history.clear()
    st.session_state.diagnostic_history.clear()
    st.session_state.patient_status = "Stable"
    st.session_state.case_start_time = time.time()
    st.session_state.last_update = time.time()
    st.session_state.mistakes = 0
    st.session_state.case_complete = False


def restart_simulation():
    for k, v in defaults.items():
        st.session_state[k] = v


def update_vitals(effect):
    if st.session_state.paused:
        return

    v = st.session_state.patient["vitals"]

    hr = int(v["HR"])
    o2 = int(v["O2"].replace("%", ""))
    rr = int(v["RR"])
    temp = float(v["Temp"])
    sys, dia = map(int, v["BP"].split("/"))

    if effect == "improve":
        hr = max(55, hr - random.randint(2, 6))
        o2 = min(100, o2 + random.randint(2, 5))
        rr = max(12, rr - random.randint(1, 3))
        sys = min(140, sys + random.randint(2, 5))
        dia = min(90, dia + random.randint(1, 3))
        temp = max(36.5, temp - random.uniform(0.1, 0.3))
    else:
        hr = min(170, hr + random.randint(4, 8))
        o2 = max(65, o2 - random.randint(3, 6))
        rr = min(40, rr + random.randint(2, 4))
        sys = max(70, sys - random.randint(4, 8))
        dia = max(40, dia - random.randint(2, 4))
        temp = min(41.0, temp + random.uniform(0.2, 0.4))

    v["HR"] = hr
    v["O2"] = f"{o2}%"
    v["RR"] = rr
    v["BP"] = f"{sys}/{dia}"
    v["Temp"] = round(temp, 1)


def gradual_deterioration():
    if st.session_state.paused:
        return
    if time.time() - st.session_state.last_update > 45:
        update_vitals("worsen")
        st.session_state.last_update = time.time()


def check_patient_outcome():
    if st.session_state.paused:
        return
    p = st.session_state.patient
    hr = int(p["vitals"]["HR"])
    o2 = int(p["vitals"]["O2"].replace("%", ""))

    if hr > 130 or hr < 45 or o2 < 85:
        st.session_state.patient_status = "Critical"
    else:
        st.session_state.patient_status = "Stable"

    if o2 <= 70 or hr >= 160 or hr <= 35 or st.session_state.mistakes >= 5:
        st.session_state.patient_status = "Deceased"
        st.session_state.case_complete = True

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("⏸️ Game Control")

    if st.session_state.paused:
        if st.button("▶️ Resume"):
            st.session_state.paused = False
            st.session_state.last_update = time.time()
            st.rerun()
    else:
        if st.button("⏸️ Pause"):
            st.session_state.paused = True
            st.rerun()

    if st.session_state.paused:
        st.warning("Simulation Paused")

    st.divider()
    st.header("🏥 ER Simulation")
    st.session_state.room = st.radio(
        "Select Room",
        ["ER", "Supply Room", "Medstation", "Diagnostic Lab"]
    )

    st.subheader("📦 Inventory")
    if st.session_state.inventory:
        for i in st.session_state.inventory:
            st.write(f"- {i}")
    else:
        st.info("Inventory empty")

# --------------------------------------
# LAYOUT
# --------------------------------------
col2, col3 = st.columns([3.4, 1.3])

# --------------------------------------
# CENTER COLUMN
# --------------------------------------
with col2:

    if st.session_state.room == "ER":

        if not st.session_state.patient:
            st.header("🏥 Emergency Room")
            if st.button("🆕 Generate Patient"):
                assign_patient()
                st.rerun()

        else:
            gradual_deterioration()
            check_patient_outcome()

            p = st.session_state.patient
            v = p["vitals"]
            st.subheader(f"Status: {st.session_state.patient_status}")

            def vital_color(val, low, high):
                if val < low:
                    return "#f1c40f"
                if val > high:
                    return "#e74c3c"
                return "#2ecc71"

            sys, dia = map(int, v["BP"].split("/"))
            hr = v["HR"]
            o2 = int(v["O2"].replace("%", ""))
            rr = v["RR"]
            temp = v["Temp"]

            st.markdown(
                f"""
                <div style="background:#000;padding:16px;border-radius:12px;
                            box-shadow:0 0 14px rgba(0,255,0,0.35);font-family:monospace;">
                    <h4 style="color:#39FF14;">📺 Patient Monitor</h4>
                    <div style="color:{vital_color(hr,60,110)};">❤️ HR: {hr} bpm</div>
                    <div style="color:{vital_color(o2,92,100)};">💨 SpO₂: {o2}%</div>
                    <div style="color:{vital_color(rr,12,20)};">🫁 RR: {rr} /min</div>
                    <div style="color:{vital_color(sys,90,140)};">🩺 BP: {sys}/{dia}</div>
                    <div style="color:{vital_color(temp,36.0,38.0)};">🌡 Temp: {temp:.1f} °C</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            ecg_values = generate_ecg(p["diagnosis"], hr)
            ecg_df = pd.DataFrame({"Time": range(len(ecg_values)), "ECG": ecg_values})

            ecg_chart = (
                alt.Chart(ecg_df)
                .mark_line(color="#39FF14")
                .encode(
                    x=alt.X("Time", title=None),
                    y=alt.Y("ECG", scale=alt.Scale(domain=[-1, 5]), title=None),
                )
                .properties(height=160)
            )

            st.altair_chart(ecg_chart, use_container_width=True)

            st.divider()
            st.subheader("🧰 Use Supplies")

            if st.session_state.inventory:
                selected_item = st.selectbox(
                    "Select supply",
                    st.session_state.inventory,
                    key="use_supply_dropdown"
                )

                if st.button("Use Selected Supply"):
                    if selected_item == "Oxygen Mask":
                        update_vitals("improve")
                        st.session_state.score += 5
                        message = "🫁 Oxygen mask applied — breathing improved."
                    else:
                        update_vitals("worsen")
                        st.session_state.mistakes += 1
                        message = f"⚠️ {selected_item} used — limited clinical effect."

                    st.session_state.inventory.remove(selected_item)
                    st.session_state.treatment_history.append(message)
                    st.session_state.last_update = time.time()
                    st.toast(message)
                    st.rerun()
            else:
                st.info("No supplies available in inventory.")

            # -------- Clinical Reasoning --------
            st.divider()
            st.subheader("🧠 Clinical Reasoning")

            st.text_input(
                "Enter Working Diagnosis",
                key="entered_diagnosis",
                placeholder="e.g. Pneumonia, Stroke, Heart attack"
            )

            if st.button("Confirm Diagnosis"):
                correct_dx = p["diagnosis"].lower()
                entered_dx = st.session_state.entered_diagnosis.lower().strip()

                if correct_dx in entered_dx or entered_dx in correct_dx:
                    st.success("✅ Correct diagnosis identified.")
                    st.session_state.score += 15
                    st.session_state.treatment_history.append(
                        f"🧠 Correct diagnosis identified: {p['diagnosis']}."
                    )
                else:
                    st.error("❌ Incorrect diagnosis.")
                    st.session_state.mistakes += 1
                    st.session_state.treatment_history.append(
                        f"❌ Incorrect diagnosis entered: '{st.session_state.entered_diagnosis}'."
                    )

            # -------- Handoff --------
            st.divider()
            st.subheader("📞 Patient Handoff")

            handoff = st.radio(
                "Choose Handoff Destination",
                ["Discharge", "Prep for Surgery", "Send to ICU"],
                key="handoff_decision"
            )

            if st.button("Complete Handoff"):
                correct_handoff = {
                    "Heart attack": "Send to ICU",
                    "Pneumonia": "Discharge",
                    "Stroke": "Prep for Surgery",
                }

                expected = correct_handoff[p["diagnosis"]]

                if handoff == expected:
                    st.success(f"✅ Appropriate handoff: {handoff}")
                    st.session_state.score += 20
                    st.session_state.treatment_history.append(
                        f"📞 Appropriate handoff — patient sent to {handoff}."
                    )
                else:
                    st.warning(f"⚠️ Suboptimal handoff. Expected: {expected}")
                    st.session_state.mistakes += 1
                    st.session_state.treatment_history.append(
                        f"⚠️ Suboptimal handoff — sent to {handoff}, expected {expected}."
                    )

                st.session_state.patient_status = "Stabilized"
                st.session_state.case_complete = True
                st.rerun()

            if st.session_state.case_complete:
                elapsed = int(time.time() - st.session_state.case_start_time)
                score = st.session_state.score
                grade = (
                    "A" if score >= 85 else
                    "B" if score >= 70 else
                    "C" if score >= 55 else
                    "D" if score >= 40 else "F"
                )

                with st.expander("🏁 End-of-Case Summary", expanded=True):
                    if st.session_state.patient_status == "Deceased":
                        st.markdown("## 💀 Patient Deceased")
                    else:
                        st.markdown("## ✅ Patient Stabilized & Handed Off")

                    st.metric("Final Score", score)
                    st.metric("Time in Care (sec)", elapsed)
                    st.metric("Mistakes", st.session_state.mistakes)
                    st.metric("Grade", grade)

                    st.divider()
                    st.subheader("📋 Action Log")
                    for entry in st.session_state.treatment_history:
                        st.markdown(f"- {entry}")

                    if st.button("🔄 Start New Case"):
                        restart_simulation()
                        st.rerun()

                st.stop()

    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")

    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")

    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")

# --------------------------------------
# RIGHT COLUMN
# --------------------------------------
with col3:
    st.subheader("👩‍⚕️ Patient Info")
    if st.session_state.patient:
        st.write(st.session_state.patient["name"])
        st.write(st.session_state.patient["symptoms"])

    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)

    st.divider()
    st.subheader("📋 Action Log")
    if st.session_state.treatment_history:
        for entry in reversed(st.session_state.treatment_history):
            st.markdown(f"- {entry}")
    else:
        st.info("No actions taken yet.")
