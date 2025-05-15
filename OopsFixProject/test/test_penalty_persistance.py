# test_penalty_persistence.py

from users.paid_user import PaidUser
from services.user_manager import save_user, load_user
from services.collaboration import CollaborationService, penalize_inviter_on_rejection
import os
import json

def test_penalty_persistence():
    print("\n--- STEP 1: Create Khalid with 50 tokens ---")
    khalid = PaidUser("Khalid")
    khalid.tokens = 50
    khalid.saved_texts = ["shared_file.txt"]
    save_user(khalid)

    print("Saved Khalid with 50 tokens.")

    print("\n--- STEP 2: Invite Alice ---")
    cs = CollaborationService()
    cs._save_data({
        "shared_file.txt": {
            "owner": "Khalid",
            "collaborators": [
                {"username": "Alice", "status": "pending"}
            ]
        }
    })

    print("Sent invite to Alice for shared_file.txt.")

    print("\n--- STEP 3: Simulate Alice rejecting invite ---")
    penalize_inviter_on_rejection("shared_file.txt")

    print("Penalty function called.")

    print("\n--- STEP 4: Reload Khalid and check token balance ---")
    khalid_reloaded = load_user("Khalid")
    print(f"Khalid's token count after rejection: {khalid_reloaded.tokens}")

if __name__ == "__main__":
    test_penalty_persistence()