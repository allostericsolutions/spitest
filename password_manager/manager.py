# password_manager/manager.py
import json
import streamlit as st
from datetime import datetime

# --- Constantes (podrían estar en constants.py) ---
CONFIG_PATH = 'data/config.json'
PASSWORDS_KEY = "passwords"
TYPE_KEY = "type"
ACTIVE_KEY = "active"
USED_KEY = "used"
EXPIRY_DATE_KEY = "expiry_date"
ADMIN_SHORT_TYPE = "admin_short"
ADMIN_FULL_TYPE = "admin_full"
SHORT_TYPE = "short"
FULL_TYPE = "full"
ADMIN_PASSWORD_KEY = "admin_password"

# --- Funciones de acceso a datos ---

def load_config():
    """Carga la configuración desde el archivo JSON."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Guarda la configuración en el archivo JSON."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

# --- Función de verificación de contraseña ---

def verify_password(input_password):
    """Verifica una contraseña y establece el tipo de examen."""
    config = load_config()
    passwords = config.get(PASSWORDS_KEY, {})

    if input_password in passwords:
        password_data = passwords[input_password]
        if password_data[ACTIVE_KEY]:
            if password_data[TYPE_KEY] == ADMIN_SHORT_TYPE:
                st.session_state["exam_type"] = SHORT_TYPE
                return True
            elif password_data[TYPE_KEY] == ADMIN_FULL_TYPE:
                st.session_state["exam_type"] = FULL_TYPE
                return True
            elif not password_data.get(USED_KEY, False):
                expiry_date_str = password_data.get(EXPIRY_DATE_KEY)
                if expiry_date_str:
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    if today <= expiry_date:
                        st.session_state["exam_type"] = password_data[TYPE_KEY]
                        return True
                    else:
                        return False
                else:
                    st.session_state["exam_type"] = password_data[TYPE_KEY]
                    return True
            else:
                return False
        else:
            return False
    else:
        return False

# --- Función para marcar como usada ---

def mark_password_as_used(password):
    """Marca una contraseña como usada."""
    config = load_config()
    if password in config[PASSWORDS_KEY]:
        config[PASSWORDS_KEY][password][USED_KEY] = True
        save_config(config)

# --- Funciones de la interfaz de administración ---
def admin_screen():
    """Pantalla de administración (simplificada)."""

    st.title("Password Administration")
    st.warning("Changes are saved immediately!")

    config = load_config()
    admin_password_attempt = st.text_input("Enter Admin Password:", type="password")

    if admin_password_attempt == config.get(ADMIN_PASSWORD_KEY):
        # --- Agregar nueva contraseña ---
        st.subheader("Add New Password")
        new_password = st.text_input("New Password")
        new_password_type = st.selectbox("Exam Type", [SHORT_TYPE, FULL_TYPE])
        add_button = st.button("Add Password")
        if add_button:
            if new_password:
                if new_password not in config[PASSWORDS_KEY]:
                    config[PASSWORDS_KEY][new_password] = {
                        TYPE_KEY: new_password_type,
                        ACTIVE_KEY: True,
                        USED_KEY: False,
                        EXPIRY_DATE_KEY: None  # O una fecha por defecto
                    }
                    save_config(config)
                    st.success(f"Password '{new_password}' added.")
                    st.rerun()
                else:
                    st.error("Password already exists.")
            else:
                st.error("Please enter a password.")

        # --- Mostrar y editar contraseñas existentes ---
        st.subheader("Manage Existing Passwords")
        passwords = config[PASSWORDS_KEY]
        for password, data in passwords.items():
            with st.container():  # Contenedor para cada fila
                col1, col2, col3,col4, col5 = st.columns([3,1,1,2,1]) #Más columnas
                with col1:
                    st.write(f"**{password}**")  # Contraseña en negrita

                with col2:
                    # Tipo no modificable para contraseñas de administrador
                    if data[TYPE_KEY] in (ADMIN_SHORT_TYPE, ADMIN_FULL_TYPE):
                        st.write(data[TYPE_KEY]) # Mostrar, pero no permitir edición
                    else:

                        # Selector para el tipo (short/full)
                        new_type = st.selectbox(
                            "Type",
                            [SHORT_TYPE, FULL_TYPE],
                            index=0 if data[TYPE_KEY] == SHORT_TYPE else 1,
                            key=f"type_{password}"
                        )
                        if new_type != data[TYPE_KEY]: #Si se ha cambiado
                            data[TYPE_KEY] = new_type
                            save_config(config) #Guardar
                            st.rerun()

                with col3:
                    # Checkbox para activar/desactivar
                     # Activo no modificable para contraseñas de administrador
                    if data[TYPE_KEY] in (ADMIN_SHORT_TYPE, ADMIN_FULL_TYPE):
                        st.write(data[ACTIVE_KEY])
                    else:
                        new_active = st.checkbox("Active", value=data[ACTIVE_KEY], key=f"active_{password}")
                        if new_active != data[ACTIVE_KEY]: #Si se ha cambiado
                            data[ACTIVE_KEY] = new_active
                            save_config(config) #Guardar
                            st.rerun()

                with col4:
                    # Campo para la fecha de expiración
                    # Expiración no modificable para contraseñas de administrador
                    if data[TYPE_KEY] in (ADMIN_SHORT_TYPE, ADMIN_FULL_TYPE):
                         st.write(data.get(EXPIRY_DATE_KEY, "Never"))
                    else:
                        expiry_date_str = data.get(EXPIRY_DATE_KEY)
                        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date() if expiry_date_str else None
                        new_expiry_date = st.date_input(
                            "Expiry Date",
                            value=expiry_date,
                            key=f"expiry_{password}",
                            format="YYYY-MM-DD"
                        )
                        #Si se ha cambiado y no es la fecha por defecto (evita errores)
                        if new_expiry_date != expiry_date and new_expiry_date is not None:
                            data[EXPIRY_DATE_KEY] = new_expiry_date.strftime("%Y-%m-%d")
                            save_config(config)
                            st.rerun() #Esto evita el error

                with col5:
                    # Checkbox para marcar como usada/no usada
                    # Used no modificable para contraseñas de administrador
                    if data[TYPE_KEY] in (ADMIN_SHORT_TYPE, ADMIN_FULL_TYPE):
                        st.write(data[USED_KEY])
                    else:
                        new_used = st.checkbox("Used", value=data[USED_KEY], key=f"used_{password}")
                        if new_used != data[USED_KEY]:
                            data[USED_KEY] = new_used
                            save_config(config)
                            st.rerun()

    else:
        if admin_password_attempt: #Evita mostrar siempre el error
            st.error("Incorrect Admin Password")
