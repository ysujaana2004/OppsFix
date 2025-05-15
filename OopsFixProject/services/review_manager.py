# services/review_manager.py

from services.llm_handler import LLMHandler

def review_llm_corrections(user, original_text, corrected_text):
    """
    Compare original and corrected text and return a list of changes for GUI display.
    Does NOT automatically apply any token deduction.
    """
    from difflib import SequenceMatcher

    original_words = original_text.strip().split()
    corrected_words = corrected_text.strip().split()

    matcher = SequenceMatcher(None, original_words, corrected_words)
    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ["replace", "delete", "insert"]:
            original_segment = " ".join(original_words[i1:i2])
            corrected_segment = " ".join(corrected_words[j1:j2])
            changes.append({
                "tag": tag,
                "original_start": i1,
                "original_end": i2,
                "corrected_start": j1,
                "corrected_end": j2,
                "from": original_segment,
                "to": corrected_segment
            })
    
    # Ignore words which are in whitelist (user marked as correct)
    if hasattr(user, "whitelist"):
        changes = [c for c in changes if c["from"] not in user.whitelist]

    # Return original, corrected, and diffs for GUI-based handling
    return {
        "original": original_text,
        "corrected": corrected_text,
        "diffs": changes
    }

