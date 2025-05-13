# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
from user import PaidUser, FreeUser
from editor import Editor
from blacklist import filter_blacklisted_words
import time

class TextEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Text Editor")
        self.root.geometry("800x600")
        self.user = None
        self.editor = None
        self.highlighted_ranges = []

        self.login_screen()

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Select User Type:", font=('Helvetica', 14)).pack(pady=20)
        tk.Button(self.root, text="Free User", width=20, command=self.init_free_user).pack(pady=10)
        tk.Button(self.root, text="Paid User", width=20, command=self.init_paid_user).pack(pady=10)

    def init_free_user(self):
        self.user = FreeUser("FreeUser")
        self.editor = Editor(self.user)
        self.main_screen()

    def init_paid_user(self):
        self.user = PaidUser("PaidUser", tokens=100)
        self.editor = Editor(self.user)
        self.main_screen()

    def main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        if isinstance(self.user, PaidUser):
            self.token_label = tk.Label(top_frame, text=f"Tokens: {self.user.token_manager.get_tokens()}")
            self.token_label.pack()

        self.text_widget = tk.Text(self.root, wrap=tk.WORD, height=20)
        self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Load from File", command=self.load_file).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Submit for Correction", command=self.submit_text).pack(side=tk.LEFT, padx=5)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, content)

    def submit_text(self):
        text = self.text_widget.get("1.0", tk.END).strip()

        if isinstance(self.user, FreeUser) and len(text.split()) > 20:
            messagebox.showerror("Limit Exceeded", "Free users can only submit up to 20 words.")
            return

        filtered_text, blacklist_cost = filter_blacklisted_words(text)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, filtered_text)

        correction_mode = messagebox.askquestion("Correction", "Use LLM Correction?\n(Click 'No' for Self-Correction)")
        if correction_mode == 'yes':
            self.apply_llm_correction(filtered_text)
        else:
            corrected = self.editor.self_correction_mode(filtered_text)
            self.show_final_text(corrected)

        if isinstance(self.user, PaidUser):
            self.token_label.config(text=f"Tokens: {self.user.token_manager.get_tokens()}")

    def apply_llm_correction(self, text):
        filtered_text, corrections, preview = self.editor.get_llm_corrections(text)

        self.text_widget.delete("1.0", tk.END)
        self.highlighted_ranges.clear()

        words = filtered_text.strip().split()
        word_positions = []  # (start_idx, end_idx) for each word
        pos = "1.0"

        for word in words:
            start = self.text_widget.index(tk.INSERT)
            self.text_widget.insert(tk.END, word + " ")
            end = self.text_widget.index(tk.INSERT)
            word_positions.append((start, end))


        for idx, (orig, sugg, i1, i2) in enumerate(corrections):
            start_idx, _ = word_positions[i1]
            _, end_idx = word_positions[i2 - 1]  # i2 is exclusive
            tag_name = f"change_{idx}"
            self.text_widget.tag_add(tag_name, start_idx, end_idx)
            self.text_widget.tag_config(tag_name, background="yellow")
            self.text_widget.tag_bind(tag_name, "<Button-3>", lambda e, o=orig, s=sugg, t=tag_name: self.show_accept_popup(e, o, s, t))
            self.text_widget.tag_bind(tag_name, "<Control-Button-1>", lambda e, o=orig, s=sugg, t=tag_name: self.show_accept_popup(e, o, s, t))


        self.text_widget.insert(tk.END, "\n\n(Right-click highlighted text to accept/reject changes)")

        # Save reference to preview for later if needed
        self.preview_text = preview


    def show_accept_popup(self, event, original, corrected, tag_start):
        popup = tk.Toplevel()
        popup.geometry("+{}+{}".format(event.x_root, event.y_root))
        popup.title("Suggestion")
        tk.Label(popup, text=f"Original: {original}").pack()
        tk.Label(popup, text=f"Suggested: {corrected}").pack()
        tk.Button(popup, text="Accept", command=lambda: self.accept_change(popup, corrected, tag_start)).pack(side=tk.LEFT)
        tk.Button(popup, text="Reject", command=lambda: self.reject_change(popup, original, tag_start)).pack(side=tk.LEFT)

    def accept_change(self, popup, corrected, tag_start):
        self._replace_tagged_text(tag_start, corrected)
        popup.destroy()

    def reject_change(self, popup, original, tag_start):
        self._replace_tagged_text(tag_start, original)
        popup.destroy()

    def _replace_tagged_text(self, tag_name, replacement):
        tag_range = self.text_widget.tag_ranges(tag_name)
        if tag_range:
            self.text_widget.delete(tag_range[0], tag_range[1])
            self.text_widget.insert(tag_range[0], replacement + " ")
            self.text_widget.tag_delete(tag_name)


    def show_final_text(self, text):
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text)

    # Internal: mimic difflib matcher from editor
    def _get_sequence_matcher(self, a, b):
        import difflib
        return difflib.SequenceMatcher(None, a, b)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditorGUI(root)
    root.mainloop()