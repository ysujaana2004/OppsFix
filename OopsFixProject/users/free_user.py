# users/free_user.py

from users.user_base import User

class FreeUser(User):
    def __init__(self, username):
        super().__init__(username, user_type='free')

    def can_submit_text(self, text):
        """
        Returns True if the text is within 20 words.
        """
        word_count = len(text.strip().split())
        return word_count <= 20

    def submit_text(self, text):
        """
        Validates and submits the text if allowed.
        """
        if not self.can_submit_text(text):
            return False, "Submission failed: Free users can only submit texts with up to 20 words."
        
        self.add_text_history(text)
        return True, "Text submitted successfully."

    def suggest_blacklist_word(self, word):
        """
        Submit a word for blacklist review.
        """
        return {
            'suggested_word': word,
            'user': self.username
        }

