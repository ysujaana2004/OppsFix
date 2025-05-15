# test_invite_rejection_penalty.py

from users.paid_user import PaidUser
from services.collaboration import CollaborationService, penalize_inviter_on_rejection

def test_penalty():
    inviter = PaidUser("Khalid")
    inviter.tokens = 20
    invitee = "Alice"
    text_id = "testfile.txt"

    print(f"[Before Rejection] Khalid tokens: {inviter.tokens}")

    # Simulate sending an invite
    cs = CollaborationService()
    cs._save_data({
        text_id: {
            "owner": inviter.username,
            "collaborators": [
                {"username": invitee, "status": "pending"}
            ]
        }
    })

    # Simulate rejection
    penalize_inviter_on_rejection(text_id)

    # Tokens in this context are not persisted across instances
    # So this will still show 20 unless you manage shared user state

    print(f"[After Rejection] Khalid tokens: {inviter.tokens} (note: won't reflect change unless state is shared)")

if __name__ == "__main__":
    test_penalty()
