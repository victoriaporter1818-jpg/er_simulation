import streamlit as st
import random

st.set_page_config(page_title="AI Emergency Room Simulation", layout="wide")

# ------------------------------
# BASIC SIMULATION SETUP
# ------------------------------
st.title("🏥 AI Emergency Room Simulation")
st.subheader("Choose your role and interact with dynamic patient cases.")

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
st.write("🚑 Patients will begin arriving soon...")

import streamlit.components.v1 as components

# ---------------------------------
# 3D INTERACTIVE HOSPITAL ENVIRONMENT
# ---------------------------------
st.write("---")
st.subheader("🧠 Interactive Hospital Room")

html_code = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <script src="https://aframe.io/releases/1.5.0/aframe.min.js"></script>
  </head>
  <body>
    <a-scene embedded vr-mode-ui="enabled: false" style="height: 600px; width: 100%;">
      
      <!-- Room -->
      <a-box position="0 0 -5" width="10" height="4" depth="0.1" color="#d9e4ec"></a-box>
      <a-box position="-5 0 0" rotation="0 90 0" width="10" height="4" depth="0.1" color="#d9e4ec"></a-box>
      <a-box position="5 0 0" rotation="0 90 0" width="10" height="4" depth="0.1" color="#d9e4ec"></a-box>
      <a-plane rotation="-90 0 0" width="10" height="10" color="#f2f2f2"></a-plane>

      <!-- Hospital Bed -->
      <a-box position="0 0.5 -3" width="2" height="0.3" depth="1" color="#8eb5c4"></a-box>
      <a-box position="0 0.8 -3" width="2" height="0.1" depth="1" color="#b0cfd9"></a-box>
      <a-entity text="value: Patient Bed; color: black; width: 3;" position="-1.2 1 -3"></a-entity>

      <!-- Vitals Machine -->
      <a-box id="vitals" position="2 1 -3" width="0.6" height="0.5" depth="0.3" color="#222"></a-box>
      <a-entity text="value: Vitals Monitor; color: white; width: 3;" position="1.3 1.5 -3"></a-entity>
      <a-box id="vitals-screen" position="2 1.1 -2.85" width="0.5" height="0.3" depth="0.01" color="#0f0"></a-box>

      <!-- Computer Station -->
      <a-box id="computer" position="-2 1 -3" width="0.7" height="0.5" depth="0.3" color="#333"></a-box>
      <a-box id="computer-screen" position="-2 1.1 -2.85" width="0.6" height="0.35" depth="0.01" color="#44f"></a-box>
      <a-entity text="value: Computer Station; color: white; width: 3;" position="-3 1.5 -3"></a-entity>

      <!-- Supply Room -->
      <a-box id="supply-door" position="0 1 -9" width="2" height="2" depth="0.1" color="#99c"></a-box>
      <a-entity text="value: Supply Room; color: black; width: 5;" position="-1 2.2 -9"></a-entity>

      <!-- Medstation -->
      <a-box id="medstation" position="3 1 -1" width="1" height="1" depth="0.5" color="#c33"></a-box>
      <a-entity text="value: Medstation; color: white; width: 3;" position="2 2 -1"></a-entity>

      <!-- Lights and Camera -->
      <a-entity light="type: ambient; intensity: 0.7"></a-entity>
      <a-entity light="type: point; intensity: 1" position="0 3 0"></a-entity>
      <a-entity camera look-controls position="0 1.6 5"></a-entity>

      <!-- Interactions -->
      <a-entity id="cursor" cursor="rayOrigin: mouse"></a-entity>

      <script>
        const vitals = document.querySelector('#vitals');
        const computer = document.querySelector('#computer');
        const medstation = document.querySelector('#medstation');
        const supply = document.querySelector('#supply-door');

        vitals.addEventListener('click', () => {
          alert('🩺 Vitals Machine: HR 95 | BP 120/80 | O2 98%');
        });
        computer.addEventListener('click', () => {
          alert('💻 Computer: Lab results show mild infection.');
        });
        medstation.addEventListener('click', () => {
          alert('💊 Medstation: You picked up antibiotics.');
        });
        supply.addEventListener('click', () => {
          alert('📦 Supply Room: Collected IV, bandages, and ice packs.');
        });
      </script>
    </a-scene>
  </body>
</html>
"""

components.html(html_code, height=650)

import time

# ------------------------------
# PATIENT CASE GENERATOR
# ------------------------------
patients = [
    {
        "name": "John Doe",
        "age": 45,
        "symptoms": "severe chest pain and shortness of breath",
        "vitals": {"BP": "90/60", "HR": 120, "O2": "85%"},
        "diagnosis": "Heart attack",
        "treatment": "Administer aspirin and prepare for angioplasty"
    },
    {
        "name": "Sarah Li",
        "age": 29,
        "symptoms": "high fever, cough, and low oxygen",
        "vitals": {"BP": "110/70", "HR": 95, "O2": "88%"},
        "diagnosis": "Pneumonia",
        "treatment": "Start IV antibiotics and oxygen therapy"
    },
    {
        "name": "Carlos Vega",
        "age": 60,
        "symptoms": "sudden weakness on one side and slurred speech",
        "vitals": {"BP": "150/90", "HR": 82, "O2": "97%"},
        "diagnosis": "Stroke",
        "treatment": "Call stroke team and prepare for CT scan"
    },
    {
        "name": "Emma Brown",
        "age": 8,
        "symptoms": "abdominal pain and vomiting for 12 hours",
        "vitals": {"BP": "100/65", "HR": 110, "O2": "98%"},
        "diagnosis": "Appendicitis",
        "treatment": "Schedule emergency appendectomy"
    }
]

if role != "-- Choose --":
    if st.button("🚨 Receive Next Patient"):
        patient = random.choice(patients)
        st.session_state.patient = patient
        st.session_state.result = None

    if "patient" in st.session_state:
        p = st.session_state.patient
        st.header(f"🧍 Patient: {p['name']} (Age {p['age']})")
        st.write(f"**Symptoms:** {p['symptoms']}")
        if role == "Nurse":
            st.subheader("👩‍⚕️ Take Vitals and Record Info")
            st.json(p["vitals"])
            if st.button("Administer Initial Care"):
                st.success("Vitals recorded and patient stabilized for doctor review.")
        elif role == "Doctor":
            st.subheader("⚕️ Diagnosis & Treatment Plan")
            choice = st.radio(
                "What’s your diagnosis?",
                ["Heart attack", "Pneumonia", "Stroke", "Appendicitis"]
            )
            if st.button("Confirm Diagnosis"):
                if choice == p["diagnosis"]:
                    st.success("✅ Correct! Begin treatment.")
                    st.info(p["treatment"])
                else:
                    st.error(f"❌ Incorrect — the correct diagnosis was {p['diagnosis']}.")
        elif role == "Surgeon":
            st.subheader("🔪 Surgical Decision")
            st.write(f"Recommended action: {p['treatment']}")
            proceed = st.checkbox("Confirm patient prepped for surgery")
            if proceed and st.button("Perform Surgery"):
                with st.spinner("Performing surgery..."):
                    time.sleep(2)
                outcome = random.choice(["success", "complication"])
                if outcome == "success":
                    st.success("🎉 Surgery successful! Patient stable.")
                else:
                    st.warning("⚠️ Minor complication — patient requires post-op monitoring.")
