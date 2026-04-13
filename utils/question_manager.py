import json
import random
import streamlit as st

def load_questions():
    """
    Loads all questions from 'data/preguntas.json'.
    """
    with open('data/preguntas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def _qid(q):
    """
    Identificador único de pregunta.
    """
    return str(q.get("id") or q.get("enunciado"))

def _has_image(q):
    """
    Determina si la pregunta tiene imagen.
    """
    img = q.get("image")
    return bool(img and str(img).strip())

def ensure_additional_images_by_distribution(selected_questions, add_distribution):
    """
    Post-proceso para inyectar imágenes por categoría.
    """
    if not add_distribution:
        return selected_questions

    source = load_questions()
    selected_ids = {_qid(q) for q in selected_questions}

    victims_by_class = {}
    for idx, q in enumerate(selected_questions):
        c = q.get("clasificacion", "Other")
        if c in add_distribution and not _has_image(q):
            if c not in victims_by_class:
                victims_by_class[c] = []
            victims_by_class[c].append(idx)

    pool_by_class = {}
    for q in source:
        c = q.get("clasificacion", "Other")
        if c in add_distribution and _has_image(q):
            if _qid(q) not in selected_ids:
                if c not in pool_by_class:
                    pool_by_class[c] = []
                pool_by_class[c].append(q)

    for c in victims_by_class:
        random.shuffle(victims_by_class[c])
    for c in pool_by_class:
        random.shuffle(pool_by_class[c])

    for c, target in add_distribution.items():
        victims = victims_by_class.get(c, [])
        pool = pool_by_class.get(c, [])
        count = 0
        while count < target and victims and pool:
            v_idx = victims.pop()
            cand = pool.pop()
            selected_questions[v_idx] = cand
            selected_ids.add(_qid(cand))
            count += 1
            
    return selected_questions

def select_random_questions(total=120):
    preguntas = load_questions()
    classification_percentages = {
       "Physical Principles": 15,
       "Ultrasound Transducers": 16,
       "Doppler Imaging Concepts": 31,
       "Imaging Principles and Instrumentation": 28,
       "Clinical Safety, Patient Care, and Quality Assurance": 10,
    }

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
            available = clasificaciones[clasif]
            selected_questions.extend(random.sample(available, min(num_questions, len(available))))

    remaining = total - len(selected_questions)
    if remaining > 0:
        current_ids = {_qid(s) for s in selected_questions}
        remaining_pool = [p for p in preguntas if _qid(p) not in current_ids]
        selected_questions.extend(random.sample(remaining_pool, min(remaining, len(remaining_pool))))

    add_plan_by_class = {
        "Doppler Imaging Concepts": 12,
        "Imaging Principles and Instrumentation": 10,
        "Ultrasound Transducers": 6,
        "Physical Principles": 5,
        "Clinical Safety, Patient Care, and Quality Assurance": 4,
    }
    
    selected_questions = ensure_additional_images_by_distribution(selected_questions, add_plan_by_class)

    random.shuffle(selected_questions)
    return selected_questions

def shuffle_options(question):
    opciones = question.get("opciones", []).copy()
    random.shuffle(opciones)
    return opciones

# ---------------------------------------------------------
# ✅ FUNCIÓN calculate_score() RESTAURADA (CON LOG COMPLETO)
# ---------------------------------------------------------
def calculate_score():
    """
    Calculates the exam score and stores incorrect answers.
    Also calculates a classification-wise count of correct answers.
    """
    questions = st.session_state.selected_questions
    total_questions = len(questions)
    if total_questions == 0:
        return 0

    correct_count = 0
    classification_stats = {}

    user_name = st.session_state.get('user_data', {}).get('nombre', 'Unknown User')

    for idx, question in enumerate(questions):
        clasif = question.get("clasificacion", "Other")
        if clasif not in classification_stats:
            classification_stats[clasif] = {"correct": 0, "total": 0}
        classification_stats[clasif]["total"] += 1

        user_answer = st.session_state.answers.get(str(idx), None)

        # LOG EN CONSOLA
        print(f"[{user_name}] Pregunta {idx}: Respuesta del usuario: {user_answer}, Respuesta correcta: {question['respuesta_correcta']}")

        if user_answer is not None and user_answer in question["respuesta_correcta"]:
            correct_count += 1
            classification_stats[clasif]["correct"] += 1
        elif user_answer is not None:
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

            # LOG EN CONSOLA
            print(f"[{user_name}] Añadida respuesta incorrecta a la lista: {incorrect_info}")

    # LOG FINAL
    print(f"[{user_name}] Total de respuestas correctas: {correct_count}")
    print(f"[{user_name}] Lista final de respuestas incorrectas en calculate_score: {st.session_state.incorrect_answers}")

    st.session_state.classification_stats = classification_stats

    x = correct_count / total_questions
    if x <= 0:
        final_score = 0
    elif x <= 0.75:
        final_score = (555 / 0.75) * x
    else:
        final_score = ((700 - 555) / (1 - 0.75)) * (x - 0.75) + 555

    return int(final_score)

# ------------------------------------------
# Para examen corto
# ------------------------------------------
def load_short_questions():
    with open('data/preguntas_corto.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_short_questions(total=30):
    questions = load_short_questions()
    if total > len(questions):
        total = len(questions)
    selected_questions = random.sample(questions, total)
    random.shuffle(selected_questions)
    return selected_questions
