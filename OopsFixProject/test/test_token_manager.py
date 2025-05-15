# test_token_manager.py

from users.paid_user import PaidUser
from services.token_manager import TokenManager

def test_token_manager():
    user = PaidUser("bob")
    user.tokens = 20
    tm = TokenManager(user)

    print("[Init] Tokens:", user.tokens)

    # Text submission test (15 words)
    print("[Submit Text] 15 words:", tm.apply_text_submission_cost(15))
    print("Remaining Tokens:", user.tokens)

    # Submission that should trigger penalty
    print("[Submit Text] 10 words (should fail):", tm.apply_text_submission_cost(10))
    print("Remaining Tokens:", user.tokens)

    # Add tokens
    print("[Bonus] Adding 5 tokens")
    tm.apply_bonus(5)
    print("Tokens after bonus:", user.tokens)

    # Blacklist penalty (8 chars)
    print("[Blacklist] Deduct 8 chars:", tm.apply_blacklist_penalty(8))
    print("Tokens after blacklist penalty:", user.tokens)

    # Self correction cost (4 words corrected)
    print("[Self Correction] 4 words:", tm.apply_self_correction_cost(4))
    print("Tokens after self correction:", user.tokens)

    # LLM acceptance (3 corrections accepted)
    print("[LLM Accept] 3 corrections:", tm.apply_llm_accept_cost(3))
    print("Tokens after LLM correction:", user.tokens)

    # Save file
    print("[Save] Deduct 5 tokens to save:")
    tm.apply_save_cost()
    print("Tokens after saving:", user.tokens)

    # Reckless invite
    print("[Invite Rejection Penalty]:")
    tm.apply_invite_rejection_penalty()
    print("Tokens after invite penalty:", user.tokens)

if __name__ == "__main__":
    test_token_manager()
