import json

def load_config():
    """
    Carga el archivo 'config.json' y retorna su contenido
    como un diccionario de Python.
    """
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_password(input_password):
    """
    Verifica que la contraseña ingresada por el usuario (input_password)
    coincida con la contraseña guardada en 'config.json'.
    """
    config = load_config()
    return input_password == config.get("password", "")

def change_password(new_password):
    """
    Permite cambiar la contraseña guardada en 'config.json'.
    Esta función es opcional si más adelante quieres habilitar
    la opción de que un administrador modifique la contraseña.
    """
    config = load_config()
    config["password"] = new_password
    with open('data/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
