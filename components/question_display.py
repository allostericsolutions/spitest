import streamlit as st
import os  # Asegúrate de tener esta importación

def display_question(question, question_num):
    """
    Displays the question statement, image (if it exists), and options.
    """
    st.subheader(f"Question {question_num}:")
    st.write(question['enunciado'])

    if question['image']:
        image_path = os.path.join("assets", "images", question['image'])
        try:  # Maneja el caso en que la imagen pueda no existir.
            st.image(image_path, use_column_width=True)
        except FileNotFoundError:
          st.error(f"Image not found: {image_path}") # Informa al usuario.

    selected = st.radio(
        "Select an answer:",
        options=question['opciones'],
        key=f"respuesta_{question_num}"
    )
    st.session_state.answers[str(question_num - 1)] = selected
