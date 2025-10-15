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
