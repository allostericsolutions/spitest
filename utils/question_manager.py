import random

def select_questions_by_percentage(questions, num_questions=120):
    # Configuración de porcentajes por grupo de clasificaciones
    percentages = {
        "Perform Ultrasound Examinations": 0.23,
        "Manage Ultrasound Transducers": 0.07,
        "Optimize Sonographic Images": 0.26,
        "Apply Doppler Concepts": 0.34,
        "Provide Clinical Safety & Quality Assurance": 0.10
    }
    
    # Mapear clasificaciones individuales a los grupos principales
    classification_map = {
        "Perform Ultrasound Examinations": [
            "Wave Properties and Interactions with matter",
            "Image Display, Processing, and Artifacts",
            "Patient care and new technology"
        ],
        "Manage Ultrasound Transducers": [
            "Instruments (Transducers Construction and function; Image Settings and Display)",
            "Transducers, Resolution, and Image Formation."
        ],
        "Optimize Sonographic Images": [
            "Basic Physics (Frequency, Wavelength, Period, and Propagation)",
            "Basic Physics Concepts, Wave Parameters, and Attenuation",
            "Transducers, Resolution, and Image Formation.",
            "Image Display, Processing, and Artifacts"
        ],
        "Apply Doppler Concepts": [
            "Doppler Physics and Instrumentation",
            "Hemodynamics and Doppler Principles"
        ],
        "Provide Clinical Safety & Quality Assurance": [
            "Bioeffects, Spatial, Temporal Resolution",
            "Safety and Risk Management and new tech",
            "Quality Assurance and Quality Control"
        ]
    }

    # Almacenar las preguntas seleccionadas
    selected_questions = []

    for group, classifications in classification_map.items():
        # Total de preguntas a seleccionar para este grupo de clasificaciones
        total_group_questions = int(num_questions * percentages[group])
        
        # Filtrar preguntas por clasificaciones correspondientes a este grupo
        group_questions = [q for q in questions if q['clasificacion'] in classifications]
        
        # Selección aleatoria de preguntas
        selected_group_questions = random.sample(group_questions, min(total_group_questions, len(group_questions)))
        
        # Agregar al conjunto de preguntas seleccionadas
        selected_questions.extend(selected_group_questions)

    # Devolver la lista final de preguntas seleccionadas
    return selected_questions

def validate_selection(selected_questions):
    # Contar preguntas por clasificación
    classification_count = {}
    for question in selected_questions:
        classification = question['clasificacion']
        if classification not in classification_count:
            classification_count[classification] = 0
        classification_count[classification] += 1
    
    # Imprimir resultados
    print("Distribución de preguntas seleccionadas:")
    for classification, count in classification_count.items():
        print(f"{classification}: {count} preguntas")
