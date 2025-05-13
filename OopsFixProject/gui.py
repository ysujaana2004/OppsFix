# gui.py

import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
from user import FreeUser, PaidUser
from editor import Editor

class TextEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OopsFix Text Editor")
        self.user = None
        self.editor = None

        self.login_screen()

    def login_screen(self):
        self.clear_window()

        tk.Label(self.root, text="Login as:").pack(pady=10)
        tk.Button(self.root, text="Free User", command=self.login_free).pack(pady=5)
        tk.Button(self.root, text="Paid User", command=self.login_paid).pack(pady=5)

    def login_free(self):
        name = simpledialog.askstring("Free User", "Enter your name:")
        if name:
            self.user = FreeUser(name)
            self.editor = Editor(self.user)
            self.editor_screen()

    def login_paid(self):
        name = simpledialog.askstring("Paid User", "Enter your name:")
        if name:
            self.user = PaidUser(name, tokens=100)
            self.editor = Editor(self.user)
            self.editor_screen()

    def editor_screen(self):
        self.clear_window()

        tk.Label(self.root, text=f"Welcome, {self.user.name} ({'Paid' if isinstance(self.user, PaidUser) else 'Free'})").pack(pady=5)

        self.text_input = scrolledtext.ScrolledText(self.root, height=10, width=60)
        self.text_input.pack(pady=5)

        tk.Button(self.root, text="LLM Correction", command=self.llm_correction).pack(pady=2)
        tk.Button(self.root, text="Self-Correction", command=self.self_correction).pack(pady=2)

        if isinstance(self.user, PaidUser):
            tk.Button(self.root, text="Save to File (5 tokens)", command=self.save_to_file).pack(pady=2)
            self.token_label = tk.Label(self.root, text=f"Tokens: {self.user.tokens}")
            self.token_label.pack(pady=2)

        tk.Button(self.root, text="Show Correction History", command=self.show_history).pack(pady=2)
        tk.Button(self.root, text="Logout", command=self.login_screen).pack(pady=10)

    def llm_correction(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Text cannot be empty.")
            return

        corrected = self.editor.correct_with_llm(text)
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert(tk.END, corrected)

        if isinstance(self.user, PaidUser):
            self.token_label.config(text=f"Tokens: {self.user.tokens}")

    def self_correction(self):
        original = self.text_input.get("1.0", tk.END).strip()
        if not original:
            messagebox.showwarning("Warning", "Text cannot be empty.")
            return

        corrected = simpledialog.askstring("Self Correction", "Enter your corrected version:", initialvalue=original)
        if corrected:
            final = self.editor.self_correction_mode(original_text=original)
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert(tk.END, final)

            if isinstance(self.user, PaidUser):
                self.token_label.config(text=f"Tokens: {self.user.tokens}")

    def save_to_file(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Nothing to save.")
            return

        filename = simpledialog.askstring("Save File", "Enter filename:", initialvalue="corrected_output.txt")
        if filename:
            success = self.editor.save_text_to_file(text, filename)
            if success:
                messagebox.showinfo("Saved", f"Text saved to {filename}.")
            else:
                messagebox.showerror("Error", "Could not save file.")

            self.token_label.config(text=f"Tokens: {self.user.tokens}")

    def show_history(self):
        history = self.user.accepted_corrections if hasattr(self.user, 'accepted_corrections') else []
        self_corrections = self.user.corrections if hasattr(self.user, 'corrections') else []

        if not history and not self_corrections:
            messagebox.showinfo("History", "No corrections recorded yet.")
            return

        win = tk.Toplevel(self.root)
        win.title("Correction History")

        text = ""
        if history:
            text += "\n🔁 Accepted LLM Corrections:\n"
            for i, (o, c) in enumerate(history, 1):
                text += f"{i}. '{o}' → '{c}'\n"
        if self_corrections:
            text += "\n✍️ Self-Corrections (full text):\n"
            for i, (o, c) in enumerate(self_corrections, 1):
                text += f"{i}. '{o}' → '{c}'\n"

        tk.Label(win, text=text, justify="left").pack(padx=10, pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditorGUI(root)
    root.mainloop()
