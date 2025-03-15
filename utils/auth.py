import bcrypt
import streamlit as st

# CONTRASEÑA DE ADMIN *HARDCODEADA* (¡CAMBIAR ESTO!) Y CON HASHING
ADMIN_PASSWORD_HASHED = b'$2b$12$qRyAP.AsfK4hNp/8OSWbM.jODU.9Ekm/pAANAg/p.j7qXuzrA/rG.'  # Hash de 'admin_password'

def authenticate_admin(password):
    """
    Autentica al administrador (usando bcrypt para comparar hashes).
    """
    return bcrypt.checkpw(password.encode('utf-8'), ADMIN_PASSWORD_HASHED)

def admin_login_screen():
    """
    Pantalla de login para el administrador (ahora en la barra lateral).
    """
    st.sidebar.title("Admin Login")
    password = st.sidebar.text_input("Admin Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate_admin(password):
            st.session_state.admin_authenticated = True
            st.sidebar.success("Admin login successful.")  # Mensaje en la sidebar
            # No usamos st.rerun() aquí para evitar el parpadeo
        else:
            st.sidebar.error("Incorrect admin password.")  # Error en la sidebar
