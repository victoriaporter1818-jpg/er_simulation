# --------------------------------------
# RIGHT COLUMN (Patient Data & Logs)
# --------------------------------------

with col2:
    # Show Patient Data in the Right Column
    if st.session_state.patient:
        patient = st.session_state.patient
        st.header("👨‍⚕️ Patient Data")

        # Display Patient Information
        st.subheader("Patient Information")
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Symptoms:** {patient['symptoms']}")
        st.write(f"**Diagnosis:** {patient['diagnosis']}")

        # Display Patient Vitals
        st.subheader("Vitals")
        if "vitals" in patient:
            st.write(f"**Blood Pressure:** {patient['vitals']['BP']}")
            st.write(f"**Heart Rate:** {patient['vitals']['HR']}")
            st.write(f"**Oxygen Saturation:** {patient['vitals']['O2']}")
        else:
            st.warning("Vitals data not available for this patient.")

        # Display Treatment History (for context)
        st.subheader("Treatment History")
        if st.session_state.treatment_history:
            for treatment in st.session_state.treatment_history:
                st.write(treatment)
        else:
            st.write("No treatments administered yet.")

        # Display Medical History Form (Patient-Specific)
        st.subheader("📜 Medical History Form")
        medical_history = patient['medical_history']
        for key, value in medical_history.items():
            st.write(f"**{key}:** {value}")
        
        # Display Score (for context)
        st.subheader("🏆 Score")
        st.metric("Total Score", st.session_state.score)
    else:
        st.info("No active patient.")
