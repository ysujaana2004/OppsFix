from users.paid_user import PaidUser
from services.user_manager import save_user, load_user
from services.complaint_handler import ComplaintHandler

def test_complaint_flow():
    print("\n--- STEP 1: Set Up Users ---")
    alice = PaidUser("Alice")
    bob = PaidUser("Bob")
    alice.tokens = 20
    bob.tokens = 20
    save_user(alice)
    save_user(bob)

    print("Alice tokens:", alice.tokens)
    print("Bob tokens:", bob.tokens)

    handler = ComplaintHandler()

    print("\n--- STEP 2: Alice Files Complaint Against Bob ---")
    complaint_id = handler.file_complaint("Alice", "Bob", "shared_file.txt", "Edited the file without asking")
    print("Complaint ID:", complaint_id)

    print("\n--- STEP 3: Bob Responds to Complaint ---")
    success, msg = handler.respond_to_complaint(complaint_id, "I thought I had permission.")
    print("Response:", msg)

    print("\n--- STEP 4: SuperUser Reviews and Penalizes Bob ---")
    success, msg = handler.review_complaint(complaint_id, "Bob", 5)
    print("Review Result:", msg)

    print("\n--- STEP 5: Reload Bob to Check Tokens ---")
    updated_bob = load_user("Bob")
    print("Bob's tokens after penalty:", updated_bob.tokens)

    print("\n--- STEP 6: View Final Complaint Record ---")
    all_complaints = handler.get_all_complaints()
    print(all_complaints[complaint_id])

if __name__ == "__main__":
    test_complaint_flow()
