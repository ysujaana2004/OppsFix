# users/paid_user.py

from users.user_base import User
import os 

class PaidUser(User):
    def __init__(self, username):
        super().__init__(username, user_type='paid')
        self.collaborators = set()
        self.saved_texts = []   # names or paths of saved texts

    def has_enough_tokens(self, required):
        return self.tokens >= required

    def charge_tokens(self, amount):
        self.tokens -= amount
        if self.tokens < 0:
            self.tokens = 0

    def submit_text(self, text):
        """
        Charges 1 token per word. If not enough tokens, charge penalty.
        """
        word_count = len(text.strip().split())
        if self.tokens >= word_count:
            self.charge_tokens(word_count)
            self.add_text_history(text)
            return True, "Text submitted successfully."
        else:
            penalty = self.tokens // 2
            self.charge_tokens(penalty)
            return False, f"Not enough tokens. Penalty of {penalty} tokens applied."

    def process_blacklisted_words(self, text, blacklisted_words):
        """
        Replaces blacklisted words and charges token per character.
        Returns (processed_text, total_penalty).
        """
        processed = text
        penalty = 0

        for word in blacklisted_words:
            if word in processed:
                masked = '*' * len(word)
                processed = processed.replace(word, masked)
                penalty += len(word)

        self.charge_tokens(penalty)
        return processed, penalty

    def apply_self_correction(self, original_text, corrected_text):
        """
        Charge 0.5 token per corrected word.
        """
        orig_words = original_text.split()
        corr_words = corrected_text.split()

        corrections = sum(1 for o, c in zip(orig_words, corr_words) if o != c)
        charge = int(corrections * 0.5)
        self.charge_tokens(charge)

        self.add_correction(original_text, corrected_text, method='self')
        return charge

    def accept_llm_correction(self, original_text, corrected_text, num_accepts):
        """
        Charge 1 token per accepted correction.
        """
        self.charge_tokens(num_accepts)
        self.add_correction(original_text, corrected_text, method='llm')

    def save_text_file(self, text, filename):
        """
        Save text to disk and charge 5 tokens.
        """
        path = os.path.join("data", "texts", filename)

        try:
            with open(path, "w") as f:
                f.write(text)
            self.charge_tokens(5)
            self.saved_texts.append(filename)
            return True, f"Text saved as {filename}. 5 tokens deducted."
        except Exception as e:
            return False, f"Failed to save file: {str(e)}"

    def invite_collaborator(self, username):
        """
        Track invited collaborators (actual logic elsewhere).
        """
        self.collaborators.add(username)

    def reject_invitation_penalty(self):
        self.charge_tokens(3)

    def add_bonus_tokens(self, amount=3):
        self.tokens += amount

    def overwrite_shared_file(self, filename, new_text):
        path = f"data/texts/{filename}"
        try:
            with open(path, 'w') as f:
                f.write(new_text)
            return True, f"Shared file '{filename}' updated successfully."
        except Exception as e:
            return False, f"Failed to update shared file: {e}"

