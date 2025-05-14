# test_full_project_flow.py

from users.free_user import FreeUser
from services.upgrade_manager import upgrade_to_paid
from services.token_manager import TokenManager
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections
from services.self_correction import handle_self_correction
import os

def run_full_flow():
    print("\n--- Step 1: Create FreeUser ---")
    free_user = FreeUser("alice")

    long_text = "This is a deliberately long sentence that goes way beyond the twenty word limit set for free users so it should be rejected."

    success, msg = free_user.submit_text(long_text)
    print("Attempted long submission:", msg)

    print("\n--- Step 2: Upgrade to PaidUser with 50 tokens ---")
    paid_user, msg = upgrade_to_paid(free_user, 50)
    print(msg)
    print(f"User type: {paid_user.user_type}, Tokens: {paid_user.tokens}")

    tm = TokenManager(paid_user)

    print("\n--- Step 3: Submit a valid text ---")
    text1 = "She go to school every day but not on weekend."
    word_count = len(text1.split())
    success, msg = tm.apply_text_submission_cost(word_count)
    print("Submission result:", msg)

    print("\n--- Step 4: Use LLM to correct ---")
    llm = LLMHandler()
    corrected1 = llm.correct_text(text1)
    print("Original:", text1)
    print("LLM Correction:", corrected1)

    final_text1, tokens_used = review_llm_corrections(paid_user, text1, corrected1)

    print("\n--- Step 5: Save corrected text ---")
    os.makedirs("data/texts", exist_ok=True)
    success, msg = paid_user.save_text_file(final_text1, "corrected_text1.txt")
    print(msg)

    print("\n--- Step 6: Submit another text ---")
    text2 = "He go store buy apple juice"
    word_count = len(text2.split())
    success, msg = tm.apply_text_submission_cost(word_count)
    print("Submission result:", msg)

    print("\n--- Step 7: Self-correct ---")
    user_corrected2 = "He goes to the store and buys apple juice"
    success, msg = handle_self_correction(paid_user, text2, user_corrected2)
    print("Self-correction result:", msg)

    print("\n--- Step 8: Save self-corrected text ---")
    success, msg = paid_user.save_text_file(user_corrected2, "self_corrected_text2.txt")
    print(msg)

    print("\n--- Final Token Count ---")
    print(f"Tokens left: {paid_user.tokens}")

    print("\n--- Correction History ---")
    for c in paid_user.corrections:
        print(f"{c['method'].upper()} | From: {c['original']} | To: {c['corrected']}")

    print("\n--- Saved Files ---")
    for fname in paid_user.saved_texts:
        print(fname)

if __name__ == "__main__":
    run_full_flow()
