def finalize_exam():
    """
    Marks the exam as finished and displays the results.
    Generates a PDF (without including questions or answers).
    """
    st.session_state.end_exam = True

    # Calcular puntaje con la nueva lógica: 75% → 555, 100% → 700
    score = calculate_score()

    # Determinar si aprueba o no
    if score >= config["passing_score"]:
        status = "Passed"
    else:
        status = "Not Passed"

    st.header("Exam Results")
    st.write(f"Score Obtained: **{score}**")
    st.write(f"Status: **{status}**")

    # Generar PDF y permitir descarga
    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Results generated in PDF.")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Results (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )
