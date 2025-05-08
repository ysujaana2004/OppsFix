import time
from token_manager import TokenManager
# General user class 
class User:
    def __init__(self, name):
        self.name = name
        self.corrections = []
        self.submissions = []

class FreeUser(User):
    def __init__(self, name):
        super().__init__(name)
        self.last_submission_time = 0

    def can_submit(self, text):
        word_count = len(text.split())

        # cannot submit text of more than 20 words
        if word_count > 20:
            print("❌ Free users can only submit up to 20 words.")
            return False
        
        # submissions must be 3 minutes apart
        current_time = time.time()
        if current_time - self.last_submission_time < 180:  # 3 minutes = 180 seconds
            print("You must wait 3 minutes between submissions.")
            return False

        self.last_submission_time = current_time
        return True

class PaidUser(User):
    def __init__(self, name, tokens=0):
        super().__init__(name)
        self.tokens = tokens
        self.token_manager = TokenManager(self)
        self.collaborators = []
        self.blacklist_suggestions = []
        self.borrowed_tokens = 0
        self.borrowed_time = None

    def has_enough_tokens(self, cost):
        return self.tokens >= cost

    def deduct_tokens(self, amount):
        if self.has_enough_tokens(amount):
            self.tokens -= amount
            return True
        print("❌ Not enough tokens!")
        return False

    def add_tokens(self, amount):
        self.tokens += amount

    def record_correction(self, original, corrected):
        self.corrections.append((original, corrected))
    
    def submit_text(self, text):
        word_count = len(text.split())

        if self.token_manager.has_tokens(word_count):
            self.token_manager.deduct_tokens(word_count)
            self.submissions.append(text)
            print(f"✅ Submitted. {word_count} tokens deducted.")
            return True
        else:
            penalty = self.token_manager.penalty_half_tokens()
            print(f"❌ Not enough tokens. Penalty applied: {penalty} tokens.")
            return False

    def save_file(self, text):
        if self.token_manager.deduct_tokens(5):
            print("✅ File saved (simulation).")
            return True
        print("❌ Not enough tokens to save.")
        return False

class SuperUser(PaidUser):
    def __init__(self, name, tokens=100):
        super().__init__(name, tokens)
        self.blacklist_suggestions = []

    def review_blacklist_word(self, word, approve=True):
        if approve:
            print(f"✅ Word '{word}' approved for blacklist.")
        else:
            print(f"❌ Word '{word}' rejected from blacklist.")


if __name__ == "__main__":
    # define a free user named Alice; check if she can submit short entry
    free = FreeUser("Alice")
    print(free.can_submit("Hi!"))
    print(free.can_submit("Hi! My name is Alice. This text submission is too long \
                          and I should not be allowed to submit it. Extra words to \
                          make sure it's really too long."))

    # define paid user Bob, check what he can do
    paid = PaidUser("Bob", 25)
    print(paid.tokens)
    paid.submit_text("This is a longer sentence. It is more than 20 words. \
                     But since Bob only has 25 tokens, we need.")
    paid.save_file("saved version")
    print(paid.tokens)

    
