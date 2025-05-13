from enum import Enum, auto
from datetime import datetime
from typing import Optional
from user import User, PaidUser, SuperUser

class ComplaintStatus(Enum):
    OPEN = auto()
    RESOLVED_VALID = auto()
    RESOLVED_INVALID = auto()

class Complaint:
    """Tracks a user‑to‑user complaint reviewed by a super user."""
    def __init__(self, complainant: User, accused: User, description: str):
        self.complainant = complainant
        self.accused = accused
        self.description = description
        self.timestamp = datetime.now()
        self.status = ComplaintStatus.OPEN
        self.resolution_comment: Optional[str] = None

    # ----------------- Review & resolution ----------------- #
    def resolve(self, su: SuperUser, valid: bool, comment: str = "") -> None:
        if self.status != ComplaintStatus.OPEN:
            print("Complaint already resolved.")
            return

        self.status = ComplaintStatus.RESOLVED_VALID if valid else ComplaintStatus.RESOLVED_INVALID
        self.resolution_comment = comment or ("Valid complaint – accused penalized." if valid else "Baseless complaint – complainant penalized.")

        # Apply penalties
        if valid:
            self.accused.token_manager.deduct_tokens(5)
            print(f"⚖️ Complaint upheld – {self.accused.name} loses 5 tokens.")
        else:
            self.complainant.token_manager.deduct_tokens(5)
            print(f"⚖️ Complaint dismissed – {self.complainant.name} loses 5 tokens.")

        print("📄 Resolution recorded by", su.name)
