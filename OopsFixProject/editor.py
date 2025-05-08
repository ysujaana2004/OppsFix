# editor.py

from blacklist import filter_blacklisted_words
from llm import correct_text
import difflib

class Editor:
    def __init__(self, user):
        self.user = user

    def display_corrections(self):
        """
        Displays user’s correction history
        """
        print("Correction History:")
        for i, (orig, corr) in enumerate(self.user.corrections):
            print(f"{i+1}. \"{orig}\" → \"{corr}\"")

    def accept_self_correction(self, original, corrected):
        """
        For manual (self) correction: applies, records, charges half-token per word changed
        """
        words_changed = len(corrected.split())  # rough approximation
        cost = words_changed // 2

        if hasattr(self.user, 'token_manager') and self.user.token_manager.deduct_tokens(cost):
            self.user.record_correction(original, corrected)
            print(f"Self-correction accepted. {cost} tokens deducted.")
            return True
        else:
            print("Not enough tokens to apply self-correction.")
            return False

    def correct_with_llm(self, text):
        """
        Performs LLM correction and interactively allows user to accept/reject each individual suggestion.
        Charges 1 token per accepted suggestion.
        """
        corrected = correct_text(text)

        # Check if there were zero corrections
        no_change = corrected.strip() == text.strip()
        word_count = len(text.strip().split())

        # If so, and word count > 10 → give bonus
        if no_change and word_count > 10:
            if hasattr(self.user, 'token_manager'):
                self.user.token_manager.add_tokens(3)
                print(f"No errors found! You earned a 3-token bonus.")
            return text  # No correction needed

        original_words = text.strip().split()
        corrected_words = corrected.strip().split()
        sm = difflib.SequenceMatcher(None, original_words, corrected_words)

        final_output = []
        accepted_suggestions = 0  # Track number of accepted changes

        print("\n Accept or Reject Corrections:")
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                final_output.extend(original_words[i1:i2])
            else:
                orig_snippet = " ".join(original_words[i1:i2])
                corr_snippet = " ".join(corrected_words[j1:j2])

                print(f"\n🔴 Original:   {orig_snippet or '[INSERT]'}")
                print(f"🟢 Suggestion: {corr_snippet or '[DELETE]'}")
                choice = input("✅ Accept this change? (y/n): ").strip().lower()
                while choice not in {"y", "n"}:
                    choice = input("Please enter 'y' or 'n': ").strip().lower()

                if choice == "y":
                    final_output.extend(corrected_words[j1:j2])
                    accepted_suggestions += 1  # Count this as an accepted change
                else:
                    final_output.extend(original_words[i1:i2])

        # Token deduction based on accepted suggestions
        if hasattr(self.user, 'token_manager'):
            if accepted_suggestions > 0:
                if self.user.token_manager.deduct_tokens(accepted_suggestions):
                    merged_text = " ".join(final_output)
                    self.user.record_correction(text, merged_text)
                    print(f"\n✅ Final version saved. {accepted_suggestions} tokens deducted.")
                    return merged_text
                else:
                    print("❌ Not enough tokens. Changes discarded.")
                    return text
            else:
                print("🚫 No suggestions accepted. No tokens deducted.")
                return text
        
    def submit_and_correct(self, text):
        """
        Complete flow: submission charge + blacklist filtering + LLM correction + token deductions.
        """

        word_count = len(text.strip().split())

        # Step 0: Submission cost (1 token per word)
        if hasattr(self.user, 'token_manager'):
            if not self.user.token_manager.deduct_tokens(word_count):
                print(f"❌ Submission failed. Requires {word_count} tokens, but you don’t have enough.")
                return text
            else:
                print(f"✅ Submission accepted. {word_count} tokens deducted.")

        # Step 1: Blacklist filtering
        filtered_text, blacklist_cost = filter_blacklisted_words(text)
        print(f" Filtered Text: {filtered_text}")
        print(f" Blacklist Token Cost: {blacklist_cost}")

        if blacklist_cost > 0:
            if not self.user.token_manager.deduct_tokens(blacklist_cost):
                print("❌ Not enough tokens for blacklist filtering.")
                return text

        # Step 2: LLM Correction
        return self.correct_with_llm(filtered_text)



if __name__ == "__main__":
    from user import PaidUser

    print(" OopsFix Editor Test\n")
    test_user = PaidUser("Bob", tokens=50)
    editor = Editor(test_user)

    text = input("Enter text to correct:\n")
    final = editor.submit_and_correct(text)

    print("\n Final Output:\n", final)
    print("Remaining tokens:", test_user.tokens)
    editor.display_corrections()
