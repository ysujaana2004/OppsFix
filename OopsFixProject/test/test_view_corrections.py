# test_view_corrections.py

from users.paid_user import PaidUser
from services.self_correction import handle_self_correction
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections

def test_view_corrections():
    user = PaidUser("alice")
    user.tokens = 100

    # Simulate LLM correction
    original1 = "He go store."
    llm = LLMHandler()
    corrected1 = llm.correct_text(original1)
    review_llm_corrections(user, original1, corrected1)

    # Simulate self correction
    original2 = "She walk home"
    user_edit = "She walks home"
    handle_self_correction(user, original2, user_edit)

    # View stored corrections
    print("\n--- Correction History ---")
    for idx, entry in enumerate(user.corrections, 1):
        print(f"#{idx} | Method: {entry['method'].upper()}")
        print("Original:", entry['original'])
        print("Corrected:", entry['corrected'])
        if 'diffs' in entry and entry['diffs']:
            print("Individual Changes:")
            for d in entry['diffs']:
                print(f"  - {d['from']} → {d['to']}")
        print("---")

if __name__ == "__main__":
    test_view_corrections()