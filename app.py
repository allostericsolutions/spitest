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

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="expanded",  # <-- Barra lateral siempre abierta
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
        background-size: contain; /* 'contain' asegura que la imagen se vea completa */
        background-position: center top; /* Centrada horizontalmente, arriba verticalmente */
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
        max-height: 200px; /* Ajusta este valor según tus necesidades */
        overflow-y: auto;  /* Scroll vertical solo para las opciones */
    }

    /* Contenedor para la imagen (con altura máxima) */
    .image-container {
        max-height: 300px; /* Ajusta este valor según el tamaño máximo de tus imágenes */
        overflow: hidden; /* Oculta cualquier parte de la imagen que exceda la altura máxima */
    }

    /* --- ESTILOS PARA LA BARRA LATERAL FIJA --- */
    .sidebar-header {
        position: sticky;
        top: 0;
        background-color: #f0f2f6; /* Un color de fondo para que se vea bien */
        z-index: 1000; /* Asegura que esté por encima del contenido con scroll */
        padding: 10px; /* Espacio alrededor del contenido */
    	border-bottom: 1px solid #ccc;
    }

    .sidebar-content {
        max-height: calc(100vh - 150px); /* Ajusta 150px según la altura de tu header */
        overflow-y: auto;
        padding: 10px;
    }
    /* --- FIN DE ESTILOS PARA LA BARRA LATERAL --- */
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
        st.session_state.answers = {}  # Inicialmente vacío
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
    with st.container():  # Usamos un contenedor
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
    """
    Screen for user data input (name and ID).
    """
    with st.form("user_form"):
        st.header("User Data")
        nombre = st.text_input("Full Name:")
        identificacion = st.text_input("ID or Student Number:")

        submitted = st.form_submit_button("Start Exam")
        if submitted:
            if nombre.strip() and identificacion.strip():
                st.session_state.user_data = {
                    "nombre": nombre.strip(),
                    "id": identificacion.strip()
                }
                st.success("Data registered. Preparing the exam...")

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
                if st.button(f"Question ", key=f"goto_"):
                    st.session_state.current_question_index = index
                    st.rerun()
            with col2:
                if st.button("X", key=f"unmark_"):
                    st.session_state.marked.remove(index)
                    st.rerun()

def exam_screen():
    """
    Main exam screen.
    """
    # --- Información del Usuario y Tiempo en la Barra Lateral (Opción 2) ---
    nombre = st.session_state.user_data.get('nombre', '')
    identificacion = st.session_state.user_data.get('id', '')
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time
    minutes_remaining = int(remaining_time // 60)

     # --- Barra Lateral Fija ---
    with st.sidebar:
        # --- CONTENEDOR PARA LA CABECERA FIJA ---
        st.markdown("<div class='sidebar-header'>", unsafe_allow_html=True)
        with st.container():
            st.subheader("User Information")
            st.text_input("Name", value=nombre, disabled=True)
            st.text_input("ID", value=identificacion, disabled=True)
            st.markdown("---")
            st.markdown(
                f"""
                <div style='text-align: left; font-size: 16px;'>
                <strong>Minutes Remaining:</strong> 
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True) # Cierre del contenedor de la cabecera

        # --- CONTENEDOR PARA EL CONTENIDO CON SCROLL ---
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        with st.container():
            display_marked_questions_sidebar()
        st.markdown("</div>", unsafe_allow_html=True) # Cierre del contenedor de contenido

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
    st.write(f"Score Obtained: ")
    st.write(f"Status: ")

    # --- INTEGRACIÓN CON OPENAI ---
    explanations = get_openai_explanation(st.session_state.incorrect_answers)
    st.session_state.explanations = explanations  # Guarda las explicaciones

    # Mostrar las explicaciones en la barra lateral (para depurar)
    st.sidebar.write("Respuestas incorrectas:", st.session_state.incorrect_answers)
    st.sidebar.write("Explicaciones de OpenAI:", st.session_state.explanations)

    # --- (Fin de la integración) ---

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
        user_data_input()
    elif not st.session_state.end_exam:
        main_screen()
    else:
        finalize_exam()


if __name__ == "__main__":
    main()
