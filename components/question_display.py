# components/question_display.py
import streamlit as st
import os

def display_question(question, question_num):
    """
    Displays the question statement, image (if it exists), and options.
    """
    # --- MODIFICACIÓN AQUÍ ---
    col1, col2 = st.columns([1, 3])  # Divide el espacio en dos columnas (ajusta la proporción según necesites)
    with col1:
        st.subheader(f"Question {question_num}:")
    with col2:
        st.subheader("SPI Practice Exam - ARDMS") #Se pone como subheader
    # --- FIN DE LA MODIFICACIÓN ---

    # Contenedor para el enunciado
    with st.container():
        st.write(question['enunciado'])

    # Contenedor para la imagen
    with st.container():
        if question['image']:
            image_path = os.path.join("assets", "images", question['image'])
            try:
                st.image(image_path, use_column_width=True)
            except FileNotFoundError:
                st.error(f"Image not found: {image_path}")

    # Contenedor para las opciones (con scroll interno si es necesario)
    with st.container():
        # Recuperar la respuesta ya seleccionada, si existe
        existing_answer = st.session_state.answers.get(str(question_num - 1), None)

        # Si existe una respuesta previa, hallamos su índice en la lista de opciones.
        # De lo contrario, None para que no haya preselección.
        if existing_answer is not None and existing_answer in question['opciones']:
            selected_index = question['opciones'].index(existing_answer)
        else:
            selected_index = None

        # Usar una clave "estable" (sin time.time()).
        stable_key = f"respuesta_{question_num}"

        selected = st.radio(
            "Select an answer:",
            options=question['opciones'],
            index=selected_index,  # None cuando no haya respuesta previa
            key=stable_key
        )

        # Almacenar la elección en session_state para su persistencia
        st.session_state.answers[str(question_num - 1)] = selected
