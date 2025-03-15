import streamlit as st
import json
import time
import os

# Importamos nuestras utilerías y componentes
#from utils.auth import verify_password  # <-- ELIMINAR ESTA LÍNEA
from utils.question_manager import select_random_questions, shuffle_options, calculate_score
from utils.pdf_generator import generate_pdf
from components.question_display import display_question
from components.navigation import display_navigation
from openai_utils.explanations import get_openai_explanation
from screens.user_data_input import user_data_input

# --- NUEVAS IMPORTACIONES ---
from password_manager.manager import verify_password, mark_password_as_used, admin_screen
from instrucctions.tab_view.instructions_tab import instructions_tab

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

def load_css():
    """Carga el archivo CSS personalizado."""
    with open("assets/styles/custom.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# YA NO SE USA, AHORA SE CARGA DESDE EL MANAGER
#def load_config():
#    """
#    Loads the data/config.json file.
#    """
#    with open('data/config.json', 'r', encoding='utf-8') as f:
#        return json.load(f)
#
#config = load_config()

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
    #Añadido para controlar el password
    if 'password_used' not in st.session_state:
        st.session_state.password_used = None
    if 'admin_mode' not in st.session_state:
        st.session_state.admin_mode = False
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False


def authentication_screen():
    """
    Authentication screen: prompts the user for the password.
    """
    with st.container():
        st.title("Authentication")
        password = st.text_input("Enter the password to access the exam:", type="password")
        if st.button("Enter"):
            #if verify_password(password):  # <-- ASÍ ESTABA
            if verify_password(password):      # <-- ASÍ QUEDA (llamada a la nueva función)
                st.session_state.authenticated = True
                st.session_state.password_used = password  # <-- GUARDAR LA CONTRASEÑA
                st.success("Authentication successful.")
                st.rerun()
            else:
                st.error("Incorrect password, inactive, used, or expired.")  # <-- MENSAJE MÁS DESCRIPTIVO

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
            #question_number = index + 1 # Ya no se usa
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
    from password_manager.manager import load_config #Se importa dentro
    config = load_config()  # Se carga la configuración
    nombre = st.session_state.user_data.get('nombre', '')
    email = st.session_state.user_data.get('email', '')

    # Mostramos Name y Email en la barra lateral
    with st.sidebar:
        st.write("User Information")
        st.text_input("Name", value=nombre, disabled=True)
        st.text_input("Email", value=email, disabled=True)
    # --- ASIGNACIÓN DEL TIEMPO RESTANTE (simplificada) ---
    elapsed_time = time.time() - st.session_state.start_time
    if st.session_state.exam_type == "short":
        remaining_time = 1200 - elapsed_time  # 20 minutos
    #Se agrega para usar los tiempos de config
    elif st.session_state.exam_type == "full":
        remaining_time = config["time_limit_seconds_full"] - elapsed_time
    #En caso de error
    else:
        remaining_time = 0

    minutes_remaining = int(remaining_time // 60)

    # Resto de la pantalla principal: tiempo, preguntas, etc.

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

        # --- BLOQUE DE FINALIZACIÓN (CON FORMULARIO) ---
        if 'confirm_finish' not in st.session_state:
            st.session_state.confirm_finish = False

        with st.form("finish_form"):
            st.warning("When you are ready to finish the exam, press 'Confirm Completion' and then conclude by pressing 'Finish Exam'.")
            if st.form_submit_button("Confirm Completion"):
                st.session_state.confirm_finish = True

        if st.button("Finish Exam"):
                if st.session_state.confirm_finish:
                    st.session_state.end_exam = True
                    finalize_exam()
                else:
                    st.warning("Please confirm completion using the button above.")

        # --- FIN DEL BLOQUE CON FORMULARIO ---

# YA NO SE USA, AHORA SE HACE EN EL MANAGER
#def save_config(config):
#    """Guarda la configuración en el archivo JSON."""
#    with open('data/config.json', 'w', encoding='utf-8') as f:
#        json.dump(config, f, indent=4)

def finalize_exam():
    """
    Marks the exam as finished, displays results, and generates the PDF.
    """
    from password_manager.manager import load_config #Se importa dentro
    config = load_config()  # Se carga la configuración
    st.session_state.end_exam = True
    score = calculate_score()

    if score >= config["passing_score"]:
        status = "Passed"
    else:
        status = "Not Passed"

    st.header("Exam Results")
    st.write(f"Score Obtained: {score}")
    st.write(f"Status: {status}")

    # --- MARCAR LA CONTRASEÑA COMO USADA (CRÍTICO) ---
    password = st.session_state.get("password_used")
    if password:
        mark_password_as_used(password)  # <-- LLAMADA A LA NUEVA FUNCIÓN

    # -------------------------------------------------

    if "classification_stats" in st.session_state:
        st.sidebar.subheader("Detailed Breakdown by Topic")
        for clasif, stats in st.session_state.classification_stats.items():
            if stats["total"] > 0:
                percent = (stats["correct"] / stats["total"]) * 100
            else:
                percent = 0.0
            st.sidebar.write(f"{clasif}: {percent:.2f}%")

    explanations = get_openai_explanation(st.session_state.incorrect_answers)
    st.session_state.explanations = explanations

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

# YA NO SE USA
#def admin_screen():
#    """Pantalla de administración (simplificada)."""

# --- FUNCIÓN PRINCIPAL (main) ---

def main():
    """Función principal de la aplicación."""
    initialize_session()
    load_css()
    instructions_tab()

    with st.sidebar:
        st.write("Adjust Font Size")
        font_size_multiplier = st.slider(
            "Font Size",
            min_value=0.8,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key="font_size_slider"
        )

    st.markdown(f"""
        <style>
            :root {{
                --base-font-size: {16 * font_size_multiplier}px;
            }}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.write("Adjust Logo Size")
        image_width_multiplier = st.slider(
            "Logo Width",
            min_value=0.2,
            max_value=2.0,
            value=0.5,
            step=0.1,
            key="image_size_slider"
        )
        image_url = "https://storage.googleapis.com/allostericsolutionsr/Allosteric_Solutions.png"
        st.image(image_url, width=int(200 * image_width_multiplier))

        # --- Botón de administración ---
        # Si  está autenticado como admin, no mostrar
        if not st.session_state.get('is_admin', False):
            if st.button("Admin"):
                st.session_state.admin_mode = True
                st.rerun()

    #Mostrar la pantalla de admin, si ha sido selecionado.
    if st.session_state.get('admin_mode', False):
        admin_screen() #Se llama desde el manager

    elif not st.session_state.authenticated:
        authentication_screen()
    elif not st.session_state.user_data:
        user_data_input()
    elif not st.session_state.end_exam:
        main_screen()
    else:
        finalize_exam()

# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    main()
