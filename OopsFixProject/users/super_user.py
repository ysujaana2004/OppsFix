# users/super_user.py

from users.user_base import User

class SuperUser(User):
    def __init__(self, username):
        super().__init__(username, user_type='super')
        self.review_queue = []         # pending blacklist or LLM rejections
        self.complaints_to_review = [] # complaint IDs (to be pulled from complaint system)

    def approve_paid_user(self, user):
        """
        Promote a user to 'paid' (external system will persist changes).
        """
        if user.user_type == 'free':
            user.user_type = 'paid'
            user.tokens = 20  # starter tokens or defined elsewhere
            return True
        return False

    def suspend_user(self, user):
        """
        Suspend a user (external system should enforce).
        """
        user.suspended = True  # must be checked before any user action
        return f"{user.username} has been suspended."

    def fine_user(self, user, amount):
        """
        Deduct tokens as a penalty.
        """
        user.tokens -= amount
        if user.tokens < 0:
            user.tokens = 0
        return f"{amount} tokens deducted from {user.username}."

    def terminate_user(self, user):
        """
        Mark user for termination (external system deletes data).
        """
        user.terminated = True
        return f"{user.username} marked for termination."

    def review_blacklist_suggestion(self, word, approve=True):
        """
        Decide whether to approve or deny a blacklist suggestion.
        """
        if approve:
            return {'action': 'add', 'word': word}
        else:
            return {'action': 'deny', 'word': word}

    def review_llm_rejection(self, reason, approve=True):
        """
        Determine if user's reason for rejecting LLM correction is valid.
        """
        return {'valid': approve}

    def review_complaint(self, complaint_id, punish_user, amount):
        """
        Decide who to punish in a complaint and how much.
        """
        return {
            'complaint_id': complaint_id,
            'punish': punish_user,
            'amount': amount
        }

