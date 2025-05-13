from datetime import datetime
from typing import List, Tuple
from user import PaidUser

class CollaborationSession:
    """Represents a live or asynchronous co‑editing session between two paid users."""

    def __init__(self, inviter: PaidUser, invitee: PaidUser, document: str = ""):
        self.inviter = inviter
        self.invitee = invitee
        self.document = document
        self.active = False
        self.edit_log: List[Tuple[datetime, str, str]] = []  # (timestamp, editor, new_text)

    # ------------------------------------------------------------------ #
    # Invitation workflow
    # ------------------------------------------------------------------ #
    def send_invitation(self) -> None:
        print(f"📤 {self.inviter.name} invited {self.invitee.name} to collaborate.")

    def accept(self) -> None:
        self.active = True
        self.inviter.collaborators.append(self.invitee)
        self.invitee.collaborators.append(self.inviter)
        print("✅ Invitation accepted – collaboration session started.")

    def reject(self) -> None:
        print("❌ Invitation rejected.")
        # Penalty of 3 tokens to inviter
        if not self.inviter.token_manager.deduct_tokens(3):
            print("⚠️ Inviter lacks 3 tokens – no further penalty.")
        self.active = False

    # ------------------------------------------------------------------ #
    # Editing
    # ------------------------------------------------------------------ #
    def add_edit(self, editor: PaidUser, new_text: str) -> None:
        if not self.active:
            print("🚫 Collaboration session is not active.")
            return
        if editor not in (self.inviter, self.invitee):
            print("🚫 Editor is not part of this session.")
            return

        timestamp = datetime.now()
        self.edit_log.append((timestamp, editor.name, new_text))
        self.document = new_text
        print(f"📝 {editor.name} updated the document at {timestamp:%H:%M:%S}.")
