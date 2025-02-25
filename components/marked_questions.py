# components/marked_questions.py
import streamlit as st

def display_marked_questions_sidebar():
    """Displays the sidebar with marked questions."""

    if st.session_state.marked:
        st.markdown("""
        <style>
        .title {
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            position: absolute;
            top: 50%;
            left: 0px;
            transform-origin: center;
            white-space: nowrap;
            display: block;
            font-size: 1.2em;
        }
        </style>
        """, unsafe_allow_html=True)

        for index in st.session_state.marked:
            question_number = index + 1
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                if st.button(f"Question {question_number}", key=f"goto_{index}"):
                    st.session_state.current_question_index = index
                    st.rerun()
            with col2:
                if st.button("X", key=f"unmark_{index}"):
                    st.session_state.marked.remove(index)
                    st.rerun()
