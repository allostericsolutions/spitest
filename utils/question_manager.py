import json
import random
import streamlit as st  # Importante: Asegúrate de tener esta línea

def load_questions():
    """
    Carga todas las preguntas desde 'data/preguntas.json'.
    Retorna una lista de diccionarios.
    """
    with open('data/preguntas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_random_questions(total=120):
    """
    Selecciona preguntas aleatoriamente, basándose en porcentajes por clasificación.
    """
    preguntas = load_questions()

    # --- PORCENTAJES DEFINIDOS AQUÍ ---
    classification_percentages = {
        "Basic Physics (Frequency, Wavelength, Period, and Propagation)": 6,
        "Instruments (Transducers Construction and function; Image Settings and Display)": 4,
        "Doppler Physics and Instrumentation": 17,
        "Wave Properties and Interactions with matter": 8,
        "Bioeffects, Spatial, Temporal Resolution": 3,
        "Safety and Risk Management and new tech": 3,
        "Basic Physics Concepts, Wave Parameters, and Attenuation": 6,
        "Transducers, Resolution, and Image Formation.": 9,
        "Image Display, Processing, and Artifacts": 16,
        "Hemodynamics and Doppler Principles": 17,
        "Quality Assurance and Quality Control": 4,
        "Patient care and new technology": 7
    }

    # --- Verificación de suma de porcentajes (Opcional pero recomendado) ---
    total_percentage = sum(classification_percentages.values())
    if total_percentage != 100:
        raise ValueError("The sum of classification percentages must be 100.")

    # Agrupar preguntas por clasificación
    clasificaciones = {}
    for pregunta in preguntas:
        clasif = pregunta.get("clasificacion", "Other")  # Valor por defecto "Other"
        if clasif not in clasificaciones:
            clasificaciones[clasif] = []
        clasificaciones[clasif].append(pregunta)

    selected_questions = []

    # --- Selección basada en porcentajes ---
    for clasif, percentage in classification_percentages.items():
        if clasif in clasificaciones:  # Asegurarse de que la clasificación existe
            num_questions = int(total * (percentage / 100))  # Calcular número
            available_questions = clasificaciones[clasif]

            # Seleccionar aleatoriamente, o todas si no hay suficientes
            selected_questions.extend(random.sample(available_questions, min(num_questions, len(available_questions))))

    # --- Relleno (si es necesario) ---
    remaining = total - len(selected_questions)
    if remaining > 0:
        remaining_pool = [p for p in preguntas if p not in selected_questions]
        selected_questions.extend(random.sample(remaining_pool, remaining))

    random.shuffle(selected_questions)
    return selected_questions

def shuffle_options(question):
    """
    Mezcla aleatoriamente las opciones de una pregunta.
    """
    opciones = question.get("opciones", []).copy()
    random.shuffle(opciones)
    return opciones

def calculate_score():
    """
    Count correct answers. Then, we segment:
    - 0% to 75% correct: line from 0 points to 555
    - 75% to 100% correct: line from 555 to 700
    """
    questions = st.session_state.selected_questions
    total_questions = len(questions)
    if total_questions == 0:
        return 0

    st.session_state.incorrect_answers = []
    correct_count = 0

    for idx, question in enumerate(questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        print(f"Pregunta {idx}: Respuesta del usuario: {user_answer}, Respuesta correcta: {question['respuesta_correcta']}")  # AÑADE ESTO

        if user_answer and user_answer in question["respuesta_correcta"]:
            correct_count += 1
        else:
            if user_answer is not None:
                incorrect_info = {
                    "pregunta": {
                        "enunciado": question["enunciado"],
                        "opciones": question["opciones"],
                        "respuesta_correcta": question["respuesta_correcta"],
                        "image": question.get("image")
                    },
                    "respuesta_usuario": user_answer,
                    "indice_pregunta": idx
                }
                st.session_state.incorrect_answers.append(incorrect_info)
                print(f"Añadida respuesta incorrecta a la lista: {incorrect_info}")  # AÑADE ESTO

    print(f"Total de respuestas correctas: {correct_count}")  # AÑADE ESTO
    print(f"Lista final de respuestas incorrectas: {st.session_state.incorrect_answers}") # AÑADE ESTO

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
