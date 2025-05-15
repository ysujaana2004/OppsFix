# services/rejection_review_handler.py

import json
import os
import uuid

REJECTION_FILE = "data/rejections.json"

class RejectionReviewHandler:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(REJECTION_FILE) or os.path.getsize(REJECTION_FILE) == 0:
            with open(REJECTION_FILE, 'w') as f:
                json.dump({}, f)

    def _load_data(self):
        with open(REJECTION_FILE, 'r') as f:
            return json.load(f)

    def _save_data(self, data):
        with open(REJECTION_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def log_rejection(self, user, original_phrase, corrected_phrase, reason):
        data = self._load_data()
        rejection_id = str(uuid.uuid4())
        data[rejection_id] = {
            "user": user,
            "original": original_phrase,
            "suggested": corrected_phrase,
            "reason": reason,
            "status": "pending",
            "penalty": None
        }
        self._save_data(data)
        return rejection_id

    def get_pending_reviews(self):
        data = self._load_data()
        return {rid: r for rid, r in data.items() if r["status"] == "pending"}

    def resolve_rejection(self, rejection_id, approved):
        data = self._load_data()
        if rejection_id not in data:
            return False, "Invalid ID."

        penalty = 1 if approved else 5
        data[rejection_id]["status"] = "resolved"
        data[rejection_id]["penalty"] = penalty
        self._save_data(data)

        return True, penalty
