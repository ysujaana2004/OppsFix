# test_token_purchase.py

from users.paid_user import PaidUser
from services.token_manager import TokenManager

def test_token_purchase():
    user = PaidUser("alice")
    user.tokens = 5
    tm = TokenManager(user)

    print(f"[Start] Tokens: {user.tokens}")

    print("\n[Attempting Valid Purchase]")
    success, msg = tm.purchase_tokens(20)
    print(msg)
    print("Tokens after purchase:", user.tokens)

    print("\n[Attempting Invalid Purchase (negative)]")
    success, msg = tm.purchase_tokens(-10)
    print(msg)
    print("Tokens after failed purchase:", user.tokens)

if __name__ == "__main__":
    test_token_purchase()
