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
from screens.user_data_input import user_data_input  # Importamos la pantalla de ingreso de datos

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- ESTILOS CSS MÁS ESPECÍFICOS Y AJUSTADOS ---
st.markdown(
    """
    <style>
    /* Reducir márgenes generales (con cuidado) */
    body {
        margin: 0;
        padding: 0;
    }

    /* Ajustes específicos para la imagen de fondo */
    body {
        background-image: url("https://storage.googleapis.com/allostericsolutionsr/Allosteric_Solutions.png");
        background-repeat: no-repeat;
        background-size: contain;
        background-position: center top;
        background-attachment: fixed; /* Imagen fija */
    }

    /* Reducir márgenes superiores e inferiores de los títulos */
    h1 {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        text-align: center;
    }

    /* Reducir márgenes de los inputs de texto */
    .stTextInput > div > div > input {
        color: black !important;
        margin-bottom: 5px !important;
    }

    /* Contenedor de autenticación (para agrupar) */
    .auth-container {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    /* Contenedor de datos de usuario (para agrupar) */
    .user-data-container {
        padding: 15px;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    /* Estilos para la pantalla de preguntas */
    .question-container {
        /* Puedes agregar estilos generales aquí si es necesario */
    }

    .options-container {
        /*
        max-height: 200px;  Ajusta este valor según tus necesidades
        overflow-y: auto;   Scroll vertical solo para las opciones
        */
    }

    /* Contenedor para la imagen (con altura máxima) */
    .image-container {
        max-height: 300px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def load_config():
    """
    Loads the data/config.json file.
    """
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

def initialize_session():
    """
    Initializes the application's state variables (Session State).
    """
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
    if 'incorrect_answers' not in st.session_state:
        st.session_state.incorrect_answers = []
    if 'explanations' not in st.session_state:
        st.session_state.explanations = {}

def authentication_screen():
    """
    Authentication screen: prompts the user for the password.
    """
    with st.container():
        st.title("Authentication")
        password = st.text_input("Enter the password to access the exam:", type="password")
        if st.button("Enter"):
            if verify_password(password):
                st.session_state.authenticated = True
                st.success("Authentication successful.")
                st.rerun()
            else:
                st.error("Incorrect password.")

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
                if st.button(f"Question ", key=f"goto_{index}"):
                    st.session_state.current_question_index = index
                    st.rerun()
            with col2:
                if st.button("X", key=f"unmark_{index}"):
                    st.session_state.marked.remove(index)
                    st.rerun()

def exam_screen():
    """
    Main exam screen.
    """
    nombre = st.session_state.user_data.get('nombre', '')
    email = st.session_state.user_data.get('email', '')

    # Mostramos Name y Email en la barra lateral
    with st.sidebar:
        st.write("User Information")
        st.text_input("Name", value=nombre, disabled=True)
        st.text_input("Email", value=email, disabled=True)

    # Resto de la pantalla principal: tiempo, preguntas, etc.
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
        display_question(question, current_index + 1)
        display_navigation()

        if st.button("Finish Exam"):
            unanswered = [
                i + 1 for i, q in enumerate(st.session_state.selected_questions)
                if str(i) not in st.session_state.answers
            ]
            if unanswered:
                st.warning(
                    f"There are {len(unanswered)} unanswered questions. Are you sure you want to finish the exam?"
                )
                if st.button("Confirm Completion"):
                    finalize_exam()
            else:
                finalize_exam()

def finalize_exam():
    """
    Marks the exam as finished, displays results, and generates the PDF.
    """
    st.session_state.end_exam = True
    score = calculate_score()

    if score >= config["passing_score"]:
        status = "Passed"
    else:
        status = "Not Passed"

    st.header("Exam Results")
    st.write(f"Score Obtained: {score}")
    st.write(f"Status: {status}")

    # ──────────────────────────────────────────────────────────
    # NUEVO BLOQUE: Mostrar desglose por clasificación
    # ──────────────────────────────────────────────────────────
    if "classification_stats" in st.session_state:
        st.sidebar.subheader("Detailed Breakdown by Topic")
        for clasif, stats in st.session_state.classification_stats.items():
            if stats["total"] > 0:
                percent = (stats["correct"] / stats["total"]) * 100
            else:
                percent = 0.0
            st.sidebar.write(f"{clasif}: {percent:.2f}%")

    # --- INTEGRACIÓN CON OPENAI ---
    explanations = get_openai_explanation(st.session_state.incorrect_answers)
    st.session_state.explanations = explanations  # Guarda las explicaciones

    # Mostrar las explicaciones en la barra lateral (para depurar)
    st.sidebar.write("Respuestas incorrectas:", st.session_state.incorrect_answers)
    st.sidebar.write("Explicaciones de OpenAI:", st.session_state.explanations)

    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Results generated in PDF.")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Results (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

def main_screen():
    """
    Screen that calls exam_screen() if the exam has not finished.
    """
    exam_screen()

def main():
    """
    MAIN EXECUTION.
    """
    initialize_session()

    if not st.session_state.authenticated:
        authentication_screen()
    elif not st.session_state.user_data:
        user_data_input()  # Se llama la pantalla de ingreso de datos importada de screens/user_data_input.py
    elif not st.session_state.end_exam:
        main_screen()
    else:
        finalize_exam()

if __name__ == "__main__":
    main()
