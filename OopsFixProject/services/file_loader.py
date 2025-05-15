import os

def load_text_from_file(filepath):
    """
    Loads plain text from a file.
    :param filepath: Path to the .txt file
    :return: (success: bool, result: str or error message)
    """
    if not filepath or not os.path.exists(filepath):
        return False, "File not found."

    if not filepath.lower().endswith('.txt'):
        return False, "Only .txt files are supported."

    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return True, content
    except Exception as e:
        return False, f"Error reading file: {e}"
