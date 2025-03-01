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
        # Para usar en footer (total de páginas)
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
        page_text = f"Page {self.page_no()}/{''}"
        page_text = to_latin1(page_text)
        self.cell(0, 5, page_text, align='C')

        # Debajo, fecha/hora
        self.set_y(-10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp = to_latin1(timestamp)
        self.cell(0, 5, f"Generated on: ", align='C')

def _draw_classification_row(pdf: CustomPDF, classification: str, questions_asked: int, correct_answers: int, percent: float, feedback: str):
    """
    Dibuja una fila en la tabla de clasificación del PDF.
    """
    # Ajustes para la nueva tabla
    col_width_class = 70  # Reducido para dar espacio
    col_width_asked = 25
    col_width_correct = 25
    col_width_percent = 20
    col_width_feedback = 40 # Ajustado
    line_height = 6

    # Clasificación (con posible multilínea)
    wrapped_lines = textwrap.wrap(classification, width=25)  # Ajusta el ancho según sea necesario
    num_lines = max(1, len(wrapped_lines))
    total_height = num_lines * line_height

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    # Parte de clasificación (multilínea)
    for i, txt in enumerate(wrapped_lines):
        if i == 0:
            border_mode = "LTR" if num_lines > 1 else "LRB"
        elif i == num_lines - 1:
            border_mode = "LRB"
        else:
            border_mode = "LR"
        pdf.cell(col_width_class, line_height, txt, border=border_mode, ln=1 if i < num_lines -1 else 0, align='L')
        if i < num_lines -1:
          pdf.set_x(x_start)

    pdf.set_xy(x_start + col_width_class, y_start)


    # Preguntas hechas
    pdf.cell(col_width_asked, total_height, str(questions_asked), border="LTRB", align='C')

    # Respuestas correctas
    pdf.cell(col_width_correct, total_height, str(correct_answers), border="LTRB", align='C')

    # Porcentaje
    pdf.cell(col_width_percent, total_height, f"{percent:.2f}%", border="LTRB", align='C')

    # Feedback
    pdf.cell(col_width_feedback, total_height, feedback, border="LTRB", ln=1, align='C')
    #pdf.set_y(y_start + total_height) #Ya no es necesario.



def get_feedback(percent: float) -> str:
    """
    Devuelve el comentario de retroalimentación basado en el porcentaje.
    """
    if percent >= 95:
        return "Excellent"
    elif 80 <= percent <= 94:
        return "Satisfactory"
    elif 61 <= percent <= 79:
        return "May Require Further Study"
    elif percent <= 60:
        return "Requires Further Study"
    return "Unknown"  # En caso de un valor inesperado

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Genera el PDF (con tabla detallada, comentarios y puntajes).
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


    # --- Puntuaciones ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, to_latin1(f"Passing Score: 555"), ln=True)  # Passing Score fijo
    pdf.cell(0, 10, to_latin1(f"Your Score: {score}"), ln=True)  # Puntaje del usuario
    pdf.cell(0, 10, to_latin1(f"Status: {status}"), ln=True)  # Mostrar estado
    pdf.ln(5)


    # --- Desglose por Clasificación (Tabla Detallada) ---
    classification_stats = st.session_state.get("classification_stats")
    if classification_stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, to_latin1("Detailed Breakdown by Topic"), ln=True)

        # Encabezados de la tabla
        pdf.cell(70, 8, to_latin1("Classification"), border=1, ln=0, align='C')
        pdf.cell(25, 8, to_latin1("Questions Asked"), border=1, ln=0, align='C')
        pdf.cell(25, 8, to_latin1("Correct Answers"), border=1, ln=0, align='C')
        pdf.cell(20, 8, to_latin1("Percent"), border=1, ln=0, align='C')
        pdf.cell(40, 8, to_latin1("Feedback"), border=1, ln=1, align='C') #Aumente el ancho
        pdf.set_font("Arial", '', 12)

        total_questions_asked = 0
        total_correct_answers = 0

        for clasif, stats in classification_stats.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            percent = (correct / total) * 100 if total > 0 else 0.0
            feedback = get_feedback(percent)  # Obtener el comentario

            _draw_classification_row(pdf, clasif, total, correct, percent, feedback)

            total_questions_asked += total
            total_correct_answers += correct

        # Fila de totales
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(70, 8, to_latin1("TOTAL"), border=1, ln=0, align='C')
        pdf.cell(25, 8, str(total_questions_asked), border=1, ln=0, align='C')
        pdf.cell(25, 8, str(total_correct_answers), border=1, ln=0, align='C')
        total_percent = (total_correct_answers / total_questions_asked) * 100 if total_questions_asked > 0 else 0.0
        pdf.cell(20, 8, f"{total_percent:.2f}%", border=1, ln=0, align='C')
        pdf.cell(40, 8, get_feedback(total_percent), border=1, ln=1, align='C')


    pdf.ln(5)

    # --- Explicaciones y Feedback ---
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
            line_text = f". {to_latin1(exp_text)}"
            pdf.multi_cell(0, 6, line_text)
            pdf.ln(4)

    # Guardar PDF
    if not os.path.exists("results"):
        os.makedirs("results")
    file_name = f"{user_data.get('email', 'unknown')}_result.pdf"
    path = os.path.join("results", file_name)
    pdf.output(path)
    return path
