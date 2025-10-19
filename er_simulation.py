import streamlit as st
import random
import time

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=2000, key="ecg_refresh")  # every 2 seconds


# --------------------------------------
# STYLE FOR TRANSFER MODAL
# --------------------------------------
st.markdown("""
<style>
div[data-testid="stExpander"] {
    background-color: #f9f9f9;
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
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
if "next_patient_button_clicked" not in st.session_state:
    st.session_state.next_patient_button_clicked = False
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%", "Temp": "37.0°C"},
     "diagnosis": "Heart attack",
     "medical_history": {"Allergies": "None", "Past Surgeries": "None", "Current Medications": "None", "Chronic Conditions": "None"}},
    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%", "Temp": "39.2°C"},
     "diagnosis": "Pneumonia",
     "medical_history": {"Allergies": "Penicillin", "Past Surgeries": "Appendectomy", "Current Medications": "Ibuprofen", "Chronic Conditions": "Asthma"}},
    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%", "Temp": "36.8°C"},
     "diagnosis": "Stroke",
     "medical_history": {"Allergies": "None", "Past Surgeries": "Knee Replacement", "Current Medications": "Aspirin", "Chronic Conditions": "Hypertension"}}
]

# --------------------------------------
# FUNCTIONS
# --------------------------------------
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []
    st.session_state.score = 0
    st.session_state.last_update = time.time()

# --------------------------------------
# DYNAMIC VITALS UPDATE
# --------------------------------------
def update_vitals(effect):
    """Adjust patient vitals dynamically depending on treatment effectiveness."""
    p = st.session_state.get("patient")
    if not p or "vitals" not in p:
        return

    vitals = p["vitals"]

    def parse_bp(bp_str):
        try:
            systolic, diastolic = bp_str.split("/")
            return int(systolic), int(diastolic)
        except Exception:
            return (100, 70)

    sys, dia = parse_bp(vitals.get("BP", "100/70"))
    hr = int(vitals.get("HR", 80))
    o2 = int(vitals.get("O2", "95%").strip("%"))

    if effect == "improve":
        o2 = min(100, o2 + random.randint(2, 5))
        hr = max(55, hr - random.randint(2, 6))
        sys = min(140, sys + random.randint(1, 3))
        dia = min(90, dia + random.randint(1, 2))
    elif effect == "worsen":
        o2 = max(70, o2 - random.randint(3, 7))
        hr = min(160, hr + random.randint(5, 10))
        sys = max(80, sys - random.randint(3, 6))
        dia = max(50, dia - random.randint(2, 5))

    vitals["BP"] = f"{sys}/{dia}"
    vitals["HR"] = hr
    vitals["O2"] = f"{o2}%"
    st.session_state.patient["vitals"] = vitals

# --------------------------------------
# PASSIVE PATIENT DETERIORATION OVER TIME
# --------------------------------------
def gradual_deterioration():
    """Slowly worsens vitals if too much time passes without treatment."""
    if "last_update" not in st.session_state:
        st.session_state.last_update = time.time()
        return

    now = time.time()
    elapsed = now - st.session_state.last_update

    # Every 45 seconds without treatment = mild deterioration
    if elapsed > 45:
        update_vitals("worsen")
        st.session_state.last_update = now
        st.toast("⏳ Patient condition is deteriorating due to delay!", icon="⚠️")

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 Emergency Room Simulation")
    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"])
    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist"])
    rooms = ["ER", "Supply Room", "Medstation", "Diagnostic Lab"]
    st.session_state.room = st.radio(
        "Select a Room",
        rooms,
        index=rooms.index(st.session_state.room) if st.session_state.room in rooms else 0
    )

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
        st.rerun()

# --------------------------------------
# MAIN LAYOUT
# --------------------------------------
col1, col2, col3 = st.columns([0.3, 3.4, 1.3])

# ---- CENTER COLUMN ----
with col2:
    if st.session_state.room == "ER":
        st.header("🏥 Emergency Room")

        if st.button("Next Patient"):
            st.session_state.next_patient_button_clicked = True

        if st.session_state.get("next_patient_button_clicked", False):
            assign_patient()
            st.session_state.next_patient_button_clicked = False

        if st.session_state.patient:
            # Passive deterioration on each rerun
            gradual_deterioration()

            p = st.session_state.patient
            st.subheader("Patient Information")
            st.write(f"**Name:** {p['name']}")
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Symptoms:** {p['symptoms']}")
            st.subheader("📜 Medical History Form")
            for k, v in p["medical_history"].items():
                st.write(f"**{k}:** {v}")

            # ---------------- USE SUPPLIES ----------------
            if st.session_state.inventory:
                st.subheader("🧰 Use Supplies")
                selected_item = st.selectbox("Select an item to use:", st.session_state.inventory)
                if st.button("Use Selected Item"):
                    diagnosis = p["diagnosis"]
                    correct_uses = {
                        "Heart attack": ["Defibrillator and Pads", "Oxygen Mask", "IV Kit", "Aspirin"],
                        "Pneumonia": ["Oxygen Mask", "Thermometer", "IV Kit"],
                        "Stroke": ["Oxygen Mask", "IV Kit", "Glucometer", "Blood Pressure Cuff"]
                    }
                    if selected_item in correct_uses.get(diagnosis, []):
                        st.session_state.score += 5
                        feedback = f"✅ Correct use! {selected_item} was appropriate. (+5 points)"
                        update_vitals("improve")
                    else:
                        feedback = f"⚠️ {selected_item} had limited effect."
                        update_vitals("worsen")

                    st.session_state.treatment_history.append(
                        f"Used {selected_item} on {p['name']}. {feedback}"
                    )
                    st.session_state.inventory.remove(selected_item)
                    st.success(feedback)
                    st.toast(feedback, icon="💉")
                    st.session_state.last_update = time.time()
                    st.rerun()
            else:
                st.info("No available supplies in your inventory to use.")

            # ---------------- GIVE MEDICATION ----------------
            meds_in_inventory = [m for m in st.session_state.inventory if m.lower() in [
                "acetaminophen", "morphine", "motrin", "ondansetron", "phenytoin",
                "epinephrine", "glucose", "hydralazine", "midodrine", "heparin", "lasix", "naloxone"
            ]]
            if meds_in_inventory:
                st.subheader("💊 Give Medication")
                selected_med = st.selectbox("Select a medication to administer:", meds_in_inventory)
                if st.button("Give Medication"):
                    diagnosis = p["diagnosis"]
                    correct_meds = {
                        "Heart attack": ["Morphine", "Heparin", "Oxygen Mask"],
                        "Pneumonia": ["Motrin", "Acetaminophen", "Oxygen Mask"],
                        "Stroke": ["Heparin", "Glucose"]
                    }
                    if selected_med in correct_meds.get(diagnosis, []):
                        st.session_state.score += 10
                        feedback = f"💊 Correct treatment! {selected_med} helped improve the patient's condition. (+10 points)"
                        update_vitals("improve")
                    else:
                        feedback = f"⚠️ {selected_med} was not very effective for this condition."
                        update_vitals("worsen")

                    st.session_state.treatment_history.append(
                        f"Gave {selected_med} to {p['name']}. {feedback}"
                    )
                    st.session_state.inventory.remove(selected_med)
                    st.success(feedback)
                    st.toast(feedback, icon="💊")
                    st.session_state.last_update = time.time()
                    st.rerun()
            else:
                st.info("No medications available in your inventory.")

            # ---------------- TRANSFER PATIENT ----------------
            st.subheader("🏥 Transfer Patient")
            transfer_option = st.selectbox(
                "Select Transfer Destination:",
                ["-- Select --", "Discharge", "Send to Surgery", "Send to ICU"],
                key="transfer_destination"
            )

            if st.button("Confirm Transfer", key="confirm_transfer"):
                with st.expander("🏁 Patient Transfer Summary", expanded=True):
                    total_score = max(0, min(100, int(st.session_state.score)))
                    effectiveness = total_score
                    history = st.session_state.get("treatment_history", [])

                    correct_diagnostics = sum(("✅" in e and "test" in e.lower()) for e in history)
                    incorrect_diagnostics = sum(("⚠️" in e and "test" in e.lower()) for e in history)

                    diagnostic_accuracy = 60 + (10 * correct_diagnostics) - (5 * incorrect_diagnostics)
                    diagnostic_accuracy = max(0, min(diagnostic_accuracy, 100))
                    resource_efficiency = random.randint(50, 95)

                    if total_score >= 85:
                        outcome, color = "🏆 Excellent", "#2ecc71"
                    elif total_score >= 70:
                        outcome, color = "🙂 Good", "#27ae60"
                    elif total_score >= 50:
                        outcome, color = "⚠️ Fair", "#f1c40f"
                    else:
                        outcome, color = "💀 Poor", "#e74c3c"

                    st.markdown(
                        f"<h3 style='text-align:center;color:{color};margin-bottom:0;'>"
                        f"{outcome} — Score: {total_score}/100"
                        f"</h3>",
                        unsafe_allow_html=True
                    )
                    st.caption(f"Transfer decision: **{transfer_option}**")

                    st.write("**Treatment Effectiveness**")
                    st.progress(effectiveness / 100)
                    st.write("**Diagnostic Accuracy**")
                    st.progress(diagnostic_accuracy / 100)
                    st.write("**Resource Management**")
                    st.progress(resource_efficiency / 100)

                    st.write("---")
                    correct_acts = sum("✅" in line for line in st.session_state.treatment_history)
                    limited_acts = sum("limited" in line.lower() for line in st.session_state.treatment_history)
                    st.markdown("**Action Summary**")
                    st.write(f"- ✅ Effective actions: **{correct_acts}**")
                    st.write(f"- ⚠️ Limited/ineffective actions: **{limited_acts}**")

                    feedback_pool = [
                        "Great clinical judgment and timely interventions!",
                        "Diagnostics were appropriate; consider earlier imaging next time.",
                        "Supplies were used efficiently; watch for redundant meds.",
                        "Good stabilization—optimize sequence of care for better outcomes.",
                        "Consider reassessing vitals before transfer to ensure stability."
                    ]
                    st.write("---")
                    st.markdown(f"**Feedback:** {random.choice(feedback_pool)}")

                    if st.button("🆕 Start New Case", key="start_new_case"):
                        st.session_state.patient = None
                        st.session_state.treatment_history = []
                        st.session_state.score = 0
                        st.rerun()
        else:
            st.info("No active patient.")

    # ---------------- SUPPLY ROOM ----------------
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
                        if st.button(f"Add {item} to Inventory", key=f"supply_{item}"):
                            if item not in st.session_state.inventory:
                                st.session_state.inventory.append(item)
                                st.success(f"{item} added to inventory.")
                                st.toast(f"✅ {item} added!", icon="📦")
                                st.rerun()
                            else:
                                st.warning(f"{item} already in inventory.")

    # ---------------- MEDSTATION ----------------
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
                        if st.button(f"Add {med} to Inventory", key=f"med_{med}"):
                            if med not in st.session_state.inventory:
                                st.session_state.inventory.append(med)
                                st.success(f"{med} added to inventory.")
                                st.toast(f"💊 {med} collected!", icon="💊")
                                st.rerun()
                            else:
                                st.warning(f"{med} already in inventory.")

    # ---------------- DIAGNOSTIC LAB ----------------
    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")

        st.markdown("""
        Perform diagnostic imaging and laboratory tests to confirm or refine your diagnosis.  
        Choose the most relevant tests — accurate selections improve your diagnostic accuracy!
        """)

        body_part_options = ["Chest", "Head", "Abdomen", "Pelvis", "Extremities"]

        imaging_tests = {
            "X-Ray": "Uses radiation to view bone and lung structures.",
            "CT Scan": "Cross-sectional imaging for strokes, trauma, or internal bleeding.",
            "MRI": "Detailed soft-tissue imaging — excellent for brain, spine, and joint evaluation.",
            "Ultrasound": "Real-time imaging to visualize organs or fluid buildup."
        }

        lab_tests = {
            "CBC": "Complete blood count; detects infection or anemia.",
            "Blood Test": "Analyzes infection markers, glucose, and clotting levels.",
            "Urinalysis": "Detects infection or metabolic issues.",
            "Biopsy": "Examines tissue samples for cancer or disease."
        }

        correct_tests = {
            "Heart attack": {"CT Scan": ["Chest"], "MRI": ["Chest"], "Blood Test": None},
            "Pneumonia": {"X-Ray": ["Chest"], "CBC": None, "Blood Test": None},
            "Stroke": {"CT Scan": ["Head"], "MRI": ["Head"], "Blood Test": None}
        }

        results = {
            "X-Ray": "Imaging shows patchy infiltrates — possible pneumonia.",
            "CT Scan": "Cross-sectional scan reveals ischemic changes.",
            "MRI": "High-resolution scan confirms soft-tissue abnormalities.",
            "Ultrasound": "No free fluid; normal abdominal structures.",
            "CBC": "Elevated WBC count — suggests infection.",
            "Blood Test": "Elevated cardiac enzymes — myocardial injury likely.",
            "Urinalysis": "Normal — no infection or glucose present.",
            "Biopsy": "Tissue sample pending pathology report."
        }

        col_imaging, col_lab = st.columns(2)

        # ---- Imaging Column ----
        with col_imaging:
            st.markdown(
                "<h4 style='background-color:#fff176;padding:6px;border-radius:8px;'>Diagnostic Imaging</h4>",
                unsafe_allow_html=True
            )
            for test_name, desc in imaging_tests.items():
                st.write(f"**{test_name}** — {desc}")
                selected_part = st.selectbox(
                    f"Select body part for {test_name}",
                    options=["-- Select --"] + body_part_options,
                    key=f"body_part_{test_name.replace(' ', '_')}"
                )
                if st.button(f"Run {test_name}", key=f"imaging_{test_name.replace(' ', '_')}"):
                    p = st.session_state.get("patient")
                    if not p:
                        st.warning("No active patient.")
                        st.stop()

                    diagnosis = p.get("diagnosis")
                    body_part = selected_part if selected_part != "-- Select --" else "unspecified area"
                    result_text = results.get(test_name, "Results pending.")
                    feedback = f"🧾 {test_name} ({body_part}) completed.\n\n**Result:** {result_text}"

                    # Scoring logic: test type + body part relevance
                    test_correct = False
                    if diagnosis in correct_tests:
                        match_data = correct_tests[diagnosis]
                        if test_name in match_data:
                            correct_parts = match_data[test_name]
                            if correct_parts is None or body_part in correct_parts:
                                test_correct = True

                    if test_correct:
                        st.session_state.score += 7
                        feedback += " ✅ Correct test and target area! (+7 points)"
                    else:
                        feedback += " ⚠️ Test or body part provided limited diagnostic value."

                    st.session_state.treatment_history.append(f"Ran {test_name} ({body_part}). {feedback}")
                    st.success(feedback)
                    st.toast(f"✅ {test_name} ({body_part}) completed!", icon="🧪")
                    st.session_state.last_update = time.time()
                    st.experimental_rerun()

        # ---- Laboratory Tests Column ----
        with col_lab:
            st.markdown(
                "<h4 style='background-color:#a5d6a7;padding:6px;border-radius:8px;'>Laboratory Tests</h4>",
                unsafe_allow_html=True
            )
            for test_name, desc in lab_tests.items():
                st.write(f"**{test_name}** — {desc}")
                if st.button(f"Run {test_name}", key=f"lab_{test_name.replace(' ', '_')}"):
                    p = st.session_state.get("patient")
                    if not p:
                        st.warning("No active patient.")
                        st.stop()

                    diagnosis = p.get("diagnosis")
                    result_text = results.get(test_name, "Results pending.")
                    feedback = f"🧾 {test_name} completed.\n\n**Result:** {result_text}"

                    test_correct = (
                        diagnosis in correct_tests
                        and test_name in correct_tests[diagnosis]
                    )

                    if test_correct:
                        st.session_state.score += 7
                        feedback += " ✅ Correct test ordered! (+7 points)"
                    else:
                        feedback += " ⚠️ Test provided limited diagnostic value."

                    st.session_state.treatment_history.append(f"Ran {test_name}. {feedback}")
                    st.success(feedback)
                    st.toast(f"✅ {test_name} completed!", icon="🧪")
                    st.session_state.last_update = time.time()
                    st.experimental_rerun()

# ---- RIGHT COLUMN ----
with col3:
    st.subheader("👩‍⚕️ Patient Data")

    p = st.session_state.get("patient")
    if p:
        st.write(f"**Name:** {p.get('name', 'Unknown')}")
        st.write(f"**Age:** {p.get('age', 'N/A')}")
        st.write(f"**Symptoms:** {p.get('symptoms', 'N/A')}")

        # ==== REAL-TIME MONITOR PANEL ====
if p and "vitals" in p:
    st.markdown("<h4>📺 Real-Time Monitor</h4>", unsafe_allow_html=True)

    # ==== REAL-TIME MONITOR PANEL ====
if p and "vitals" in p:
    st.markdown("<h4>📺 Real-Time Monitor</h4>", unsafe_allow_html=True)

    # --- ECG waveform (using Streamlit's native chart) ---
    import pandas as pd
    import math

    # create a smooth sine wave that "moves" with time
    x = list(range(60))
    phase = int(time.time() * 2) % 60  # scrolls horizontally
    y = [
        0.1 * math.sin((i + phase) * 0.3) +
        0.02 * math.sin((i + phase) * 3) +
        (0.4 if i == 30 else 0)  # small heartbeat spike
        for i in x
    ]
    df = pd.DataFrame({"ECG": y})
    st.line_chart(df, height=100, use_container_width=True)

    # --- Extract vitals safely ---
    vitals = p["vitals"]
    try:
        hr = int(vitals.get("HR", 0))
        o2 = int(vitals.get("O2", "0%").strip("%"))
        temp_str = str(vitals.get("Temp", "0")).replace("°C", "")
        temp = float(temp_str)
    except Exception:
        hr, o2, temp = 0, 0, 0

    # --- Color-coded readouts ---
    def colorize(value, normal_low, normal_high):
        if value < normal_low:
            return "🟠"
        elif value > normal_high:
            return "🔴"
        return "🟢"

    hr_icon = colorize(hr, 60, 110)
    o2_icon = colorize(o2, 92, 100)
    temp_icon = colorize(temp, 36, 38.5)

    st.markdown(
        f"""
        **{hr_icon} Heart Rate:** {hr} bpm  
        **{o2_icon} O₂ Sat:** {o2}%  
        **{temp_icon} Temp:** {temp:.1f} °C
        """,
        unsafe_allow_html=True,
    )

    # --- Warning banner ---
    warn_msgs = []
    if hr < 50:
        warn_msgs.append("Bradycardia – HR < 50 bpm")
    elif hr > 120:
        warn_msgs.append("Tachycardia – HR > 120 bpm")
    if o2 < 90:
        warn_msgs.append("Hypoxia – O₂ < 90%")
    if temp > 39:
        warn_msgs.append("High Fever")
    if temp < 35:
        warn_msgs.append("Hypothermia")

    if warn_msgs:
        st.markdown(
            f"<div style='background:#e74c3c;color:white;padding:6px;border-radius:6px;'>⚠️ {' | '.join(warn_msgs)}</div>",
            unsafe_allow_html=True,
        )

        # Safely show vitals (color-coded + pulse indicator)
        vitals = p.get("vitals", {})
        if vitals:
            st.subheader("🩺 Patient Vitals")

            def color_vital(label, value, normal_range=None, suffix=""):
                """Render a vital with colored indicator depending on whether it's normal."""
                try:
                    if isinstance(value, str) and "%" in value:
                        numeric = int(value.strip("%"))
                    elif isinstance(value, str) and "/" in value:
                        systolic, diastolic = map(int, value.split("/"))
                        numeric = (systolic + diastolic) // 2
                    else:
                        numeric = int(value)
                except Exception:
                    numeric = 0

                color = "🟢"
                if normal_range:
                    if numeric < normal_range[0]:
                        color = "🟠"
                    elif numeric > normal_range[1]:
                        color = "🔴"

                return f"{color} **{label}:** {value}{suffix}"

            st.markdown(color_vital("BP", vitals.get("BP", "N/A"), (90, 140)))
            st.markdown(color_vital("HR", vitals.get("HR", "N/A"), (60, 110)))
            st.markdown(color_vital("O₂", vitals.get("O2", "N/A"), (92, 100), "%"))
            st.markdown(f"**Temp:** {vitals.get('Temp', 'N/A')}")

            # Pulse / Rhythm display
            try:
                hr = int(vitals.get("HR", 0))
                o2 = int(vitals.get("O2", "0%").strip("%"))
            except Exception:
                hr, o2 = 0, 0

            if hr == 0 or o2 == 0:
                st.markdown("<div style='color:#7f8c8d;'>No pulse detected.</div>", unsafe_allow_html=True)
            elif hr < 50 or o2 < 85:
                st.markdown("<div style='font-size:20px;color:#e74c3c;'>💔 Weak Pulse — Patient Deteriorating!</div>", unsafe_allow_html=True)
            elif hr > 120:
                st.markdown("<div style='font-size:20px;color:#f39c12;'>💢 Tachycardia — Monitor Closely!</div>", unsafe_allow_html=True)
            else:
                # subtle 'heartbeat' swap every rerun second
                beat = "❤️" if int(time.time()) % 2 == 0 else "💚"
                st.markdown(f"<div style='font-size:20px;color:#2ecc71;'>{beat} Stable Pulse — Normal Rhythm</div>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ No vitals available.")

        # Soft auto-refresh fallback (no extra deps)
        if st.session_state.get("patient"):
            time.sleep(3)
            st.experimental_rerun()

        # Treatment history
        st.subheader("🧾 Treatment History")
        history = st.session_state.get("treatment_history", [])
        if history:
            for t in history:
                st.write(t)
        else:
            st.info("No treatments yet.")
    else:
        st.info("No active patient.")

    # Score
    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.get("score", 0))
