from services.blacklist_review_handler import BlacklistReviewHandler

def test_blacklist_submission():
    handler = BlacklistReviewHandler()

    print("\n--- STEP 1: User Submits a Word ---")
    username = "Khalid"
    word = "dumb"
    request_id = handler.submit_request(username, word)
    print(f"Request ID: {request_id} (word: '{word}') submitted by {username}")

    print("\n--- STEP 2: Superuser Views Pending Requests ---")
    pending = handler.get_pending_requests()
    for rid, r in pending.items():
        print(f"\nID: {rid}")
        print(f"User: {r['user']}")
        print(f"Word: {r['word']}")
        print(f"Status: {r['status']}")

    print("\n--- STEP 3: Superuser Resolves Request ---")
    approved = True  # Change to False to simulate rejection
    success, msg = handler.resolve_request(request_id, approved)
    print("Review Result:", msg)

    print("\n--- STEP 4: Check Final Blacklist ---")
    with open("data/blacklist.json", "r") as f:
        blacklist = f.read()
    print("Blacklist contents:", blacklist)

if __name__ == "__main__":
    test_blacklist_submission()