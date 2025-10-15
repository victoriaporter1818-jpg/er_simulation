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
