import json
import streamlit as st

def load_config():
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_password(input_password):
    """
    Verifica si la contraseña ingresada corresponde al examen corto o completo,
    y guarda en Session State la modalidad correspondiente.
    """
    config = load_config()

    if input_password == config.get("password_short", ""):
        st.session_state["exam_type"] = "short"
        return True
    elif input_password == config.get("password_full", ""):
        st.session_state["exam_type"] = "full"
        return True
    else:
        return False
