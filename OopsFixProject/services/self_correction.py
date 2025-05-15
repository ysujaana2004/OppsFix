# services/self_correction.py

from difflib import SequenceMatcher

def compare_texts(original, corrected):
    """
    Returns the number of word-level corrections made by the user.
    """
    orig_words = original.strip().split()
    corr_words = corrected.strip().split()

    matcher = SequenceMatcher(None, orig_words, corr_words)
    changes = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            # Count modified words (only from original side)
            changes += (i2 - i1)

    return changes

def handle_self_correction(user, original, corrected):
    changed_words = compare_texts(original, corrected)
    if changed_words == 0:
        return False, "No corrections detected — no tokens deducted."

    charge = int(changed_words * 0.5) if user.user_type == 'paid' else 0
    if user.user_type == 'paid':
        user.tokens -= charge
        if user.tokens < 0:
            user.tokens = 0

    # Generate diffs
    orig_words = original.strip().split()
    corr_words = corrected.strip().split()
    diffs = []
    for o, c in zip(orig_words, corr_words):
        if o != c:
            diffs.append({'from': o, 'to': c})

    user.corrections.append({
        'original': original,
        'corrected': corrected,
        'method': 'self',
        'diffs': diffs
    })

    return True, f"{changed_words} words corrected. {charge} tokens deducted."

