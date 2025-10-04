# utils/question_manager.py
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
        "Physical Principles": 15,
        "Ultrasound Transducers": 16,
        "Doppler Imaging Concepts": 31,
        "Imaging Principles and Instrumentation": 28,
        "Clinical Safety, Patient Care, and Quality Assurance": 10,
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
    Also calculates a classification-wise count of correct answers.
    """
    questions = st.session_state.selected_questions
    total_questions = len(questions)
    
    # --- INICIO: Obtener datos del usuario para el log ---
    user_email = st.session_state.user_data.get('email', 'N/A')
    log_prefix = f"User: {user_email} | "
    # --- FIN: Obtener datos del usuario para el log ---

    # --- INICIO: Log para el inicio del cálculo detallado ---
    print(f"{log_prefix}Starting detailed score calculation for {total_questions} questions.")
    # --- FIN: Log para el inicio del cálculo detallado ---

    # --- ADDED: Initialize final_score to a default value ---
    # This ensures final_score always has a value, preventing UnboundLocalError.
    final_score = 0
    # --- END ADDED ---

    correct_count = 0 # Initialize correct_count
    classification_stats = {} # Initialize classification_stats

    # --- RESTRUCTURADO: Procesar solo si hay preguntas ---
    if total_questions > 0:
        # ──────────────────────────────────────────────────────────
        # Contadores de aciertos por clasificación
        # ──────────────────────────────────────────────────────────
        
        for idx, question in enumerate(questions):
            # Inicializar conteo para la clasificación de la pregunta
            clasif = question.get("clasificacion", "Other")
            if clasif not in classification_stats:
                classification_stats[clasif] = {"correct": 0, "total": 0}
            classification_stats[clasif]["total"] += 1

            user_answer = st.session_state.answers.get(str(idx), None)
            
            # Formatear opciones para mostrar con letras (a, b, c...)
            options_str = ", ".join([f"{chr(97 + i)}) {option}" for i, option in enumerate(question['opciones'])])

            # --- MODIFICACIÓN: Log detallado para CADA pregunta ---
            print(f"{log_prefix}--- Question {idx + 1} ---") # Número de pregunta amigable para el usuario (empezando en 1)
            print(f"{log_prefix}  Statement: {question['enunciado']}")
            print(f"{log_prefix}  Options: {options_str}")
            print(f"{log_prefix}  User Answer: '{user_answer}'")
            print(f"{log_prefix}  Correct Answer(s): '{question['respuesta_correcta']}'")

            is_correct = False
            if user_answer is not None and user_answer in question["respuesta_correcta"]:
                correct_count += 1
                classification_stats[clasif]["correct"] += 1
                is_correct = True
                print(f"{log_prefix}  Result: CORRECT")
            elif user_answer is not None: # El usuario respondió, pero fue incorrecta
                # Guardamos la información de la respuesta incorrecta para uso posterior (PDF, explicaciones)
                # Solo incluimos lo necesario, excluyendo imagen, explicacion_openai, concept_to_study
                incorrect_info = {
                    "pregunta": {
                        "enunciado": question["enunciado"],
                        "opciones": question["opciones"],
                        "respuesta_correcta": question["respuesta_correcta"],
                        # No incluimos 'image', 'explicacion_openai', 'concept_to_study' aquí
                    },
                    "respuesta_usuario": user_answer,
                    "indice_pregunta": idx
                }
                st.session_state.incorrect_answers.append(incorrect_info)
                print(f"{log_prefix}  Result: INCORRECT")
            else: # El usuario no respondió
                print(f"{log_prefix}  Result: NOT ANSWERED")
            # --- FIN MODIFICACIÓN: Log detallado para CADA pregunta ---

        # Lógica de cálculo de puntuación (solo si hay preguntas)
        x = correct_count / total_questions
        if x <= 0:
            final_score = 0
        elif x <= 0.75:
            slope1 = 555 / 0.75
            final_score = slope1 * x
        else: # This covers x > 0.75
            slope2 = (700 - 555) / (1 - 0.75)
            final_score = slope2 * (x - 0.75) + 555
        
        # Guardar la estadística de clasificaciones
        st.session_state.classification_stats = classification_stats
    # --- FIN RESTRUCTURADO ---

    # --- MODIFICACIÓN: Log resumen al final ---
    # Estos prints se ejecutarán siempre, mostrando el total de aciertos y el score final.
    # Si total_questions era 0, final_score seguirá siendo 0 (su valor inicial).
    print(f"{log_prefix}Total correct answers: {correct_count} / {total_questions}")
    print(f"{log_prefix}Calculated final score: {int(final_score)}")
    # --- FIN MODIFICACIÓN: Log resumen al final ---

    return int(final_score)

# ------------------------------------------
# Para examen corto
# ------------------------------------------
def load_short_questions():
    """
    Loads all questions from 'data/preguntas_corto.json'.
    """
    with open('data/preguntas_corto.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_short_questions(total=20):
    """
    Selects 'total' questions randomly from the short exam questions file.
    Since this is for the free/demo version, no distribution by classification is applied.
    """
    questions = load_short_questions()
    if total > len(questions):
        total = len(questions)
    selected_questions = random.sample(questions, total)
    random.shuffle(selected_questions)
    return selected_questions
