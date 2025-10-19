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
        except:
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
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 Emergency Room Simulation")
    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"])
    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist"])
    rooms = ["ER", "Supply Room", "Medstation", "Diagnostic Lab"]
    st.session_state.room = st.radio("Select a Room", rooms, index=rooms.index(st.session_state.room) if st.session_state.room in rooms else 0)

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
    # ---------------- ER ROOM ----------------
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
                    else:
                        feedback = f"⚠️ {selected_item} had limited effect."
                    st.session_state.treatment_history.append(f"Used {selected_item} on {p['name']}. {feedback}")
                    st.session_state.inventory.remove(selected_item)
                    st.success(feedback)
                    st.toast(feedback, icon="💉")
                    st.rerun()
            else:
                st.info("No available supplies in your inventory to use.")

            if selected_item in correct_uses.get(diagnosis, []):
    st.session_state.score += 5
    feedback = f"✅ Correct use! {selected_item} was appropriate. (+5 points)"
    update_vitals("improve")
else:
    feedback = f"⚠️ {selected_item} had limited effect."
    update_vitals("worsen")

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
                    else:
                        feedback = f"⚠️ {selected_med} was not very effective for this condition."
                    st.session_state.treatment_history.append(f"Gave {selected_med} to {p['name']}. {feedback}")
                    st.session_state.inventory.remove(selected_med)
                    st.success(feedback)
                    st.toast(feedback, icon="💊")
                    st.rerun()
            else:
                st.info("No medications available in your inventory.")

            if selected_med in correct_meds.get(diagnosis, []):
    st.session_state.score += 10
    feedback = f"💊 Correct treatment! {selected_med} helped improve the patient's condition. (+10 points)"
    update_vitals("improve")
else:
    feedback = f"⚠️ {selected_med} was not very effective for this condition."
    update_vitals("worsen")

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

                    # --- Diagnostic accuracy calculation ---
                    history = st.session_state.get("treatment_history", [])
                    correct_diagnostics = sum(
                        ("✅" in entry and "test" in entry.lower()) for entry in history
                    )
                    incorrect_diagnostics = sum(
                        ("⚠️" in entry and "test" in entry.lower()) for entry in history
                    )

                    diagnostic_accuracy = 60 + (10 * correct_diagnostics) - (5 * incorrect_diagnostics)
                    diagnostic_accuracy = max(0, min(diagnostic_accuracy, 100))

                    # --- Resource efficiency (placeholder logic for now) ---
                    resource_efficiency = random.randint(50, 95)

                    # --- Outcome and Display ---
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
            st.markdown(f"<h4 style='background-color:{color_map[category]};padding:6px;border-radius:8px;'>{category}</h4>", unsafe_allow_html=True)
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
            st.markdown(f"<h4 style='background-color:{color_map_meds[category]};padding:6px;border-radius:8px;'>{category}</h4>", unsafe_allow_html=True)
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

        # Define body part options for imaging
        body_part_options = ["Chest", "Head", "Abdomen", "Pelvis", "Extremities"]

        # Two main categories
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

        # Correct tests by diagnosis and appropriate body part
        correct_tests = {
            "Heart attack": {"CT Scan": ["Chest"], "MRI": ["Chest"], "Blood Test": None},
            "Pneumonia": {"X-Ray": ["Chest"], "CBC": None, "Blood Test": None},
            "Stroke": {"CT Scan": ["Head"], "MRI": ["Head"], "Blood Test": None}
        }

        # Results
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

        # Layout: 2 columns (Imaging + Lab)
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
                    st.experimental_rerun()

# ---- RIGHT COLUMN ----
with col3:
    st.subheader("👩‍⚕️ Patient Data")

    # Safely check for patient object
    p = st.session_state.get("patient")
    if p:
        st.write(f"**Name:** {p.get('name', 'Unknown')}")
        st.write(f"**Age:** {p.get('age', 'N/A')}")
        st.write(f"**Symptoms:** {p.get('symptoms', 'N/A')}")

        # Safely show vitals
        vitals = p.get("vitals", {})
        if vitals:
            st.subheader("🩺 Patient Vitals")
            st.write(f"**BP:** {vitals.get('BP', 'N/A')}")
            st.write(f"**HR:** {vitals.get('HR', 'N/A')}")
            st.write(f"**O2:** {vitals.get('O2', 'N/A')}")
            st.write(f"**Temp:** {vitals.get('Temp', 'N/A')}")
        else:
            st.warning("⚠️ No vitals available.")

        # Treatment history section
        st.subheader("🧾 Treatment History")
        history = st.session_state.get("treatment_history", [])
        if history:
            for t in history:
                st.write(t)
        else:
            st.info("No treatments yet.")

    else:
        st.info("No active patient.")

    # Always show score at bottom
    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.get("score", 0))
