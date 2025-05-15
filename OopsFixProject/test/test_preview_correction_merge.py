from services.review_manager import review_llm_corrections
from difflib import SequenceMatcher

def apply_corrections(original_text, diffs):
    """
    Applies the diffs to original_text safely by working backwards
    to prevent offset issues.
    """
    words = original_text.strip().split()
    for change in sorted(diffs, key=lambda d: d['original_start'], reverse=True):
        i1 = change['original_start']
        i2 = change['original_end']
        corrected_segment = change['to'].split()
        words[i1:i2] = corrected_segment

    return " ".join(words)

# === Example usage ===
original = "Hi, how you are? I am veery haapy today."
corrected = "Hey, how are you? I am very happy today."

result = review_llm_corrections(None, original, corrected)

print("\n[Original]")
print(original)

print("\n[Corrected by LLM]")
print(corrected)

print("\n[Diffs]")
for diff in result["diffs"]:
    print(f"- {diff['from']} → {diff['to']} ({diff['original_start']}–{diff['original_end']})")

final_text = apply_corrections(result["original"], result["diffs"])

print("\n[Reconstructed Final Text]")
print(final_text)
