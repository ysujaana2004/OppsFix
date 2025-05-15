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
    
def process_text_submission(user, text, blacklist):
    from services.token_manager import TokenManager

    # Step 1: Word count & enforce FreeUser limit
    words = text.strip().split()
    word_count = len(words)

    if user.user_type == 'free' and word_count > 20:
        return False, "Free users can only submit up to 20 words.", None

    # Step 2: Paid user token charge for word count
    if user.user_type == 'paid':
        tm = TokenManager(user)
        success, msg = tm.apply_text_submission_cost(word_count)
        if not success:
            return False, msg, None

    # Step 3: Blacklist replacement
    tp = TextProcessor(blacklist)
    masked_text, penalty, found = tp.mask_blacklisted_words(text)

    # Step 4: Deduct blacklist penalty (paid only)
    if user.user_type == 'paid':
        tm.apply_blacklist_penalty(penalty)

    # Step 5: Save to history
    user.add_text_history(masked_text)

    return True, f"Submission successful. {penalty} token penalty for blacklist words.", masked_text



