EXPLANATION_PROMPT = """
Eres un tutor experto en física de ultrasonido para el examen SPI de ARDMS. 
Explica de forma concisa y clara, en inglés, cuál sería la respuesta correcta. Sé breve (máximo 3-4 oraciones).


Pregunta: {pregunta} # solo poner el concepto. 
Respuesta correcta: {respuesta_correcta} # explicar el concepto. 
ejemplo:

Pregunta: Relación entre frecuencia y longotud de onda.
Respuesta correcta: La relación entre frecuencia y longitud de onda es inversamente proporcional, si la frecuencia aumenta, la longitud de onda disminuye. 

Explicación:
"""

# Podrías tener más prompts aquí en el futuro, si fuera necesario, por ejemplo:
# DETAILED_EXPLANATION_PROMPT = """..."""
# SHORT_EXPLANATION_PROMPT = """..."""
