# editor.py

from blacklist import filter_blacklisted_words
from llm import correct_text
from user import PaidUser
import difflib
import math
import os

class Editor:
    def __init__(self, user):
        self.user = user

    def display_corrections(self):
        print("Correction History:")

        # Display accepted LLM suggestions
        if hasattr(self.user, 'accepted_corrections') and self.user.accepted_corrections:
            print("\n🔁 Accepted LLM Corrections:")
            for i, (orig, sugg) in enumerate(self.user.accepted_corrections, 1):
                print(f"{i}. \"{orig}\" → \"{sugg}\"")

        # Display full-text self-corrections
        if hasattr(self.user, 'corrections') and self.user.corrections:
            print("\n✍️ Self-Corrections (full document):")
            for i, (orig, sugg) in enumerate(self.user.corrections, 1):
                print(f"{i}. \"{orig}\" → \"{sugg}\"")

        # Nothing recorded
        if (not getattr(self.user, 'accepted_corrections', []) and
            not getattr(self.user, 'corrections', [])):
            print("No corrections recorded.")


    def self_correction_mode(self, original_text):
        """
        Lets the user manually correct their text.
        Charges 0.5 tokens per difference (rounded up).
        """
        print("\n✍️ Self-Correction Mode:")
        print("Original:\n", original_text)
        print("\nMake your corrections below:\n")

        corrected = input("Corrected Version:\n").strip()
        if not corrected:
            print("⚠️ No correction entered.")
            return original_text

        # Use difflib to count meaningful changes
        orig_words = original_text.strip().split()
        corr_words = corrected.strip().split()

        sm = difflib.SequenceMatcher(None, orig_words, corr_words)
        diffs = [tag for tag, _, _, _, _ in sm.get_opcodes() if tag != "equal"]
        num_changes = len(diffs)

        cost = math.ceil(num_changes * 0.5)

        if num_changes == 0:
            print("✅ No changes detected. No tokens charged.")
            return original_text

        if hasattr(self.user, 'token_manager'):
            if isinstance(self.user, PaidUser):
                if self.user.token_manager.deduct_tokens(cost):
                    self.user.record_correction(original_text, corrected)
                    print(f"✅ Self-correction accepted. {cost} tokens deducted.")
                    return corrected
                else:
                    print("❌ Not enough tokens for self-correction.")
                    return original_text
            else:
                # FreeUser: no deduction
                self.user.record_correction(original_text, corrected)
                print("✅ Self-correction accepted for FreeUser. No tokens deducted.")
                return corrected

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

                    # Store accepted correction
                    if hasattr(self.user, 'accepted_corrections'):
                        self.user.accepted_corrections.append((
                            " ".join(original_words[i1:i2]),
                            " ".join(corrected_words[j1:j2])
                        ))
                else:
                    final_output.extend(original_words[i1:i2])

        # Token deduction based on accepted suggestions
        if accepted_suggestions == 0:
            print("🚫 No suggestions accepted. No tokens deducted.")
            return text

        merged_text = " ".join(final_output)

        if isinstance(self.user, PaidUser):
            if self.user.token_manager.deduct_tokens(accepted_suggestions):
                self.user.record_correction(text, merged_text)
                print(f"\n✅ Final version saved. {accepted_suggestions} tokens deducted.")
                return merged_text
            else:
                print("❌ Not enough tokens. Changes discarded.")
                return text
        else:
            # FreeUser path: no charge
            self.user.record_correction(text, merged_text)
            print(f"\n✅ Final version saved for FreeUser. No tokens deducted.")
            return merged_text
        
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
    
    def save_text_to_file(self, text, filename="corrected_output.txt"):
        """
        Saves corrected text to a file if user has enough tokens.
        Costs 5 tokens.
        """
        if isinstance(self.user, PaidUser) and self.user.token_manager.deduct_tokens(5):
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"💾 Text saved to '{filename}'. 5 tokens deducted.")
                return True
            except Exception as e:
                print("❌ Failed to save file:", e)
                return False
        else:
            print("❌ Not enough tokens to save the file.")
            return False
        
    def free_user_workflow(self, text):
        """
        Handles FreeUser-only correction flow:
        - No token logic
        - No file saving
        - No submission charges
        """
        # Step 1: Check eligibility
        if not isinstance(self.user, FreeUser):
            print("❌ This flow is only for FreeUsers.")
            return

        # Step 2: Blacklist filtering
        filtered_text, cost = filter_blacklisted_words(text)
        print(f"\n🛡️ Filtered text:\n{filtered_text}")

        # Step 3: Offer correction method
        print("\nChoose correction mode:")
        print("1. LLM Correction")
        print("2. Self-Correction")
        mode = input("Enter choice (1/2): ").strip()

        if mode == "1":
            corrected = self.correct_with_llm(filtered_text)
        elif mode == "2":
            corrected = self.self_correction_mode(filtered_text)
        else:
            print("⚠️ Invalid input.")
            return

        # Final output
        print("\n📝 Final corrected text:\n", corrected)


if __name__ == "__main__":
    from user import PaidUser, FreeUser

    """
    print("🧪 Testing FreeUser\n")
    user = FreeUser("FreeGuy")
    editor = Editor(user)

    while True:
        text = input("\n🔤 Enter text (max 20 words, or 'exit' to quit):\n").strip()
        if text.lower() == "exit":
            break

        if user.can_submit(text):
            editor.free_user_workflow(text)
    """
    
    print("🧪 Testing Editor with PaidUser (100 tokens)\n")

    # Setup: PaidUser with 100 tokens
    user = PaidUser("TestUser", tokens=100)
    editor = Editor(user)

    # Prompt for text
    original_text = input("🔤 Enter your original text:\n")

    # Ask for correction mode
    print("\nChoose correction mode:")
    print("1. LLM Correction")
    print("2. Self-Correction")
    mode = input("Enter choice (1/2): ").strip()

    if mode == "1":
        corrected = editor.submit_and_correct(original_text)

        # Offer save
        save = input("\n💾 Save corrected text to file for 5 tokens? (y/n): ").strip().lower()
        if save == "y":
            filename = input("Enter filename (default: corrected_output.txt): ").strip() or "corrected_output.txt"
            editor.save_text_to_file(corrected, filename)

    elif mode == "2":
        corrected = editor.self_correction_mode(original_text)

        # Offer save
        save = input("\n💾 Save self-corrected text to file for 5 tokens? (y/n): ").strip().lower()
        if save == "y":
            filename = input("Enter filename (default: self_corrected.txt): ").strip() or "self_corrected.txt"
            editor.save_text_to_file(corrected, filename)

    else:
        print("⚠️ Invalid choice. Exiting.")

    # Show history and balance
    print("\n📚 Correction History:")
    editor.display_corrections()
    print(f"💰 Final token balance: {user.tokens}") 
    

