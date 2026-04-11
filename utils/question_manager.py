import json
import random
import streamlit as st
from typing import List, Dict, Any

def load_questions():
    """
    Carga todas las preguntas desde 'data/preguntas.json'.
    """
    with open('data/preguntas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def _qid(q: Dict[str, Any]) -> str:
    """
    Identificador único de pregunta.
    """
    return str(q.get("id") or q.get("enunciado"))

def _has_image(q: Dict[str, Any]) -> bool:
    """
    Verifica si la pregunta tiene una imagen válida.
    """
    img = q.get("image")
    return bool(img and str(img).strip())

def ensure_additional_images_by_distribution(
    selected_questions: List[Dict[str, Any]],
    add_distribution: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Post-proceso: reemplaza preguntas de texto por imágenes dentro de la misma categoría.
    """
    if not add_distribution:
        return selected_questions

    source = load_questions()
    selected_ids = {_qid(q) for q in selected_questions}

    # Candidatas a ser reemplazadas (Texto)
    victims_by_class: Dict[str, List[int]] = {}
    for idx, q in enumerate(selected_questions):
        c = q.get("clasificacion", "Other")
        if c in add_distribution and not _has_image(q):
            victims_by_class.setdefault(c, []).append(idx)

    # Candidatas a entrar (Imagen) que no estén ya en la selección
    pool_by_class: Dict[str, List[Dict[str, Any]]] = {}
    for q in source:
        c = q.get("clasificacion", "Other")
        if c in add_distribution and _has_image(q):
            if _qid(q) not in selected_ids:
                pool_by_class.setdefault(c, []).append(q)

    for c in victims_by_class:
        random.shuffle(victims_by_class[c])
    for c in pool_by_class:
        random.shuffle(pool_by_class[c])

    # Proceso de inyección
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
    Selecciona preguntas por porcentaje e inyecta imágenes en TODAS las categorías.
    """
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

    # Relleno por redondeo
    remaining = total - len(selected_questions)
    if remaining > 0:
        already_selected = {_qid(s) for s in selected_questions}
        remaining_pool = [p for p in preguntas if _qid(p) not in already_selected]
        selected_questions.extend(random.sample(remaining_pool, min(remaining, len(remaining_pool))))

    # --- PLAN DE INYECCIÓN COMPLETO ---
    # Se definen mínimos de imágenes para cada una de las categorías del examen.
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

# Las funciones shuffle_options, calculate_score y select_short_questions 
# se mantienen igual que en tu versión original.
