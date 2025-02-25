# app.py
import streamlit as st
import json
import time
import os

# Importamos nuestras utilerías y componentes
from utils.auth import verify_password
from utils.question_manager import select_random_questions, shuffle_options, calculate_score
from utils.pdf_generator import generate_pdf
from components.question_display import display_question
from components.navigation import display_navigation
from openai_utils.explanations import get_openai_explanation
from components.marked_questions import display_marked_questions_sidebar  # <-- Importar

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CSS ---
st.markdown(
    """
    <style>
    /* (El resto de tus estilos CSS aquí) */
    /* --- ESTILOS PARA LA BARRA LATERAL FIJA --- */
    .sidebar-header {
        position: sticky;
        top: 0;
        background-color: #f0f2f6;
        z-index: 1000;
        padding: 10px;
        border-bottom: 1px solid #ccc;
    }

    .sidebar-content {
        max-height: calc(100vh - 150px); /* Ajusta según la altura de tu header */
        overflow-y: auto;
        padding: 10px;
    }
    /* --- FIN DE ESTILOS PARA LA BARRA LATERAL --- */
    </style>
    """,
    unsafe_allow_html=True,
)

# ... (Funciones load_config, initialize_session, authentication_screen, user_data_input) ...

def exam_screen():
    """
    Main exam screen.
    """
    nombre = st.session_state.user_data.get('nombre', '')
    identificacion = st.session_state.user_data.get('id', '')
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time
    minutes_remaining = int(remaining_time // 60)

    # --- Barra Lateral Fija ---
    with st.sidebar:
        with st.container(border=False) as sidebar_header:
            st.subheader("User Information")
            st.text_input("Name", value=nombre, disabled=True)
            st.text_input("ID", value=identificacion, disabled=True)
            st.markdown("---")
            st.markdown(
                f"""
                <div style='text-align: left; font-size: 16px;'>
                  <strong>Minutes Remaining:</strong> {minutes_remaining}
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.container() as sidebar_content:
            display_marked_questions_sidebar()  # <-- Llamada a la función importada
    # --- Fin de la Barra Lateral ---

    if remaining_time <= config["warning_time_seconds"] and remaining_time > 0:
        st.warning("The exam will end in 10 minutes!")

    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("Time is up. The exam will be finalized now.")
        finalize_exam()
        return

    if not st.session_state.end_exam:
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]
        display_question(question, current_index + 1)
        display_navigation()

        if st.button("Finish Exam"):
            unanswered = [
                i + 1 for i, q in enumerate(st.session_state.selected_questions)
                if str(i) not in st.session_state.answers
            ]
            if unanswered:
                st.warning(
                    f"There are {len(unanswered)} unanswered questions. Are you sure you want to finish the exam?")
                if st.button("Confirm Completion"):
                    finalize_exam()
            else:
                finalize_exam()

# ... (Función finalize_exam, main_screen, main) ...

if __name__ == "__main__":
    main()
