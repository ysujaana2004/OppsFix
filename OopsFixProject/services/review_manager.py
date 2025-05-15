# services/review_manager.py

from services.llm_handler import LLMHandler

def review_llm_corrections(user, original_text, corrected_text):
    llm = LLMHandler(user.whitelist)
    diffs = llm.compare_texts(original_text, corrected_text)

    accepted_text = []
    tokens_used = 0
    changes = []

    for orig, corr, changed in diffs:
        if not changed or llm.is_whitelisted(orig):
            accepted_text.append(corr)
            continue

        print(f"\nSuggested Correction: {orig} → {corr}")
        decision = input("Accept this correction? (y/n): ").strip().lower()

        if decision == 'y':
            accepted_text.append(corr)
            tokens_used += 1
            changes.append({'from': orig, 'to': corr})
        else:
            reason = input("Reason for rejecting? (leave empty to skip): ").strip()
            save_to_whitelist = input(f"Add '{orig}' to whitelist? (y/n): ").strip().lower()
            if save_to_whitelist == 'y':
                llm.add_to_whitelist(orig)
                print(f"'{orig}' added to whitelist.")
            accepted_text.append(orig)

    # Token logic
    if user.user_type == 'paid':
        user.tokens -= tokens_used
        if user.tokens < 0:
            user.tokens = 0

    final_text = " ".join(accepted_text)

    # Bonus: ≥10 words, no edits
    if user.user_type == 'paid' and tokens_used == 0 and len(original_text.split()) >= 10:
        user.tokens += 3
        print("Bonus: No corrections needed. 3 tokens awarded.")

    user.corrections.append({
        'original': original_text,
        'corrected': final_text,
        'method': 'llm',
        'diffs': changes
    })

    print(f"\nReview complete. {tokens_used} tokens deducted.")
    print(f"Final Corrected Text:\n{final_text}\n")
    return final_text, tokens_used
