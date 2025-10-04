# utils/logger.py
import csv
import os
from datetime import datetime
import streamlit as st

def log_exam_activity(user_data, score, status):
    """
    Registra la actividad del examen en un archivo CSV.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file = os.path.join("logs", "exam_activity.csv")

    # Crea el archivo CSV y escribe el encabezado si no existe
    if not os.path.exists(log_file):
        with open(log_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Name", "Email", "Score", "Status", "Exam Type"])

    # Añade la información del examen actual
    with open(log_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        exam_type = st.session_state.get("exam_type", "unknown") # Obtener tipo de examen
        writer.writerow([timestamp, user_data.get('nombre', ''), user_data.get('email', ''), score, status, exam_type])
