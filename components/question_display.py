# components/question_display.py
import streamlit as st
import os
import string  # <-- para etiquetas a), b), c), d)...

def display_question(question, question_num):
    """
    Displays the question statement, image (if it exists), 
    and options with labels a), b), c), d).
    """

    # Dos columnas superiores
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(f"Question {question_num}:")
    with col2:
        st.subheader("SPI Practice Exam - ARDMS")

    # Contenedor del enunciado de la pregunta
    with st.container():
        st.write(question['enunciado'])

    # Contenedor de la imagen (si existe)
    with st.container():
        if question.get('image'):
            image_path = os.path.join("assets", "images", question['image'])
            try:
                st.image(image_path, use_column_width=True)
            except FileNotFoundError:
                st.error(f"Image not found: {image_path}")

    # Generar etiquetas a), b), c), d)...
    labels = list(string.ascii_lowercase)
    labeled_options = [f"{labels[i]}) {op}" for i, op in enumerate(question['opciones'])]

    # Contenedor para las opciones
    with st.container():
        # Recuperar respuesta previa si existe
        existing_answer = st.session_state.answers.get(str(question_num - 1), None)

        # Determinar índice de la opción previamente seleccionada
        if existing_answer is not None and existing_answer in question['opciones']:
            selected_index = question['opciones'].index(existing_answer)
        else:
            selected_index = 0  # por defecto, primera opción

        stable_key = f"respuesta_{question_num}"

        # Mostrar las opciones con etiquetas
        selected_labeled = st.radio(
            "Select an answer:",
            options=labeled_options,
            index=selected_index,
            key=stable_key
        )

        # Extraer solo el texto de la opción (sin la etiqueta "a) / b) / ...")
        selected_option = selected_labeled.split(')', 1)[1].strip()

        # Guardar la respuesta en session_state
        st.session_state.answers[str(question_num - 1)] = selected_option
