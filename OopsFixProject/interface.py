import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
from users.free_user import FreeUser
from users.paid_user import PaidUser
from services.token_manager import TokenManager
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections
from services.self_correction import handle_self_correction
from services.text_processor import process_text_submission, TextProcessor
from services.statistics import correction_stats
import os

class LLMEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Text Editor")
        self.user = None
        self.text_box = None
        self.token_label = None
        self.blacklist = ['go', 'store']  # Example blacklist
        self.submitted_text = None
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
        tk.Button(self.root, text="LLM Correction Mode", command=self.llm_correct).pack()
        tk.Button(self.root, text="Self-Correction Mode", command=self.self_correct).pack()
        tk.Button(self.root, text="View Corrections", command=self.view_corrections).pack()
        if self.user.user_type == "paid":
            tk.Button(self.root, text="Save Text", command=self.save_text).pack()

    def submit_text(self):
        text = self.text_box.get("1.0", tk.END).strip()
        success, msg, masked = process_text_submission(self.user, text, self.blacklist)
        messagebox.showinfo("Submission Result", msg)
        if success:
            self.submitted_text = masked
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, masked)
        self.update_tokens()

    def llm_correct(self):
        if not self.submitted_text:
            messagebox.showinfo("Error", "Please submit text first.")
            return
        llm = LLMHandler(self.user.whitelist)
        corrected = llm.correct_text(self.submitted_text)
        final, tokens_used = review_llm_corrections(self.user, self.submitted_text, corrected)
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, final)
        self.update_tokens()
        # Show statistics popup
        self.show_correction_stats(self.submitted_text, final)
        self.submitted_text = final  # Update for further corrections

    def self_correct(self):
        if not self.submitted_text:
            messagebox.showinfo("Error", "Please submit text first.")
            return
        corrected = self.text_box.get("1.0", tk.END).strip()
        success, msg = handle_self_correction(self.user, self.submitted_text, corrected)
        messagebox.showinfo("Self Correction", msg)
        self.update_tokens()
        if success:
            self.show_correction_stats(self.submitted_text, corrected)
            self.submitted_text = corrected  # Update for further corrections

    def save_text(self):
        filename = simpledialog.askstring("Save File", "Enter filename (e.g., output.txt):")
        if filename:
            os.makedirs("data/texts", exist_ok=True)
            text = self.text_box.get("1.0", tk.END).strip()
            success, msg = self.user.save_text_file(text, filename)
            messagebox.showinfo("Save Result", msg)
            self.update_tokens()

    def view_corrections(self):
        if not self.user.corrections:
            messagebox.showinfo("Corrections", "No corrections yet.")
            return

        win = tk.Toplevel(self.root)
        win.title("Correction History")
        win.geometry("600x400")

        text_widget = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        text_widget.pack(expand=True, fill=tk.BOTH)

        for idx, entry in enumerate(self.user.corrections, 1):
            text_widget.insert(tk.END, f"#{idx} | Method: {entry['method'].upper()}\n")
            text_widget.insert(tk.END, f"Original: {entry['original']}\n")
            text_widget.insert(tk.END, f"Corrected: {entry['corrected']}\n")
            if 'diffs' in entry and entry['diffs']:
                text_widget.insert(tk.END, "Changes:\n")
                for d in entry['diffs']:
                    text_widget.insert(tk.END, f"  - {d['from']} → {d['to']}\n")
            text_widget.insert(tk.END, "---\n\n")

    def update_tokens(self):
        if self.token_label:
            self.token_label.config(text=f"Tokens: {self.user.tokens}")
    
    def show_correction_stats(self, original, corrected):
        stats = correction_stats(original, corrected)
        stats_message = (
            f"Correction Statistics:\n"
            f"Words changed: {stats['words_changed']} / {stats['total_words']} "
            f"({stats['percent_words_changed']}%)\n"
            f"Characters changed: {stats['chars_changed']} / {stats['total_chars']} "
            f"({stats['percent_chars_changed']}%)"
        )
        messagebox.showinfo("Correction Statistics", stats_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = LLMEditorApp(root)
    root.mainloop()