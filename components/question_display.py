import streamlit as st
import os
import time  # Asegúrate de tener esta importación


def display_question(question, question_num):
    """
    Displays the question statement, image (if it exists), and options.
    """
    st.subheader(f"Question {question_num}:")
    st.write(question['enunciado'])

    if question['image']:
        image_path = os.path.join("assets", "images", question['image'])
        try:
            st.image(image_path, use_column_width=True)
        except FileNotFoundError:
            st.error(f"Image not found: {image_path}")

    # --- Solución definitiva (usando index=None) ---
    dynamic_key = f"respuesta_{question_num}_{st.session_state.current_question_index}_{time.time()}"

    selected = st.radio(
        "Select an answer:",
        options=question['opciones'],
        key=dynamic_key,  # Usar la clave dinámica
        index=None  # <-- ¡CRUCIAL! Forzar a que no haya preselección
    )
    # --- Fin del cambio ---

    st.session_state.answers[str(question_num - 1)] = selected
