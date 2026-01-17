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
# SESSION STATE
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
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()
if "patient_status" not in st.session_state:
    st.session_state.patient_status = "Stable"
if "case_start_time" not in st.session_state:
    st.session_state.case_start_time = None
if "mistakes" not in st.session_state:
    st.session_state.mistakes = 0

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

# --------------------------------------
# FUNCTIONS
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
    now = time.time()
    if now - st.session_state.last_update > 45:
        update_vitals("worsen")
        st.session_state.last_update = now


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
        
def restart_simulation():
    st.session_state.patient = None
    st.session_state.inventory = []
    st.session_state.score = 0
    st.session_state.mistakes = 0
    st.session_state.patient_status = "Stable"
    st.session_state.case_start_time = None
    st.session_state.last_update = time.time()
    st.session_state.treatment_history = []
    st.session_state.room = "ER"

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
        st.info("Empty")

# --------------------------------------
# LAYOUT
# --------------------------------------
_, col2, col3 = st.columns([0.3, 3.4, 1.3])

# --------------------------------------
# CENTER COLUMN
# --------------------------------------
with col2:

    # ========= ER =========
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
        

            p = st.session_state.patient
            vitals = p["vitals"]

            st.write(f"❤️ HR: {vitals['HR']} bpm")
            st.write(f"💨 O₂: {vitals['O2']}")

            df = pd.DataFrame(
                {"ECG": [math.sin(i / 5) for i in range(50)]}
            )
            st.line_chart(df, height=120)

            if st.session_state.inventory:
                item = st.selectbox("Use supply", st.session_state.inventory)
                if st.button("Use Item"):
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
                st.info("No supplies")

    # ========= SUPPLY ROOM =========
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
            "Intubation Kit": "Contains tools for airway management.",
            "Defibrillator and Pads": "Delivers shocks for cardiac arrest."
        },
        "Circulation & IV": {
            "IV Kit": "For IV fluids or medication administration.",
            "Saline and Other IV Fluids": "Hydrates patients or delivers IV meds.",
            "Tourniquet": "Stops bleeding on limbs."
        },
        "Diagnostics": {
            "Test Swabs": "Collect samples for testing.",
            "Glucometer": "Measures blood glucose levels.",
            "Thermometer": "Measures body temperature."
        },
        "Immobilization": {
            "Cervical Collar": "Neck immobilization for trauma.",
            "Arm Splint": "Immobilizes broken or injured limbs."
        },
        "General Care": {
            "Catheter Kit": "For urinary drainage.",
            "Bed Pan": "For bedridden patients.",
            "Sutures": "Used to close wounds."
        }
    }

    for category, supplies in categorized_supplies.items():
        st.markdown(
            f"<h4 style='background-color:{color_map[category]};padding:6px;border-radius:8px;'>{category}</h4>",
            unsafe_allow_html=True
        )

        items = list(supplies.items())
        for i in range(0, len(items), 2):
            colA, colB = st.columns(2)
            for col, (item, desc) in zip((colA, colB), items[i:i+2]):
                with col.expander(item):
                    st.write(desc)
                    if st.button(f"Add {item}", key=f"supply_{item}"):
                        if item not in st.session_state.inventory:
                            st.session_state.inventory.append(item)
                            st.success(f"{item} added.")
                            st.toast(f"📦 {item} added!", icon="📦")
                            st.rerun()
                        else:
                            st.warning("Already in inventory.")

    # ========= MEDSTATION =========
    elif st.session_state.room == "Medstation":
    st.header("💊 Medstation")

    med_categories = {
        "Pain Relief": {
            "Acetaminophen": "Used for fever or mild pain.",
            "Morphine": "For severe pain.",
            "Motrin": "Anti-inflammatory pain relief."
        },
        "Antiemetics": {
            "Ondansetron": "Prevents nausea and vomiting."
        },
        "Neurological": {
            "Phenytoin": "Used for seizure control.",
            "Midodrine": "Used for low blood pressure."
        },
        "Cardiac & Emergency": {
            "Epinephrine": "Used for anaphylaxis or cardiac arrest.",
            "Hydralazine": "Lowers blood pressure.",
            "Heparin": "Prevents blood clots.",
            "Lasix": "Removes excess fluid.",
            "Naloxone": "Reverses opioid overdose."
        },
        "Metabolic": {
            "Glucose": "Used to treat low blood sugar."
        }
    }

    color_map_meds = {
        "Pain Relief": "#fde0dc",
        "Antiemetics": "#fff5d7",
        "Neurological": "#e3f2fd",
        "Cardiac & Emergency": "#e8f5e9",
        "Metabolic": "#f3e5f5"
    }

    for category, meds in med_categories.items():
        st.markdown(
            f"<h4 style='background-color:{color_map_meds[category]};padding:6px;border-radius:8px;'>{category}</h4>",
            unsafe_allow_html=True
        )

        meds_list = list(meds.items())
        for i in range(0, len(meds_list), 2):
            colA, colB = st.columns(2)
            for col, (med, desc) in zip((colA, colB), meds_list[i:i+2]):
                with col.expander(med):
                    st.write(desc)
                    if st.button(f"Add {med}", key=f"med_{med}"):
                        if med not in st.session_state.inventory:
                            st.session_state.inventory.append(med)
                            st.success(f"{med} added.")
                            st.toast(f"💊 {med} added!", icon="💊")
                            st.rerun()
                        else:
                            st.warning("Already in inventory.")

    # ========= DIAGNOSTIC LAB =========
    elif st.session_state.room == "Diagnostic Lab":
    st.header("🧪 Diagnostic Lab")

    st.markdown("""
    Perform diagnostic imaging and laboratory tests to confirm or refine your diagnosis.  
    Choose wisely — accurate tests improve outcomes.
    """)

    body_part_options = ["Chest", "Head", "Abdomen", "Pelvis", "Extremities"]

    imaging_tests = {
        "X-Ray": "Uses radiation to view bone and lung structures.",
        "CT Scan": "Cross-sectional imaging for strokes, trauma, or internal bleeding.",
        "MRI": "Detailed soft-tissue imaging — excellent for brain, spine, and joints.",
        "Ultrasound": "Real-time imaging to visualize organs or fluid buildup."
    }

    lab_tests = {
        "CBC": "Complete blood count; detects infection or anemia.",
        "Blood Test": "Analyzes infection markers, glucose, and clotting levels.",
        "Urinalysis": "Detects infection or metabolic issues.",
        "Biopsy": "Examines tissue samples for cancer or disease."
    }

    col_imaging, col_lab = st.columns(2)

    with col_imaging:
        st.markdown(
            "<h4 style='background-color:#fff176;padding:6px;border-radius:8px;'>Diagnostic Imaging</h4>",
            unsafe_allow_html=True
        )
        for test, desc in imaging_tests.items():
            st.write(f"**{test}** — {desc}")
            part = st.selectbox(
                f"Body part for {test}",
                ["-- Select --"] + body_part_options,
                key=f"img_{test}"
            )
            if st.button(f"Run {test}", key=f"run_{test}"):
                st.session_state.score += 5
                st.success(f"{test} completed for {part}")
                st.toast(f"🧪 {test} completed!", icon="🧪")
                st.session_state.last_update = time.time()
                st.rerun()

    with col_lab:
        st.markdown(
            "<h4 style='background-color:#a5d6a7;padding:6px;border-radius:8px;'>Laboratory Tests</h4>",
            unsafe_allow_html=True
        )
        for test, desc in lab_tests.items():
            st.write(f"**{test}** — {desc}")
            if st.button(f"Run {test}", key=f"lab_{test}"):
                st.session_state.score += 5
                st.success(f"{test} completed.")
                st.toast(f"🧪 {test} completed!", icon="🧪")
                st.session_state.last_update = time.time()
                st.rerun()
# --------------------------------------
# RIGHT COLUMN
# --------------------------------------
with col3:
    st.subheader("👩‍⚕️ Patient Info")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(p["name"])
        st.write(p["symptoms"])

    st.subheader("🏆 Score")
    st.metric("Score", st.session_state.score)

