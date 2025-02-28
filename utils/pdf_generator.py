# utils/pdf_generator.py
import os
import textwrap
import streamlit as st
from datetime import datetime
from fpdf import FPDF

def to_latin1(s: str) -> str:
    """
    Reemplaza caracteres fuera de rango Latin-1
    por '?' para evitar UnicodeEncodeError.
    """
    return s.encode("latin-1", errors="replace").decode("latin-1")

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Para usar  en footer (total de páginas)
        self.alias_nb_pages()

    def header(self):
        """
        Header desactivado (sello de agua comentado).
        """
        pass

    def footer(self):
        """
        Pie de página con número de página y fecha/hora.
        """
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        # Número de página
        page_text = f"Page {self.page_no()}/{'{nb}'}"  # Asegúrate de que esté correcto
        page_text = to_latin1(page_text)
        self.cell(0, 5, page_text, align='C')

        # Debajo, fecha/hora
        self.set_y(-10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = to_latin1(timestamp)
        self.cell(0, 5, f"Generated on: ", align='C')

def _draw_classification_row(pdf: CustomPDF, classification: str, percent: float,
                             col_width_class: int = 120, col_width_percent: int = 50,
                             line_height: int = 6):
    """
    Imprime la clasificación y el porcentaje en la misma fila,
    partiendo en varias líneas si la clasificación es larga.
    """
    classification = to_latin1(classification)
    wrapped_lines = textwrap.wrap(classification, width=45)
    num_lines = max(1, len(wrapped_lines))
    total_height = num_lines * line_height

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    # Parte de clasificación (multilínea)
    for i, txt in enumerate(wrapped_lines):
        txt = to_latin1(txt)
        if i == 0:
            border_mode = "LTR" if num_lines > 1 else "LRB"
        elif i == num_lines - 1:
            border_mode = "LRB"
        else:
            border_mode = "LR"
        pdf.cell(col_width_class, line_height, txt, border=border_mode, ln=1, align='L')
        pdf.set_x(x_start)

    # Celda para el porcentaje
    pdf.set_xy(x_start + col_width_class, y_start)
    s_percent = f"{percent:.2f}%"
    s_percent = to_latin1(s_percent)
    pdf.cell(col_width_percent, total_height, s_percent, border="LTRB", ln=1, align='R')
    pdf.set_y(y_start + total_height)

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Genera el PDF (con agrupación de clasificaciones y explicaciones).
    """
    pdf = CustomPDF()
    pdf.add_page()

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, to_latin1("SPI - ARDMS Exam Result"), ln=True, align='C')
    pdf.ln(10)

    # Datos de usuario
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, to_latin1(f"Name: {user_data.get('nombre', '')}"), ln=True)
    pdf.cell(0, 10, to_latin1(f"Email: {user_data.get('email', '')}"), ln=True)

    # Foto (opcional)
    if photo_path and os.path.exists(photo_path):
        pdf.image(photo_path, x=10, y=pdf.get_y() + 5, w=30)
        pdf.ln(40)

    pdf.ln(5)

    # Score y Status
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, to_latin1(f"Score: "), ln=True)  # Mostrar puntaje
    pdf.cell(0, 10, to_latin1(f"Status: "), ln=True) # Mostrar estado
    pdf.ln(5)

    # --- Desglose por Clasificación (Agrupado) ---
    classification_stats = st.session_state.get("classification_stats")
    if classification_stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, to_latin1("Detailed Breakdown by Topic"), ln=True)

        pdf.cell(120, 8, to_latin1("Classification"), border=1, ln=0, align='C')
        pdf.cell(50, 8, to_latin1("Percent (%)"), border=1, ln=1, align='C')
        pdf.set_font("Arial", '', 12)

        grouped_classifications = {
            "Clinical safety, patient care and quality assurance": [
                "Patient care and new technology",
                "Safety and Risk Management and new tec"
            ],
            "physical principles": [
                "Basic Physics (Frequency, Wavelength, Period, and Propagation)",
                "Basic Physics Concepts, Wave Parameters, and Attenuation",
                "Wave Properties and Interactions with matter"
            ],
            "ultrasound transducers": [
                "Transducers, Resolution, and Image Formation."
            ],
            "imaging, principles and instrumentation": [
                "Image Display, Processing, and Artifacts",
                "Instruments (Transducers Construction and function; Image Settings and Display)",
                "Bioeffects, Spatial, Temporal Resolution"  # Confirmé que existe
            ],
            "doppler imaging concepts": [
                "Doppler Physics and Instrumentation",
                "Hemodynamics and Doppler Principles"
            ]
        }

        for group_name, sub_classifications in grouped_classifications.items():
            total_group_percent = 0.0  # Inicializar como float
            for sub_classif in sub_classifications:
                if sub_classif in classification_stats:
                    stats = classification_stats[sub_classif]
                    total = stats.get("total", 0)
                    correct = stats.get("correct", 0)
                    percent = (correct / total) * 100 if total > 0 else 0.0
                    total_group_percent += percent

            _draw_classification_row(pdf, group_name, total_group_percent)

    pdf.ln(5)

    # --- Explicaciones y Feedback (DEBE IR AQUÍ) ---
    explanations = st.session_state.get("explanations")
    if explanations:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, to_latin1("Explanations & Feedback"), ln=True)
        pdf.set_font("Arial", '', 11)

        for q_idx, exp_text in explanations.items():
            if str(q_idx).isdigit():
                concept_number = int(q_idx) + 1
            else:
                concept_number = q_idx
            line_text = f"{concept_number}. {to_latin1(exp_text)}" #Todo en una línea
            pdf.multi_cell(0, 6, line_text)
            pdf.ln(4)  # Espacio después de cada explicación



    # Guardar PDF
    if not os.path.exists("results"):
        os.makedirs("results")
    file_name = f"{user_data.get('email', 'unknown')}_result.pdf"
    path = os.path.join("results", file_name)
    pdf.output(path)
    return path
