import json
import random
import streamlit as st
from typing import List, Dict, Any

def load_questions():
    """
    Loads all questions from 'data/preguntas.json'.
    """
    with open('data/preguntas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def _qid(q: Dict[str, Any]) -> str:
    """
    Identificador único de pregunta (usa 'id' si existe; si no, 'enunciado').
    """
    return str(q.get("id") or q.get("enunciado"))

def _has_image(q: Dict[str, Any]) -> bool:
    """
    Determina si la pregunta tiene imagen (campo 'image' no vacío).
    """
    img = q.get("image")
    return bool(img and str(img).strip())

def ensure_additional_images_by_distribution(
    selected_questions: List[Dict[str, Any]],
    add_distribution: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Post-proceso: reemplaza preguntas SIN imagen por preguntas CON imagen 
    dentro de la misma clasificación para forzar contenido visual.
    """
    if not add_distribution:
        return selected_questions

    source = load_questions()
    selected_ids = {_qid(q) for q in selected_questions}

    # Identificar preguntas sin imagen que pueden ser reemplazadas
    victims_by_class: Dict[str, List[int]] = {}
    for idx, q in enumerate(selected_questions):
        c = q.get("clasificacion", "Other")
        if c in add_distribution and not _has_image(q):
            victims_by_class.setdefault(c, []).append(idx)

    # Identificar preguntas con imagen disponibles en el banco (no seleccionadas aún)
    pool_by_class: Dict[str, List[Dict[str, Any]]] = {}
    for q in source:
        c = q.get("clasificacion", "Other")
        if c in add_distribution and _has_image(q):
            if _qid(q) not in selected_ids:
                pool_by_class.setdefault(c, []).append(q)

    # Mezclar para que la selección sea aleatoria
    for c in victims_by_class:
        random.shuffle(victims_by_class[c])
    for c in pool_by_class:
        random.shuffle(pool_by_class[c])

    # Ejecutar el intercambio (Swap)
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
    """
    Selects questions based on percentages and then forces additional images.
    """
    preguntas = load_questions()
    classification_percentages = {
       "Physical Principles": 15,
       "Ultrasound Transducers": 16,
       "Doppler Imaging Concepts": 31,
       "Imaging Principles and Instrumentation": 28,
       "Clinical Safety, Patient Care, and Quality Assurance": 10,
    }

    # Agrupar por clasificación
    clasificaciones = {}
    for pregunta in preguntas:
        clasif = pregunta.get("clasificacion", "Other")
        if clasif not in clasificaciones:
            clasificaciones[clasif] = []
        clasificaciones[clasif].append(pregunta)

    # Selección inicial basada puramente en porcentajes
    selected_questions = []
    for clasif, percentage in classification_percentages.items():
        if clasif in clasificaciones:
            num_questions = int(total * (percentage / 100))
            available = clasificaciones[clasif]
            selected_questions.extend(random.sample(available, min(num_questions, len(available))))

    # Rellenar si faltan por redondeo
    remaining = total - len(selected_questions)
    if remaining > 0:
        remaining_pool = [p for p in preguntas if _qid(p) not in {_qid(s) for s in selected_questions}]
        selected_questions.extend(random.sample(remaining_pool, min(remaining, len(remaining_pool))))

    # --- PLAN DE INYECCIÓN DE IMÁGENES (Ajustable) ---
    # Este plan intentará convertir preguntas de texto en imágenes sin cambiar el total ni la clasificación.
    add_plan_by_class = {
        "Doppler Imaging Concepts": 10,
        "Ultrasound Transducers": 5,
        "Imaging Principles and Instrumentation": 5,
    }
    
    selected_questions = ensure_additional_images_by_distribution(selected_questions, add_plan_by_class)

    random.shuffle(selected_questions)
    return selected_questions

def shuffle_options(question):
    opciones = question.get("opciones", []).copy()
    random.shuffle(opciones)
    return opciones

def calculate_score():
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
        
        # Validación de respuesta correcta
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

    st.session_state.classification_stats = classification_stats

    # Lógica de puntaje escalar
    x = correct_count / total_questions
    if x <= 0:
        final_score = 0
    elif x <= 0.75:
        final_score = (555 / 0.75) * x
    else:
        final_score = ((700 - 555) / (1 - 0.75)) * (x - 0.75) + 555

    return int(final_score)

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
