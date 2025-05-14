# services/text_processor.py

import re

class TextProcessor:
    def __init__(self, blacklist=None):
        self.blacklist = blacklist or []

    def set_blacklist(self, blacklist):
        self.blacklist = blacklist

    def count_words(self, text):
        words = text.strip().split()
        return len(words)

    def mask_blacklisted_words(self, text):
        masked_text = text
        total_chars = 0
        found_words = []

        for word in self.blacklist:
            pattern = r'\b' + re.escape(word) + r'\b'
            matches = list(re.finditer(pattern, masked_text, flags=re.IGNORECASE))

            if matches:
                found_words.append(word)
                count = len(matches)
                total_chars += len(word) * count
                masked_text = re.sub(pattern, '*' * len(word), masked_text, flags=re.IGNORECASE)

        return masked_text, total_chars, found_words


