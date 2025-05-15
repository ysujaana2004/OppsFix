# test_users.py

import time
from users.free_user import FreeUser
from users.paid_user import PaidUser
from users.super_user import SuperUser

def test_free_user():
    user = FreeUser("alice")
    print("[FreeUser] Initial login allowed:", user.can_login())
    user.login()
    print("[FreeUser] Login again immediately:", user.can_login())
    print("[FreeUser] Submitting short text:", user.submit_text("Hi there!"))
    print("[FreeUser] Submitting long text:", user.submit_text("This sentence contains more than twenty words and therefore should not be accepted by the system at all, right? This is definitely more than 20 words. It is a lot of words."))

def test_paid_user():
    user = PaidUser("bob")
    user.tokens = 10
    print("[PaidUser] Submitting 5-word text (should pass):", user.submit_text("Hello this is a test"))
    print("[PaidUser] Remaining tokens:", user.tokens)

    print("[PaidUser] Submitting 20-word text (should fail):", user.submit_text("word " * 20))
    print("[PaidUser] Remaining tokens after penalty:", user.tokens)

    print("[PaidUser] Processing blacklist words:")
    text, penalty = user.process_blacklisted_words("This is a bad word and another bad one", ["bad", "one"])
    print("Processed text:", text)
    print("Penalty:", penalty)
    print("Remaining tokens:", user.tokens)

def test_super_user():
    su = SuperUser("admin")
    paid = PaidUser("charlie")
    print("[SuperUser] Promote Free -> Paid:")
    paid.user_type = "free"
    su.approve_paid_user(paid)
    print("User type:", paid.user_type)
    print("Tokens after upgrade:", paid.tokens)

    print("[SuperUser] Fine PaidUser 5 tokens:")
    print(su.fine_user(paid, 5))
    print("Remaining tokens:", paid.tokens)

if __name__ == "__main__":
    test_free_user()
    print("\n" + "-"*40 + "\n")
    test_paid_user()
    print("\n" + "-"*40 + "\n")
    test_super_user()