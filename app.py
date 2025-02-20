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
    page_title="Examen de Práctica SPI - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

def load_config():
    """
    Carga el archivo data/config.json con:
    - Contraseña de acceso
    - Tiempo límite del examen (en segundos)
    - Tiempo de advertencia (10 minutos en segundos)
    - Puntajes mínimo y máximo
    """
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

def initialize_session():
    """
    Inicializa las variables de estado de la aplicación (Session State).
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

def authentication_screen():
    """
    Pantalla de autenticación: pide la contraseña al usuario.
    """
    st.title("Autenticación")
    password = st.text_input("Ingresa la contraseña para acceder al examen:", type="password")
    if st.button("Ingresar"):
        if verify_password(password):
            st.session_state.authenticated = True
            st.success("Autenticación exitosa.")
        else:
            st.error("Contraseña incorrecta.")

def user_data_input():
    """
    Pantalla para que el usuario ingrese su nombre completo e ID. Tras enviarlos:
    - Verifica que no estén vacíos.
    - Selecciona 120 preguntas aleatorias.
    - Mezcla las opciones.
    - Guarda el tiempo de inicio del examen.
    - Recarga para avanzar a exam_screen().
    """
    st.header("Datos del Usuario")
    with st.form("user_form"):
        nombre = st.text_input("Nombre Completo:")
        identificacion = st.text_input("ID o Número de Estudiante:")

        submitted = st.form_submit_button("Iniciar Examen")
        if submitted:
            if nombre.strip() and identificacion.strip():
                # Guardar datos del usuario
                st.session_state.user_data = {
                    "nombre": nombre.strip(),
                    "id": identificacion.strip()
                }
                st.success("Datos registrados. Preparando el examen...")

                # Selección y mezcla de preguntas
                selected = select_random_questions(total=120)
                st.session_state.selected_questions = selected
                for q in st.session_state.selected_questions:
                    q['opciones'] = shuffle_options(q)

                # Registro del tiempo de inicio
                st.session_state.start_time = time.time()

                # Recargar la aplicación para avanzar
                st.rerun()
            else:
                st.error("Por favor, completa todos los campos.")

def exam_screen():
    """
    Pantalla principal del examen:
    - Muestra nombre e ID del usuario.
    - Calcula y muestra el tiempo restante (HH:MM).
    - Presenta la pregunta actual y sus opciones.
    - Incluye navegación (Anterior, Siguiente, Marcar) y finalización del examen.
    """
    st.title("Examen de Práctica SPI - ARDMS")

    # Datos del usuario
    nombre = st.session_state.user_data.get('nombre', '')
    identificacion = st.session_state.user_data.get('id', '')
    st.write(f"Nombre: **{nombre}**")
    st.write(f"ID: **{identificacion}**")

    # Calcular el tiempo restante (en segundos) y formatearlo en HH:MM
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time

    total_minutes = int(remaining_time) // 60
    hours, minutes = divmod(total_minutes, 60)
    time_display = f"{hours:02d}:{minutes:02d}"

    # Mostrar el temporizador en la esquina superior derecha (solo HH:MM)
    st.markdown(
        f"""
        <div style='text-align: right; font-size: 16px;'>
            <strong>Tiempo Restante:</strong> {time_display}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar advertencia si faltan 10 minutos (warning_time_seconds = 600)
    if remaining_time <= config["warning_time_seconds"] and remaining_time > 0:
        st.warning("¡El examen terminará en 10 minutos!")

    # Si el tiempo ya se agotó, finalizamos el examen
    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("El tiempo se ha agotado. El examen se finalizará ahora.")
        finalize_exam()
        return

    # Si el examen sigue en curso, mostramos la pregunta actual
    if not st.session_state.end_exam:
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]

        # Mostrar la pregunta y sus opciones
        display_question(question, current_index + 1)

        # Navegación
        display_navigation()

        # Botón para finalizar el examen
        if st.button("Finalizar Examen"):
            # Verificar si hay preguntas sin responder
            unanswered = [
                i + 1 for i, q in enumerate(st.session_state.selected_questions)
                if str(i) not in st.session_state.answers
            ]
            if unanswered:
                st.warning(f"Hay {len(unanswered)} preguntas sin responder. ¿Estás seguro de que deseas finalizar el examen?")
                if st.button("Confirmar Finalización"):
                    finalize_exam()
            else:
                finalize_exam()

def finalize_exam():
    """
    Marca el examen como finalizado y muestra los resultados.
    Genera un PDF (sin incluir preguntas ni respuestas).
    """
    st.session_state.end_exam = True

    # Calcular puntaje
    score = calculate_score()

    # Determinar si aprueba o no
    status = "Aprobado" if score >= config["passing_score"] else "No Aprobado"

    st.header("Resultados del Examen")
    st.write(f"Puntaje Obtenido: **{score}**")
    st.write(f"Estado: **{status}**")

    # Generar PDF y permitir descarga
    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Resultados generados en PDF.")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Descargar Resultados (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

def calculate_score():
    """
    Recorre todas las preguntas y compara la respuesta del usuario 
    con la respuesta correcta para asignar un puntaje.
    """
    total_score = 0
    for idx, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        if user_answer and user_answer in question["respuesta_correcta"]:
            # Sumar puntos por cada acierto
            total_score += (config["maximum_score"] - config["passing_score"]) / 120 + config["passing_score"]
    return min(int(total_score), config["maximum_score"])

def main_screen():
    """
    Pantalla que llama exam_screen() si el examen no ha terminado.
    """
    exam_screen()

def main():
    """
    EJECUCIÓN PRINCIPAL:
    1. Inicializa el estado.
    2. Pantalla de autenticación si no hay sesión.
    3. Si usuario no ha ingresado datos, muestra formulario.
    4. Mientras examen no haya acabado, presenta exam_screen().
    5. Si está acabado, muestra resultados.
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
