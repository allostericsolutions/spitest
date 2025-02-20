import streamlit as st

def display_question(question, question_num):
    """
    Muestra el enunciado de la pregunta, la imagen (si existe),
    y los botones de opción para seleccionar la respuesta.
    Guarda la respuesta seleccionada en st.session_state.answers.
    """
    # Encabezado que indica el número de la pregunta
    st.subheader(f"Pregunta {question_num}:")

    # Muestra el enunciado de la pregunta
    st.write(question['enunciado'])

    # Si la pregunta tiene una imagen, la muestra
    if question['image']:
        st.image(f"assets/images/{question['image']}", use_column_width=True)
    
    # Crear un "radio" para que el usuario seleccione una opción
    selected = st.radio(
        "Selecciona una respuesta:",
        options=question['opciones'],
        key=f"respuesta_{question_num}"  # clave única para cada pregunta
    )
    
    # Almacenar la respuesta seleccionada en st.session_state
    st.session_state.answers[str(question_num - 1)] = selected

