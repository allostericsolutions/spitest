# utils/pdf_generator.py
import os
import textwrap
import streamlit as st
from datetime import datetime
from fpdf import FPDF

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Permite usar {nb} en el footer para total de páginas
        self.alias_nb_pages()

    def header(self):
        """
        Desactivado el sello/marca de agua. 
        Descomentar si se desea en el futuro.
        """
        pass

    def footer(self):
        """
        Pie de página: número de página y fecha/hora.
        """
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        page_text = f"Page {self.page_no()}/{{nb}}"
        self.cell(0, 5, page_text, align='C')

        self.set_y(-10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cell(0, 5, f"Generated on: {timestamp}", align='C')

def _draw_classification_row(pdf, classification, percent, col_width_class=120, col_width_percent=50, line_height=6):
    """
    Imprime una fila con:
      - La clasificación (con posible salto de línea si es larga)
      - El porcentaje, todo en la misma 'fila' con bordes.
    
    Se consigue calculando las líneas que ocupa la clasificación (wrap), 
    y usando esa altura para ambas celdas de la fila.
    """
    # Usamos textwrap para partir el texto en líneas cortas (aprox 40-45 chars).
    wrapped_lines = textwrap.wrap(classification, width=45) 
    # (Ajusta 'width=45' según tu gusto y el col_width_class.)
    
    # Calculamos cuántas líneas resultado hay
    num_lines = max(1, len(wrapped_lines))
    # Altura total de la celda
    total_height = num_lines * line_height
    
    # Guardamos la posición actual (X, Y) para reencuadrar.
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    # CELDA DE CLASIFICACIÓN (multilínea simulada)
    # Ponemos borde SOLO a la izquierda y arriba/abajo, iremos línea por línea.
    pdf.set_font("Arial", '', 12)
    
    for i, txt in enumerate(wrapped_lines):
        # Para la primera línea, dibujamos full border top-left-right (si deseas),
        # pero para simplificar, usaremos border=”LR” en cada línea, 
        # y en la última usamos border=”LRB” (para el borde inferior).
        if i == 0:
            # Primera línea
            border_mode = "LTR" if num_lines == 1 else "LR"
        elif i == num_lines - 1:
            # Última línea
            border_mode = "LRB"
        else:
            # Líneas intermedias
            border_mode = "LR"

        # Imprimimos la línea
        pdf.cell(col_width_class, line_height, txt, border=border_mode, ln=1, align='L')

        # Movemos X al inicio, 
        pdf.set_x(x_start)

    # Volvemos al tope de la fila para colocar el porcentaje
    # pero la X se corre a la derecha de la primera columna.
    pdf.set_xy(x_start + col_width_class, y_start)

    # CELDA DE PORCENTAJE
    # Tiene la altura total igual a total_height. 
    # Si solo queremos 1 línea, la centramos verticalmente 
    # (aquí haremos una approach simple: top alignment).
    border_percent = "LTRB"  # Borde completo en una sola celda
    pdf.cell(col_width_percent, total_height, f"{percent:.2f}%", border=border_percent, ln=1, align='R')

    # Aseguramos que la siguiente escritura sea debajo de la fila
    pdf.set_y(y_start + total_height)

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Genera un PDF con:
    - Nombre y email del usuario
    - Score obtenido
    - Estado (Passed / Not Passed)
    - Tabla de clasificaciones (con wrap de texto en la col de clasificación)
    - "Concept to Study" enumerado (sin duplicar la frase)
    - Footer con # de pag y fecha/hora
    """
    pdf = CustomPDF()
    pdf.add_page()

    # Título
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

    # Score + Status
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Score: {score}", ln=True)
    pdf.cell(0, 10, f"Status: {status}", ln=True)
    pdf.ln(5)

    # Desglose por clasificación
    classification_stats = st.session_state.get("classification_stats", None)
    if classification_stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Detailed Breakdown by Topic", ln=True)
        
        # Cabecera de la tabla
        pdf.cell(120, 8, "Classification", border=1, ln=0, align='C')
        pdf.cell(50, 8, "Percent (%)", border=1, ln=1, align='C')

        # Filas
        for clasif, stats in classification_stats.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            percent = (correct / total)*100 if total > 0 else 0.0

            _draw_classification_row(pdf, clasif, percent, col_width_class=120, col_width_percent=50, line_height=6)

        pdf.ln(5)

    # Explanations ("Concept to Study")
    explanations = st.session_state.get("explanations", None)
    if explanations:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Explanations & Feedback", ln=True)
        pdf.set_font("Arial", '', 11)

        # Para evitar duplicar "Concept to Study", 
        # iremos enumerando con "3. Concept to Study: Bistable"
        for q_idx, exp_text in explanations.items():
            # Indice de la "pregunta"
            if str(q_idx).isdigit():
                concept_num = int(q_idx) + 1
            else:
                concept_num = q_idx  # Por si acaso

            # Reemplazamos la posibilidad de que el texto YA incluya "Concept to Study:" 
            # (opcional, si deseas)
            # exp_text = exp_text.replace("Concept to Study:", "").strip()

            # Ahora imprimimos "3. " + el texto
            # Ej: "3. Concept to Study: Bistable" 
            # Queda en una sola línea junto al contenido de exp_text
            full_text = f"{concept_num}. {exp_text}"

            pdf.multi_cell(0, 6, full_text)
            pdf.ln(4)

    # Carpeta results
    if not os.path.exists('results'):
        os.makedirs('results')

    # Guardar PDF
    filename = f"{user_data.get('email', 'unknown')}_result.pdf"
    filepath = os.path.join("results", filename)
    pdf.output(filepath)

    return filepath
