# spitest/app.py

import streamlit as st
import json
import os
import random
import time
from utils.auth import verify_password, change_password
from utils.question_manager import load_questions, select_random_questions, shuffle_options
from utils.pdf_generator import generate_pdf
from components.header import display_header
from components.question_display import display_question
from components.navigation import display_navigation

# Configuración de la página
st.set_page_config(
    page_title="Examen de Práctica SPI - ARDMS",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Cargar configuración
def load_config():
    with open('data/config.json', 'r') as f:
        return json.load(f)

config = load_config()

# Función para inicializar el estado de la sesión
def initialize_session():
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

# Pantalla de autenticación
def authentication_screen():
    st.title("Autenticación")
    password = st.text_input("Ingresa la contraseña para acceder al examen:", type="password")
    if st.button("Ingresar"):
        if verify_password(password):
            st.session_state.authenticated = True
            st.success("Autenticación exitosa.")
        else:
            st.error("Contraseña incorrecta.")

# Pantalla de ingreso de datos del usuario
def user_data_input():
    st.header("Datos del Usuario")
    with st.form("user_form"):
        nombre = st.text_input("Nombre Completo:")
        identificacion = st.text_input("ID o Número de Estudiante:")
        # Si en el futuro deseas capturar una foto, puedes integrar un componente aquí
        submitted = st.form_submit_button("Iniciar Examen")
        if submitted:
            if nombre and identificacion:
                st.session_state.user_data = {
                    "nombre": nombre,
                    "id": identificacion
                }
                # Seleccionar y cargar preguntas
                selected = select_random_questions(total=120)
                st.session_state.selected_questions = selected
                # Mezclar opciones de cada pregunta
                for q in st.session_state.selected_questions:
                    q['opciones'] = shuffle_options(q)
                # Inicializar el tiempo de inicio
                st.session_state.start_time = time.time()
                st.session_state.end_exam = False
                st.experimental_rerun()
            else:
                st.error("Por favor, completa todos los campos.")

# Pantalla del examen
def exam_screen():
    # Mostrar encabezado con temporizador
    display_header(st.session_state.start_time, config["time_limit_seconds"], config["warning_time_seconds"])

    # Cálculo del tiempo restante
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = config["time_limit_seconds"] - elapsed_time

    # Mostrar advertencia si quedan 10 minutos
    if remaining_time <= config["warning_time_seconds"] and remaining_time > 0:
        st.warning("¡El examen terminará en 10 minutos!")

    # Si el tiempo se ha agotado, finalizar el examen automáticamente
    if remaining_time <= 0 and not st.session_state.end_exam:
        st.session_state.end_exam = True
        st.success("El tiempo se ha agotado. El examen se finalizará ahora.")
        finalize_exam()

    if not st.session_state.end_exam:
        # Mostrar la pregunta actual
        current_index = st.session_state.current_question_index
        question = st.session_state.selected_questions[current_index]

        display_question(question, current_index + 1)

        # Botones de navegación y marcaje
        display_navigation()

        # Botón para finalizar el examen
        if st.button("Finalizar Examen"):
            # Verificar si hay preguntas sin responder
            unanswered = [i+1 for i, q in enumerate(st.session_state.selected_questions) if str(i) not in st.session_state.answers]
            if unanswered:
                if st.confirm(f"Hay {len(unanswered)} preguntas sin responder. ¿Estás seguro de que deseas finalizar el examen?"):
                    finalize_exam()
            else:
                finalize_exam()

# Función para finalizar el examen
def finalize_exam():
    st.session_state.end_exam = True
    # Calcular puntaje
    score = calculate_score()
    # Determinar aprobado o no
    status = "Aprobado" if score >= config["passing_score"] else "No Aprobado"
    st.header("Resultados del Examen")
    st.write(f"Puntaje Obtained: **{score}**")
    st.write(f"Estado: **{status}**")

    # Generar PDF de resultados
    pdf_path = generate_pdf(st.session_state.user_data, score, status)
    st.success("Resultados generados en PDF.")

    # Opciones para descargar el PDF
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Descargar Resultados (PDF)",
            data=f,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

# Función para calcular el puntaje
def calculate_score():
    score = 0
    for idx, question in enumerate(st.session_state.selected_questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        if user_answer and user_answer in question["respuesta_correcta"]:
            # Asumiendo que el puntaje por pregunta es uniforme
            # Puedes ajustar esto si cada pregunta tiene un valor específico
            score += (config["maximum_score"] - config["passing_score"]) / 120 + config["passing_score"]
    return min(int(score), config["maximum_score"])

# Función principal de la aplicación
def main():
    initialize_session()

    if not st.session_state.authenticated:
        authentication_screen()
    elif not st.session_state.user_data:
        user_data_input()
    elif st.session_state.end_exam:
        finalize_exam()
    else:
        exam_screen()

if __name__ == "__main__":
    main()
