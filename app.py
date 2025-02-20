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

# ──────────────────────────────────────────────────────────
# FUNCIÓN PARA MOSTRAR VERSIÓN DE STREAMLIT (DEBUG)
# ──────────────────────────────────────────────────────────
def show_streamlit_version():
    """
    Muestra la versión real de Streamlit utilizada y la lista 
    de atributos disponibles en el módulo 'st'.
    Útil para diagnosticar por qué 'st.experimental_rerun' o 'st.rerun' 
    no existen en entornos extraños.
    """
    st.write("Versión real de Streamlit:", st.__version__)
    st.write("Atributos disponibles en st:", dir(st))

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Examen de Práctica SPI - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

def load_config():
    """
    Carga el archivo config.json que contiene información como:
    - Contraseña de acceso
    - Tiempo límite del examen
    - Tiempo de advertencia (10 minutos)
    - Puntajes mínimo y máximo
    """
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

def initialize_session():
    """
    Inicializa todas las variables necesarias en el estado de la sesión de Streamlit.
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
    Muestra la pantalla de autenticación donde el usuario ingresa la contraseña.
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
    Muestra un formulario para que el usuario ingrese su nombre completo y su ID.
    Al enviar el formulario:
    - Se verifica que los campos no estén vacíos.
    - Se seleccionan aleatoriamente 120 preguntas.
    - Se barajan sus opciones.
    - Se registra la hora de inicio del examen.
    """

    # LLAMAMOS A LA FUNCIÓN DE DEBUG PARA VER LA VERSIÓN DE STREAMLIT
    show_streamlit_version()

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
                st.experimental_rerun()
            else:
                st.error("Por favor, completa todos los campos.")

def exam_screen():
    """
    Muestra la pantalla principal del examen con:
    - Datos del usuario (nombre e ID)
    - Temporizador
    - Pregunta actual y sus opciones
    - Botones de navegación y marcaje
    - Botón para finalizar el examen
    """
    st.title("Examen de Práctica SPI - ARDMS")
    
    # Mostrar datos del usuario
    nombre = st.session_state.user_data.get('nombre', '')
    identificacion = st.session_state.user_data.get('id', '')
    st.write(f"Nombre: **{nombre}**")
    st.write(f"ID: **{identificacion}**")

    # Calcular tiempo restante
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time

    # Formatear el tiempo en hh:mm:ss
    minutes, seconds = divmod(int(remaining_time), 60)
    hours, minutes = divmod(minutes, 60)
    time_display = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Mostrar el temporizador en la esquina superior derecha
    st.markdown(
        f"""
        <div style='text-align: right; font-size: 16px;'>
            <strong>Tiempo Restante:</strong> {time_display}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar advertencia si quedan 10 minutos
    if remaining_time <= config["warning_time_seconds"] and remaining_time > 0:
        st.warning("¡El examen terminará en 10 minutos!")

    # Revisar si se agotó el tiempo
    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("El tiempo se ha agotado. El examen se finalizará ahora.")
        finalize_exam()
        return

    # Mostrar la pregunta actual si el examen no ha terminado
    if not st.session_state.end_exam:
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]

        # Mostrar la pregunta y sus opciones
        display_question(question, current_index + 1)

        # Navegación entre preguntas y marcaje
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
    Marca el examen como finalizado, calcula el puntaje y muestra los resultados.
    También genera un PDF con los datos del usuario y su puntaje, sin mostrar preguntas.
    """
    st.session_state.end_exam = True
    
    # Calcular el puntaje obtenido
    score = calculate_score()
    
    # Determinar si el usuario aprueba o no
    status = "Aprobado" if score >= config["passing_score"] else "No Aprobado"
    
    st.header("Resultados del Examen")
    st.write(f"Puntaje Obtenido: **{score}**")
    st.write(f"Estado: **{status}**")

    # Generar PDF con los resultados
    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Resultados generados en PDF.")

    # Opción para descargar el PDF
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Descargar Resultados (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

def calculate_score():
    """
    Recorre todas las preguntas y compara la respuesta del usuario con la respuesta correcta.
    Asigna un puntaje por cada pregunta correcta. 
    """
    total_score = 0
    for idx, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        
        # Si el usuario seleccionó una de las respuestas correctas
        if user_answer and user_answer in question["respuesta_correcta"]:
            # Sumar puntaje uniforme por cada acierto
            total_score += (config["maximum_score"] - config["passing_score"]) / 120 + config["passing_score"]
    # Limitar el puntaje al máximo definido
    return min(int(total_score), config["maximum_score"])

def main_screen():
    """
    Una vez que el usuario está autenticado y ha ingresado sus datos,
    esta función llama a exam_screen() para mostrar el examen.
    """
    exam_screen()

def main():
    """
    Función principal de la aplicación:
    1. Inicializa el estado de la sesión.
    2. Si no está autenticado, muestra la pantalla de autenticación.
    3. Si no hay datos del usuario, muestra el formulario de ingreso de datos.
    4. Si el examen no ha terminado, muestra la pantalla de examen.
    5. Si el examen está finalizado, muestra los resultados.
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
