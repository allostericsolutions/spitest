import json
import streamlit as st

def load_config():
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_password(input_password):
    """
    Verifica si la contraseña ingresada corresponde a alguna de las contraseñas
    válidas para el examen corto o completo, y guarda la modalidad en Session State.
    """
    config = load_config()

    if input_password in config.get("passwords_short", []):
        st.session_state["exam_type"] = "short"
        return True
    elif input_password in config.get("passwords_full", []):
        st.session_state["exam_type"] = "full"
        return True
    else:
        return False
