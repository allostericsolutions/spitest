# utils/pdf_generator.py
from fpdf import FPDF
import os
import streamlit as st
from datetime import datetime

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Permite usar {nb} para total de páginas en el footer
        self.alias_nb_pages()

    def header(self):
        """
        Se llama automáticamente al iniciar cada página.
        Desactivamos la marca de agua comentando el bloque correspondiente.
        """
        # EJEMPLO: CÓDIGO COMENTADO PARA SELLAR AGUA
        # if watermark_path and os.path.exists(watermark_path):
        #     x = 30
        #     y = 50
        #     w = 150
        #     self.image(watermark_path, x=x, y=y, w=w)
        pass  # No hacemos nada por ahora

    def footer(self):
        """
        Se llama automáticamente al finalizar cada página.
        Agregamos número de página y fecha/hora.
        """
        self.set_y(-15)  # A 15 mm del borde inferior
        self.set_font("Arial", 'I', 8)

        # Número de página
        page_text = f"Page {self.page_no()}/{{nb}}"
        self.cell(0, 5, page_text, align='C')

        # En la siguiente línea, la fecha/hora
        self.set_y(-10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 5, f"Generated on: {timestamp}", align='C')

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Genera un PDF con:
    - Nombre y email del usuario
    - Puntaje obtenido
    - Estado (Passed / Not Passed)
    - Tabla de desglose por clasificación (si existe)
    - "Concept to Study" (explanations) (si existe)
    - Numeración de páginas y fecha/hora en el footer
    - Marca de agua desactivada; reactivable en la clase CustomPDF (header)
    
    Retorna la ruta del archivo PDF generado.
    """

    # Instanciamos la clase que maneja headers/footers
    pdf = CustomPDF()
    pdf.add_page()

    # Título principal
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

    # Score y estado
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Score: {score}", ln=True)
    pdf.cell(0, 10, f"Status: {status}", ln=True)

    pdf.ln(5)

    # Desglose por clasificación (tabla)
    classification_stats = st.session_state.get("classification_stats", None)
    if classification_stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Detailed Breakdown by Topic", ln=True)
        pdf.set_font("Arial", '', 12)

        # Encabezados de la tabla
        pdf.cell(120, 8, "Classification", border=1, ln=0, align='C')
        pdf.cell(50, 8, "Percent (%)", border=1, ln=1, align='C')

        # Filas de la tabla
        for clasif, stats in classification_stats.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            percent = (correct/total)*100 if total > 0 else 0.0

            pdf.cell(120, 8, clasif, border=1, ln=0, align='L')
            pdf.cell(50, 8, f"{percent:.2f}%", border=1, ln=1, align='R')

        pdf.ln(5)

    # Explanations ("Concept to Study")
    explanations = st.session_state.get("explanations", None)
    if explanations:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Explanations & Feedback", ln=True)
        pdf.set_font("Arial", '', 11)

        for q_idx, exp_text in explanations.items():
            # Mostramos "Concept to Study <n>"
            if str(q_idx).isdigit():
                concept_number = int(q_idx) + 1
            else:
                concept_number = q_idx
            pdf.cell(0, 8, f"Concept to Study {concept_number}", ln=True)
            pdf.multi_cell(0, 6, exp_text)
            pdf.ln(4)

    # Creamos la carpeta de resultados si no existe
    if not os.path.exists("results"):
        os.makedirs("results")

    # Guardamos el PDF
    filename = f"{user_data.get('email', 'unknown')}_result.pdf"
    filepath = os.path.join("results", filename)
    pdf.output(filepath)

    return filepath
