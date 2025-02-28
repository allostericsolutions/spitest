# components/question_display.py
import streamlit as st
import os
import string

def display_question(question, question_num):
    """
    Muestra el enunciado de la pregunta, la imagen (si existe),
    y las opciones con labels a), b), c), etc. Sin seleccionar 
    ninguna por defecto si el usuario no ha contestado antes.
    """

    # Dividimos la parte superior en dos columnas
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(f"Question {question_num}:")
    with col2:
        st.subheader("SPI Practice Exam - ARDMS")

    # Contenedor del enunciado
    with st.container():
        st.write(question['enunciado'])

    # Contenedor de la imagen
    with st.container():
        if question.get('image'):
            image_path = os.path.join("assets", "images", question['image'])
            try:
                st.image(image_path, use_column_width=True)
            except FileNotFoundError:
                st.error(f"Image not found: {image_path}")

    # Generar etiquetas tipo a), b), c), d) para las opciones
    labels = list(string.ascii_lowercase)  # ['a', 'b', 'c', ...]
    labeled_options = [f"{labels[i]}) {op}" for i, op in enumerate(question['opciones'])]

    # Contenedor para las opciones
    with st.container():
        # Checamos si ya existía alguna respuesta guardada
        existing_answer = st.session_state.answers.get(str(question_num - 1), None)
        if existing_answer is not None and existing_answer in question['opciones']:
            # Si el usuario respondió antes, determinamos el índice de esa respuesta
            selected_index = question['opciones'].index(existing_answer)
        else:
            # Si no hay respuesta previa, no se forzará ningún índice
            selected_index = None

        # Clave estable para el radio button
        stable_key = f"respuesta_{question_num}"

        # Si hay una respuesta previa, pasamos ese índice a st.radio
        # Si no, no definimos "index" para que no seleccione nada por defecto
        if selected_index is not None:
            selected_labeled = st.radio(
                "Select an answer:",
                options=labeled_options,
                index=selected_index,
                key=stable_key
            )
        else:
            selected_labeled = st.radio(
                "Select an answer:",
                options=labeled_options,
                key=stable_key
            )

        # Quitar la etiqueta (a), b), etc.) del valor seleccionado y almacenarlo
        selected = selected_labeled.split(')', 1)[1].strip()
        st.session_state.answers[str(question_num - 1)] = selected
