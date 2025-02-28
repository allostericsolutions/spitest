import json
import streamlit as st

def load_config():
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_password(input_password):
    """
    Verifica si la contraseña ingresada corresponde al examen corto o completo,
    y guarda en st.session_state la modalidad correspondiente.
    Ahora se revisa si la contraseña está dentro de los arrays de passwords
    definidos en config.json para cada modalidad.
    """
    config = load_config()
    
    # Verifica la modalidad corta
    if input_password in config.get("exam_short", {}).get("passwords", []):
        st.session_state["exam_type"] = "short"
        return True
    # Verifica la modalidad completa
    elif input_password in config.get("exam_full", {}).get("passwords", []):
        st.session_state["exam_type"] = "full"
        return True
    else:
        return False
