from blacklist import filter_blacklisted_words
from llm import correct_text
from user import PaidUser, FreeUser
import difflib
import math
import os

class Editor:
    def __init__(self, user):
        self.user = user


    # corrections logic for incorporation into GUI
    def get_llm_corrections(self, text):
        """
        Returns:
            - filtered_text: text after blacklist replacement
            - corrections: list of tuples (original, corrected, i1, i2)
            - final_suggestion: entire corrected version for preview
        """

        filtered_text, _ = filter_blacklisted_words(text)
        original_words = filtered_text.strip().split()
        corrected_text = correct_text(filtered_text)
        corrected_words = corrected_text.strip().split()

        sm = difflib.SequenceMatcher(None, original_words, corrected_words)
        corrections = []
        final_output = []

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                final_output.extend(original_words[i1:i2])
            else:
                orig = " ".join(original_words[i1:i2]) or "[INSERT]"
                corr = " ".join(corrected_words[j1:j2]) or "[DELETE]"
                final_output.extend(corrected_words[j1:j2])
                corrections.append((orig, corr, i1, i2))

        merged_text = " ".join(final_output)
        return filtered_text, corrections, merged_text

    def display_corrections(self):
        print("Correction History:")

        # Display accepted LLM suggestions
        if hasattr(self.user, 'accepted_corrections') and self.user.accepted_corrections:
            print("\n🔁 Accepted LLM Corrections:")
            for i, (orig, sugg) in enumerate(self.user.accepted_corrections, 1):
                print(f"{i}. \"{orig}\" → \"{sugg}\"")
            print("\n📝 Final Corrected Texts:")
            for i, doc in enumerate(self.user.final_texts, 1):
                print(f"\n{i}. {doc}")

        # Display full-text self-corrections
        if hasattr(self.user, 'corrections') and self.user.corrections:
            print("\n✍️ Self-Corrections (full document):")
            for i, (orig, sugg) in enumerate(self.user.corrections, 1):
                print(f"{i}. \"{orig}\" → \"{sugg}\"")

        if (not getattr(self.user, 'accepted_corrections', []) and
            not getattr(self.user, 'corrections', [])):
            print("No corrections recorded.")

    def self_correction_mode(self, original_text):
        print("\nSelf-Correction Mode:")
        print("Original:\n", original_text)
        print("\nMake your corrections below:\n")

        corrected = input("Corrected Version:\n").strip()
        if not corrected:
            print("⚠️ No correction entered.")
            return original_text

        orig_words = original_text.strip().split()
        corr_words = corrected.strip().split()
        sm = difflib.SequenceMatcher(None, orig_words, corr_words)
        diffs = [tag for tag, _, _, _, _ in sm.get_opcodes() if tag != "equal"]
        num_changes = len(diffs)
        cost = math.ceil(num_changes * 0.5)

        if num_changes == 0:
            print("✅ No changes detected. No tokens charged.")
            return original_text

        if isinstance(self.user, PaidUser):
            if self.user.token_manager.deduct_tokens(cost):
                self.user.record_correction(original_text, corrected)
                if hasattr(self.user, 'final_texts'):
                    self.user.final_texts.append(corrected)
                print(f"✅ Self-correction accepted. {cost} tokens deducted.")
                print("\n📝 Final Corrected Text:\n", corrected)
                return corrected
            else:
                print("❌ Not enough tokens for self-correction.")
                return original_text
        else:
            self.user.record_correction(original_text, corrected)
            if hasattr(self.user, 'final_texts'):
                self.user.final_texts.append(corrected)
            print("✅ Self-correction accepted for FreeUser. No tokens deducted.")
            print("\n📝 Final Corrected Text:\n", corrected)
            return corrected

    def correct_with_llm(self, text):
        corrected = correct_text(text)
        no_change = corrected.strip() == text.strip()
        word_count = len(text.strip().split())

        if no_change and word_count > 10 and isinstance(self.user, PaidUser):
            self.user.token_manager.add_tokens(3)
            print("🎉 No errors found! You earned a 3-token bonus.")
            return text

        original_words = text.strip().split()
        corrected_words = corrected.strip().split()
        sm = difflib.SequenceMatcher(None, original_words, corrected_words)

        final_output = []
        accepted_suggestions = 0

        print("\nAccept or Reject Corrections:")
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
                    accepted_suggestions += 1
                    if hasattr(self.user, 'accepted_corrections'):
                        self.user.accepted_corrections.append((orig_snippet, corr_snippet))
                else:
                    final_output.extend(original_words[i1:i2])

        if accepted_suggestions == 0:
            print("🚫 No suggestions accepted. No tokens deducted.")
            return text

        merged_text = " ".join(final_output)

        if hasattr(self.user, 'final_texts'):
            self.user.final_texts.append(merged_text)

        if isinstance(self.user, PaidUser):
            if self.user.token_manager.deduct_tokens(accepted_suggestions):
                print(f"✅ Final version saved. {accepted_suggestions} tokens deducted.")
                print("\n📝 Final Corrected Text:\n", merged_text)
                return merged_text
            else:
                print("❌ Not enough tokens. Changes discarded.")
                return text
        else:
            print("✅ Final version saved for FreeUser. No tokens deducted.")
            print("\n📝 Final Corrected Text:\n", merged_text, '\n')
            return merged_text


    def save_text_to_file(self, text, filename="corrected_output.txt"):
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

    def submit_text_and_choose_correction(self, text):
        word_count = len(text.strip().split())
        if isinstance(self.user, PaidUser):
            if not self.user.token_manager.deduct_tokens(word_count):
                print(f"❌ Submission failed. Requires {word_count} tokens.")
                return text
            print(f"✅ Submission accepted. {word_count} tokens deducted.")

        # Step 1: Blacklist filtering
        filtered_text, blacklist_cost = filter_blacklisted_words(text)
        print(f"🛡️ Filtered Text:\n{filtered_text}")
        print(f"🪙 Blacklist Token Cost: {blacklist_cost}")

        if isinstance(self.user, PaidUser) and blacklist_cost > 0:
            if not self.user.token_manager.deduct_tokens(blacklist_cost):
                print("❌ Not enough tokens for blacklist filtering.")
                return text

        # Step 2: Choose correction mode
        print("\nChoose correction mode:")
        print("1. LLM Correction")
        print("2. Self-Correction")
        mode = input("Enter choice (1/2): ").strip()

        if mode == "1":
            return self.correct_with_llm(filtered_text)
        elif mode == "2":
            return self.self_correction_mode(filtered_text)
        else:
            print("⚠️ Invalid choice. Skipping correction.")
            return filtered_text

if __name__ == "__main__":
    from user import PaidUser, FreeUser

    print("Choose user type:")
    print("1. PaidUser")
    print("2. FreeUser")
    role_choice = input("Enter choice (1/2): ").strip()

    if role_choice == "1":
        user = PaidUser("PaidTestUser", tokens=100)
    elif role_choice == "2":
        user = FreeUser("FreeTestUser")
    else:
        print("❌ Invalid input. Exiting.")
        exit()

    editor = Editor(user)

    while True:
        text = input("\n🔤 Enter your original text (or type 'exit' to quit):\n").strip()
        if text.lower() == "exit":
            break

        if isinstance(user, FreeUser):
            if not user.can_submit(text):
                continue  # Enforce word limit and cooldown
        corrected = editor.submit_text_and_choose_correction(text)

        # Save option for PaidUser only
        if isinstance(user, PaidUser):
            save = input("\n💾 Save corrected text to file for 5 tokens? (y/n): ").strip().lower()
            if save == "y":
                filename = input("Enter filename (default: corrected_output.txt): ").strip() or "corrected_output.txt"
                editor.save_text_to_file(corrected, filename)
        else:
            print("💾 Save option not available for FreeUser.")

        # Show history and token balance (if applicable)
        print("\n📚 Correction History:")
        editor.display_corrections()
        if hasattr(user, "tokens"):
            print(f"💰 Final token balance: {user.tokens}")