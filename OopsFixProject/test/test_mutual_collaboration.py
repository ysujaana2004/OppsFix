from services.collaboration import CollaborationService, get_all_shared_files
from users.paid_user import PaidUser
from services.user_manager import save_user, load_user
import os

def overwrite_shared_file(filename, new_text):
    path = f"data/texts/{filename}"
    try:
        with open(path, 'w') as f:
            f.write(new_text)
        return True, f"Shared file '{filename}' updated successfully."
    except Exception as e:
        return False, f"Failed to update shared file: {e}"

def read_shared_file(filename):
    path = f"data/texts/{filename}"
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def test_mutual_collab():
    print("\n--- STEP 1: Set up Khalid and Alice ---")
    khalid = PaidUser("Khalid")
    alice = PaidUser("Alice")
    filename = "mutual.txt"
    initial_text = "This is a shared file."
    with open(f"data/texts/{filename}", "w") as f:
        f.write(initial_text)
    khalid.saved_texts.append(filename)
    save_user(khalid)
    save_user(alice)

    print("\n--- STEP 2: Khalid invites Alice ---")
    cs = CollaborationService()
    cs._save_data({
        filename: {
            "owner": "Khalid",
            "collaborators": [
                {"username": "Alice", "status": "accepted"}  # simulate already accepted
            ]
        }
    })

    print("\n--- STEP 3: Check shared file visibility ---")
    print("Khalid sees:", get_all_shared_files("Khalid"))
    print("Alice sees:", get_all_shared_files("Alice"))

    print("\n--- STEP 4: Alice overwrites shared file ---")
    edited_text = "Alice was here."
    success, msg = overwrite_shared_file(filename, edited_text)
    print(msg)

    print("\n--- STEP 5: Khalid reads shared file again ---")
    content = read_shared_file(filename)
    print("File content:", content)

if __name__ == "__main__":
    test_mutual_collab()
