import streamlit as st
import random
import time
import math
import pandas as pd

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
        "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"},
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "diagnosis": "Pneumonia",
        "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"},
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "diagnosis": "Stroke",
        "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"},
    },
]

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

    if effect == "improve":
        hr = max(55, hr - random.randint(2, 6))
        o2 = min(100, o2 + random.randint(3, 6))
    else:
        hr = min(170, hr + random.randint(5, 10))
        o2 = max(65, o2 - random.randint(4, 8))

    v["HR"] = hr
    v["O2"] = f"{o2}%"


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
            st.subheader(f"Status: {st.session_state.patient_status}")
            st.write(f"❤️ HR: {p['vitals']['HR']} bpm")
            st.write(f"💨 O₂: {p['vitals']['O2']}")

            df = pd.DataFrame({"ECG": [math.sin(i / 5) for i in range(50)]})
            st.line_chart(df, height=120)

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
                        message = f"⚠️ {selected_item} used — limited effect."

                    st.session_state.inventory.remove(selected_item)
                    st.session_state.treatment_history.append(message)
                    st.session_state.last_update = time.time()
                    st.toast(message)
                    st.rerun()
            else:
                st.info("No supplies available.")

            st.divider()
            st.subheader("🧠 Clinical Reasoning")

            st.text_input(
                "Enter Working Diagnosis",
                key="entered_diagnosis",
            )

            if st.button("Confirm Diagnosis"):
                if p["diagnosis"].lower() in st.session_state.entered_diagnosis.lower():
                    st.success("Correct diagnosis.")
                    st.session_state.score += 15
                else:
                    st.error("Incorrect diagnosis.")
                    st.session_state.mistakes += 1

            st.divider()
            st.subheader("📞 Patient Handoff")

            handoff = st.radio(
                "Choose Handoff Destination",
                ["Discharge", "Prep for Surgery", "Send to ICU"],
                key="handoff_decision"
            )

            if st.button("Complete Handoff"):
                st.session_state.case_complete = True
                st.rerun()

            if st.session_state.case_complete:
                st.subheader("🏁 End of Case")
                st.metric("Score", st.session_state.score)
                if st.button("🔄 Restart"):
                    restart_simulation()
                    st.rerun()

    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")

        color_map = {
            "Airway & Breathing": "#d0f0fd",
            "Circulation & IV": "#d0ffd0",
            "Diagnostics": "#fff6d0",
            "Immobilization": "#ffe0d0",
            "General Care": "#e0d0ff",
        }

        categorized_supplies = {
            "Airway & Breathing": ["Oxygen Mask", "Nebulizer", "Intubation Kit", "Defibrillator"],
            "Circulation & IV": ["IV Kit", "Saline", "Tourniquet"],
            "Diagnostics": ["Test Swabs", "Glucometer", "Thermometer"],
            "Immobilization": ["Cervical Collar", "Arm Splint"],
            "General Care": ["Catheter Kit", "Bed Pan", "Sutures"],
        }

        for cat, items in categorized_supplies.items():
            st.markdown(
                f"<h4 style='background:{color_map[cat]};padding:6px;border-radius:6px'>{cat}</h4>",
                unsafe_allow_html=True,
            )
            for item in items:
                if st.button(f"Add {item}", key=f"supply_{item}"):
                    if item not in st.session_state.inventory:
                        st.session_state.inventory.append(item)

    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")

        med_categories = {
            "Pain Relief": ["Acetaminophen", "Morphine", "Motrin"],
            "Antiemetics": ["Ondansetron"],
            "Neurological": ["Phenytoin"],
            "Cardiac & Emergency": ["Epinephrine", "Heparin", "Lasix"],
            "Respiratory": ["Albuterol"],
            "Infectious Disease": ["Broad-Spectrum Antibiotics"],
        }

        color_map = {
            "Pain Relief": "#fde0dc",
            "Antiemetics": "#fff5d7",
            "Neurological": "#e3f2fd",
            "Cardiac & Emergency": "#e8f5e9",
            "Respiratory": "#e0f7fa",
            "Infectious Disease": "#fff3e0",
        }

        for cat, meds in med_categories.items():
            st.markdown(
                f"<h4 style='background:{color_map[cat]};padding:6px;border-radius:6px'>{cat}</h4>",
                unsafe_allow_html=True,
            )
            for med in meds:
                if st.button(f"Add {med}", key=f"med_{med}"):
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)

    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")

        p = st.session_state.patient
        if not p:
            st.info("No active patient.")
        else:
            colA, colB = st.columns(2)

            with colA:
                st.subheader("📸 Imaging")
                for test in ["X-Ray", "CT Scan", "MRI", "Ultrasound"]:
                    if st.button(test):
                        st.session_state.diagnostic_history.append(test)

            with colB:
                st.subheader("🧫 Labs")
                for test in ["CBC", "Blood Test", "Urinalysis", "Biopsy"]:
                    if st.button(test):
                        st.session_state.diagnostic_history.append(test)

            st.divider()
            for r in st.session_state.diagnostic_history:
                st.markdown(f"- {r}")

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

    st.subheader("📋 Action Log")
    for entry in st.session_state.treatment_history:
        st.markdown(f"- {entry}")
