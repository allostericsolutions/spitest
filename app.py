import streamlit as st
import json
import time
import os

# Importamos nuestras utilerías y componentes
from utils.auth import verify_password
from utils.question_manager import select_random_questions, shuffle_options
from utils.pdf_generator import generate_pdf
from components.question_display import display_question
from components.navigation import display_navigation

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="SPI Practice Exam - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    body {
        background-image: url("https://storage.googleapis.com/allostericsolutionsr/Allosteric_Solutions.png");
        background-repeat: no-repeat;
        background-size: contain; /* Or cover, or specific dimensions */
        background-position: center; /* Or other position */
    }

    /* Optional: Adjust padding/margins of other elements if needed */
    .stApp {
      padding-top: 0px !important;
    }
    h1{
        margin-top: 5px !important;
        margin-bottom: 10px !important;
        text-align: center; /* Center the title */
    }
    .stTextInput > div > div > input {
            color: black !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


def load_config():
    """
    Loads the data/config.json file with:
    - Access password
    - Exam time limit (in seconds)
    - Warning time (10 minutes in seconds)
    - Minimum and maximum scores
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
        st.session_state.answers = {} # Inicialmente vacío
    if 'marked' not in st.session_state:
        st.session_state.marked = set()
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'end_exam' not in st.session_state:
        st.session_state.end_exam = False

def authentication_screen():
    """
    Authentication screen: prompts the user for the password.
    """
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
    Screen for the user to enter their full name and ID. After submitting:
    - Checks that they are not empty.
    - Selects 120 random questions.
    - Shuffles the options.
    - Saves the exam start time.
    - Reloads to advance to exam_screen().
    """
    st.header("User Data")
    with st.form("user_form"):
        nombre = st.text_input("Full Name:")
        identificacion = st.text_input("ID or Student Number:")

        submitted = st.form_submit_button("Start Exam")
        if submitted:
            if nombre.strip() and identificacion.strip():
                # Guardar datos del usuario
                st.session_state.user_data = {
                    "nombre": nombre.strip(),
                    "id": identificacion.strip()
                }
                st.success("Data registered. Preparing the exam...")

                # Selección y mezcla de preguntas
                selected = select_random_questions(total=120)
                st.session_state.selected_questions = selected
                for q in st.session_state.selected_questions:
                    q['opciones'] = shuffle_options(q)

                # Inicializar answers *después* de seleccionar las preguntas
                st.session_state.answers = {str(i): None for i in range(len(st.session_state.selected_questions))}


                # Registro del tiempo de inicio
                st.session_state.start_time = time.time()

                # Recargar la aplicación *después* de inicializar answers
                st.rerun()
            else:
                st.error("Please, complete all fields.")

def display_marked_questions_sidebar():
    """Displays the sidebar with the list of marked questions."""

    if st.session_state.marked:  # Only shows if there are marked questions
      # Título de la barra lateral (HTML/CSS personalizado)
      st.markdown("""
        <style>
        .title {
          writing-mode: vertical-rl;
          transform: rotate(180deg);
          position: absolute;
          top: 50%;
          left: 0px; /* Ajusta según sea necesario */
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
            # Botón para navegar a la pregunta
            if st.button(f"Question {question_number}", key=f"goto_{index}"):
                st.session_state.current_question_index = index
                st.rerun()
        with col2:
            #Botón para desmarcar pregunta
            if st.button("X",key=f"unmark_{index}"):
                st.session_state.marked.remove(index)
                st.rerun()

def exam_screen():
    """
    Main exam screen:
    - Displays the user's name and ID.
    - Calculates and displays the remaining time in minutes only.
    - Presents the current question and its options.
    - Includes navigation (Previous, Next, Mark) and exam finalization.
    """
    # Logo de la empresa is in the background now

    st.title("SPI Practice Exam - ARDMS")

    # Datos del usuario
    nombre = st.session_state.user_data.get('nombre', '')
    identificacion = st.session_state.user_data.get('id', '')
    st.write(f"Name: **{nombre}**")
    st.write(f"ID: **{identificacion}**")

    # Calcular el tiempo restante (en segundos) y formatearlo solo en minutos
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time

    # Convierte a minutos (número entero)
    minutes_remaining = int(remaining_time // 60)

    # Mostrar el temporizador en la esquina superior derecha con solo minutos
    st.markdown(
        f"""
        <div style='text-align: right; font-size: 16px;'>
            <strong>Minutes Remaining:</strong> {minutes_remaining}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar advertencia si faltan 10 minutos (warning_time_seconds = 600)
    if remaining_time <= config["warning_time_seconds"] and remaining_time > 0:
        st.warning("The exam will end in 10 minutes!")

    # Si el tiempo ya se agotó, finalizamos el examen
    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("Time is up. The exam will be finalized now.")
        finalize_exam()
        return

    # Barra lateral de preguntas marcadas
    display_marked_questions_sidebar()

    # Si el examen sigue en curso, mostramos la pregunta actual
    if not st.session_state.end_exam:
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]

        # Mostrar la pregunta y sus opciones
        display_question(question, current_index + 1)

        # Navegación
        display_navigation()


        # Botón para finalizar el examen
        if st.button("Finish Exam"):
            # Verificar si hay preguntas sin responder
            unanswered = [
                i + 1 for i, q in enumerate(st.session_state.selected_questions)
                if str(i) not in st.session_state.answers
            ]
            if unanswered:
                st.warning(f"There are {len(unanswered)} unanswered questions. Are you sure you want to finish the exam?")
                if st.button("Confirm Completion"):
                    finalize_exam()
            else:
                finalize_exam()

def finalize_exam():
    """
    Marks the exam as finished and displays the results.
    Generates a PDF (without including questions or answers).
    """
    st.session_state.end_exam = True

    # Calcular puntaje con la nueva lógica: 75% → 555, 100% → 700
    score = calculate_score()

    # Determinar si aprueba o no
    if score >= config["passing_score"]:
        status = "Passed"
    else:
        status = "Not Passed"

    st.header("Exam Results")
    st.write(f"Score Obtained: **{score}**")
    st.write(f"Status: **{status}**")

    # Generar PDF y permitir descarga
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
    """
    Count correct answers. Then, we segment:
    - 0% to 75% correct: line from 0 points to 555
    - 75% to 100% correct: line from 555 to 700
    """
    questions = st.session_state.selected_questions
    total_questions = len(questions)
    if total_questions == 0:
        return 0  # previene divisiones entre 0 si algo falla

    # Contar cuántas respuestas correctas
    correct_count = 0
    for idx, question in enumerate(questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        if user_answer and user_answer in question["respuesta_correcta"]:
            correct_count += 1

    # Fracción de aciertos (0.0 → 1.0)
    x = correct_count / total_questions

    # Por tramos:
    # 0% → 0, 75% → 555, 100% → 700
    if x <= 0:
        final_score = 0
    elif x <= 0.75:
        # Sube de 0 a 555 linealmente
        slope1 = 555 / 0.75  # 555 ÷ 0.75 = 740
        final_score = slope1 * x
    else:
        # De 75% a 100%, sube de 555 a 700
        slope2 = (700 - 555) / (1 - 0.75)  # 145 ÷ 0.25 = 580
        final_score = slope2 * (x - 0.75) + 555

    # Convertir a entero
    return int(final_score)

def main_screen():
    """
    Screen that calls exam_screen() if the exam has not finished.
    """
    exam_screen()

def main():
    """
    MAIN EXECUTION:
    1. Initializes the state.
    2. Authentication screen if there is no session.
    3. If the user has not entered data, shows the form.
    4. While the exam has not finished, presents exam_screen().
    5. If it is finished, shows the results.
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
