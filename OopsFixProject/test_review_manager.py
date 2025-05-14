# test_review_manager.py

from users.paid_user import PaidUser
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections

def run_test():
    user = PaidUser("alice")
    user.tokens = 10

    original = "He go to the market and buy apple."
    llm = LLMHandler()
    corrected = llm.correct_text(original)

    print("\n[LLM Suggested Correction]")
    print("Original:", original)
    print("Corrected:", corrected)

    final_text, tokens_spent = review_llm_corrections(user, original, corrected)
    print(f"Tokens left: {user.tokens}")

if __name__ == "__main__":
    run_test()
