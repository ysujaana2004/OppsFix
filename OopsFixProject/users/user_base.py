# users/user_base.py

import time
import uuid

class User:
    def __init__(self, username, user_type):
        self.user_id = str(uuid.uuid4())       # unique identifier
        self.username = username
        self.user_type = user_type             # 'free', 'paid', or 'super'
        self.last_login_time = 0               # used for free user login delay
        self.tokens = 0                        # only relevant to paid users
        self.text_history = []                 # list of past submitted texts
        self.corrections = []                  # history of LLM/self corrections
        self.whitelist = set()

    def can_login(self):
        """
        Allow login if 3 minutes have passed since last login (for free users only).
        """
        if self.user_type != 'free':
            return True
        return (time.time() - self.last_login_time) > 180

    def login(self):
        """
        Record the login time.
        """
        self.last_login_time = time.time()

    def add_text_history(self, text):
        """
        Store submitted text in user history.
        """
        self.text_history.append(text)

    def add_correction(self, original, corrected, method):
        """
        Store a record of a correction made.
        """
        self.corrections.append({
            'original': original,
            'corrected': corrected,
            'method': method,  # 'llm' or 'self'
            'timestamp': time.time()
        })

    def get_stats(self):
        """
        Return basic user stats (can be extended).
        """
        return {
            'username': self.username,
            'user_type': self.user_type,
            'tokens': self.tokens,
            'texts_submitted': len(self.text_history),
            'corrections_made': len(self.corrections)
        }

