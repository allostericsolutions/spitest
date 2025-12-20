import json
import random
import streamlit as st

def load_questions():
        return json.load(f)

# ──────────────────────────────────────────────────────────
# Utilidades para post-proceso de imágenes (solo examen full)
# ──────────────────────────────────────────────────────────
def _qid(q):
    """
    Identificador único de la pregunta: usa 'id' si existe; si no, 'enunciado'.
    """
    return str(q.get("id") or q.get("enunciado"))

def _has_image(q):
    """
    Determina si la pregunta tiene imagen (campo 'image' no vacío).
    """
    img = q.get("image")
    return bool(img and str(img).strip())

def ensure_additional_images_by_distribution(selected_questions, add_distribution):
    """
    Post-proceso: reemplaza preguntas SIN imagen por preguntas CON imagen
    dentro de la MISMA clasificación, según la distribución pedida (p.ej. 4/4/2).
    - No duplica preguntas (usa id/enunciado para evitar repetir).
    - No altera la distribución por clasificación (reemplazo 1 a 1 en la misma clase).
    - Si en alguna clase no hay suficientes víctimas o candidatas, añade las que se pueda.
    - No redistribuye el faltante a otras clases (respeta el ratio).
    """
    if not add_distribution:
        return selected_questions

    # Fuente: banco completo
    source = load_questions()

    # Conjunto de IDs ya seleccionados
    selected_ids = {_qid(q) for q in selected_questions}

    # Víctimas (SIN imagen) por clase elegible
    victims_by_class = {}
    for idx, q in enumerate(selected_questions):
        c = q.get("clasificacion", "Other")
        if c in add_distribution and not _has_image(q):
            victims_by_class.setdefault(c, []).append(idx)

    # Pool de candidatas (CON imagen) por clase elegible, evitando duplicados
    pool_by_class = {}
    for q in source:
        c = q.get("clasificacion", "Other")
        if c in add_distribution and _has_image(q):
            qid = _qid(q)
            if qid not in selected_ids:
                pool_by_class.setdefault(c, []).append(q)

    # Aleatoriedad en víctimas y pool
    for c in victims_by_class:
        random.shuffle(victims_by_class[c])
    for c in pool_by_class:
        random.shuffle(pool_by_class[c])

    # Ejecutar el plan por clase (no se redistribuye el faltante)
    for c, target in add_distribution.items():
        if target <= 0:
            continue
        victims = victims_by_class.get(c, [])
        pool = pool_by_class.get(c, [])
        while target > 0 and victims and pool:
            v_idx = victims.pop()
            cand = pool.pop()
            selected_questions[v_idx] = cand
            selected_ids.add(_qid(cand))
            target -= 1

    return selected_questions

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

    # ──────────────────────────────────────────────────────────
    # POST-PROCESO: sumar +10 preguntas con imagen (4/4/2)
    # Clases objetivo:
    # - Doppler Imaging Concepts: 4
    # - Imaging Principles and Instrumentation: 4
    # - Ultrasound Transducers: 2
    # ──────────────────────────────────────────────────────────
    add_plan_by_class = {
        "Doppler Imaging Concepts": 4,
        "Imaging Principles and Instrumentation": 4,
        "Ultrasound Transducers": 2,
    }
    selected_questions = ensure_additional_images_by_distribution(selected_questions, add_plan_by_class)
    # ──────────────────────────────────────────────────────────

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
    if total_questions == 0:
        return 0

    correct_count = 0
    # ──────────────────────────────────────────────────────────
    # Contadores de aciertos por clasificación
    # ──────────────────────────────────────────────────────────
    classification_stats = {}

    # --- CAMBIO AQUÍ: Acceso más robusto al nombre del usuario ---
    # Aseguramos que user_data exista y luego obtenemos el nombre, con un fallback 'Unknown User'
    user_name = st.session_state.get('user_data', {}).get('nombre', 'Unknown User')
    # --- FIN DEL CAMBIO ---

    for idx, question in enumerate(questions):
        # Inicializar conteo para la clasificación de la pregunta
        clasif = question.get("clasificacion", "Other")
        if clasif not in classification_stats:
            classification_stats[clasif] = {"correct": 0, "total": 0}
        classification_stats[clasif]["total"] += 1

        user_answer = st.session_state.answers.get(str(idx), None)
        # Añadir el nombre del usuario al print
        print(f"[{user_name}] Pregunta {idx}: Respuesta del usuario: {user_answer}, Respuesta correcta: {question['respuesta_correcta']}")  # DEBUG

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
            # Añadir el nombre del usuario al print
            print(f"[{user_name}] Añadida respuesta incorrecta a la lista: {incorrect_info}")  # DEBUG

    # Añadir el nombre del usuario al print
    print(f"[{user_name}] Total de respuestas correctas: {correct_count}")  # DEBUG
    print(f"[{user_name}] Lista final de respuestas incorrectas en calculate_score: {st.session_state.incorrect_answers}")  # DEBUG

    # Guardar la estadística de clasificaciones
    st.session_state.classification_stats = classification_stats

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

# ------------------------------------------
# Para examen corto
# ------------------------------------------
def load_short_questions():
    """
    Loads all questions from 'data/preguntas_corto.json'.
    """
    with open('data/preguntas_corto.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_short_questions(total=30):
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
