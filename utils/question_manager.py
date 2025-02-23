import json
import random

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
