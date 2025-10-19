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
