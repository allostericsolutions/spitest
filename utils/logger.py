# utils/logger.py
import os
from datetime import datetime
import streamlit as st # Importado por si acaso otras utilidades lo usaran, aunque no es estrictamente necesario para print()

def log_exam_activity(user_data, score, status):
    """
    Registra la actividad del examen imprimiéndola directamente en la consola.
    """
    # Obtener la marca de tiempo actual
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Obtener el tipo de examen del estado de la sesión
    exam_type = st.session_state.get("exam_type", "unknown")

    # Imprimir la información formateada en la consola
    print("\n--- EXAM LOG ENTRY ---")
    print(f"Timestamp: {timestamp}")
    # Usar .get() con un valor por defecto 'N/A' por si user_data estuviera incompleto
    print(f"Name: {user_data.get('nombre', 'N/A')}")
    print(f"Email: {user_data.get('email', 'N/A')}")
    print(f"Score: {score}")
    print(f"Status: {status}")
    print(f"Exam Type: {exam_type}")
    print("----------------------\n")
