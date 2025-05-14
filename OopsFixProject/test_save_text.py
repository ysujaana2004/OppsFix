# test_save_text.py

from users.paid_user import PaidUser
import os

def test_save_text():
    user = PaidUser("alice")
    user.tokens = 10

    text_to_save = "This is a test document to be saved."
    filename = "test_saved_file.txt"

    # Ensure the target folder exists
    os.makedirs("data/texts", exist_ok=True)

    success, msg = user.save_text_file(text_to_save, filename)
    print(msg)

    # Check if file was written
    path = os.path.join("data", "texts", filename)
    if success and os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        print("File content:", content)
        print("Remaining tokens:", user.tokens)
    else:
        print("Failed to save or verify file.")

if __name__ == "__main__":
    test_save_text()