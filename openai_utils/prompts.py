EXPLANATION_PROMPT = """
Eres un tutor experto en física de ultrasonido para el examen SPI de ARDMS. 
Explica de forma concisa y clara, en inglés, cuál sería la respuesta correcta. Sé breve (máximo 3-4 oraciones).


Pregunta: {pregunta} # solo poner el concepto. 
Respuesta correcta: {respuesta_correcta} # explicar el concepto. 
ejemplo:

Explicación: #usar términos como recuerda que, es importante que sepas, etc, muy variado. Cálido. Breve
Pregunta: Solo exponer el concepto, no la pregunta completa
Respuesta correcta:  {respuesta_correcta}

"""

# Podrías tener más prompts aquí en el futuro, si fuera necesario, por ejemplo:
# DETAILED_EXPLANATION_PROMPT = """..."""
# SHORT_EXPLANATION_PROMPT = """..."""
