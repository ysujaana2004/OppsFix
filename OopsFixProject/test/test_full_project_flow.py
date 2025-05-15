# test_full_project_flow.py

from users.free_user import FreeUser
from services.upgrade_manager import upgrade_to_paid
from services.token_manager import TokenManager
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections
from services.self_correction import handle_self_correction
from services.text_processor import process_text_submission
import os

def run_full_flow():
    print("\n===== FREE USER FLOW =====")
    blacklist = ['go', 'store']

    # Step 1: Free user submits valid text
    free_user = FreeUser("bob")
    text = "He go to store quickly."
    success, msg, processed_text = process_text_submission(free_user, text, blacklist)
    print("Submit Result:", msg)
    print("Masked Text:", processed_text)

    # Step 2: LLM correction (no tokens)
    llm = LLMHandler()
    corrected = llm.correct_text(processed_text)
    print("LLM Suggestion:", corrected)
    final_text, tokens_used = review_llm_corrections(free_user, processed_text, corrected)
    print("LLM tokens used (should be 0):", tokens_used)

    # Step 3: Self-correction (no tokens)
    user_edit = "He goes to the store quickly."
    success, msg = handle_self_correction(free_user, processed_text, user_edit)
    print("Self-Correction Result:", msg)

    print("\n===== PAID USER FLOW =====")

    # Step 4: Upgrade user to paid
    paid_user, msg = upgrade_to_paid(free_user, 50)
    print(msg)
    tm = TokenManager(paid_user)

    # Step 5: Paid user submits new text
    text1 = "She go to school every day but not on weekend."
    success, msg, processed1 = process_text_submission(paid_user, text1, blacklist)
    print("Submit Result:", msg)
    print("Masked Text:", processed1)

    # Step 6: LLM correction
    corrected1 = llm.correct_text(processed1)
    print("LLM Suggestion:", corrected1)
    final_text1, tokens_used = review_llm_corrections(paid_user, processed1, corrected1)

    # Step 7: Save corrected text
    os.makedirs("data/texts", exist_ok=True)
    success, msg = paid_user.save_text_file(final_text1, "corrected_text1.txt")
    print("Save Result:", msg)

    # Step 8: Paid user submits another text
    text2 = "He go store buy apple juice"
    success, msg, processed2 = process_text_submission(paid_user, text2, blacklist)
    print("Submit Result:", msg)
    print("Masked Text:", processed2)

    # Step 9: Self-correction
    user_corrected2 = "He goes to the store and buys apple juice"
    success, msg = handle_self_correction(paid_user, processed2, user_corrected2)
    print("Self-correction Result:", msg)

    # Step 10: Save second corrected text
    success, msg = paid_user.save_text_file(user_corrected2, "self_corrected_text2.txt")
    print("Save Result:", msg)

    # Final Summary
    print("\n===== FINAL STATUS =====")
    print("Tokens Left:", paid_user.tokens)
    print("Correction History:")
    for c in paid_user.corrections:
        print(f"{c['method'].upper()} | From: {c['original']} → {c['corrected']}")
    print("Saved Files:")
    for fname in paid_user.saved_texts:
        print(fname)

if __name__ == "__main__":
    run_full_flow()