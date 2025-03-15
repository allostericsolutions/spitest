import streamlit as st
import time
from utils.question_manager import select_random_questions, select_short_questions, shuffle_options
#from password_manager.manager import verify_password # COMENTAR/DESCOMENTAR PARA REVERTIR

def user_data_input():
    """
    Screen for user data input (name and email).
    """
    with st.form("user_form"):
        st.header("User Data")
        nombre = st.text_input("Full Name:")
        email = st.text_input("Email:")

        submitted = st.form_submit_button("Start Exam")
        if submitted:
            if nombre.strip() and email.strip():
                st.session_state.user_data = {
                    "nombre": nombre.strip(),
                    "email": email.strip()
                }
                st.success("Data registered. Preparing the exam...")

                # --- Selección de preguntas (directamente basada en exam_type) ---
                exam_type = st.session_state.get("exam_type", "full")  # Valor por defecto: "full"
                if exam_type == "short":
                    selected = select_short_questions(total=20)
                else:  # "full" o cualquier otro valor
                    selected = select_random_questions(total=120)
                # --- Fin de la selección de preguntas ---

                st.session_state.selected_questions = selected
                for q in st.session_state.selected_questions:
                    q['opciones'] = shuffle_options(q)

                st.session_state.answers = {str(i): None for i in range(len(st.session_state.selected_questions))}
                st.session_state.start_time = time.time()
                st.rerun()
            else:
                st.error("Please, complete all fields.")

# --- CÓDIGO ANTIGUO (COMENTADO, PARA REFERENCIA) ---
# Parte que se elimina/modifica si usas password_manager
#            exam_type_option = "full"  # Valor por defecto
#            if st.session_state.get("exam_type") == "admin":
#                exam_type_option = st.selectbox("Select Exam Type:", ["full", "short"])
#            if exam_type_option == "short":
#                selected = select_short_questions(total=20)
#            else:  # "full" o cualquier otro valor
#                selected = select_random_questions(total=120)

# --- VERSIÓN ANTERIOR COMPLETA (COMENTADA, PARA REVERSIÓN FÁCIL) ---
# import streamlit as st
# import time
# from utils.question_manager import select_random_questions, select_short_questions, shuffle_options

# def user_data_input():
#     """
#     Screen for user data input (name and email).
#     """
#     with st.form("user_form"):
#         st.header("User Data")
#         nombre = st.text_input("Full Name:")
#         email = st.text_input("Email:")

#         submitted = st.form_submit_button("Start Exam")
#         if submitted:
#             if nombre.strip() and email.strip():
#                 st.session_state.user_data = {
#                     "nombre": nombre.strip(),
#                     "email": email.strip()
#                 }
#                 st.success("Data registered. Preparing the exam...")

#                 # ───────────────────────────────────────────────
#                 # BLOQUE IMPORTANTE: SELECCIÓN DE MODO DE EXAMEN
#                 # ───────────────────────────────────────────────
#                 exam_type = st.session_state.get("exam_type", "full")
#                 if exam_type == "short":
#                     selected = select_short_questions
