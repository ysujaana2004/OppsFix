# services/text_processor.py

import re
import json
import time
from services.user_manager import save_user

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
    
def load_blacklist():
    try:
        with open("data/blacklist.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

def process_text_submission(user, text):
    words = text.strip().split()
    word_count = len(words)

    # Free user word limit check
    if user.user_type == "free" and word_count > 20:
        user.last_login_time = time.time()
        save_user(user)
        return False, "Free users can only submit up to 20 words. You’ve been logged out for 3 minutes.", None

    is_paid = user.user_type == "paid"
    blacklist = load_blacklist()
    masked_text = []
    penalty = 0

    if is_paid:
        if user.tokens < word_count:
            penalty = user.tokens // 2
            user.tokens -= penalty
            save_user(user)
            return False, f"Not enough tokens to submit ({word_count} needed). {penalty} tokens deducted as penalty.", None
        else:
            user.tokens -= word_count  # base cost: 1 token per word

    for word in words:
        clean = word.strip('.,!?')
        if clean.lower() in blacklist:
            masked_word = '*' * len(clean)
            penalty += len(clean) if is_paid else 0
            masked_text.append(word.replace(clean, masked_word))
        else:
            masked_text.append(word)

    final_text = " ".join(masked_text)

    if is_paid:
        if user.tokens < penalty:
            return False, "Not enough tokens for blacklisted words.", final_text
        user.tokens -= penalty
        save_user(user)

    return True, f"Text submitted successfully. Penalty: {penalty} tokens for blacklist.", final_text




