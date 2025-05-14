# services/complaint_handler.py

import json
import os
import uuid

COMPLAINT_FILE = "data/complaints.json"

class ComplaintHandler:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(COMPLAINT_FILE) or os.path.getsize(COMPLAINT_FILE) == 0:
            with open(COMPLAINT_FILE, 'w') as f:
                json.dump({}, f)

    def _load_data(self):
        with open(COMPLAINT_FILE, 'r') as f:
            return json.load(f)

    def _save_data(self, data):
        with open(COMPLAINT_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def file_complaint(self, complainant, defendant, text_id, reason):
        data = self._load_data()
        complaint_id = str(uuid.uuid4())
        data[complaint_id] = {
            "complainant": complainant,
            "defendant": defendant,
            "text_id": text_id,
            "reason": reason,
            "response": None,
            "status": "pending",
            "super_user_resolution": None,
            "token_penalty": None
        }
        self._save_data(data)
        return complaint_id

    def get_pending_complaints_for_user(self, username):
        data = self._load_data()
        return {
            cid: c for cid, c in data.items()
            if c['defendant'] == username and c['status'] == 'pending'
        }

    def respond_to_complaint(self, complaint_id, response_text):
        data = self._load_data()
        if complaint_id not in data:
            return False, "Invalid complaint ID."
        data[complaint_id]['response'] = response_text
        data[complaint_id]['status'] = "responded"
        self._save_data(data)
        return True, "Response recorded."

    def review_complaint(self, complaint_id, punished_user, penalty_amount):
        data = self._load_data()
        if complaint_id not in data:
            return False, "Invalid complaint ID."

        data[complaint_id]['status'] = "resolved"
        data[complaint_id]['super_user_resolution'] = punished_user
        data[complaint_id]['token_penalty'] = penalty_amount
        self._save_data(data)

        return True, f"{punished_user} penalized {penalty_amount} tokens."

    def get_all_complaints(self):
        return self._load_data()