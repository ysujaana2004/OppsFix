# services/token_manager.py

class TokenManager:
    def __init__(self, user):
        self.user = user

    def has_enough_tokens(self, amount):
        return self.user.tokens >= amount

    def deduct(self, amount):
        self.user.tokens -= amount
        if self.user.tokens < 0:
            self.user.tokens = 0

    def add(self, amount):
        self.user.tokens += amount

    def apply_text_submission_cost(self, word_count):
        if self.user.tokens >= word_count:
            self.deduct(word_count)
            return True, "Tokens deducted for submission."
        else:
            penalty = self.user.tokens // 2
            self.deduct(penalty)
            return False, f"Not enough tokens. Penalty of {penalty} tokens applied."

    def apply_blacklist_penalty(self, blacklisted_chars):
        self.deduct(blacklisted_chars)
        return blacklisted_chars

    def apply_self_correction_cost(self, corrected_words):
        cost = int(corrected_words * 0.5)
        self.deduct(cost)
        return cost

    def apply_llm_accept_cost(self, num_accepts):
        self.deduct(num_accepts)
        return num_accepts

    def apply_save_cost(self):
        self.deduct(5)

    def apply_invite_rejection_penalty(self):
        self.deduct(3)

    def apply_bonus(self, amount=3):
        self.add(amount)

    def purchase_tokens(self, amount):
        if amount <= 0:
            return False, "Invalid token amount."
        
        self.add(amount)
        return True, f"{amount} tokens purchased successfully."

