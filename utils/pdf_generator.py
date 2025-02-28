from fpdf import FPDF
import os
import streamlit as st

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Generates a PDF file with the exam results:
    - User name and email
    - Score obtained
    - Status (Passed / Not Passed)
    - (Optionally) a breakdown by classification if present in st.session_state
    - (Optionally) intelligent explanations if present in st.session_state
    - (Optionally) user's photo if photo_path is provided
    Returns the path (filename) where the PDF was saved.
    """

    pdf = FPDF()
    pdf.add_page()

    # Título del PDF
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SPI - ARDMS Exam Result", ln=True, align='C')

    pdf.ln(10)

    # Datos del usuario
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Name: {user_data.get('nombre', '')}", ln=True)
    pdf.cell(0, 10, f"Email: {user_data.get('email', '')}", ln=True)

    # Foto opcional
    if photo_path and os.path.exists(photo_path):
        pdf.image(photo_path, x=10, y=pdf.get_y() + 5, w=30)
        pdf.ln(40)

    pdf.ln(5)

    # Resultado general
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Score: {score}", ln=True)
    pdf.cell(0, 10, f"Status: {status}", ln=True)

    pdf.ln(5)

    # ─────────────────────────────────────────────────
    # 1) DESGLOSE POR CLASIFICACIÓN (SI EXISTE)
    # ─────────────────────────────────────────────────
    classification_stats = st.session_state.get("classification_stats", None)
    if classification_stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Detailed Breakdown by Topic", ln=True)
        pdf.set_font("Arial", '', 12)

        for clasif, stats in classification_stats.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            percent = (correct / total * 100) if total > 0 else 0.0
            pdf.cell(0, 8, f"{clasif}: {percent:.2f}%", ln=True)

        pdf.ln(5)

    # ─────────────────────────────────────────────────
    # 2) EXPLICACIONES DE LA IA (SI EXISTEN)
    # ─────────────────────────────────────────────────
    explanations = st.session_state.get("explanations", None)
    if explanations:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Explanations & Feedback", ln=True)
        pdf.set_font("Arial", '', 11)

        for q_idx, exp_text in explanations.items():
            # q_idx usualmente es int o string con el índice de la pregunta
            # Mostramos como "Question X"
            question_number = int(q_idx) + 1 if str(q_idx).isdigit() else q_idx

            pdf.cell(0, 8, f"Question {question_number}", ln=True)
            # Usar multi_cell para que el texto se ajuste en varias líneas
            pdf.multi_cell(0, 6, exp_text)
            pdf.ln(4)

    # Crear carpeta "results" si no existe
    if not os.path.exists('results'):
        os.makedirs('results')

    # Nombrar el archivo PDF de acuerdo al email o algo distintivo
    filename = f"results/{user_data.get('email', 'unknown')}_result.pdf"
    pdf.output(filename)

    return filename

────────────────────────────────────────────────────────
3) COMPORTAMIENTO
────────────────────────────────────────────────────────
• Sin cambiar finalize_exam (ni la forma en que descargas el PDF), ahora generate_pdf() agrega dos secciones nuevas:  
  1. “Detailed Breakdown by Topic”: mostrando el porcentaje por cada clasificación.  
  2. “Explanations & Feedback”: listando cada pregunta incorrecta, con el texto devuelto por la IA (por ejemplo, “Concept to Study: Hand washing …”).  

• Si st.session_state.classification_stats o st.session_state.explanations no existen, se omiten esas secciones y no se rompe nada.  
• El botón de descarga sigue siendo el mismo, ya que finalize_exam llama generate_pdf y luego hace st.download_button con el path devuelto.

────────────────────────────────────────────────────────
4) RESULTADO EN EL PDF
────────────────────────────────────────────────────────
El PDF contendrá algo como:

----------------------------------------------------------------
SPI - ARDMS Exam Result  
(Name & Email)  

Score: 650  
Status: Passed  

Detailed Breakdown by Topic
• Basic Physics (Frequency…): 70.00%  
• Instruments (Transducers…): 85.00%  
• Doppler Physics…: 90.00%  
(etc.)

Explanations & Feedback
Question 1
Concept to Study: Hand washing
Hand washing is the most effective method
to prevent the spread of infections…

Question 5
Concept to Study: Shorter wavelength
(…resto de la explicación)

