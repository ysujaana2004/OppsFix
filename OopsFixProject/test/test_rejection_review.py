from services.rejection_review_handler import RejectionReviewHandler

def test_rejection_review():
    handler = RejectionReviewHandler()

    print("\n--- STEP 1: Log a Rejection ---")
    user = "Khalid"
    original = "veery haapy"
    suggested = "very happy"
    reason = "I use this spelling as a poetic expression."

    rejection_id = handler.log_rejection(user, original, suggested, reason)
    print("Logged Rejection ID:", rejection_id)

    print("\n--- STEP 2: Fetch Pending Reviews ---")
    pending = handler.get_pending_reviews()
    for rid, entry in pending.items():
        print(f"\nID: {rid}")
        print(f"User: {entry['user']}")
        print(f"Original: {entry['original']} → Suggested: {entry['suggested']}")
        print(f"Reason: {entry['reason']}")
        print(f"Status: {entry['status']}")

    print("\n--- STEP 3: Superuser Resolves the Rejection ---")
    # Simulate approving the reason
    approved = True  # Change to False to test 5-token penalty
    success, penalty = handler.resolve_rejection(rejection_id, approved)
    print("Review Result:", "Approved" if approved else "Rejected")
    print("Assigned Penalty:", penalty)

    print("\n--- STEP 4: Re-check Status ---")
    final_state = handler.get_pending_reviews()
    print("Remaining Pending Reviews:", len(final_state))

if __name__ == "__main__":
    test_rejection_review()