# admin_app.py
import streamlit as st
import pandas as pd
import json

# --- Lógica de autenticación (DUPLICADA desde app.py) ---
def load_config():
    """Carga la configuración desde config.json."""
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_password(input_password):
    """Verifica la contraseña del administrador (HARDCODEADA - NO RECOMENDADO)."""
    admin_password = "rogeliofontan14%"  # CAMBIA ESTO!!!
    return input_password == admin_password

def authentication_screen():
    """Pantalla de autenticación (simplificada)."""
    st.title("Admin Authentication")
    password = st.text_input("Enter the admin password:", type="password")
    if st.button("Login"):
        if verify_password(password):
            st.session_state.admin_authenticated = True
            st.success("Authentication successful.")
            st.rerun()
        else:
            st.error("Incorrect password.")

# --- Lógica de visualización del CSV ---
def admin_screen():
    """Muestra la tabla de registros."""
    st.title("Exam Activity Log")
    try:
        df = pd.read_csv("logs/exam_activity.csv")
        st.dataframe(df)
    except FileNotFoundError:
        st.write("No activity log found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- Función principal ---
def main():
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        authentication_screen()
    else:
        admin_screen()

if __name__ == "__main__":
    main()
