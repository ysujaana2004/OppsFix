# services/upgrade_manager.py

from users.paid_user import PaidUser

def upgrade_to_paid(free_user, token_amount=50):
    """
    Upgrades a FreeUser to a PaidUser by charging them a token amount.
    Returns a new PaidUser instance with the same username.
    """
    if free_user.user_type != 'free':
        return None, "User is already a paid user."

    if token_amount < 50:
        return None, "Minimum 50 tokens required for upgrade."

    # Create new PaidUser with initial tokens
    upgraded_user = PaidUser(free_user.username)
    upgraded_user.tokens = token_amount
    upgraded_user.text_history = free_user.text_history  # optional
    upgraded_user.corrections = free_user.corrections    # optional

    return upgraded_user, f"Successfully upgraded to paid with {token_amount} tokens."
