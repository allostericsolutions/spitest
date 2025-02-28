# utils/pdf_generator.py
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

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SPI - ARDMS Exam Result", ln=True, align='C')

    pdf.ln(10)

    # User data
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Name: {user_data.get('nombre', '')}", ln=True)
    pdf.cell(0, 10, f"Email: {user_data.get('email', '')}", ln=True)

    # Optional photo
    if photo_path and os.path.exists(photo_path):
        pdf.image(photo_path, x=10, y=pdf.get_y() + 5, w=30)
        pdf.ln(40)

    pdf.ln(5)

    # Score and status
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Score: {score}", ln=True)
    pdf.cell(0, 10, f"Status: {status}", ln=True)

    pdf.ln(5)

    # Classification breakdown (if any)
    classification_stats = st.session_state.get("classification_stats", None)
    if classification_stats:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Detailed Breakdown by Topic", ln=True)
        pdf.set_font("Arial", '', 12)

        for clasif, stats in classification_stats.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            if total > 0:
                percent = (correct / total) * 100
            else:
                percent = 0.0
            pdf.cell(0, 8, f"{clasif}: {percent:.2f}%", ln=True)

        pdf.ln(5)

    # Explanations (if any)
    explanations = st.session_state.get("explanations", None)
    if explanations:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Explanations & Feedback", ln=True)
        pdf.set_font("Arial", '', 11)

        for q_idx, exp_text in explanations.items():
            # Determine the question number
            if str(q_idx).isdigit():
                question_number = int(q_idx) + 1
            else:
                question_number = q_idx

            pdf.cell(0, 8, f"Question {question_number}", ln=True)
            pdf.multi_cell(0, 6, exp_text)
            pdf.ln(4)

    # Create the "results" folder if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")

    # Generate a filename based on the user's email (or 'unknown')
    file_name = f"{user_data.get('email', 'unknown')}_result.pdf"
    file_path = os.path.join("results", file_name)
    pdf.output(file_path)
    return file_path
