import json
import streamlit as st

def load_config():
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open('data/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def add_password(exam_type, new_password):
    """Añade una contraseña al tipo de examen especificado."""
    config = load_config()
    key = f"passwords_{exam_type}"
    if key in config:
        if new_password not in config[key]:  # Evitar duplicados
            config[key].append(new_password)
            save_config(config)
            st.success(f"Password '{new_password}' added for {exam_type} exam.")
        else:
            st.warning(f"Password '{new_password}' already exists for {exam_type} exam.")
    else:
        st.error(f"Invalid exam type: {exam_type}")

def remove_password(exam_type, password_to_remove):
    """Elimina una contraseña del tipo de examen especificado."""
    config = load_config()
    key = f"passwords_{exam_type}"
    if key in config:
        if password_to_remove in config[key]:
            config[key].remove(password_to_remove)
            save_config(config)
            st.success(f"Password '{password_to_remove}' removed from {exam_type} exam.")
        else:
            st.warning(f"Password '{password_to_remove}' not found for {exam_type} exam.")
    else:
        st.error(f"Invalid exam type: {exam_type}")

def get_passwords(exam_type):
    """Obtiene la lista de contraseñas para un tipo de examen."""
    config = load_config()
    key = f"passwords_{exam_type}"
    return config.get(key, [])
