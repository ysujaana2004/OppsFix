import time

class TokenManager:
    def __init__(self, user):
        self.user = user
    
    # access tokens
    def get_tokens(self):
        return self._tokens

    # check if user has <cost> tokens
    def has_tokens(self, cost):
        return self.user.tokens >= cost

    # deduct cost tokens if user has enough
    def deduct_tokens(self, cost):
        if self.has_tokens(cost):
            self.user.tokens -= cost
            return True
        return False

    def add_tokens(self, amount):
        self.user.tokens += amount

    # deduct half the user's tokens
    def penalty_half_tokens(self):
        penalty = self.user.tokens // 2
        self.user.tokens -= penalty
        return penalty

    def emergency_borrow(self):
        # check if user alreadu has borrowed tokens
        if hasattr(self.user, "borrowed_tokens") and self.user.borrowed_tokens > 0:
            print("⚠️ Already borrowed tokens. Repay before borrowing again.")
            return False
        # otherwise, give user emergency tokens
        self.user.tokens += 10
        self.user.borrowed_tokens = 10
        self.user.borrowed_time = time.time()
        print("Borrowed 10 emergency tokens.")
        return True

    def repay_borrowed_tokens(self):
        if getattr(self.user, "borrowed_tokens", 0) > 0:
            if self.user.tokens >= self.user.borrowed_tokens:
                self.user.tokens -= self.user.borrowed_tokens
                self.user.borrowed_tokens = 0
                print("✅ Borrowed tokens repaid.")
                return True
            else:
                print("❌ Not enough tokens to repay.")
        return False

    def check_borrow_timeout(self):
        if hasattr(self.user, "borrowed_time"):
            elapsed = time.time() - self.user.borrowed_time
            if elapsed > 48 * 3600:  # 48 hours
                print("❌ Borrowed tokens not repaid in time. Access restricted.")
                self.user.tokens = 0  # or you could flag this account as restricted


if __name__ == "__main__":
    # Quick and dirty test
    class DummyUser:
        def __init__(self):
            self.tokens = 10

    user = DummyUser()
    tm = TokenManager(user)

    print("Before:", user.tokens)
    tm.deduct_tokens(3)
    print("After:", user.tokens)  # Should be 7

