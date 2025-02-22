import streamlit as st

def unmark_question(index):
    """ Callback function to unmark a question """
    st.session_state.marked.remove(index)

def mark_current_question():
    """ Callback function to mark the current question"""
    current_index = st.session_state.current_question_index
    st.session_state.marked.add(current_index)
    # st.success("Question marked for review.") #Texto en ingles - Removed

def display_navigation():
    """
    Displays three buttons for:
    - Mark and review the question later
    - Move to the previous question
    - Move to the next question
    """
    col1, col2, col3 = st.columns(3)

    # Botón para marcar la pregunta
    with col1:
        if st.button("Mark for review", on_click=mark_current_question): #Texto en ingles
            pass # Ya no es necesaria accion, el callback lo hace

    # Botón para ir a la pregunta anterior
    with col2:
        if st.button("Previous"): #Texto en ingles
            if st.session_state.current_question_index > 0:
                st.session_state.current_question_index -= 1
                st.rerun() # Se añade rerun
            else:
                st.warning("This is the first question.") #Texto en ingles

    # Botón para ir a la pregunta siguiente
    with col3:
        if st.button("Next"): #Texto en ingles
            if st.session_state.current_question_index < len(st.session_state.selected_questions) - 1:
                st.session_state.current_question_index += 1
                st.rerun() #Se añade rerun
            else:
                st.warning("This is the last question.")#Texto en ingles
