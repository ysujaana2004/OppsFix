def correction_stats(original, corrected):
    """
    Returns statistics about corrections:
    - percent_words_changed: % of words changed
    - percent_chars_changed: % of characters changed
    """
    orig_words = original.strip().split()
    corr_words = corrected.strip().split()
    total_words = max(len(orig_words), len(corr_words))
    changed_words = sum(1 for o, c in zip(orig_words, corr_words) if o != c)
    # Account for added/removed words
    changed_words += abs(len(orig_words) - len(corr_words))

    percent_words_changed = (changed_words / total_words) * 100 if total_words else 0

    orig_chars = list(original)
    corr_chars = list(corrected)
    total_chars = max(len(orig_chars), len(corr_chars))
    changed_chars = sum(1 for o, c in zip(orig_chars, corr_chars) if o != c)
    changed_chars += abs(len(orig_chars) - len(corr_chars))

    percent_chars_changed = (changed_chars / total_chars) * 100 if total_chars else 0

    return {
        "percent_words_changed": round(percent_words_changed, 2),
        "percent_chars_changed": round(percent_chars_changed, 2),
        "words_changed": changed_words,
        "total_words": total_words,
        "chars_changed": changed_chars,
        "total_chars": total_chars
    }