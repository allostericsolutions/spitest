import streamlit as st
import os  # Asegúrate de tener os importado

def save_answer(question_num, selected_option, options):
    """Guarda la respuesta seleccionada en st.session_state.

    Args:
        question_num (int): Número de pregunta (índice + 1).
        selected_option (str):  La opción seleccionada por el usuario.
        options (list): Lista de opciones.  Necesaria para obtener el índice.
    """
    # Encuentra el ÍNDICE de la opción seleccionada.  Esto es crucial.
    try:
        selected_index = options.index(selected_option)
    except ValueError:
        selected_index = 0  # Si por algún motivo no se encuentra, usa 0.

    st.session_state.answers[str(question_num - 1)] = selected_option



def display_question(question, question_num):
    """Muestra la pregunta, imagen y opciones, y guarda la respuesta."""
    st.subheader(f"Question {question_num}:")
    st.write(question['enunciado'])

    if question['image']:
        image_path = os.path.join("assets", "images", question['image'])
        try:
            st.image(image_path, use_column_width=True)
        except FileNotFoundError:
            st.error(f"Image not found: {image_path}")

    # ---  Obtener el índice de la respuesta previamente guardada ---
    previous_answer = st.session_state.answers.get(str(question_num - 1))
    if previous_answer:
        try:
            #  Encuentra el índice de la respuesta anterior en la lista de opciones *actual*.
            #  Importante:  Las opciones pueden estar en diferente orden (shuffle).
            selected_index = question['opciones'].index(previous_answer)
        except ValueError:
            # Si la opción previamente seleccionada ya no existe (raro, pero posible),
            #  ponemos el índice en 0 (primera opción)
            selected_index = 0
    else:
        selected_index = 0  # Si es la primera vez que se ve, selecciona la primera.


    # ---  Usar st.radio con index y on_change ---
    selected = st.radio(
        "Select an answer:",
        options=question['opciones'],
        index=selected_index,  #  <-  ¡Aquí está el truco!
        key=f"respuesta_{question_num}",
        on_change=save_answer,  #  <-  Guardado automático
        args=(question_num, st.session_state.get(f"respuesta_{question_num}") , question['opciones'])  # Pasamos args a la función callback
    )
     # Ya no necesitamos esto, save_answer se encarga
     # st.session_state.answers[str(question_num - 1)] = selected
