# utils/exam_manager.py
import streamlit as st
import os
from utils.pdf_generator import generate_pdf  # Asegúrate de que esta importación esté
from utils.question_manager import calculate_score  # Y esta también
from utils.logger import log_exam_activity  # IMPORTA EL NUEVO MÓDULO

def finalize_exam():
    """
    Marks the exam as finished and displays the results.
    Generates a PDF (without including questions or answers).
    """
    st.session_state.end_exam = True

    # Calcular puntaje con la nueva lógica: 75% → 555, 100% → 700
    score = calculate_score()

    # Determinar si aprueba o no
    if score >= st.session_state.get("passing_score", 555):  # Usar un valor predeterminado
        status = "Passed"
    else:
        status = "Not Passed"

    st.header("Exam Results")
    st.write(f"Score Obtained: **{score}**")
    st.write(f"Status: **{status}**")

    # Generar PDF y permitir descarga
    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Results generated in PDF.")

    # --- INICIO DE LA SECCIÓN AÑADIDA ---
    # Llama a la función de registro para guardar la actividad del examen.
    # Esta función está definida en el módulo utils/logger.py.
    log_exam_activity(st.session_state.user_data, score, status)
    # --- FIN DE LA SECCIÓN AÑADIDA ---

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Results (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )
