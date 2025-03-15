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
from screens.user_data_input import user_data_input
# NUEVOS IMPORTS
from utils.admin_auth import admin_login_screen
from utils.password_manager import add_password, remove_password, get_passwords
# ─────────────────────────────────────────────────────────────
# NUEVO IMPORT para las instrucciones
# ─────────────────────────────────────────────────────────────
from instrucctions.tab_view.instructions_tab import instructions_tab
# ─────────────────────────────────────────────────────────────

# --- Configuración de la página de Streamlit ---
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

def load_css():
    """Carga el archivo CSS personalizado."""
    with open("assets/styles/custom.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_config():
    """
    Loads the data/config.json file.
    """
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()


def initialize_session():
    """
    Inicializa las variables de estado de la aplicación.
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
    if 'admin_authenticated' not in st.session_state: # <-- AÑADIDO
        st.session_state.admin_authenticated = False


def authentication_screen():
    """
    Pantalla de autenticación: solicita la contraseña al usuario.
    """
    with st.container():
        st.title("Authentication")
        password = st.text_input("Enter the password to access the exam:", type="password")
        if st.button("Enter"):
            if verify_password(password):
                st.session_state.authenticated = True
                st.success("Authentication successful.")#Texto en ingles
                st.rerun()
            else:
                st.error("Incorrect password.")#Texto en ingles

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
        st.write("User Information")#Texto en ingles
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
        st.warning("The exam will end in 10 minutes!")#Texto en ingles

    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("Time is up. The exam will be finalized now.")#Texto en ingles
        finalize_exam()
        return

    display_marked_questions_sidebar()


    if not st.session_state.end_exam:
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]
        display_question(question, current_index + 1)
        display_navigation()


        # --- BLOQUE DE FINALIZACIÓN (CON FORMULARIO) ---
        if 'confirm_finish' not in st.session_state:
            st.session_state.confirm_finish = False

        with st.form("finish_form"):
            st.warning("When you are ready to finish the exam, press 'Confirm Completion' and then conclude by pressing 'Finish Exam'.")#Texto en ingles
            if st.form_submit_button("Confirm Completion"):#Texto en ingles
                st.session_state.confirm_finish = True

        if st.button("Finish Exam"):#Texto en ingles
                if st.session_state.confirm_finish:
                    st.session_state.end_exam = True
                    finalize_exam()
                else:
                    st.warning("Please confirm completion using the button above.")#Texto en ingles

        # --- FIN DEL BLOQUE CON FORMULARIO ---


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

    st.header("Exam Results")#Texto en ingles
    st.write(f"Score Obtained: {score}")#Texto en ingles
    st.write(f"Status: {status}")#Texto en ingles

    # ──────────────────────────────────────────────────────────
    # NUEVO BLOQUE: Mostrar desglose por clasificación
    # ──────────────────────────────────────────────────────────
    if "classification_stats" in st.session_state:
        st.sidebar.subheader("Detailed Breakdown by Topic")#Texto en ingles
        for clasif, stats in st.session_state.classification_stats.items():
            if stats["total"] > 0:
                percent = (stats["correct"] / stats["total"]) * 100
            else:
                percent = 0.0
            st.sidebar.write(f"{clasif}: {percent:.2f}%")

    # --- INTEGRACIÓN CON OPENAI ---
    explanations = get_openai_explanation(st.session_state.incorrect_answers)
    st.session_state.explanations = explanations    # Guarda las explicaciones

    # Mostrar las explicaciones en la barra lateral (para depurar)
    # st.sidebar.write("Respuestas incorrectas:", st.session_state.incorrect_answers)
    # st.sidebar.write("Explicaciones de OpenAI:", st.session_state.explanations)

    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Results generated in PDF.")#Texto en ingles

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Results (PDF)",#Texto en ingles
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

def main_screen():
    """
    Screen that calls exam_screen() if the exam has not finished.
    """
    exam_screen()

def admin_screen():
    """
    Pantalla de administración para gestionar contraseñas (en la barra lateral).
    """
    st.sidebar.title("Password Management")

    # Añadir contraseña
    st.sidebar.header("Add Password")
    exam_type = st.sidebar.selectbox("Exam Type", ["short", "full"])
    new_password = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Add Password"):
        add_password(exam_type, new_password)

    # Eliminar contraseña
    st.sidebar.header("Remove Password")
    exam_type_remove = st.sidebar.selectbox("Exam Type to Remove From", ["short", "full"], key="exam_type_remove")
    passwords = get_passwords(exam_type_remove)
    if passwords:
        password_to_remove = st.sidebar.selectbox("Password to Remove", passwords)
        if st.sidebar.button("Remove Password"):
            remove_password(exam_type_remove, password_to_remove)
    else:
        st.sidebar.write(f"No passwords found for {exam_type_remove} exam.")


def main():
    """
    MAIN EXECUTION.
    """
    initialize_session()
    load_css()
        # ─────────────────────────────────────────────────────────
        # LLAMADO para mostrar las instrucciones (Expander)
        # ─────────────────────────────────────────────────────────
    instructions_tab()

        # --- Control de tamaño de fuente (AÑADIDO) ---
    with st.sidebar:
        st.write("Adjust Font Size")#Texto en ingles
        font_size_multiplier = st.slider(
            "Font Size",#Texto en ingles
            min_value=0.8,
            max_value=2.0,
            value=1.0,    # Valor inicial (1.0 = tamaño predeterminado)
            step=0.1,
            key="font_size_slider"
        )

    # Inyectar CSS para aplicar el tamaño de fuente (AÑADIDO)
    st.markdown(f"""
        <style>
            :root {{
                --base-font-size: {16 * font_size_multiplier}px; /* Tamaño base dinámico */
            }}
        </style>
    """, unsafe_allow_html=True)

    admin_login_screen() # Esto siempre se va a mostrar

    if st.session_state.admin_authenticated: # Y esto si se autentica el admin.
        admin_screen()
    elif not st.session_state.authenticated:
        authentication_screen()
    elif not st.session_state.user_data:
        user_data_input()
    elif not st.session_state.end_exam:
        main_screen()
    else:
        finalize_exam()

if __name__ == "__main__":
    main()
