import streamlit as st

def unmark_question(index):
    """ Funcion callback para desmarcar pregunta """
    st.session_state.marked.remove(index)

def mark_current_question():
    """ Funcion callback para marcar la pregunta actual"""
    current_index = st.session_state.current_question_index
    st.session_state.marked.add(current_index)
    st.success("Pregunta marcada para revisar.")

def display_navigation():
    """
    Muestra tres botones para:
    - Marcar y revisar la pregunta más tarde
    - Mover a la pregunta anterior
    - Mover a la siguiente pregunta
    """
    col1, col2, col3 = st.columns(3)

    # Botón para marcar la pregunta
    with col1:
        if st.button("Marcar para revisar", on_click=mark_current_question):
            pass # Ya no es necesaria accion, el callback lo hace

    # Botón para ir a la pregunta anterior
    with col2:
        if st.button("Anterior"):
            if st.session_state.current_question_index > 0:
                st.session_state.current_question_index -= 1
                st.rerun() # Se añade rerun
            else:
                st.warning("Esta es la primera pregunta.")

    # Botón para ir a la pregunta siguiente
    with col3:
        if st.button("Siguiente"):
            if st.session_state.current_question_index < len(st.session_state.selected_questions) - 1:
                st.session_state.current_question_index += 1
                st.rerun() #Se añade rerun
            else:
                st.warning("Esta es la última pregunta.")
