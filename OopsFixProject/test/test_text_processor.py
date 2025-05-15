# test_text_processor.py

from services.text_processor import TextProcessor

def test_text_processor():
    blacklist = ['bad', 'ugly', 'stupid']
    tp = TextProcessor(blacklist)

    text = "This is a bad example with ugly words and stupid ideas. Bad things are bad."
    print("[Original Text]")
    print(text)

    print("\n[Word Count]")
    print(tp.count_words(text))  # Should count total words

    print("\n[Blacklisted Masking]")
    masked_text, total_chars, found_words = tp.mask_blacklisted_words(text)
    print("Masked Text:", masked_text)
    print("Total Blacklisted Chars:", total_chars)
    print("Blacklisted Words Found:", found_words)

if __name__ == "__main__":
    test_text_processor()
