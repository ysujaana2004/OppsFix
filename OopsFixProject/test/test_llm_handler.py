# test_llm_handler.py

from services.llm_handler import LLMHandler

def test_llm_handler():
    handler = LLMHandler()

    # Sample input with grammatical errors
    original = "She go to the market every weekends. They has many apple."
    print("[Original Text]")
    print(original)

    # Step 1: Get LLM correction
    corrected = handler.correct_text(original)
    print("\n[Corrected Text]")
    print(corrected)

    # Step 2: Compare corrections
    differences = handler.compare_texts(original, corrected)
    print("\n[Differences (word-by-word)]")
    for orig, corr, changed in differences:
        marker = "✓" if not changed else "✗"
        print(f"{orig} → {corr}   {marker}")

    # Step 3: Test whitelist
    print("\n[Whitelist Test]")
    test_word = "apple"
    print(f"Is '{test_word}' whitelisted before?:", handler.is_whitelisted(test_word))
    handler.add_to_whitelist(test_word)
    print(f"Is '{test_word}' whitelisted after?:", handler.is_whitelisted(test_word))

if __name__ == "__main__":
    test_llm_handler()
