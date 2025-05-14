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
        self.setup_window()
        self.user = None
        self.editor = None
        self.highlighted_ranges = []
        self.create_login_screen()

    def setup_window(self):
        """Initialize window properties"""
        self.root.title("OopsFix Text Editor")
        self.root.geometry("800x600")
        self.styles = {
            'button': {'width': 20, 'pady': 5},
            'label': {'font': ('Helvetica', 14)},
            'text': {'wrap': tk.WORD, 'height': 20}
        }

    def clear_screen(self):
        """Clear all widgets from screen"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_button(self, parent, text, command, **kwargs):
        """Create a standardized button"""
        button_config = {**self.styles['button'], **kwargs}
        return tk.Button(parent, text=text, command=command, **button_config)

    def create_label(self, parent, text, **kwargs):
        """Create a standardized label"""
        label_config = {**self.styles['label'], **kwargs}
        return tk.Label(parent, text=text, **label_config)

    def create_login_screen(self):
        """Create the initial login screen"""
        self.clear_screen()
        
        login_frame = tk.Frame(self.root)
        login_frame.pack(expand=True)
        
        self.create_label(login_frame, "Select User Type:").pack(pady=20)
        self.create_button(login_frame, "Free User", 
                          lambda: self.initialize_user("free")).pack(pady=10)
        self.create_button(login_frame, "Paid User", 
                          lambda: self.initialize_user("paid")).pack(pady=10)

    def initialize_user(self, user_type):
        """Initialize user based on type"""
        self.user = FreeUser("FreeUser") if user_type == "free" \
                   else PaidUser("PaidUser", tokens=100)
        self.editor = Editor(self.user)
        self.create_main_screen()

    def create_main_screen(self):
        """Create the main editor screen"""
        self.clear_screen()

        # Top frame for tokens/status
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        if isinstance(self.user, PaidUser):
            self.token_label = self.create_label(
                top_frame, 
                f"Tokens: {self.user.token_manager.get_tokens()}")
            self.token_label.pack()

        # Text area
        self.text_widget = tk.Text(self.root, **self.styles['text'])
        self.text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Control buttons
        self.create_button(button_frame, "Load File", 
                          self.load_file, width=15).pack(side=tk.LEFT, padx=5)
        self.create_button(button_frame, "Submit", 
                          self.submit_text, width=15).pack(side=tk.LEFT, padx=5)
        self.create_button(button_frame, "Switch User", 
                          self.create_login_screen, width=15).pack(side=tk.LEFT, padx=5)

    def update_token_display(self):
        """Update token display for paid users"""
        if isinstance(self.user, PaidUser) and hasattr(self, 'token_label'):
            self.token_label.config(text=f"Tokens: {self.user.token_manager.get_tokens()}")

    def handle_correction(self, text):
        """Handle text correction process"""
        correction_mode = messagebox.askquestion(
            "Correction", 
            "Use LLM Correction?\n(Click 'No' for Self-Correction)")
            
        if correction_mode == 'yes':
            self.apply_llm_correction(text)
        else:
            self.show_self_correction_interface(text)
    
        self.update_token_display()


    def show_self_correction_interface(self, original_text):
        """Create a popup window for self-correction"""
        self.correction_window = tk.Toplevel(self.root)
        self.correction_window.title("Self-Correction Mode")
        self.correction_window.geometry("600x400")

        # Original text display
        tk.Label(self.correction_window, text="Original Text:", 
                font=('Helvetica', 12)).pack(pady=5)
        original_display = tk.Text(self.correction_window, height=5, width=50)
        original_display.pack(pady=5, padx=10)
        original_display.insert("1.0", original_text)
        original_display.config(state='disabled')

        # Correction input
        tk.Label(self.correction_window, text="Make your corrections below:", 
                font=('Helvetica', 12)).pack(pady=5)
        self.correction_input = tk.Text(self.correction_window, height=5, width=50)
        self.correction_input.pack(pady=5, padx=10)
        self.correction_input.insert("1.0", original_text)

        def submit_correction():
            corrected = self.correction_input.get("1.0", "end-1c").strip()
            if not corrected:
                messagebox.showwarning("Warning", "No correction entered.")
                return
            
            # Pass both original and corrected text to editor
            corrected_text = self.editor.self_correction_mode(original_text, corrected)
            self.show_final_text(corrected_text)
            self.correction_window.destroy()

        # Submit button
        tk.Button(self.correction_window, text="Submit Correction", 
                 command=submit_correction).pack(pady=10)
    
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, f.read())

    def submit_text(self):
        text = self.text_widget.get("1.0", tk.END).strip()

        if isinstance(self.user, FreeUser) and len(text.split()) > 20:
            messagebox.showerror("Error", "Free users limited to 20 words")
            return

        filtered_text, cost = filter_blacklisted_words(text)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, filtered_text)
        
        self.handle_correction(filtered_text)
   
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
            # Allow multiple types of clicks to trigger suggestion popup
            self.text_widget.tag_bind(tag_name, "<Button-1>", lambda e, o=orig, s=sugg, t=tag_name: self.show_accept_popup(e, o, s, t))
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