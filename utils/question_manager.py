import json
import random

def load_questions():
    """
    Carga todas las preguntas desde 'data/preguntas.json'.
    Retorna una lista de diccionarios con toda la información de cada pregunta.
    """
    with open('data/preguntas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def select_random_questions(total=120):
    """
    Selecciona aleatoriamente 'total' preguntas del banco,
    tratando de balancear según la clasificación (campo 'clasificacion' en cada pregunta).
    
    - Crea un diccionario de clasificaciones.
    - Distribuye preguntas de cada clasificación para aproximarse al número 'total'.
    - Si no se alcanza el número, rellena con preguntas de otras clasificaciones.
    - Mezcla el orden final antes de retornar la lista.
    """
    preguntas = load_questions()
    
    # Agrupar preguntas por su clasificación
    clasificaciones = {}
    for pregunta in preguntas:
        clasif = pregunta.get("clasificacion", None)
        if clasif not in clasificaciones:
            clasificaciones[clasif] = []
        clasificaciones[clasif].append(pregunta)
    
    selected_questions = []
    num_clasificaciones = len(clasificaciones)
    
    # Cantidad base de preguntas por clasificación
    questions_per_clasif = total // num_clasificaciones if num_clasificaciones > 0 else total
    
    # Seleccionar preguntas de cada clasificación
    for clasif, lista_preguntas in clasificaciones.items():
        if len(lista_preguntas) >= questions_per_clasif:
            selected_questions.extend(random.sample(lista_preguntas, questions_per_clasif))
        else:
            # Si no hay suficientes en esta clasificación, toma todas
            selected_questions.extend(lista_preguntas)
    
    # Si no llegamos a 'total', completamos con preguntas aleatorias
    remaining = total - len(selected_questions)
    if remaining > 0:
        # Preguntas que no han sido tomadas aún
        remaining_pool = [p for p in preguntas if p not in selected_questions]
        if len(remaining_pool) >= remaining:
            selected_questions.extend(random.sample(remaining_pool, remaining))
        else:
            selected_questions.extend(remaining_pool)
    
    # Mezcla final de las preguntas seleccionadas
    random.shuffle(selected_questions)
    return selected_questions

def shuffle_options(question):
    """
    Toma las opciones de la pregunta y las mezcla aleatoriamente.
    Retorna una nueva lista con el orden de opciones reordenado.
    """
    opciones = question.get("opciones", []).copy()
    random.shuffle(opciones)
    return opciones
