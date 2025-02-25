import openai
import os
import streamlit as st
from .prompts import EXPLANATION_PROMPT  # Importa el prompt

# Configuración de la API Key (desde Streamlit Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

def format_question_for_openai(question_data, user_answer):
    """
    Formats a single question and the user's incorrect answer.
    """
    enunciado = question_data["enunciado"]
    opciones = question_data["opciones"]
    respuesta_correcta = question_data["respuesta_correcta"]

    opciones_str = "\n".join([f"{chr(97 + i)}) {opcion}" for i, opcion in enumerate(opciones)])

    formatted_question = (
        f"Pregunta: {enunciado}\n"
        f"Opciones:\n{opciones_str}\n"
        f"Respuesta incorrecta: {user_answer}\n"
        f"Respuesta correcta: {', '.join(respuesta_correcta)}"
    )
    return formatted_question

def get_openai_explanation(incorrect_answers): #Quitamos user_name
    """
    Gets explanations from OpenAI for incorrect answers.
    Returns:
      str:  Explicaciones en texto plano, o una cadena vacía si hay error.
    """
    formatted_questions = []
    for answer_data in incorrect_answers:
        question_data = answer_data["pregunta"]
        user_answer = answer_data["respuesta_usuario"]
        formatted_questions.append(format_question_for_openai(question_data, user_answer))

    all_questions_str = "\n\n".join(formatted_questions)

    prompt = EXPLANATION_PROMPT.format(
        preguntas_formateadas=all_questions_str,
        # nombre_estudiante=user_name  <--  Se elimina esta línea
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",  #  o el modelo que prefieras
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000,  # Ajusta según necesidad! (y costos)
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        explanation = response.choices[0].message.content.strip()
        return explanation  # Devolvemos la explicación completa como texto

    except openai.OpenAIError as e:
        print(f"Error de OpenAI: {e}")
        st.error(f"Error al obtener la explicación de OpenAI: {e}")
        return ""
    except Exception as e:
        print(f"Error inesperado: {e}")
        st.error(f"Ocurrió un error inesperado: {e}")
        return ""
