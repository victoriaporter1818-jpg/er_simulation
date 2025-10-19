diff --git a/er_simulation.py b/er_simulation.py
index 234b1dadc952b1561777414fc197a4090993735f.8c0b8c19c12ab7854c06252e2c7d3e80f35c6815 100644
--- a/er_simulation.py
+++ b/er_simulation.py
@@ -1,28 +1,30 @@
-import streamlit as st
 import random
 
+import streamlit as st
+import streamlit.components.v1 as components
+
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
@@ -105,85 +107,128 @@ div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
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
-    st.session_state.test_results = None
+    st.session_state.test_results = []
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
-    {"name": "John Doe", "age": 45, "symptoms": "severe chest pain and shortness of breath",
-     "vitals": {"BP": "90/60", "HR": 120, "O2": "85%", "Temp": "37.0°C"},
-     "diagnosis": "Heart attack",
-     "medical_history": {"Allergies": "None", "Past Surgeries": "None", "Current Medications": "None", "Chronic Conditions": "None"}},
-    {"name": "Sarah Li", "age": 29, "symptoms": "high fever, cough, and low oxygen",
-     "vitals": {"BP": "110/70", "HR": 95, "O2": "88%", "Temp": "39.2°C"},
-     "diagnosis": "Pneumonia",
-     "medical_history": {"Allergies": "Penicillin", "Past Surgeries": "Appendectomy", "Current Medications": "Ibuprofen", "Chronic Conditions": "Asthma"}},
-    {"name": "Carlos Vega", "age": 60, "symptoms": "sudden weakness on one side and slurred speech",
-     "vitals": {"BP": "150/90", "HR": 82, "O2": "97%", "Temp": "36.8°C"},
-     "diagnosis": "Stroke",
-     "medical_history": {"Allergies": "None", "Past Surgeries": "Knee Replacement", "Current Medications": "Aspirin", "Chronic Conditions": "Hypertension"}},
+    {
+        "name": "John Doe",
+        "age": 45,
+        "symptoms": "severe chest pain and shortness of breath",
+        "vitals": {
+            "BP": "90/60",
+            "HR": 120,
+            "O2": "85%",
+            "Temp": "37.0°C",
+        },
+        "diagnosis": "Heart attack",
+        "medical_history": {
+            "Allergies": "None",
+            "Past Surgeries": "None",
+            "Current Medications": "None",
+            "Chronic Conditions": "None",
+        },
+    },
+    {
+        "name": "Sarah Li",
+        "age": 29,
+        "symptoms": "high fever, cough, and low oxygen",
+        "vitals": {
+            "BP": "110/70",
+            "HR": 95,
+            "O2": "88%",
+            "Temp": "39.2°C",
+        },
+        "diagnosis": "Pneumonia",
+        "medical_history": {
+            "Allergies": "Penicillin",
+            "Past Surgeries": "Appendectomy",
+            "Current Medications": "Ibuprofen",
+            "Chronic Conditions": "Asthma",
+        },
+    },
+    {
+        "name": "Carlos Vega",
+        "age": 60,
+        "symptoms": "sudden weakness on one side and slurred speech",
+        "vitals": {
+            "BP": "150/90",
+            "HR": 82,
+            "O2": "97%",
+            "Temp": "36.8°C",
+        },
+        "diagnosis": "Stroke",
+        "medical_history": {
+            "Allergies": "None",
+            "Past Surgeries": "Knee Replacement",
+            "Current Medications": "Aspirin",
+            "Chronic Conditions": "Hypertension",
+        },
+    },
 ]
 
 # --------------------------------------
 # FUNCTIONS
 # --------------------------------------
 def assign_patient():
     patient = random.choice(patients)
     st.session_state.patient = patient
     st.session_state.treatment_history = []
     st.session_state.score = 0  # reset score per new case
+    st.session_state.test_results = []
 
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
@@ -234,63 +279,123 @@ med_categories = {
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
 
+# --------------------------------------
+# DIAGNOSTIC LAB (GROUPED & COLORED)
+# --------------------------------------
+diagnostic_tests = {
+    "Imaging": {
+        "Chest X-Ray": "Visualizes lungs, heart, and chest structures to assess respiratory distress.",
+        "CT Scan": "Provides detailed imaging for suspected stroke or internal injuries.",
+        "ECG": "Captures electrical activity of the heart to identify cardiac events."
+    },
+    "Laboratory": {
+        "Cardiac Enzymes": "Measures troponin levels to detect myocardial injury.",
+        "CBC": "Evaluates infection or anemia via complete blood count.",
+        "Blood Gas": "Analyzes oxygenation and acid-base status from arterial blood."
+    },
+    "Rapid Tests": {
+        "Viral Panel": "Screens for viral pathogens causing respiratory symptoms.",
+        "Rapid Strep": "Detects group A strep for throat infections.",
+        "D-Dimer": "Helps assess clot formation or pulmonary embolism risk."
+    }
+}
+
+diagnostic_color_map = {
+    "Imaging": "#e0f2fe",
+    "Laboratory": "#fef3c7",
+    "Rapid Tests": "#ede9fe"
+}
+
+diagnostic_results_map = {
+    "Heart attack": {
+        "ECG": "ST elevations noted in leads II, III, aVF indicative of inferior MI.",
+        "Cardiac Enzymes": "Troponin I markedly elevated at 3.2 ng/mL.",
+        "CT Scan": "No acute intracranial findings; ordered to rule out stroke mimics.",
+        "Blood Gas": "Mild metabolic acidosis with lactate of 3.1 mmol/L.",
+        "D-Dimer": "Within normal range, low suspicion for PE."
+    },
+    "Pneumonia": {
+        "Chest X-Ray": "Right lower lobe consolidation with air bronchograms.",
+        "CBC": "Leukocytosis at 15k with left shift.",
+        "Blood Gas": "PaO2 62 mmHg on room air indicating hypoxemia.",
+        "Viral Panel": "Negative for influenza A/B; COVID-19 PCR pending.",
+        "Rapid Strep": "Negative result."
+    },
+    "Stroke": {
+        "CT Scan": "Hypodensity in left MCA territory consistent with acute ischemic stroke.",
+        "ECG": "Atrial fibrillation with rapid ventricular response.",
+        "CBC": "Within normal limits.",
+        "D-Dimer": "Elevated at 820 ng/mL — consider concurrent thrombotic process.",
+        "Blood Gas": "Normal acid-base status.",
+        "Cardiac Enzymes": "Slightly elevated troponin at 0.08 ng/mL from demand ischemia."
+    }
+}
+
+
+def get_diagnostic_result(test_name: str, patient: dict) -> str:
+    if not patient:
+        return "No patient assigned."
+    diagnosis = patient.get("diagnosis")
+    diagnosis_results = diagnostic_results_map.get(diagnosis, {})
+    return diagnosis_results.get(test_name, "Result pending; follow up with the lab soon.")
+
 # --------------------------------------
 # SIDEBAR
 # --------------------------------------
 with st.sidebar:
     st.header("🏥 Emergency Room Simulation")
 
     difficulty = st.selectbox("Choose Difficulty", ["Easy", "Medium", "Hard"], key="difficulty")
     st.write(f"Selected Difficulty: {difficulty}")
 
     role = st.radio("Select Your Role", ["Doctor", "Nurse", "Radiologist"], key="role")
     st.write(f"Selected Role: {role}")
 
-    rooms = ["ER", "Supply Room", "Medstation"]
+    rooms = ["ER", "Supply Room", "Medstation", "Diagnostic Lab"]
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
@@ -419,73 +524,114 @@ with col2:
 
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
 
+    # --------------------------- DIAGNOSTIC LAB ---------------------------
+    elif st.session_state.room == "Diagnostic Lab":
+        st.header("🧪 Diagnostic Lab")
+        patient = st.session_state.patient
+        if not patient:
+            st.info("Assign a patient in the ER to order diagnostic tests.")
+        else:
+            st.write(
+                "Order imaging, laboratory, or rapid tests to gather more data for your working diagnosis."
+            )
+            for category, tests in diagnostic_tests.items():
+                st.markdown(
+                    f"<h4 class='room-tag' style='background:{diagnostic_color_map[category]}'>{category}</h4>",
+                    unsafe_allow_html=True
+                )
+                test_items = list(tests.items())
+                for i in range(0, len(test_items), 2):
+                    colA, colB = st.columns(2)
+                    for col, (test_name, desc) in zip((colA, colB), test_items[i:i+2]):
+                        with col.expander(test_name):
+                            st.write(desc)
+                            if st.button(
+                                f"Order {test_name}",
+                                key=f"diagnostic_{category}_{test_name}"
+                            ):
+                                result_text = get_diagnostic_result(test_name, patient)
+                                st.session_state.test_results.append(
+                                    {"test": test_name, "result": result_text}
+                                )
+                                st.session_state.treatment_history.append(
+                                    f"Ordered {test_name}. Result: {result_text}"
+                                )
+                                st.success(f"Results received for {test_name}.")
+                                st.toast(f"🧪 {test_name} results ready!", icon="🧪")
+
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
+        st.subheader("🔬 Diagnostic Results")
+        if st.session_state.test_results:
+            for result in st.session_state.test_results:
+                st.write(f"**{result['test']}:** {result['result']}")
+        else:
+            st.write("No diagnostic tests ordered yet.")
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
@@ -502,45 +648,45 @@ if st.session_state.get("show_summary", False):
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
 
-    st.html(overlay_html)  # ✅ Renders as styled HTML
+    components.html(overlay_html, height=620)  # ✅ Renders as styled HTML
 
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
