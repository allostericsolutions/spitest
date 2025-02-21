import json

def load_config():
    """
    Loads the 'config.json' file and returns its content
    as a Python dictionary.
    """
    with open('data/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_password(input_password):
    """
    Verifies that the password entered by the user (input_password)
    matches the password saved in 'config.json'.
    """
    config = load_config()
    return input_password == config.get("password", "")

def change_password(new_password):
    """
    Allows changing the password saved in 'config.json'.
    This function is optional if you later want to enable
    the option for an administrator to modify the password.
    """
    config = load_config()
    config["password"] = new_password
    with open('data/config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
