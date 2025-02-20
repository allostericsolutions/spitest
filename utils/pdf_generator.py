from fpdf import FPDF
import os

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Genera un archivo PDF con los resultados del examen:
    - Nombre y ID del usuario
    - Puntaje obtenido
    - Estado (Aprobado / No Aprobado)
    - (Opcional) La foto del usuario, si se provee la ruta en photo_path
    Retorna la ruta (filename) donde se guardó el PDF.
    """

    pdf = FPDF()
    pdf.add_page()

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Resultado del Examen SPI - ARDMS", ln=True, align='C')
    
    # Espacio entre líneas
    pdf.ln(10)

    # Datos del usuario
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Nombre: {user_data['nombre']}", ln=True)
    pdf.cell(0, 10, f"ID: {user_data['id']}", ln=True)

    # Agregar la foto si se proporcionó una ruta válida
    if photo_path and os.path.exists(photo_path):
        # Ajusta la posición e imprime la imagen del usuario
        pdf.image(photo_path, x=10, y=50, w=30)
        pdf.ln(40)  # Mover el cursor para evitar sobreposición
    
    pdf.ln(10)

    # Resultados del examen
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Puntaje: {score}", ln=True)
    pdf.cell(0, 10, f"Estado: {status}", ln=True)

    # Crear carpeta "results" si no existe
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Guardar el PDF
    filename = f"results/{user_data['id']}_resultado.pdf"
    pdf.output(filename)

    return filename
