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
    "last_update": time.time(),
    "patient_status": "Stable",
    "case_start_time": None,
    "mistakes": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "diagnosis": "Heart attack",
        "vitals": {"BP": "90/60", "HR": 120, "O2": "85%", "Temp": "37.0°C"},
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "diagnosis": "Pneumonia",
        "vitals": {"BP": "110/70", "HR": 95, "O2": "88%", "Temp": "39.2°C"},
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "diagnosis": "Stroke",
        "vitals": {"BP": "150/90", "HR": 82, "O2": "97%", "Temp": "36.8°C"},
    },
]

diagnostic_results = {
    "Heart attack": {
        "X-Ray": "Chest X-ray shows mild pulmonary congestion.",
        "CT Scan": "CT chest shows coronary artery calcifications.",
        "MRI": "MRI reveals myocardial ischemia.",
        "Ultrasound": "Echocardiogram shows reduced left ventricular function.",
        "CBC": "CBC within normal limits.",
        "Blood Test": "Troponin markedly elevated — myocardial infarction confirmed.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated for acute coronary syndrome."
    },
    "Pneumonia": {
        "X-Ray": "Chest X-ray shows right lower lobe infiltrates.",
        "CT Scan": "CT chest shows consolidation consistent with pneumonia.",
        "MRI": "MRI not typically indicated for pneumonia.",
        "Ultrasound": "Lung ultrasound shows B-lines and consolidation.",
        "CBC": "Elevated white blood cell count — infection likely.",
        "Blood Test": "Inflammatory markers elevated.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated — infection suspected."
    },
    "Stroke": {
        "X-Ray": "Chest X-ray unremarkable.",
        "CT Scan": "CT head shows acute ischemic changes.",
        "MRI": "MRI brain confirms ischemic stroke.",
        "Ultrasound": "Carotid ultrasound shows reduced flow.",
        "CBC": "CBC within normal limits.",
        "Blood Test": "Glucose mildly elevated.",
        "Urinalysis": "Normal urinalysis.",
        "Biopsy": "Not indicated for acute stroke."
    }
}

# --------------------------------------
# CORE FUNCTIONS
# --------------------------------------
def assign_patient():
    p = random.choice(patients)
    st.session_state.patient = p
    st.session_state.inventory = []
    st.session_state.score = 0
    st.session_state.treatment_history = []
    st.session_state.patient_status = "Stable"
    st.session_state.case_start_time = time.time()
    st.session_state.last_update = time.time()
    st.session_state.mistakes = 0


def restart_simulation():
    for key, value in defaults.items():
        st.session_state[key] = value


def update_vitals(effect):
    p = st.session_state.patient
    v = p["vitals"]

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
    p["vitals"] = v


def gradual_deterioration():
    if time.time() - st.session_state.last_update > 45:
        update_vitals("worsen")
        st.session_state.last_update = time.time()


def check_patient_outcome():
    p = st.session_state.patient
    if not p:
        return

    hr = int(p["vitals"]["HR"])
    o2 = int(p["vitals"]["O2"].replace("%", ""))

    if hr > 130 or hr < 45 or o2 < 85:
        st.session_state.patient_status = "Critical"
    else:
        st.session_state.patient_status = "Stable"

    if o2 <= 70 or hr >= 160 or hr <= 35 or st.session_state.mistakes >= 5:
        st.session_state.patient_status = "Deceased"

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 ER Simulation")
    st.session_state.room = st.radio(
        "Select Room",
        ["ER", "Supply Room", "Medstation", "Diagnostic Lab"],
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
_, col2, col3 = st.columns([0.3, 3.4, 1.3])

# --------------------------------------
# CENTER COLUMN
# --------------------------------------
with col2:

    # ================= ER =================
    if st.session_state.room == "ER":

        if not st.session_state.patient:
            st.header("🏥 Emergency Room")
            if st.button("🆕 Generate Patient"):
                assign_patient()
                st.rerun()

        else:
            gradual_deterioration()
            check_patient_outcome()

            status_colors = {
                "Stable": "#2ecc71",
                "Critical": "#f1c40f",
                "Deceased": "#e74c3c",
            }

            st.markdown(
                f"<h3 style='color:{status_colors[st.session_state.patient_status]}'>"
                f"Patient Status: {st.session_state.patient_status}</h3>",
                unsafe_allow_html=True,
            )

            if st.session_state.patient_status == "Deceased":
                elapsed = int(time.time() - st.session_state.case_start_time)
                st.error("💀 Patient has died")
                st.write(f"⏱️ Time in care: {elapsed}s")
                st.write(f"❌ Mistakes: {st.session_state.mistakes}")
                st.write(f"🏆 Score: {st.session_state.score}")

                if st.button("🔄 Restart Simulation"):
                    restart_simulation()
                    st.rerun()

                st.stop()

            p = st.session_state.patient
            vitals = p["vitals"]

            st.write(f"❤️ HR: {vitals['HR']} bpm")
            st.write(f"💨 O₂: {vitals['O2']}")

            df = pd.DataFrame(
                {"ECG": [math.sin(i / 5) for i in range(50)]}
            )
            st.line_chart(df, height=120)

            if st.session_state.inventory:
                item = st.selectbox(
                    "Use supply",
                    st.session_state.inventory,
                    key="use_supply_select",
                )
                if st.button("Use Item", key="use_supply_button"):
                    correct = {
                        "Heart attack": ["Oxygen Mask"],
                        "Pneumonia": ["Oxygen Mask"],
                        "Stroke": ["Oxygen Mask"],
                    }
                    if item in correct.get(p["diagnosis"], []):
                        update_vitals("improve")
                        st.session_state.score += 5
                    else:
                        update_vitals("worsen")
                        st.session_state.mistakes += 1

                    st.session_state.inventory.remove(item)
                    st.session_state.last_update = time.time()
                    st.rerun()
            else:
                st.info("No supplies available")

    # ================= SUPPLY ROOM =================
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
            "Airway & Breathing": {
                "Oxygen Mask": "Delivers oxygen.",
                "Intubation Kit": "Airway management.",
                "Defibrillator and Pads": "Cardiac shocks.",
            },
            "Circulation & IV": {
                "IV Kit": "IV access.",
                "Saline and Other IV Fluids": "Hydration.",
                "Tourniquet": "Bleeding control.",
            },
            "Diagnostics": {
                "Test Swabs": "Sample collection.",
                "Glucometer": "Blood glucose.",
                "Thermometer": "Body temperature.",
            },
            "Immobilization": {
                "Cervical Collar": "Neck support.",
                "Arm Splint": "Limb immobilization.",
            },
            "General Care": {
                "Catheter Kit": "Urinary drainage.",
                "Bed Pan": "Bedside toileting.",
                "Sutures": "Wound closure.",
            },
        }

        for category, items in categorized_supplies.items():
            st.markdown(
                f"<h4 style='background:{color_map[category]};padding:6px;border-radius:6px'>{category}</h4>",
                unsafe_allow_html=True,
            )
            for item, desc in items.items():
                with st.expander(item):
                    st.write(desc)
                    if st.button(
                        f"Add {item}",
                        key=f"supply_{item}",
                    ):
                        if item not in st.session_state.inventory:
                            st.session_state.inventory.append(item)
                            st.toast(f"📦 {item} added")
                            st.rerun()

    # ================= MEDSTATION =================
    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")

        meds = {
            "Pain Relief": ["Acetaminophen", "Morphine", "Motrin"],
            "Antiemetics": ["Ondansetron"],
            "Neurological": ["Phenytoin", "Midodrine"],
            "Cardiac & Emergency": ["Epinephrine", "Hydralazine", "Heparin", "Lasix", "Naloxone"],
            "Metabolic": ["Glucose"],
        }

        for category, meds_list in meds.items():
            st.markdown(
                f"<h4 style='background:#eee;padding:6px;border-radius:6px'>{category}</h4>",
                unsafe_allow_html=True,
            )
            for med in meds_list:
                with st.expander(med):
                    if st.button(
                        f"Add {med}",
                        key=f"med_{med}",
                    ):
                        if med not in st.session_state.inventory:
                            st.session_state.inventory.append(med)
                            st.toast(f"💊 {med} added")
                            st.rerun()

        # ================= DIAGNOSTIC LAB =================
    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")

        st.markdown(
            "Run diagnostic imaging or lab tests. Results will vary based on the patient's condition."
        )

        imaging_tests = ["X-Ray", "CT Scan", "MRI", "Ultrasound"]
        lab_tests = ["CBC", "Blood Test", "Urinalysis", "Biopsy"]

        p = st.session_state.get("patient")
        diagnosis = p["diagnosis"] if p else None

        colA, colB = st.columns(2)

        # ---------- IMAGING ----------
        with colA:
            st.subheader("📸 Imaging")
            for test in imaging_tests:
                if st.button(f"Run {test}", key=f"diag_img_{test}"):
                    if not p:
                        st.warning("No active patient.")
                        st.stop()

                    result = diagnostic_results.get(diagnosis, {}).get(
                        test, "No significant findings."
                    )

                    st.session_state.treatment_history.append(
                        f"🧪 {test}: {result}"
                    )

                    st.success(f"{test} completed")
                    st.info(f"**Result:** {result}")
                    st.session_state.score += 5
                    st.session_state.last_update = time.time()

        # ---------- LABS ----------
        with colB:
            st.subheader("🧫 Laboratory Tests")
            for test in lab_tests:
                if st.button(f"Run {test}", key=f"diag_lab_{test}"):
                    if not p:
                        st.warning("No active patient.")
                        st.stop()

                    result = diagnostic_results.get(diagnosis, {}).get(
                        test, "Results pending or normal."
                    )

                    st.session_state.treatment_history.append(
                        f"🧪 {test}: {result}"
                    )

                    st.success(f"{test} completed")
                    st.info(f"**Result:** {result}")
                    st.session_state.score += 5
                    st.session_state.last_update = time.time()

# --------------------------------------
# RIGHT COLUMN
# --------------------------------------
with col3:
    st.subheader("👩‍⚕️ Patient Info")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Symptoms:** {p['symptoms']}")

    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)
