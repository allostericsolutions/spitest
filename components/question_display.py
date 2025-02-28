# components/question_display.py
import streamlit as st
import os
import string

def display_question(question, question_num):
    """
    Muestra la pregunta, su imagen (si existe) y sus opciones,
    agregando etiquetas a), b), c), d). No se marca la primera
    opción por defecto si el usuario no ha respondido antes.
    """

    # ----- Encabezados en dos columnas (idéntico a lo original) -----
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader(f"Question {question_num}:")
    with col2:
        st.subheader("SPI Practice Exam - ARDMS")

    # ----- Enunciado de la pregunta -----
    with st.container():
        st.write(question["enunciado"])

    # ----- Imagen (si existiera) -----
    with st.container():
        if question.get("image"):
            image_path = os.path.join("assets", "images", question["image"])
            try:
                st.image(image_path, use_column_width=True)
            except FileNotFoundError:
                st.error(f"Image not found: {image_path}")

    # ----- Generar etiquetas a), b), c), d), etc. -----
    labels = list(string.ascii_lowercase)  # ['a', 'b', 'c', 'd', ...]
    labeled_options = [f"{labels[i]}) {op}" for i, op in enumerate(question["opciones"])]

    # ----- Revisar si ya existía una respuesta previa -----
    existing_answer = st.session_state.answers.get(str(question_num - 1), None)
    if existing_answer is not None and existing_answer in question["opciones"]:
        # Si el usuario ya respondió antes, hallamos el índice de esa respuesta
        selected_index = question["opciones"].index(existing_answer)
    else:
        # De lo contrario, no hay índice seleccionado => sin selección por defecto
        selected_index = None

    # Clave estable para el st.radio (igual que en el original)
    stable_key = f"respuesta_{question_num}"

    # ----- Mostrar el radio button sin forzar la primera opción -----
    if selected_index is not None:
        # Hay respuesta previa: usamos index=selected_index para resaltarla
        selected_labeled = st.radio(
            "Select an answer:",
            options=labeled_options,
            index=selected_index,
            key=stable_key
        )
    else:
        # No hay respuesta previa: no se define index => ninguna opción marcada
        selected_labeled = st.radio(
            "Select an answer:",
            options=labeled_options,
            key=stable_key
        )

    # ----- Quitar la etiqueta (a), b), etc.) de la respuesta seleccionada -----
    selected_option = selected_labeled.split(")", 1)[1].strip()

    # Guardamos en session_state la respuesta SIN la etiqueta
    st.session_state.answers[str(question_num - 1)] = selected_option
