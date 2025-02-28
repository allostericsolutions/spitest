# components/question_display.py
import streamlit as st
import os
import string  # Importar string para etiquetas

def display_question(question, question_num):
    """
    Displays the question statement, image (if it exists), and options with labels a), b), c), d).
    """
    # Divide el espacio en dos columnas
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(f"Question {question_num}:")
    with col2:
        st.subheader("SPI Practice Exam - ARDMS")  # Título secundario

    # Contenedor para el enunciado
    with st.container():
        st.write(question['enunciado'])

    # Contenedor para la imagen
    with st.container():
        if question.get('image'):
            image_path = os.path.join("assets", "images", question['image'])
            try:
                st.image(image_path, use_column_width=True)
            except FileNotFoundError:
                st.error(f"Image not found: {image_path}")

    # Generar etiquetas a), b), c), d), etc.
    labels = list(string.ascii_lowercase)
    labeled_options = [f"{labels[i]}) {option}" for i, option in enumerate(question['opciones'])]

    # Contenedor para las opciones
    with st.container():
        # Recuperar la respuesta ya seleccionada, si existe
        existing_answer = st.session_state.answers.get(str(question_num - 1), None)

        # Determinar el índice seleccionado basado en la respuesta existente
        if existing_answer is not None and existing_answer in question['opciones']:
            selected_index = question['opciones'].index(existing_answer)
        else:
            selected_index = 0  # Predeterminado al primer elemento

        # Clave estable para el radio button
        stable_key = f"respuesta_{question_num}"

        # Mostrar las opciones con etiquetas
        selected_labeled = st.radio(
            "Select an answer:",
            options=labeled_options,
            index=selected_index,
            key=stable_key
        )

        # Extraer el texto de la opción sin la etiqueta y almacenar en session_state
        selected = selected_labeled.split(')', 1)[1].strip()
        st.session_state.answers[str(question_num - 1)] = selected
