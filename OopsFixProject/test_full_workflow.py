from users.paid_user import PaidUser
from services.token_manager import TokenManager
from services.text_processor import TextProcessor
from services.llm_handler import LLMHandler
from services.collaboration import CollaborationService
from services.complaint_handler import ComplaintHandler

def test_full_workflow():
    print("\n--- Creating Paid User ---")
    user = PaidUser("alice")
    user.tokens = 20
    tm = TokenManager(user)
    print(f"{user.username} starts with {user.tokens} tokens.")

    print("\n--- Submitting Text ---")
    text = "He go to the stupid market with bad idea."
    word_count = text.count(" ") + 1
    success, msg = tm.apply_text_submission_cost(word_count)
    print("Text submission:", msg)
    print("Tokens remaining:", user.tokens)

    print("\n--- Processing Blacklist ---")
    tp = TextProcessor(['stupid', 'bad'])
    masked, penalty, found = tp.mask_blacklisted_words(text)
    tm.apply_blacklist_penalty(penalty)
    print("Masked Text:", masked)
    print("Blacklist Penalty:", penalty)
    print("Tokens remaining:", user.tokens)

    print("\n--- LLM Correction ---")
    llm = LLMHandler()
    corrected = llm.correct_text(masked)
    diffs = llm.compare_texts(masked, corrected)
    accepts = sum(1 for _, _, changed in diffs if changed)
    tm.apply_llm_accept_cost(accepts)
    print("Original vs Corrected:")
    for orig, corr, changed in diffs:
        print(f"{orig} → {corr}   {'✗' if changed else '✓'}")
    print("Tokens remaining:", user.tokens)

    print("\n--- Inviting Collaborator ---")
    cs = CollaborationService()
    text_id = "text_full_001"
    success, msg = cs.invite_user(text_id, "alice", "bob")
    print("Invite result:", msg)

    print("\n--- Filing Complaint ---")
    ch = ComplaintHandler()
    cid = ch.file_complaint("alice", "bob", text_id, "Deleted a paragraph without asking.")
    print("Complaint filed:", cid)

    print("\n--- Responding to Complaint ---")
    ch.respond_to_complaint(cid, "I thought it was a mistake.")
    
    print("\n--- Super User Reviews Complaint ---")
    ch.review_complaint(cid, "bob", 3)
    print("Complaint resolved. (bob penalized 3 tokens)")

    print("\n--- Test Completed ---")
    print(f"Final token count for {user.username}:", user.tokens)

if __name__ == "__main__":
    test_full_workflow()
