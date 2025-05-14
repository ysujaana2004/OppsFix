# services/review_manager.py

from services.llm_handler import LLMHandler

def review_llm_corrections(user, original_text, corrected_text):
    """
    Interactive CLI to step through each LLM-suggested correction.
    Deducts tokens for accepted changes, updates user history and whitelist.
    """
    llm = LLMHandler(user.whitelist)
    diffs = llm.compare_texts(original_text, corrected_text)

    accepted_text = []
    tokens_used = 0

    for orig, corr, changed in diffs:
        if not changed or llm.is_whitelisted(orig):
            accepted_text.append(corr)
            continue

        print(f"\nSuggested Correction: {orig} → {corr}")
        decision = input("Accept this correction? (y/n): ").strip().lower()

        if decision == 'y':
            accepted_text.append(corr)
            tokens_used += 1
        else:
            reason = input("Reason for rejecting? (leave empty to skip): ").strip()
            save_to_whitelist = input(f"Add '{orig}' to whitelist? (y/n): ").strip().lower()
            if save_to_whitelist == 'y':
                llm.add_to_whitelist(orig)
                print(f"'{orig}' added to whitelist.")
            accepted_text.append(orig)

    # Deduct tokens and update correction history
    user.tokens -= tokens_used
    if user.tokens < 0:
        user.tokens = 0

    final_text = " ".join(accepted_text)
    user.add_correction(original_text, final_text, method='llm')

    print(f"\nReview complete. {tokens_used} tokens deducted.")
    print(f"Final Corrected Text:\n{final_text}\n")
    return final_text, tokens_used
