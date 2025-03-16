# utils/validators.py
import re

def es_correo_valido(correo):
    """Verifica si una cadena tiene formato de correo electrónico."""
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(patron, correo) is not None
