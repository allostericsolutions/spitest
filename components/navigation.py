import streamlit as st

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
        if st.button("Marcar para revisar"):
            current_index = st.session_state.current_question_index
            st.session_state.marked.add(current_index)
            st.success("Pregunta marcada para revisar.")

    # Botón para ir a la pregunta anterior
    with col2:
        if st.button("Anterior"):
            if st.session_state.current_question_index > 0:
                st.session_state.current_question_index -= 1
            else:
                st.warning("Esta es la primera pregunta.")

    # Botón para ir a la pregunta siguiente
    with col3:
        if st.button("Siguiente"):
            if st.session_state.current_question_index < len(st.session_state.selected_questions) - 1:
                st.session_state.current_question_index += 1
            else:
                st.warning("Esta es la última pregunta.")
