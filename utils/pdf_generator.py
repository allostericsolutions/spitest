from fpdf import FPDF
import os

def generate_pdf(user_data, score, status, photo_path=None):
    """
    Generates a PDF file with the exam results:
    - User's name and ID
    - Score obtained
    - Status (Passed / Not Passed)
    - (Optional) The user's photo, if the path is provided in photo_path
    Returns the path (filename) where the PDF was saved.
    """

    pdf = FPDF()
    pdf.add_page()

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SPI - ARDMS Exam Result", ln=True, align='C') #Texto en ingles

    # Espacio entre líneas
    pdf.ln(10)

    # Datos del usuario
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Name: {user_data['nombre']}", ln=True) #Texto en ingles
    pdf.cell(0, 10, f"ID: {user_data['id']}", ln=True) #Texto en ingles

    # Agregar la foto si se proporcionó una ruta válida
    if photo_path and os.path.exists(photo_path):
        # Ajusta la posición e imprime la imagen del usuario
        pdf.image(photo_path, x=10, y=50, w=30)
        pdf.ln(40)  # Mover el cursor para evitar sobreposición

    pdf.ln(10)

    # Resultados del examen
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Score: {score}", ln=True) #Texto en ingles
    pdf.cell(0, 10, f"Status: {status}", ln=True) #Texto en ingles

    # Crear carpeta "results" si no existe
    if not os.path.exists('results'):
        os.makedirs('results')

    # Guardar el PDF
    filename = f"results/{user_data['id']}_result.pdf" #Texto en ingles
    pdf.output(filename)

    return filename
