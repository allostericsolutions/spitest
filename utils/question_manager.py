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
    
    # --- ADDED: Get user email and create log prefix ---
    # Obtiene el email del usuario del session state, o 'N/A' si no está disponible.
    user_email = st.session_state.user_data.get('email', 'N/A')
    # Crea el prefijo que se añadirá a todas las líneas de log.
    log_prefix = f"User: {user_email} | "
    # --- END ADDED ---

    if total_questions == 0:
        # Si no hay preguntas, retorna 0 y no ejecuta el resto del código,
        # manteniendo el comportamiento original.
        return 0

    correct_count = 0
    # ──────────────────────────────────────────────────────────
    # Contadores de aciertos por clasificación
    # ──────────────────────────────────────────────────────────
    classification_stats = {}

    for idx, question in enumerate(questions):
        # Inicializar conteo para la clasificación de la pregunta
        clasif = question.get("clasificacion", "Other")
        if clasif not in classification_stats:
            classification_stats[clasif] = {"correct": 0, "total": 0}
        classification_stats[clasif]["total"] += 1

        user_answer = st.session_state.answers.get(str(idx), None)
        
        # --- MODIFIED: Prepend prefix to original print ---
        # Añade el prefijo a la línea de log original.
        print(f"{log_prefix}Pregunta {idx}: Respuesta del usuario: {user_answer}, Respuesta correcta: {question['respuesta_correcta']}")  # DEBUG

        if user_answer is not None and user_answer in question["respuesta_correcta"]:
            correct_count += 1
            classification_stats[clasif]["correct"] += 1
        elif user_answer is not None:  # Solo registra si el usuario respondió
            # Construimos la info de respuesta incorrecta
            incorrect_info = {
                "pregunta": {
                    "enunciado": question["enunciado"],
                    "opciones": question["opciones"],
                    "respuesta_correcta": question["respuesta_correcta"],
                    "image": question.get("image"),
                    "explicacion_openai": question.get("explicacion_openai", ""),
                    "concept_to_study": question.get("concept_to_study", "")
                },
                "respuesta_usuario": user_answer,
                "indice_pregunta": idx
            }
            st.session_state.incorrect_answers.append(incorrect_info)
            # --- MODIFIED: Prepend prefix to original print ---
            # Añade el prefijo a la línea de log original.
            print(f"{log_prefix}Añadida respuesta incorrecta a la lista: {incorrect_info}")  # DEBUG

    # --- MODIFIED: Prepend prefix to original prints ---
    # Añade el prefijo a las líneas de log originales.
    print(f"{log_prefix}Total de respuestas correctas: {correct_count}")  # DEBUG
    print(f"{log_prefix}Lista final de respuestas incorrectas en calculate_score: {st.session_state.incorrect_answers}")  # DEBUG
    # --- END MODIFIED ---

    # Guardar la estadística de clasificaciones
    st.session_state.classification_stats = classification_stats

    # Cálculo de la puntuación (sin modificar la lógica)
    x = correct_count / total_questions
    if x <= 0:
        final_score = 0
    elif x <= 0.75:
        slope1 = 555 / 0.75
        final_score = slope1 * x
    else: # Esto cubre x > 0.75
        slope2 = (700 - 555) / (1 - 0.75)
        final_score = slope2 * (x - 0.75) + 555

    # --- ADDED: Print the calculated final score with prefix ---
    # Nueva línea de log para mostrar el score final calculado, con el prefijo.
    print(f"{log_prefix}Calculated final score: {int(final_score)}")
    # --- END ADDED ---

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
