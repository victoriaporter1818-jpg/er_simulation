import random

import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------
# GLOBAL CSS (layout, spacing, overlay)
# --------------------------------------
st.markdown("""
<style>
/* Tighten global padding to maximize horizontal space */
main[data-testid="stAppViewContainer"] { padding: 0 !important; }
.block-container { padding: 1rem 1.5rem !important; }

/* Columns: small gutter between center and right */
div[data-testid="stHorizontalBlock"] { gap: 0.75rem !important; }

/* Make center column hug the left (near sidebar) without big gap */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
  margin-left: 0 !important;
  padding-left: 0 !important;
}

/* ---------- Transfer Overlay (cinematic, solid white panel) ---------- */
#overlay-backdrop {
  position: fixed; inset: 0;
  background: rgba(10, 20, 30, 0.35);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999;
  animation: fadeIn 250ms ease-out forwards;
}

#overlay-panel {
  width: min(860px, 92vw);
  border-radius: 16px;
  background: #ffffff; /* SOLID white per request */
  box-shadow: 0 18px 60px rgba(0,0,0,0.25);
  overflow: hidden;
  transform: translateY(24px);
  opacity: 0;
  animation: slideUp 320ms ease-out forwards;
}

/* Colored header strip — color injected inline via Python */
.overlay-head {
  padding: 14px 18px;
  color: #0f172a;
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: 0.2px;
  background: var(--outcomeColor, #e2e8f0);
  border-bottom: 1px solid rgba(0,0,0,0.06);
}

/* Body */
.overlay-body {
  padding: 16px 18px 10px 18px;
}

.overlay-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.overlay-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px 14px;
  background: #fff;
}

.overlay-footer {
  display: flex; gap: 8px; justify-content: flex-end;
  padding: 8px 18px 16px 18px;
}

/* Buttons look */
.btn-primary {
  background: #2563eb; color: white; border: none;
  padding: 9px 14px; border-radius: 10px; font-weight: 600;
}
.btn-secondary {
  background: #f3f4f6; color: #111827; border: 1px solid #e5e7eb;
  padding: 9px 14px; border-radius: 10px; font-weight: 600;
}

/* Keyframes */
@keyframes fadeIn {
  from { opacity: 0 }
  to   { opacity: 1 }
}
@keyframes slideUp {
  from { transform: translateY(24px); opacity: 0 }
  to   { transform: translateY(0);    opacity: 1 }
}

/* Color tags for room sections */
h4.room-tag {
  padding: 6px 10px; border-radius: 8px; display: inline-block;
  font-weight: 700; font-size: 0.95rem; margin: 6px 0 6px 0;
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
if "test_results" not in st.session_state:
    st.session_state.test_results = []
if "next_patient_button_clicked" not in st.session_state:
    st.session_state.next_patient_button_clicked = False
# overlay state
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False
if "summary_payload" not in st.session_state:
    st.session_state.summary_payload = {}

# --------------------------------------
# PATIENT DATA
# --------------------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "vitals": {
            "BP": "90/60",
            "HR": 120,
            "O2": "85%",
            "Temp": "37.0°C",
        },
        "diagnosis": "Heart attack",
        "medical_history": {
            "Allergies": "None",
            "Past Surgeries": "None",
            "Current Medications": "None",
            "Chronic Conditions": "None",
        },
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "vitals": {
            "BP": "110/70",
            "HR": 95,
            "O2": "88%",
            "Temp": "39.2°C",
        },
        "diagnosis": "Pneumonia",
        "medical_history": {
            "Allergies": "Penicillin",
            "Past Surgeries": "Appendectomy",
            "Current Medications": "Ibuprofen",
            "Chronic Conditions": "Asthma",
        },
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "vitals": {
            "BP": "150/90",
            "HR": 82,
            "O2": "97%",
            "Temp": "36.8°C",
        },
        "diagnosis": "Stroke",
        "medical_history": {
            "Allergies": "None",
            "Past Surgeries": "Knee Replacement",
            "Current Medications": "Aspirin",
            "Chronic Conditions": "Hypertension",
        },
    },
]

# --------------------------------------
# FUNCTIONS
# --------------------------------------
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []
    st.session_state.score = 0  # reset score per new case
    st.session_state.test_results = []

def compute_summary(score: int):
    total = max(0, min(100, int(score)))
    if total >= 85:
        outcome, color = "🏆 Excellent", "#22c55e"  # green
    elif total >= 70:
        outcome, color = "🙂 Good", "#84cc16"       # lime/green
    elif total >= 50:
        outcome, color = "⚠️ Fair", "#f59e0b"       # amber
    else:
        outcome, color = "💀 Poor", "#ef4444"       # red
    # Some playful variety
    diagnostic_accuracy = random.randint(60, 100)
    resource_efficiency = random.randint(50, 95)
    return {
        "total_score": total,
        "outcome": outcome,
        "color": color,
        "diagnostic_accuracy": diagnostic_accuracy,
        "resource_efficiency": resource_efficiency
    }

# --------------------------------------
# SUPPLY ROOM ITEMS (GROUPED & COLORED)
# --------------------------------------
categorized_supplies = {
    "Airway & Breathing": {
        "Oxygen Mask": "Used to deliver oxygen to patients with breathing difficulties.",
        "Intubation Kit": "Contains tools required to insert a breathing tube into the airway.",
        "Defibrillator and Pads": "Delivers electric shocks to the heart in case of cardiac arrest."
    },
    "Circulation & IV": {
        "IV Kit": "Includes catheter and supplies for IV fluids or medications.",
        "Saline and Other IV Fluids": "Used to hydrate or deliver IV medications.",
        "Tourniquet": "Stops blood flow to a limb in severe bleeding."
    },
    "Diagnostics": {
        "Test Swabs": "Used to take samples of bodily fluids for infection testing.",
        "Glucometer": "Measures blood glucose levels.",
        "Thermometer": "Measures body temperature."
    },
    "Immobilization": {
        "Cervical Collar": "Immobilizes the neck to prevent further injury.",
        "Arm Splint": "Used to immobilize broken or injured limbs."
    },
    "General Care": {
        "Catheter Kit": "Used for urinary drainage in immobile patients.",
        "Bed Pan": "For bedridden patients to use safely.",
        "Sutures": "Used to close wounds or surgical incisions."
    }
}
supply_color_map = {
    "Airway & Breathing": "#d0f0fd",
    "Circulation & IV": "#d0ffd0",
    "Diagnostics": "#fff6d0",
    "Immobilization": "#ffe0d0",
    "General Care": "#e0d0ff"
}

# --------------------------------------
# MEDSTATION (GROUPED & COLORED)
# --------------------------------------
med_categories = {
    "Pain Relief": {
        "Acetaminophen": "Used to reduce fever and relieve mild pain.",
        "Morphine": "Powerful opioid used for severe pain management.",
        "Motrin": "Anti-inflammatory and pain relief medication (ibuprofen)."
    },
    "Antiemetics": {
        "Ondansetron": "Used to prevent nausea and vomiting."
    },
    "Neurological": {
        "Phenytoin": "Used to control seizures.",
        "Midodrine": "Used to raise low blood pressure."
    },
    "Cardiac & Emergency": {
        "Epinephrine": "Used for severe allergic reactions and cardiac arrest.",
        "Hydralazine": "Used to treat high blood pressure.",
        "Heparin": "Prevents blood clots.",
        "Lasix": "Diuretic used to remove excess fluid.",
        "Naloxone": "Used to reverse opioid overdose."
    },
    "Metabolic": {
        "Glucose": "Used to treat low blood sugar."
    }
}
med_color_map = {
    "Pain Relief": "#fde0dc",
    "Antiemetics": "#fff5d7",
    "Neurological": "#e3f2fd",
    "Cardiac & Emergency": "#e8f5e9",
    "Metabolic": "#f3e5f5"
}

# --------------------------------------
# DIAGNOSTIC LAB (GROUPED & COLORED)
# --------------------------------------
diagnostic_tests = {
    "Imaging": {
        "Chest X-Ray": "Visualizes lungs, heart, and chest structures to assess respiratory distress.",
        "CT Scan": "Provides detailed imaging for suspected stroke or internal injuries.",
        "ECG": "Captures electrical activity of the heart to identify cardiac events."
    },
    "Laboratory": {
        "Cardiac Enzymes": "Measures troponin levels to detect myocardial injury.",
        "CBC": "Evaluates infection or anemia via complete blood count.",
        "Blood Gas": "Analyzes oxygenation and acid-base status from arterial blood."
    },
    "Rapid Tests": {
        "Viral Panel": "Screens for viral pathogens causing respiratory symptoms.",
        "Rapid Strep": "Detects group A strep for throat infections.",
        "D-Dimer": "Helps assess clot formation or pulmonary embolism risk."
    }
}

diagnostic_color_map = {
    "Imaging": "#e0f2fe",
    "Laboratory": "#fef3c7",
    "Rapid Tests": "#ede9fe"
}

diagnostic_results_map = {
    "Heart attack": {
        "ECG": "ST elevations noted in leads II, III, aVF indicative of inferior MI.",
        "Cardiac Enzymes": "Troponin I markedly elevated at 3.2 ng/mL.",
        "CT Scan": "No acute intracranial findings; ordered to rule out stroke mimics.",
        "Blood Gas": "Mild metabolic acidosis with lactate of 3.1 mmol/L.",
        "D-Dimer": "Within normal range, low suspicion for PE."
    },
    "Pneumonia": {
        "Chest X-Ray": "Right lower lobe consolidation with air bronchograms.",
        "CBC": "Leukocytosis at 15k with left shift.",
        "Blood Gas": "PaO2 62 mmHg on room air indicating hypoxemia.",
        "Viral Panel": "Negative for influenza A/B; COVID-19 PCR pending.",
        "Rapid Strep": "Negative result."
    },
    "Stroke": {
        "CT Scan": "Hypodensity in left MCA territory consistent with acute ischemic stroke.",
        "ECG": "Atrial fibrillation with rapid ventricular response.",
        "CBC": "Within normal limits.",
        "D-Dimer": "Elevated at 820 ng/mL — consider concurrent thrombotic process.",
        "Blood Gas": "Normal acid-base status.",
        "Cardiac Enzymes": "Slightly elevated troponin at 0.08 ng/mL from demand ischemia."
    }
}


def get_diagnostic_result(test_name: str, patient: dict) -> str:
    if not patient:
        return "No patient assigned."
    diagnosis = patient.get("diagnosis")
    diagnosis_results = diagnostic_results_map.get(diagnosis, {})
    return diagnosis_results.get(test_name, "Result pending; follow up with the lab soon.")

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 Emergency Room Simulation")

    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    st.write(f"Selected Difficulty: {difficulty}")

    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist"], key="role")
    st.write(f"Selected Role: {role}")

    rooms = ["ER", "Supply Room", "Medstation", "Diagnostic Lab"]
    st.session_state.room = st.radio("Select a Room", rooms, index=rooms.index(st.session_state.room))

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
        st.rerun()  # immediate refresh

# --------------------------------------
# MAIN LAYOUT
# --------------------------------------
col1, col2, col3 = st.columns([0.3, 3, 1.3])  # center wide

# ---- CENTER COLUMN ----
with col2:

    # --------------------------- ER ROOM ---------------------------
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

            # -------------------- USE SUPPLIES --------------------
            if st.session_state.inventory:
                st.subheader("🧰 Use Supplies")
                available_supplies = [x for grp in categorized_supplies.values() for x in grp.keys()]
                supplies_you_have = [s for s in st.session_state.inventory if s in available_supplies]
                if supplies_you_have:
                    selected_item = st.selectbox("Select an item to use from inventory:", supplies_you_have)
                    if st.button("Use Selected Item"):
                        diagnosis = p["diagnosis"]
                        correct_uses = {
                            "Heart attack": ["Defibrillator and Pads", "Oxygen Mask", "IV Kit"],
                            "Pneumonia": ["Oxygen Mask", "Thermometer", "IV Kit"],
                            "Stroke": ["Oxygen Mask", "IV Kit", "Glucometer"]
                        }
                        if selected_item in correct_uses.get(diagnosis, []):
                            st.session_state.score += 5
                            feedback = f"✅ Correct use! {selected_item} was appropriate. (+5 points)"
                        else:
                            feedback = f"⚠️ {selected_item} had limited effect."
                        st.session_state.treatment_history.append(
                            f"Used {selected_item} on {p['name']}. {feedback}"
                        )
                        st.session_state.inventory.remove(selected_item)
                        st.success(feedback)
                        st.toast(feedback, icon="💉")
                        st.rerun()
                else:
                    st.info("No available supplies in your inventory to use.")
            else:
                st.info("No available supplies in your inventory to use.")

            # -------------------- GIVE MEDICATION --------------------
            meds_whitelist = [
                "Acetaminophen", "Morphine", "Motrin", "Ondansetron", "Phenytoin",
                "Epinephrine", "Glucose", "Hydralazine", "Midodrine", "Heparin", "Lasix", "Naloxone"
            ]
            meds_in_inventory = [m for m in st.session_state.inventory if m in meds_whitelist]
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
                    st.session_state.treatment_history.append(
                        f"Gave {selected_med} to {p['name']}. {feedback}"
                    )
                    st.session_state.inventory.remove(selected_med)
                    st.success(feedback)
                    st.toast(feedback, icon="💊")
                    st.rerun()
            else:
                st.info("No medications available in your inventory.")

            # -------------------- TRANSFER PATIENT (ER ONLY) --------------------
            st.subheader("🏥 Transfer Patient")
            transfer_option = st.selectbox(
                "Select Transfer Destination:",
                ["-- Select --", "Discharge", "Send to Surgery", "Send to ICU"],
                key="transfer_destination"
            )
            if st.button("Confirm Transfer", key="confirm_transfer"):
                # compute & store summary payload, then show overlay
                payload = compute_summary(st.session_state.score)
                payload["transfer_option"] = transfer_option
                st.session_state.summary_payload = payload
                st.session_state.show_summary = True
                st.rerun()

        else:
            st.info("No active patient.")

    # --------------------------- SUPPLY ROOM ---------------------------
    elif st.session_state.room == "Supply Room":
        st.header("🛒 Supply Room")
        for category, supplies in categorized_supplies.items():
            st.markdown(
                f"<h4 class='room-tag' style='background:{supply_color_map[category]}'>{category}</h4>",
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
                                st.toast(f"✅ {item} added to inventory!", icon="📦")
                                st.rerun()
                            else:
                                st.warning(f"{item} already in inventory.")
                                st.toast(f"⚠️ {item} already in inventory.", icon="⚠️")

    # --------------------------- MEDSTATION ---------------------------
    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")
        for category, meds in med_categories.items():
            st.markdown(
                f"<h4 class='room-tag' style='background:{med_color_map[category]}'>{category}</h4>",
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
                                st.toast(f"⚠️ {med} already in inventory.", icon="⚠️")

    # --------------------------- DIAGNOSTIC LAB ---------------------------
    elif st.session_state.room == "Diagnostic Lab":
        st.header("🧪 Diagnostic Lab")
        patient = st.session_state.patient
        if not patient:
            st.info("Assign a patient in the ER to order diagnostic tests.")
        else:
            st.write(
                "Order imaging, laboratory, or rapid tests to gather more data for your working diagnosis."
            )
            for category, tests in diagnostic_tests.items():
                st.markdown(
                    f"<h4 class='room-tag' style='background:{diagnostic_color_map[category]}'>{category}</h4>",
                    unsafe_allow_html=True
                )
                test_items = list(tests.items())
                for i in range(0, len(test_items), 2):
                    colA, colB = st.columns(2)
                    for col, (test_name, desc) in zip((colA, colB), test_items[i:i+2]):
                        with col.expander(test_name):
                            st.write(desc)
                            if st.button(
                                f"Order {test_name}",
                                key=f"diagnostic_{category}_{test_name}"
                            ):
                                result_text = get_diagnostic_result(test_name, patient)
                                st.session_state.test_results.append(
                                    {"test": test_name, "result": result_text}
                                )
                                st.session_state.treatment_history.append(
                                    f"Ordered {test_name}. Result: {result_text}"
                                )
                                st.success(f"Results received for {test_name}.")
                                st.toast(f"🧪 {test_name} results ready!", icon="🧪")

# ---- RIGHT COLUMN ----
with col3:
    st.subheader("👩‍⚕️ Patient Data")
    if st.session_state.patient:
        p = st.session_state.patient
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Age:** {p['age']}")
        st.write(f"**Symptoms:** {p['symptoms']}")
        if "vitals" in p and p["vitals"]:
            vitals = p["vitals"]
            st.subheader("🩺 Patient Vitals")
            st.write(f"**BP:** {vitals.get('BP', 'N/A')}")
            st.write(f"**HR:** {vitals.get('HR', 'N/A')}")
            st.write(f"**O2:** {vitals.get('O2', 'N/A')}")
            st.write(f"**Temp:** {vitals.get('Temp', 'N/A')}")
        else:
            st.warning("⚠️ No vitals available for this patient.")
        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for t in st.session_state.treatment_history:
                st.write(t)
        else:
            st.write("No treatments administered yet.")
        st.subheader("🔬 Diagnostic Results")
        if st.session_state.test_results:
            for result in st.session_state.test_results:
                st.write(f"**{result['test']}:** {result['result']}")
        else:
            st.write("No diagnostic tests ordered yet.")
    else:
        st.info("No active patient.")
    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)

# --------------------------------------
# RENDER TRANSFER OVERLAY (if flagged)
# --------------------------------------
if st.session_state.get("show_summary", False):
    payload = st.session_state.get("summary_payload", {})
    color = payload.get("color", "#e2e8f0")
    total_score = payload.get("total_score", 0)
    outcome = payload.get("outcome", "Summary")
    transfer_option = payload.get("transfer_option", "-- Select --")
    diag = payload.get("diagnostic_accuracy", 75)
    res = payload.get("resource_efficiency", 75)

    # Inject proper HTML overlay (rendered, not escaped)
    overlay_html = f"""
    <div id="overlay-backdrop">
      <div id="overlay-panel">
        <div class="overlay-head" style="--outcomeColor:{color}">
          Patient Transfer Summary — <span style="opacity:.9">Score: {total_score}/100</span>
        </div>
        <div class="overlay-body">
          <h3 style="margin:0 0 8px 0;">{outcome}</h3>
          <div style="margin-bottom:8px; color:#334155;">Transfer decision: <b>{transfer_option}</b></div>

          <div class="overlay-grid" style="margin-top:8px;">
            <div class="overlay-card">
              <div style="font-weight:700; margin-bottom:6px;">Treatment Effectiveness</div>
              <div style="height:10px;background:#e5e7eb;border-radius:999px;overflow:hidden;">
                <div style="height:10px;width:{total_score}%;background:{color};"></div>
              </div>
            </div>
            <div class="overlay-card">
              <div style="font-weight:700; margin-bottom:6px;">Diagnostic Accuracy</div>
              <div style="height:10px;background:#e5e7eb;border-radius:999px;overflow:hidden;">
                <div style="height:10px;width:{diag}%;background:#60a5fa;"></div>
              </div>
            </div>
            <div class="overlay-card">
              <div style="font-weight:700; margin-bottom:6px;">Resource Management</div>
              <div style="height:10px;background:#e5e7eb;border-radius:999px;overflow:hidden;">
                <div style="height:10px;width:{res}%;background:#f59e0b;"></div>
              </div>
            </div>
            <div class="overlay-card">
              <div style="font-weight:700; margin-bottom:6px;">Quick Tips</div>
              <div style="color:#475569;">
                Keep stabilizing ABCs, reassess vitals, and match interventions to likely etiology.
                Consider earlier imaging and avoid redundant meds.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """

    components.html(overlay_html, height=620)  # ✅ Renders as styled HTML

    footer_cols = st.columns([5, 1.2, 1.6])
    with footer_cols[1]:
        cancel = st.button("Close", key="close_overlay")
    with footer_cols[2]:
        new_case = st.button("🆕 Start New Case", key="overlay_new_case")

    if new_case:
        st.session_state.patient = None
        st.session_state.treatment_history = []
        st.session_state.score = 0
        st.session_state.show_summary = False
        st.session_state.summary_payload = {}
        st.rerun()

    if cancel:
        st.session_state.show_summary = False
        st.session_state.summary_payload = {}
        st.rerun()
