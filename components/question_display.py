import streamlit as st

def display_question(question, question_num):
    """
    Displays the question statement, the image (if it exists),
    and the option buttons to select the answer.
    Saves the selected answer in st.session_state.answers.
    """
    # Encabezado que indica el número de la pregunta
    st.subheader(f"Question {question_num}:") #Texto en ingles

    # Muestra el enunciado de la pregunta
    st.write(question['enunciado'])

    # Si la pregunta tiene una imagen, la muestra
    if question['image']:
        image_path = os.path.join("assets", "images", question['image'])
        try:  # Maneja el caso en que la imagen pueda no existir.
            st.image(image_path, use_column_width=True)
        except FileNotFoundError:
          st.error(f"Image not found: {image_path}") # Informa al usuario.

    # Crear un "radio" para que el usuario seleccione una opción
    selected = st.radio(
        "Select an answer:", #Texto en ingles
        options=question['opciones'],
        key=f"respuesta_{question_num}"  # clave única para cada pregunta
    )

    # Almacenar la respuesta seleccionada en st.session_state
    st.session_state.answers[str(question_num - 1)] = selected
