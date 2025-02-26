import json
import random
import streamlit as st

def load_questions():
    """
    Loads all questions from 'data/preguntas.json'.
    """
    with open('data/preguntas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_random_questions(total=120):
    """
    Selects questions randomly, based on classification percentages.
    """
    preguntas = load_questions()
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
    total_percentage = sum(classification_percentages.values())
    if total_percentage != 100:
        raise ValueError("The sum of classification percentages must be 100.")

    clasificaciones = {}
    for pregunta in preguntas:
        clasif = pregunta.get("clasificacion", "Other")
        if clasif not in clasificaciones:
            clasificaciones[clasif] = []
        clasificaciones[clasif].append(pregunta)

    selected_questions = []
    for clasif, percentage in classification_percentages.items():
        if clasif in clasificaciones:
            num_questions = int(total * (percentage / 100))
            available_questions = clasificaciones[clasif]
            selected_questions.extend(random.sample(available_questions, min(num_questions, len(available_questions))))

    remaining = total - len(selected_questions)
    if remaining > 0:
        remaining_pool = [p for p in preguntas if p not in selected_questions]
        selected_questions.extend(random.sample(remaining_pool, remaining))

    random.shuffle(selected_questions)
    return selected_questions

def shuffle_options(question):
    """
    Shuffles the options of a question randomly.
    """
    opciones = question.get("opciones", []).copy()
    random.shuffle(opciones)
    return opciones

def calculate_score():
    """
    Calculates the exam score and stores incorrect answers.
    """
    questions = st.session_state.selected_questions
    total_questions = len(questions)
    if total_questions == 0:
        return 0

    # st.session_state.incorrect_answers = [] # YA NO ES NECESARIO AQUI, se inicializa en initialize_session
    correct_count = 0

    for idx, question in enumerate(questions):
        user_answer = st.session_state.answers.get(str(idx), None)
        print(f"Pregunta {idx}: Respuesta del usuario: {user_answer}, Respuesta correcta: {question['respuesta_correcta']}")  # DEBUG

        if user_answer is not None and user_answer in question["respuesta_correcta"]:  # Comprobación más precisa
            correct_count += 1
        elif user_answer is not None:  # Solo registra si el usuario *respondió*
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
            print(f"Añadida respuesta incorrecta a la lista: {incorrect_info}")  # DEBUG

    print(f"Total de respuestas correctas: {correct_count}")  # DEBUG
    print(f"Lista final de respuestas incorrectas en calculate_score: {st.session_state.incorrect_answers}") # DEBUG

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
