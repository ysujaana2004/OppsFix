import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from users.free_user import FreeUser
from users.paid_user import PaidUser
from services.token_manager import TokenManager
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections
from services.self_correction import handle_self_correction
import os

class LLMEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Text Editor")
        self.user = None
        self.text_box = None
        self.token_label = None
        self.create_login_screen()

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Enter username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Button(self.root, text="Login as Free User", command=self.login_free).pack()
        tk.Button(self.root, text="Login as Paid User", command=self.login_paid).pack()

    def login_free(self):
        username = self.username_entry.get()
        self.user = FreeUser(username)
        self.create_main_screen()

    def login_paid(self):
        username = self.username_entry.get()
        self.user = PaidUser(username)
        self.user.tokens = 50
        self.create_main_screen()

    def create_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Welcome {self.user.username} ({self.user.user_type})").pack()
        if self.user.user_type == "paid":
            self.token_label = tk.Label(self.root, text=f"Tokens: {self.user.tokens}")
            self.token_label.pack()

        self.text_box = scrolledtext.ScrolledText(self.root, width=60, height=10)
        self.text_box.pack()

        tk.Button(self.root, text="Submit Text", command=self.submit_text).pack()
        if self.user.user_type == "paid":
            tk.Button(self.root, text="Use LLM Correction", command=self.llm_correct).pack()
            tk.Button(self.root, text="Self-Correct and Submit", command=self.self_correct).pack()
            tk.Button(self.root, text="Save Text", command=self.save_text).pack()

    def submit_text(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if self.user.user_type == "free":
            success, msg = self.user.submit_text(text)
            messagebox.showinfo("Submission Result", msg)
        else:
            tm = TokenManager(self.user)
            word_count = len(text.split())
            success, msg = tm.apply_text_submission_cost(word_count)
            messagebox.showinfo("Submission Result", msg)
            if success:
                self.user.add_text_history(text)
            self.update_tokens()

    def llm_correct(self):
        original = self.text_box.get("1.0", tk.END).strip()
        llm = LLMHandler(self.user.whitelist)
        corrected = llm.correct_text(original)
        final, tokens_used = review_llm_corrections(self.user, original, corrected)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, final)
        self.update_tokens()

    def self_correct(self):
        original = simpledialog.askstring("Original Text", "Paste the original text:")
        corrected = self.text_box.get("1.0", tk.END).strip()
        success, msg = handle_self_correction(self.user, original, corrected)
        messagebox.showinfo("Self Correction", msg)
        self.update_tokens()

    def save_text(self):
        filename = simpledialog.askstring("Save File", "Enter filename (e.g., output.txt):")
        if filename:
            os.makedirs("data/texts", exist_ok=True)
            text = self.text_box.get("1.0", tk.END).strip()
            success, msg = self.user.save_text_file(text, filename)
            messagebox.showinfo("Save Result", msg)
            self.update_tokens()

    def update_tokens(self):
        if self.token_label:
            self.token_label.config(text=f"Tokens: {self.user.tokens}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LLMEditorApp(root)
    root.mainloop()