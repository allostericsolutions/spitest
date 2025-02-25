EXPLANATION_PROMPT = """
Eres un tutor experto en física de ultrasonido para el examen SPI de ARDMS. 
Explica de forma concisa y clara por qué la siguiente respuesta es incorrecta, 
y cuál sería la respuesta correcta. Sé breve (máximo 3-4 oraciones).

Pregunta: {pregunta}
Respuesta incorrecta: {respuesta_incorrecta}
Respuesta correcta: {respuesta_correcta}

Explicación:
"""

# Podrías tener más prompts aquí en el futuro, si fuera necesario, por ejemplo:
# DETAILED_EXPLANATION_PROMPT = """..."""
# SHORT_EXPLANATION_PROMPT = """..."""
