import streamlit as st
import random
import math
import copy

# --------------------------------------
# PAGE CONFIGURATION
# --------------------------------------
st.set_page_config(
    page_title="Emergency Room Simulation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------
# CSS FOR SPACING & ALIGNMENT
# --------------------------------------
st.markdown("""
<style>
/* Tighten global padding */
main[data-testid="stAppViewContainer"] { padding-left: 0 !important; margin-left: 0 !important; }
.block-container { padding-left: 0 !important; margin-left: 0 !important; width: 100% !important; }
/* Add small gaps between columns */
div[data-testid="stHorizontalBlock"] { gap: 1.2rem !important; }
/* Nudge center column flush toward the sidebar with a tiny left padding and small right margin */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
    padding-left: 0.4rem !important;
    margin-right: 0.6rem !important; /* small space to the right of center column contents */
}
/* Right column: align content slightly inward */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) * {
    text-align: left !important;
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
    st.session_state.test_results = None
if "next_patient_button_clicked" not in st.session_state:
    st.session_state.next_patient_button_clicked = False
# vitals state
if "baseline_vitals" not in st.session_state:
    st.session_state.baseline_vitals = None  # dict (numeric)
if "current_vitals" not in st.session_state:
    st.session_state.current_vitals = None   # dict (numeric)
if "allergic_reaction_active" not in st.session_state:
    st.session_state.allergic_reaction_active = False

# --------------------------------------
# UTILS FOR VITALS
# --------------------------------------
def parse_bp_str(bp_str: str):
    # "120/80" -> (120, 80)
    try:
        s, d = bp_str.split("/")
        return int(s), int(d)
    except Exception:
        return 120, 80

def format_bp(s, d):
    return f"{int(round(s))}/{int(round(d))}"

def format_o2(o2):
    return f"{int(round(o2))}%"

def format_temp_c(t):
    return f"{t:.1f}°C"

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# --------------------------------------
# PATIENT DATA (with diagnosis & allergies in history)
# --------------------------------------
patients = [
    {
        "name": "John Doe", "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "diagnosis": "Heart attack",
        "medical_history": {
            "Allergies": "None", "Past Surgeries": "None",
            "Current Medications": "None", "Chronic Conditions": "None"
        }
    },
    {
        "name": "Sarah Li", "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "diagnosis": "Pneumonia",
        "medical_history": {
            "Allergies": "Penicillin", "Past Surgeries": "Appendectomy",
            "Current Medications": "Ibuprofen", "Chronic Conditions": "Asthma"
        }
    },
    {
        "name": "Carlos Vega", "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "diagnosis": "Stroke",
        "medical_history": {
            "Allergies": "None", "Past Surgeries": "Knee Replacement",
            "Current Medications": "Aspirin", "Chronic Conditions": "Hypertension"
        }
    },
]

# --------------------------------------
# DIAGNOSIS-BASED BASELINE VITALS (numeric)
# --------------------------------------
def baseline_for_diagnosis(dx: str):
    # returns dict with numeric values: BP_sys, BP_dia, HR, O2, TempC
    # All temps shown in Celsius
    baselines = {
        "Heart attack": dict(BP_sys=90, BP_dia=60, HR=120, O2=85, TempC=37.2),
        "Pneumonia": dict(BP_sys=110, BP_dia=70, HR=95, O2=88, TempC=38.5),
        "Stroke": dict(BP_sys=150, BP_dia=90, HR=82, O2=97, TempC=37.0),
        "Appendicitis": dict(BP_sys=100, BP_dia=65, HR=110, O2=98, TempC=38.0),
        "Seizure": dict(BP_sys=130, BP_dia=85, HR=112, O2=94, TempC=37.2),
        "Anaphylaxis": dict(BP_sys=80, BP_dia=50, HR=140, O2=82, TempC=37.2),
        "Diabetic Crisis": dict(BP_sys=120, BP_dia=80, HR=105, O2=96, TempC=37.2),
    }
    return copy.deepcopy(baselines.get(dx, dict(BP_sys=120, BP_dia=80, HR=80, O2=98, TempC=37.0)))

# --------------------------------------
# FUNCTIONS
# --------------------------------------
def assign_patient():
    patient = random.choice(patients)
    st.session_state.patient = patient
    st.session_state.treatment_history = []
    st.session_state.test_results = None
    st.session_state.score += 10
    st.session_state.allergic_reaction_active = False

    # set baseline & current vitals from diagnosis
    base = baseline_for_diagnosis(patient["diagnosis"])
    st.session_state.baseline_vitals = base
    st.session_state.current_vitals = copy.deepcopy(base)

def get_allergies_list(patient):
    allergies_str = (patient.get("medical_history", {}).get("Allergies") or "").strip()
    if not allergies_str or allergies_str.lower() == "none":
        return []
    return [a.strip().lower() for a in allergies_str.split(",")]

# --------------------------------------
# SUPPLIES & MEDS
# --------------------------------------
emergency_supplies = {
    "Defibrillator and Pads": "Used to deliver electric shocks to the heart in case of cardiac arrest.",
    "Oxygen Mask": "Used to deliver oxygen to patients who are experiencing breathing difficulties.",
    "Intubation Kit": "Contains tools to insert a breathing tube into the airway.",
    "IV Kit": "Includes catheter & supplies to administer IV fluids/medications.",
    "Saline and Other IV Fluids": "Used to hydrate or deliver IV medications.",
    "Catheter Kit": "Used for urinary drainage in immobile patients.",
    "Bed Pan": "For bedridden patients to use safely.",
    "Tourniquet": "Stops blood flow to a limb in severe bleeding.",
    "Sutures": "Used to close wounds or surgical incisions.",
    "Cervical Collar": "Immobilizes the neck after trauma.",
    "Arm Splint": "Immobilizes broken or injured limbs.",
    "Test Swabs": "For sample collection to test infections.",
    "Glucometer": "Measures blood glucose.",
    "Thermometer": "Measures body temperature."
}

# Medstation meds (added Penicillin for allergy scenario)
medstation_meds = {
    "Acetaminophen": "Reduces fever & mild pain.",
    "Morphine": "Strong opioid for severe pain.",
    "Motrin (Ibuprofen)": "NSAID for inflammation & pain.",
    "Ondansetron": "Treats nausea/vomiting.",
    "Phenytoin": "Anticonvulsant for seizures.",
    "Epinephrine": "Treats anaphylaxis; increases BP/HR.",
    "Glucose": "Treats hypoglycemia.",
    "Hydralazine": "Lowers blood pressure.",
    "Midodrine": "Raises blood pressure in hypotension.",
    "Heparin": "Anticoagulant to prevent clots.",
    "Lasix (Furosemide)": "Diuretic for fluid overload.",
    "Naloxone": "Reverses opioid overdose.",
    "Penicillin": "Antibiotic; may trigger allergy if allergic."
}

# Sets used to partition inventory
SUPPLY_ITEM_NAMES = set(emergency_supplies.keys())
MED_ITEM_NAMES = set(medstation_meds.keys())

# --------------------------------------
# EFFECT MODELS
# --------------------------------------
def apply_supply_effect(item: str, diagnosis: str, allergies: list, v: dict):
    """
    Mutates vitals dict v in place; returns (feedback:str, score_delta:int)
    v has numeric keys: BP_sys, BP_dia, HR, O2, TempC
    """
    score = 0
    feedback = None

    if item == "Oxygen Mask":
        # raise O2 by 7 (5–10-ish), clamp
        prev = v["O2"]
        v["O2"] = clamp(v["O2"] + 7, 70, 100)
        delta = v["O2"] - prev
        feedback = f"🫁 Oxygen applied, O₂ +{int(delta)}%."
        if diagnosis in ["Pneumonia", "Heart attack", "Anaphylaxis"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif item == "Intubation Kit":
        prevO2 = v["O2"]
        v["O2"] = clamp(v["O2"] + 10, 70, 100)
        v["HR"] = clamp(v["HR"] - 5, 30, 180)
        feedback = f"🫁 Airway secured, O₂ +{int(v['O2']-prevO2)}%, HR -5."
        if diagnosis in ["Heart attack", "Anaphylaxis", "Stroke"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif item in ["IV Kit", "Saline and Other IV Fluids"]:
        # stabilize BP/HR toward normal (120/80 and HR 80)
        target_sys, target_dia, target_hr = 120, 80, 80
        v["BP_sys"] = clamp(v["BP_sys"] + (target_sys - v["BP_sys"]) * 0.4, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] + (target_dia - v["BP_dia"]) * 0.4, 40, 120)
        v["HR"] = clamp(v["HR"] + (target_hr - v["HR"]) * 0.4, 30, 180)
        feedback = "💧 IV access/fluids started. BP/HR trending toward normal."
        if diagnosis in ["Heart attack", "Pneumonia", "Stroke", "Diabetic Crisis", "Anaphylaxis"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif item == "Defibrillator and Pads":
        # Best when heart attack; improve BP/HR modestly
        v["BP_sys"] = clamp(v["BP_sys"] + 8, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] + 5, 40, 120)
        v["HR"] = clamp(v["HR"] - 10, 30, 180)
        feedback = "⚡ Defibrillator used. HR improved; BP up slightly."
        if diagnosis == "Heart attack":
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif item == "Glucometer":
        feedback = "🩸 Checked blood glucose."
        if diagnosis == "Diabetic Crisis":
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif item == "Thermometer":
        feedback = "🌡️ Checked temperature."
        if diagnosis in ["Pneumonia", "Appendicitis"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    else:
        # neutral items
        feedback = f"ℹ️ {item} used. Limited effect."
        score += 0

    return feedback, score

def apply_medication_effect(med: str, diagnosis: str, allergies: list, v: dict):
    """
    Mutates vitals dict v in place; returns (feedback:str, score_delta:int)
    Handles allergy trigger & reversal.
    """
    score = 0
    feedback = None
    alrx = st.session_state.allergic_reaction_active

    if med in ["Motrin (Ibuprofen)", "Acetaminophen"]:
        prev = v["TempC"]
        v["TempC"] = clamp(v["TempC"] - random.uniform(1.0, 1.5), 34.0, 41.0)
        feedback = f"🧊 {med} given. Temp {prev:.1f}°C → {v['TempC']:.1f}°C."
        if diagnosis in ["Pneumonia", "Appendicitis"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Morphine":
        v["HR"] = clamp(v["HR"] - 6, 30, 180)
        v["BP_sys"] = clamp(v["BP_sys"] - 4, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] - 3, 40, 120)
        feedback = "💊 Morphine given. HR and BP slightly reduced."
        if diagnosis in ["Heart attack", "Appendicitis"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Ondansetron":
        feedback = "🤢 Ondansetron given for nausea."
        score += 2

    elif med == "Phenytoin":
        v["HR"] = clamp(v["HR"] - 5, 30, 180)
        feedback = "⚡ Phenytoin given to control seizures."
        if diagnosis == "Seizure":
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Epinephrine":
        # Reverse anaphylaxis if active; otherwise boost BP/HR slightly
        if alrx:
            st.session_state.allergic_reaction_active = False
            v["BP_sys"] = clamp(v["BP_sys"] + 20, 70, 200)
            v["BP_dia"] = clamp(v["BP_dia"] + 10, 40, 120)
            v["HR"] = clamp(v["HR"] - 10, 30, 180)
            v["O2"] = clamp(v["O2"] + 6, 70, 100)
            feedback = "🧯 Epinephrine reversed allergic reaction. Vitals improved."
            score += 8
        else:
            v["BP_sys"] = clamp(v["BP_sys"] + 8, 70, 200)
            v["BP_dia"] = clamp(v["BP_dia"] + 4, 40, 120)
            v["HR"] = clamp(v["HR"] + 6, 30, 180)
            feedback = "🚑 Epinephrine given. BP/HR increased."
            if diagnosis == "Anaphylaxis":
                score += 5
                feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Glucose":
        v["BP_sys"] = clamp(v["BP_sys"] + 6, 70, 200)
        v["HR"] = clamp(v["HR"] - 4, 30, 180)
        feedback = "🍬 Glucose given. BP up slightly, HR stabilized."
        if diagnosis == "Diabetic Crisis":
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Hydralazine":
        v["BP_sys"] = clamp(v["BP_sys"] - 12, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] - 8, 40, 120)
        feedback = "⬇️ Hydralazine given. BP reduced."
        if diagnosis in ["Stroke", "Hypertensive Emergency"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Midodrine":
        v["BP_sys"] = clamp(v["BP_sys"] + 10, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] + 6, 40, 120)
        feedback = "⬆️ Midodrine given. BP increased."
        if diagnosis in ["Anaphylaxis", "Hypotension"]:
            score += 5
            feedback += " ✅ Appropriate. (+5 points)"

    elif med == "Heparin":
        v["BP_sys"] = clamp(v["BP_sys"] - 2, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] - 1, 40, 120)
        feedback = "🩸 Heparin administered. Anticoagulation started."

    elif med == "Lasix (Furosemide)":
        v["BP_sys"] = clamp(v["BP_sys"] - 6, 70, 200)
        v["BP_dia"] = clamp(v["BP_dia"] - 4, 40, 120)
        v["O2"] = clamp(v["O2"] + 3, 70, 100)
        feedback = "💧 Lasix given. BP reduced slightly; O₂ improved."

    elif med == "Naloxone":
        # reverse opioid effect (e.g., from Morphine overload); improve HR/O2
        v["HR"] = clamp(v["HR"] + 6, 30, 180)
        v["O2"] = clamp(v["O2"] + 5, 70, 100)
        feedback = "🛑 Naloxone administered. Reversed opioid effects."

    elif med == "Penicillin":
        # Trigger allergy if allergic
        if "penicillin" in allergies:
            st.session_state.allergic_reaction_active = True
            v["BP_sys"] = clamp(v["BP_sys"] - 15, 70, 200)
            v["BP_dia"] = clamp(v["BP_dia"] - 10, 40, 120)
            v["HR"] = clamp(v["HR"] + 15, 30, 180)
            v["O2"] = clamp(v["O2"] - 6, 70, 100)
            feedback = "⚠️ Allergic reaction triggered by Penicillin! BP ↓, HR ↑, O₂ ↓."
            score -= 5
        else:
            feedback = "💊 Penicillin administered."

    else:
        feedback = f"ℹ️ {med} given."
        score += 0

    return feedback, score

# --------------------------------------
# SIDEBAR
# --------------------------------------
with st.sidebar:
    st.header("🏥 Emergency Room Simulation")

    difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
    st.write(f"Selected Difficulty: {difficulty}")

    role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist", "Admin"], key="role")
    st.write(f"Selected Role: {role}")

    rooms = ["ER", "Supply Room", "Medstation", "Operating Room", "Radiology Lab", "Pharmacy"]
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
            p = st.session_state.patient
            st.subheader("Patient Information")
            st.write(f"**Name:** {p['name']}")
            st.write(f"**Age:** {p['age']}")
            st.write(f"**Symptoms:** {p['symptoms']}")

            # Show baseline reminder (optional)
            st.caption(f"Diagnosis: {p['diagnosis']} — vitals reset to diagnosis baseline on Next Patient.")

            # Show simple history
            st.subheader("📜 Medical History")
            for k, v in p["medical_history"].items():
                st.write(f"**{k}:** {v}")

            # -----------------------------
            # 🧰 USE SUPPLIES (Supply Room items only)
            # -----------------------------
            available_supplies = [it for it in st.session_state.inventory if it in SUPPLY_ITEM_NAMES]
            if available_supplies:
                st.subheader("🧰 Use Supplies")
                selected_supply = st.selectbox(
                    "Select a supply to use:",
                    available_supplies,
                    key="use_supply_select"
                )
                if st.button("Use Selected Supply"):
                    v = st.session_state.current_vitals
                    dx = p["diagnosis"]
                    allergies = get_allergies_list(p)

                    feedback, pts = apply_supply_effect(selected_supply, dx, allergies, v)
                    st.session_state.score += pts
                    st.session_state.treatment_history.append(
                        f"Used {selected_supply} on {p['name']}. {feedback}"
                    )
                    # Supplies are generally reusable; do NOT remove from inventory
                    st.success(feedback)
                    st.toast(feedback, icon="🧰")
                    st.rerun()
            else:
                st.info("No available supplies from your inventory to use.")

            # -----------------------------
            # 💊 GIVE MEDICATION (Medstation meds only)
            # -----------------------------
            available_meds = [m for m in st.session_state.inventory if m in MED_ITEM_NAMES]
            if available_meds:
                st.subheader("💊 Give Medication")
                selected_med = st.selectbox(
                    "Select a medication to give:",
                    available_meds,
                    key="give_med_select"
                )
                if st.button("Give Selected Medication"):
                    v = st.session_state.current_vitals
                    dx = p["diagnosis"]
                    allergies = get_allergies_list(p)

                    feedback, pts = apply_medication_effect(selected_med, dx, allergies, v)
                    st.session_state.score += pts
                    st.session_state.treatment_history.append(
                        f"Gave {selected_med} to {p['name']}. {feedback}"
                    )
                    # Meds are consumed on use
                    st.session_state.inventory.remove(selected_med)
                    st.success(feedback)
                    st.toast(feedback, icon="💊")
                    st.rerun()
            else:
                st.info("No medications in your inventory. Collect some in the Medstation.")

        else:
            st.info("No active patient.")

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
                "Oxygen Mask": emergency_supplies["Oxygen Mask"],
                "Intubation Kit": emergency_supplies["Intubation Kit"],
                "Defibrillator and Pads": emergency_supplies["Defibrillator and Pads"]
            },
            "Circulation & IV": {
                "IV Kit": emergency_supplies["IV Kit"],
                "Saline and Other IV Fluids": emergency_supplies["Saline and Other IV Fluids"],
                "Tourniquet": emergency_supplies["Tourniquet"]
            },
            "Diagnostics": {
                "Test Swabs": emergency_supplies["Test Swabs"],
                "Glucometer": emergency_supplies["Glucometer"],
                "Thermometer": emergency_supplies["Thermometer"]
            },
            "Immobilization": {
                "Cervical Collar": emergency_supplies["Cervical Collar"],
                "Arm Splint": emergency_supplies["Arm Splint"]
            },
            "General Care": {
                "Catheter Kit": emergency_supplies["Catheter Kit"],
                "Bed Pan": emergency_supplies["Bed Pan"],
                "Sutures": emergency_supplies["Sutures"]
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
                for col, (item, description) in zip((colA, colB), items[i:i+2]):
                    with col.expander(item):
                        st.write(description)
                        if st.button(f"Add {item} to Inventory", key=f"supply_{item}"):
                            if item not in st.session_state.inventory:
                                st.session_state.inventory.append(item)
                                st.success(f"{item} added to inventory.")
                                st.toast(f"✅ {item} added!", icon="📦")
                                st.rerun()
                            else:
                                st.warning(f"{item} already in inventory.")

    elif st.session_state.room == "Medstation":
        st.header("💊 Medstation")
        for med, desc in medstation_meds.items():
            with st.expander(med):
                st.write(desc)
                if st.button(f"Add {med} to Inventory", key=f"med_{med}"):
                    if med not in st.session_state.inventory:
                        st.session_state.inventory.append(med)
                        st.success(f"{med} added to inventory.")
                        st.toast(f"💊 {med} collected!", icon="💊")
                        st.rerun()
                    else:
                        st.warning(f"{med} already in inventory.")

    else:
        st.header(f"🚪 {st.session_state.room}")
        st.info("Room functionality coming soon!")

# ---- RIGHT COLUMN ----
with col3:
    st.subheader("👩‍⚕️ Patient Data")
    if st.session_state.patient and st.session_state.current_vitals:
        p = st.session_state.patient
        v = st.session_state.current_vitals
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Age:** {p['age']}")
        st.write(f"**Symptoms:** {p['symptoms']}")
        st.subheader("🩺 Patient Vitals")
        st.write(f"**BP:** {format_bp(v['BP_sys'], v['BP_dia'])}")
        st.write(f"**HR:** {int(round(v['HR']))}")
        st.write(f"**O₂:** {format_o2(v['O2'])}")
        st.write(f"**Temp:** {format_temp_c(v['TempC'])}")

        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for t in st.session_state.treatment_history:
                st.write(t)
        else:
            st.write("No treatments administered yet.")
    else:
        st.info("No active patient.")

    st.subheader("🏆 Score")
    st.metric("Total Score", st.session_state.score)
