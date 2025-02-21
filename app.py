import os
import subprocess
import tempfile
import datetime
import streamlit as st
import json
import time
import random
from fpdf import FPDF

# --- Imports de tus módulos (asumiendo que existen) ---
from utils.auth import verify_password
from utils.question_manager import select_random_questions, shuffle_options
from utils.pdf_generator import generate_pdf
from components.question_display import display_question
from components.navigation import display_navigation



# --- Configuración de la página ---
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Funciones (definiciones) ---

def load_config():
    """Carga config.json."""
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

def initialize_session():
    """Inicializa variables de sesión."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'marked' not in st.session_state:
        st.session_state.marked = set()
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'end_exam' not in st.session_state:
        st.session_state.end_exam = False

def authentication_screen():
    """Pantalla de autenticación."""
    st.title("Authentication")
    password = st.text_input("Enter the password to access the exam:", type="password")
    if st.button("Enter"):
        if verify_password(password):
            st.session_state.authenticated = True
            st.success("Authentication successful.")
            st.rerun()
        else:
            st.error("Incorrect password.")

def user_data_input():
    """Entrada de datos del usuario."""
    st.header("User Data")
    with st.form("user_form"):
        nombre = st.text_input("Full Name:")
        identificacion = st.text_input("ID or Student Number:")

        submitted = st.form_submit_button("Start Exam")
        if submitted:
            if nombre.strip() and identificacion.strip():
                st.session_state.user_data = {
                    "nombre": nombre.strip(),
                    "id": identificacion.strip()
                }
                st.success("Data registered.  Preparing the exam...")

                selected = select_random_questions(total=120)
                st.session_state.selected_questions = selected
                for q in st.session_state.selected_questions:
                    q['opciones'] = shuffle_options(q)

                st.session_state.answers = {str(i): None for i in range(len(st.session_state.selected_questions))}
                st.session_state.start_time = time.time()
                st.rerun()
            else:
                st.error("Please, complete all fields.")



def display_marked_questions_sidebar():
    """Muestra la barra lateral con preguntas marcadas y el logo."""

    # ---  Logo en la Barra Lateral ---
    st.sidebar.image("https://storage.googleapis.com/allostericsolutionsr/Allosteric_Solutions.png", width=200)

    if st.session_state.marked:
        st.sidebar.markdown("""
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
        st.sidebar.markdown("<div class='title'>Marked Questions</div>", unsafe_allow_html=True)

        for index in st.session_state.marked:
            question_number = index + 1
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                # Botón para ir a la pregunta
                if st.button(f"Question {question_number}", key=f"goto_{index}"):
                    st.session_state.current_question_index = index
                    st.rerun()
            with col2:
                # Botón para desmarcar (azul)
                if st.button("X", key=f"unmark_{index}", button_type="primary"):
                    st.session_state.marked.remove(index)
                    st.rerun()

def exam_screen():
    """Pantalla principal del examen."""

    st.title("SPI Practice Exam - ARDMS")

    nombre = st.session_state.user_data.get('nombre', '')
    identificacion = st.session_state.user_data.get('id', '')
    st.write(f"Name: **{nombre}**")
    st.write(f"ID: **{identificacion}**")

    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time
    minutes_remaining = int(remaining_time // 60)

    st.markdown(
        f"""
        <div style='text-align: right; font-size: 16px;'>
            <strong>Minutes Remaining:</strong> {minutes_remaining}
        </div>
        """,
        unsafe_allow_html=True
    )

    if remaining_time <= config["warning_time_seconds"] and remaining_time > 0:
        st.warning("The exam will end in 10 minutes!")

    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("Time is up. The exam will be finalized now.")
        finalize_exam()
        return

    display_marked_questions_sidebar()

    if not st.session_state.end_exam:
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]

        # ---  Mostrar la Pregunta (MODIFICADO) ---
        display_question(question, current_index + 1)

        display_navigation()

        if st.button("Finish Exam"):
            unanswered = [
                i + 1 for i, q in enumerate(st.session_state.selected_questions)
                if str(i) not in st.session_state.answers
            ]
            if unanswered:
                st.warning(
                    f"There are {len(unanswered)} unanswered questions.  Are you sure you want to finish the exam?")
                if st.button("Confirm Completion"):
                    finalize_exam()
            else:
                finalize_exam()

    # --- (Temporal) Mostrar st.session_state.answers  ---
    st.write("Contenido de st.session_state.answers:")
    st.write(st.session_state.answers)
    # --- (Fin temporal) ---


def finalize_exam():
    """Finaliza el examen y muestra resultados."""
    st.session_state.end_exam = True
    score = calculate_score()

    if score >= config["passing_score"]:
        status = "Passed"
    else:
        status = "Not Passed"

    st.header("Exam Results")
    st.write(f"Score Obtained: **{score}**")
    st.write(f"Status: **{status}**")

    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Results generated in PDF.")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Results (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

def calculate_score():
    """Calcula el puntaje."""
    questions = st.session_state.selected_questions
    total_questions = len(questions)
    if total_questions == 0:
        return 0

    correct_count = 0
    for idx, question in enumerate(questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        if user_answer and user_answer in question["respuesta_correcta"]:
            correct_count += 1

    x = correct_count / total_questions

    if x <= 0:
        final_score = 0
    elif x <= 0.75:
        slope1 = 555 / 0.75
        final_score = slope1 * x
    else:
        slope2 = (700 - 555) / (1 - 0.75)
        final_score = slope2 * (x - 0.75) + 555

    return int(final_score)

def main_screen():
    """Pantalla principal."""
    exam_screen()

def main():
    """Función principal."""
    initialize_session()

    if not st.session_state.authenticated:
        authentication_screen()
    elif not st.session_state.user_data:
        user_data_input()
    elif not st.session_state.end_exam:
        main_screen()
    else:
        finalize_exam()

if __name__ == "__main__":
    main()
