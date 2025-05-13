class PaymentError(Exception):
    """Raised when a payment fails."""
    pass

class PaymentProcessor:
    """Very small, fake payment processor stub – always succeeds unless amount==0."""
    def charge(self, user_name: str, dollars: float) -> None:
        if dollars <= 0:
            raise PaymentError("Invalid payment amount.")
        # In a real system you’d integrate Stripe/PayPal/etc. Here we just print.
        print(f"💳 Charged ${dollars:.2f} to {user_name}’s card.")

def purchase_tokens(user, dollars: int, processor: PaymentProcessor = None) -> None:
    """Convert dollars to tokens 1‑for‑1 and credit them to the user."""
    processor = processor or PaymentProcessor()
    try:
        processor.charge(user.name, dollars)
        user.token_manager.add_tokens(dollars)
        print(f"✅ Added {dollars} tokens to {user.name}’s balance.")
    except PaymentError as e:
        print("🚫 Payment failed:", e)
