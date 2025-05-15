# test_self_correction.py

from users.paid_user import PaidUser
from services.self_correction import handle_self_correction

def test_self_edit():
    # Step 1: Create user
    user = PaidUser("alice")
    user.tokens = 10
    print(f"[Start] Tokens: {user.tokens}")

    # Step 2: Original vs corrected text
    original = "He go to the store and buy apple."
    user_edit = "He goes to the store and buys apples."

    # Step 3: Apply self-correction
    success, msg = handle_self_correction(user, original, user_edit)
    print(f"[Correction Result] {msg}")
    print(f"[End] Tokens: {user.tokens}")

    # Step 4: Confirm history update
    print("\n[Correction History]")
    for entry in user.corrections:
        print(f"Method: {entry['method']}")
        print(f"Original: {entry['original']}")
        print(f"Corrected: {entry['corrected']}")

if __name__ == "__main__":
    test_self_edit()
