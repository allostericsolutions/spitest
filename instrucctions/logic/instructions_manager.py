def get_instructions_text():
    """
    Loads the Markdown file with the instructions
    and returns it as a string.
    """
    with open("instrucctions/instructions.md", "r", encoding="utf-8") as f:
        instrucciones = f.read()
    return instrucciones
