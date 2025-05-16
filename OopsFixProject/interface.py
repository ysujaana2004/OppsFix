import tkinter as tk
import time
from tkinter import simpledialog, messagebox, scrolledtext, filedialog
from users.free_user import FreeUser
from users.paid_user import PaidUser
from services.token_manager import TokenManager
from services.llm_handler import LLMHandler
from services.review_manager import review_llm_corrections
from services.self_correction import handle_self_correction
from services.text_processor import process_text_submission, TextProcessor
from services.collaboration import CollaborationService, get_shared_files_for_user, penalize_inviter_on_rejection, get_all_shared_files
from services.user_manager import save_user, load_user
from services.file_loader import load_text_from_file
from services.complaint_handler import ComplaintHandler
from services.rejection_review_handler import RejectionReviewHandler
from services.blacklist_review_handler import BlacklistReviewHandler
from services.statistics import get_user_statistics


import os
import json

NOTIF_PATH = "data/notifications.json"

class LLMEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LLM Text Editor")
        self.user = None
        self.text_box = None
        self.token_label = None
        self.blacklist = ['go', 'store']
        self.submitted_text = None
        self.current_shared_file = None
        self.create_login_screen()

    def view_shared_files(self):
        shared = get_all_shared_files(self.user.username)
        if not shared:
            messagebox.showinfo("Shared Files", "You have no shared files.")
            return

        selected = simpledialog.askstring("Shared Files", f"Choose one: {', '.join(shared)}")
        if selected and selected in shared:
            try:
                with open(f"data/texts/{selected}", "r") as f:
                    contents = f.read()
                self.submitted_text = contents
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, contents)
                self.current_shared_file = selected  # Track file for overwrite
                messagebox.showinfo("Loaded", f"Loaded shared file: {selected}")
            except FileNotFoundError:
                messagebox.showerror("Error", f"File {selected} not found on disk.")

    def save_text(self):
        if self.current_shared_file:
            try:
                with open(f"data/texts/{self.current_shared_file}", "w") as f:
                    f.write(self.text_box.get("1.0", tk.END).strip())
                messagebox.showinfo("Save", f"Shared file '{self.current_shared_file}' updated.")
                self.submitted_text = self.text_box.get("1.0", tk.END).strip()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save shared file: {e}")
        else:
            filename = simpledialog.askstring("Save File", "Enter filename (e.g., output.txt):")
            if filename:
                os.makedirs("data/texts", exist_ok=True)
                text = self.text_box.get("1.0", tk.END).strip()
                success, msg = self.user.save_text_file(text, filename)
                messagebox.showinfo("Save Result", msg)
                save_user(self.user)
                self.update_tokens()

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Enter username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Button(self.root, text="Login as Free User", command=self.login_free).pack()
        tk.Button(self.root, text="Login as Paid User", command=self.login_paid).pack()
        tk.Button(self.root, text="Login as SuperUser", command=self.login_super).pack()

    def login_free(self):
        username = self.username_entry.get()
        user = load_user(username)
        if not user:
            user = FreeUser(username)
        else:
            now = time.time()
            if user.user_type == "free" and now - user.last_login_time < 180:
                wait = int(180 - (now - user.last_login_time))
                messagebox.showerror("Access Denied", f"You’ve been locked out for submitting too many words.\nTry again in {wait} seconds.")
                return
        self.user = user
        self.create_main_screen()

    def login_paid(self):
        username = self.username_entry.get()
        user = load_user(username)

        if not user:
            # User doesn't exist yet — offer to create
            create = messagebox.askyesno("Create Account", f"No account found for '{username}'. Create a new paid account?")
            if not create:
                return
            password = simpledialog.askstring("Set Password", "Create a password for your paid account:")
            if not password:
                return
            from users.paid_user import PaidUser
            user = PaidUser(username)
            user.tokens = 20
            user.password = password
            save_user(user)
            messagebox.showinfo("Account Created", f"Paid account '{username}' created successfully.")
        else:
            if user.user_type != "paid":
                messagebox.showerror("Error", "This user is not a paid user.")
                return
            password = simpledialog.askstring("Password", "Enter your password:")
            if password != user.password:
                messagebox.showerror("Error", "Incorrect password.")
                return

        self.user = user
        self.create_main_screen()


    def login_super(self):
        username = self.username_entry.get()
        user = load_user(username)
        if not user:
            from users.super_user import SuperUser
            user = SuperUser(username)
        self.user = user
        self.create_main_screen()


    def create_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Welcome {self.user.username} ({self.user.user_type})").pack()

        if self.user.user_type == "paid":
            # Premium UI panel for paid users
            stats_frame = tk.Frame(self.root, bg="#f0f4f8", bd=2, relief=tk.GROOVE, padx=10, pady=5)
            stats_frame.pack(fill=tk.X, pady=5)

            # Calculate stats
            total_texts = len(self.user.text_history)
            llm_corrections = sum(1 for c in self.user.corrections if c["method"].lower() == "llm")
            self_corrections = sum(1 for c in self.user.corrections if c["method"].lower() == "self")
            remaining_tokens = self.user.tokens

            tk.Label(stats_frame, text="PAID USER DASHBOARD", bg="#f0f4f8", font=("Arial", 12, "bold")).grid(row=0, columnspan=2, pady=2)
            self.token_label = tk.Label(stats_frame, text=f"Tokens Left: {remaining_tokens}", bg="#f0f4f8", fg="green")
            self.token_label.grid(row=3, column=0, pady=2)

            self.llm_label = tk.Label(stats_frame, text=f"LLM Corrections: {llm_corrections}", bg="#f0f4f8")
            self.llm_label.grid(row=1, column=0, sticky='w')

            self.self_label = tk.Label(stats_frame, text=f"Self Corrections: {self_corrections}", bg="#f0f4f8")
            self.self_label.grid(row=2, column=0, sticky='w')


        self.text_box = scrolledtext.ScrolledText(self.root, width=60, height=10)
        self.text_box.pack()

        # === Core features (Free + Paid) ===
        if self.user.user_type in ("free", "paid"):
            tk.Button(self.root, text="Submit Text", command=self.submit_text).pack()
            tk.Button(self.root, text="Import from File", command=self.import_text_file).pack()
            tk.Button(self.root, text="LLM Correction Mode", command=self.llm_correct).pack()
            tk.Button(self.root, text="Self-Correction Mode", command=self.self_correct).pack()
            tk.Button(self.root, text="Propose Blacklist Word", command=self.submit_blacklist_word_gui).pack()

        # Upgrade to paid button (only for free users)
        if self.user.user_type == "free":
            tk.Button(self.root, text="Upgrade to Paid", command=self.upgrade_to_paid_gui).pack()

        # === Paid-only features ===
        if self.user.user_type == "paid":
            tk.Button(self.root, text="View Corrections", command=self.view_corrections).pack()
            tk.Button(self.root, text="Save Text", command=self.save_text).pack()
            tk.Button(self.root, text="Invite Collaborator", command=self.invite_collaborator).pack()
            tk.Button(self.root, text="View Invitations", command=self.view_invitations).pack()
            tk.Button(self.root, text="Purchase Tokens", command=self.purchase_tokens_gui).pack()
            tk.Button(self.root, text="View Shared Files", command=self.view_shared_files).pack()
            tk.Button(self.root, text="View Notifications", command=self.view_notifications).pack()
            tk.Button(self.root, text="View Usage Stats", command=self.view_statistics_gui).pack()
            tk.Button(self.root, text="File Complaint", command=self.file_complaint_gui).pack()
            tk.Button(self.root, text="Respond to Complaint", command=self.respond_to_complaints_gui).pack()


        # === Superuser-only features ===
        if self.user.user_type == "super":
            tk.Button(self.root, text="Review LLM Rejections", command=self.review_llm_rejections_gui).pack()
            tk.Button(self.root, text="Review Blacklist Requests", command=self.review_blacklist_requests_gui).pack()
            tk.Button(self.root, text="Review Complaints", command=self.review_complaints_gui).pack()

        # === Common to all ===
        tk.Button(self.root, text="Refresh Tokens", command=self.refresh_user).pack()


    def import_text_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filepath:
            success, content = load_text_from_file(filepath)
            if success:
                self.submitted_text = content
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, content)
                messagebox.showinfo("Imported", f"Text loaded from: {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", content)

    def purchase_tokens_gui(self):
        try:
            amount = int(simpledialog.askstring("Purchase Tokens", "Enter number of tokens to purchase:"))
        except (TypeError, ValueError):
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
            return

        tm = TokenManager(self.user)
        success, msg = tm.purchase_tokens(amount)
        messagebox.showinfo("Purchase Result", msg)
        save_user(self.user)
        self.update_tokens()

    def submit_text(self):
        text = self.text_box.get("1.0", tk.END).strip()
        success, msg, masked = process_text_submission(self.user, text)

        if not success:
            messagebox.showerror("Submission Failed", msg)
            self.update_tokens()
            if "logged out for 3 minutes" in msg:
                self.create_login_screen()  # redirect to login screen
            return
        messagebox.showinfo("Submission Result", msg)

        if success:
            self.submitted_text = masked
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, masked)
            save_user(self.user)
        self.update_tokens()

    def llm_correct(self):
        if not self.submitted_text:
            messagebox.showinfo("Error", "Please submit text first.")
            return

        llm = LLMHandler(self.user.whitelist)
        corrected_text = llm.correct_text(self.submitted_text)
        result = review_llm_corrections(self.user, self.submitted_text, corrected_text)
        if result.get("bonus"):
            messagebox.showinfo("Bonus!", "No errors detected. You’ve earned 3 bonus tokens!")
            self.update_tokens()
        self.llm_diffs_state = [{"diff": d, "accepted": None} for d in result["diffs"]]

        self.submitted_text_words = self.submitted_text.strip().split()
        self.render_llm_text()

    def render_llm_text(self):
        """Render the current state of the text with highlights."""
        words = self.submitted_text_words[:]
        for state in sorted(self.llm_diffs_state, key=lambda d: d["diff"]["original_start"], reverse=True):
            d = state["diff"]
            if state["accepted"] is True:
                words[d["original_start"]:d["original_end"]] = d["to"].split()
            elif state["accepted"] is False:
                continue  # keep original
            else:
                # highlight undecided
                words[d["original_start"]:d["original_end"]] = [f"[{d['from']}]"]

        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, " ".join(words))

        for i, state in enumerate(self.llm_diffs_state):
            if state["accepted"] is not None:
                continue
            d = state["diff"]
            tag = f"llm_tag_{i}"
            start = "1.0"
            while True:
                pos = self.text_box.search(f"[{d['from']}]", start, tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(d['from'])+2}c"
                self.text_box.tag_add(tag, pos, end)
                self.text_box.tag_config(tag, background="yellow", underline=True)
                self.text_box.tag_bind(tag, "<Button-1>", self.make_llm_popup(i))
                break  # only bind first instance

    def make_llm_popup(self, idx):
        def on_click(event=None):
            d = self.llm_diffs_state[idx]["diff"]
            popup = tk.Toplevel(self.root)
            popup.title("Accept Correction?")
            popup.geometry("300x100")
            tk.Label(popup, text=f"{d['from']} → {d['to']}?").pack(pady=10)

            def accept():
                self.llm_diffs_state[idx]["accepted"] = True
                if hasattr(self.user, "tokens"):
                    self.user.tokens = max(0, self.user.tokens - 1)
                    self.update_tokens()
                if hasattr(self.user, "corrections"):
                    self.user.corrections.append({
                        "method": "llm",
                        "original": d["from"],
                        "corrected": d["to"],
                        "diffs": [{"from": d["from"], "to": d["to"]}]
                    })
                self.render_llm_text()
                save_user(self.user)
                popup.destroy()

            def reject():
                self.llm_diffs_state[idx]["accepted"] = False
                self.render_llm_text()
                popup.destroy()

                def ask_whitelist():
                    if messagebox.askyesno("Whitelist?", f"Do you want to whitelist '{d['from']}' for future corrections?"):
                        if hasattr(self.user, "whitelist"):
                            if d["from"] not in self.user.whitelist:
                                self.user.whitelist.append(d["from"])
                                save_user(self.user)
                                messagebox.showinfo("Whitelisted", f"'{d['from']}' added to whitelist.")
                            else:
                                messagebox.showinfo("Already Whitelisted", f"'{d['from']}' is already in your whitelist.")
                    else:
                        reason = simpledialog.askstring("Rejection Reason", f"Why are you rejecting the correction '{d['from']}' → '{d['to']}'?")
                        if reason:
                            handler = RejectionReviewHandler()
                            handler.log_rejection(self.user.username, d['from'], d['to'], reason)
                            messagebox.showinfo("Submitted", "Your reason has been submitted for superuser review.")

                self.root.after(100, ask_whitelist)


            tk.Button(popup, text="Accept", command=accept).pack(side=tk.LEFT, padx=20)
            tk.Button(popup, text="Reject", command=reject).pack(side=tk.RIGHT, padx=20)

        return on_click


    def self_correct(self):
        if not self.submitted_text:
            messagebox.showinfo("Error", "Please submit text first.")
            return
        corrected = self.text_box.get("1.0", tk.END).strip()
        success, msg = handle_self_correction(self.user, self.submitted_text, corrected)
        messagebox.showinfo("Self Correction", msg)
        save_user(self.user)
        self.update_tokens()

    def save_text(self):
        filename = simpledialog.askstring("Save File", "Enter filename (e.g., output.txt):")
        if filename:
            os.makedirs("data/texts", exist_ok=True)
            text = self.text_box.get("1.0", tk.END).strip()
            success, msg = self.user.save_text_file(text, filename)
            messagebox.showinfo("Save Result", msg)
            save_user(self.user)
            self.update_tokens()

    def invite_collaborator(self):
        if not self.user.saved_texts:
            messagebox.showinfo("No Files", "You must save at least one file before inviting collaborators.")
            return

        filename = simpledialog.askstring("Text ID", "Enter filename to share:")
        if filename not in self.user.saved_texts:
            messagebox.showinfo("Invalid", "You can only invite collaborators to files you've saved.")
            return

        invitee = simpledialog.askstring("Invite Collaborator", "Enter username of the collaborator:")
        if invitee:
            cs = CollaborationService()
            success, msg = cs.invite_user(filename, self.user.username, invitee)
            messagebox.showinfo("Invite Result", msg)
            if not success:
                self.update_tokens()
            save_user(self.user)

    def view_invitations(self):
        cs = CollaborationService()
        pending = cs._load_data()
        invitations = []

        for text_id, entry in pending.items():
            for c in entry['collaborators']:
                if c['username'] == self.user.username and c['status'] == 'pending':
                    invitations.append((text_id, entry['owner']))

        if not invitations:
            messagebox.showinfo("Invitations", "No pending invitations.")
            return

        def handle_response(text_id, accept):
            if not accept:
                penalize_inviter_on_rejection(text_id)
                self._log_notification_for_inviter(text_id, self.user.username)

            result, msg = cs.respond_to_invite(text_id, self.user.username, accept)
            messagebox.showinfo("Response", msg)
            self.update_tokens()
            save_user(self.user)
            invite_window.destroy()

        invite_window = tk.Toplevel(self.root)
        invite_window.title("Respond to Invitations")
        invite_window.geometry("500x300")

        for text_id, inviter in invitations:
            frame = tk.Frame(invite_window)
            frame.pack(pady=5)
            tk.Label(frame, text=f"From: {inviter}, File: {text_id}").pack(side=tk.LEFT)
            tk.Button(frame, text="Accept", command=lambda t=text_id: handle_response(t, True)).pack(side=tk.LEFT)
            tk.Button(frame, text="Reject", command=lambda t=text_id: handle_response(t, False)).pack(side=tk.LEFT)

    def view_shared_files(self):
        shared = get_shared_files_for_user(self.user.username)
        if not shared:
            messagebox.showinfo("Shared Files", "You have no shared files.")
            return

        selected = simpledialog.askstring("Shared Files", f"Choose one: {', '.join(shared)}")
        if selected and selected in shared:
            try:
                with open(f"data/texts/{selected}", "r") as f:
                    contents = f.read()
                self.submitted_text = contents
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, contents)
                messagebox.showinfo("Loaded", f"Loaded shared file: {selected}")
            except FileNotFoundError:
                messagebox.showerror("Error", f"File {selected} not found on disk.")

    def view_notifications(self):
        if not os.path.exists(NOTIF_PATH):
            messagebox.showinfo("Notifications", "No notifications.")
            return

        with open(NOTIF_PATH, 'r') as f:
            data = json.load(f)

        user_notes = data.get(self.user.username, [])
        if not user_notes:
            messagebox.showinfo("Notifications", "No notifications.")
            return

        win = tk.Toplevel(self.root)
        win.title("Notifications")
        win.geometry("400x200")

        box = scrolledtext.ScrolledText(win, wrap=tk.WORD)
        box.pack(expand=True, fill=tk.BOTH)

        for note in user_notes:
            box.insert(tk.END, f"- {note}\n")

        data[self.user.username] = []
        with open(NOTIF_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_notification_for_inviter(self, text_id, rejected_by):
        cs = CollaborationService()
        data = cs._load_data()
        if text_id in data:
            inviter = data[text_id]['owner']
            if not os.path.exists(NOTIF_PATH):
                store = {}
            else:
                with open(NOTIF_PATH, 'r') as f:
                    store = json.load(f)
            store.setdefault(inviter, []).append(f"{rejected_by} rejected your invite to '{text_id}'.")
            with open(NOTIF_PATH, 'w') as f:
                json.dump(store, f, indent=2)

    def refresh_user(self):
        updated_user = load_user(self.user.username)
        if updated_user:
            self.user = updated_user
            self.update_tokens()
            messagebox.showinfo("Refreshed", "User tokens have been refreshed from disk.")

    def update_tokens(self):
        if self.token_label:
            self.token_label.config(text=f"Tokens: {self.user.tokens}")
        save_user(self.user)

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

    def file_complaint_gui(self):
        text_id = simpledialog.askstring("Complaint", "Enter filename (e.g., shared_file.txt):")
        if not text_id:
            return
        defendant = simpledialog.askstring("Complaint", "Enter username of the collaborator you are complaining about:")
        if not defendant:
            return
        reason = simpledialog.askstring("Complaint", "Enter the reason for the complaint:")
        if not reason:
            return

        handler = ComplaintHandler()
        complaint_id = handler.file_complaint(
            complainant=self.user.username,
            defendant=defendant,
            text_id=text_id,
            reason=reason
        )
        messagebox.showinfo("Complaint Filed", f"Complaint ID: {complaint_id}")

    def respond_to_complaints_gui(self):
        handler = ComplaintHandler()
        complaints = handler.get_pending_complaints_for_user(self.user.username)

        if not complaints:
            messagebox.showinfo("Complaints", "No complaints against you.")
            return

        window = tk.Toplevel(self.root)
        window.title("Respond to Complaints")
        window.geometry("500x400")

        for cid, complaint in complaints.items():
            frame = tk.Frame(window)
            frame.pack(pady=10, fill=tk.X)
            tk.Label(frame, text=f"From: {complaint['complainant']} | File: {complaint['text_id']}").pack()
            tk.Label(frame, text=f"Reason: {complaint['reason']}").pack()

            def make_responder(cid=cid):
                def submit():
                    response = simpledialog.askstring("Response", f"Your response to complaint {cid}:")
                    if response:
                        success, msg = handler.respond_to_complaint(cid, response)
                        messagebox.showinfo("Result", msg)
                        window.destroy()
                return submit

            tk.Button(frame, text="Respond", command=make_responder()).pack()

    def review_complaints_gui(self):
        handler = ComplaintHandler()
        all_complaints = handler.get_all_complaints()

        # Filter only complaints with a response (ready for review)
        reviewable = {
            cid: c for cid, c in all_complaints.items()
            if c['status'] == 'responded'
        }

        if not reviewable:
            messagebox.showinfo("Complaints", "No complaints ready for review.")
            return

        win = tk.Toplevel(self.root)
        win.title("Review Complaints")
        win.geometry("600x500")

        for cid, c in reviewable.items():
            frame = tk.Frame(win, relief=tk.RIDGE, borderwidth=2)
            frame.pack(padx=10, pady=10, fill=tk.X)

            tk.Label(frame, text=f"Complaint ID: {cid}").pack(anchor='w')
            tk.Label(frame, text=f"From: {c['complainant']} → Against: {c['defendant']}").pack(anchor='w')
            tk.Label(frame, text=f"File: {c['text_id']}").pack(anchor='w')
            tk.Label(frame, text=f"Reason: {c['reason']}").pack(anchor='w')
            tk.Label(frame, text=f"Response: {c['response']}").pack(anchor='w')

            def make_penalty_reviewer(cid=cid, complainant=c['complainant'], defendant=c['defendant']):
                def apply_penalty():
                    target = simpledialog.askstring("Penalty Target", f"Who do you want to penalize?\nEnter '{complainant}' or '{defendant}':")
                    if target not in [complainant, defendant]:
                        messagebox.showerror("Invalid", "You must enter one of the involved usernames.")
                        return

                    try:
                        amount = int(simpledialog.askstring("Penalty Amount", f"Tokens to deduct from {target}:"))
                    except (TypeError, ValueError):
                        messagebox.showerror("Invalid", "Enter a valid integer.")
                        return

                    success, msg = handler.review_complaint(cid, target, amount)
                    messagebox.showinfo("Result", msg)
                    win.destroy()
                return apply_penalty

            tk.Button(frame, text="Apply Penalty", command=make_penalty_reviewer()).pack(pady=5)

    def review_llm_rejections_gui(self):
        handler = RejectionReviewHandler()
        pending = handler.get_pending_reviews()

        if not pending:
            messagebox.showinfo("Review", "No pending rejections.")
            return

        win = tk.Toplevel(self.root)
        win.title("Review LLM Rejections")
        win.geometry("600x500")

        for rid, r in pending.items():
            frame = tk.Frame(win, relief=tk.RIDGE, borderwidth=2)
            frame.pack(padx=10, pady=10, fill=tk.X)

            tk.Label(frame, text=f"User: {r['user']}").pack(anchor='w')
            tk.Label(frame, text=f"Original: {r['original']} → Suggested: {r['suggested']}").pack(anchor='w')
            tk.Label(frame, text=f"Reason: {r['reason']}").pack(anchor='w')

            def make_reviewer(approved, rid=rid, username=r["user"]):
                def resolve():
                    success, penalty = handler.resolve_rejection(rid, approved)
                    if success:
                        u = load_user(username)
                        if hasattr(u, "tokens"):
                            u.tokens = max(0, u.tokens - penalty)
                            save_user(u)
                            messagebox.showinfo("Resolved", f"{username} penalized {penalty} tokens.")
                        else:
                            messagebox.showerror("Error", "Failed to load user for penalty.")
                        win.destroy()
                return resolve

            tk.Button(frame, text="Approve Reason (1 token)", command=make_reviewer(True)).pack(side=tk.LEFT, padx=10)
            tk.Button(frame, text="Reject Reason (5 tokens)", command=make_reviewer(False)).pack(side=tk.RIGHT, padx=10)

    def submit_blacklist_word_gui(self):
        word = simpledialog.askstring("Blacklist Request", "Enter the word you want to blacklist:")
        if not word:
            return

        handler = BlacklistReviewHandler()
        request_id = handler.submit_request(self.user.username, word.strip())
        messagebox.showinfo("Submitted", f"Request ID: {request_id}\nYour word will be reviewed by a superuser.")

    def review_blacklist_requests_gui(self):
        handler = BlacklistReviewHandler()
        pending = handler.get_pending_requests()

        if not pending:
            messagebox.showinfo("Review", "No pending blacklist requests.")
            return

        win = tk.Toplevel(self.root)
        win.title("Review Blacklist Requests")
        win.geometry("500x400")

        for rid, r in pending.items():
            frame = tk.Frame(win, relief=tk.RIDGE, borderwidth=2)
            frame.pack(padx=10, pady=10, fill=tk.X)

            tk.Label(frame, text=f"User: {r['user']}").pack(anchor='w')
            tk.Label(frame, text=f"Word: {r['word']}").pack(anchor='w')

            def make_resolver(approve, rid=rid):
                def resolve():
                    success, msg = handler.resolve_request(rid, approve)
                    messagebox.showinfo("Result", msg)
                    win.destroy()
                return resolve

            tk.Button(frame, text="Approve", command=make_resolver(True)).pack(side=tk.LEFT, padx=20)
            tk.Button(frame, text="Reject", command=make_resolver(False)).pack(side=tk.RIGHT, padx=20)

    def view_statistics_gui(self):
        stats = get_user_statistics(self.user)

        win = tk.Toplevel(self.root)
        win.title("Usage Statistics")
        win.geometry("400x300")

        for key, value in stats.items():
            tk.Label(win, text=f"{key}: {value}", anchor='w').pack(fill=tk.X, padx=10, pady=3)

    def upgrade_to_paid_gui(self):
        password = simpledialog.askstring("Set Password", "Create a password for your paid account:")
        if not password:
            return

        self.user.user_type = "paid"
        self.user.tokens = 20
        self.user.password = password
        save_user(self.user)
        messagebox.showinfo("Success", "Account upgraded to paid. Password saved.")
        self.create_main_screen()



if __name__ == "__main__":
    root = tk.Tk()
    app = LLMEditorApp(root)
    root.mainloop()