from services.text_processor import process_text_submission
from services.user_manager import load_user
from services.blacklist_review_handler import BlacklistReviewHandler

def test_blacklist_filtering():
    # Load paid user (or create if needed)
    username = "Khalid"
    user = load_user(username)
    if not user:
        print("User not found.")
        return

    # Example word: one recently added to blacklist via approval
    test_sentence = "This idea is really Sujana and should be banned."

    print("\n[Original Text]")
    print(test_sentence)

    success, msg, masked = process_text_submission(user, test_sentence)

    print("\n[Submission Result]")
    print("Success:", success)
    print("Message:", msg)

    print("\n[Masked Output]")
    print(masked)

if __name__ == "__main__":
    test_blacklist_filtering()
