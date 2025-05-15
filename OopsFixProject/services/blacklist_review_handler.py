# services/blacklist_review_handler.py

import json
import os
import uuid

BLACKLIST_FILE = "data/blacklist.json"
BLACKLIST_QUEUE_FILE = "data/blacklist_requests.json"

class BlacklistReviewHandler:
    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        if not os.path.exists(BLACKLIST_FILE):
            with open(BLACKLIST_FILE, 'w') as f:
                json.dump([], f)
        if not os.path.exists(BLACKLIST_QUEUE_FILE):
            with open(BLACKLIST_QUEUE_FILE, 'w') as f:
                json.dump({}, f)

    def _load_blacklist(self):
        with open(BLACKLIST_FILE, 'r') as f:
            return json.load(f)

    def _save_blacklist(self, words):
        with open(BLACKLIST_FILE, 'w') as f:
            json.dump(words, f, indent=2)

    def _load_queue(self):
        with open(BLACKLIST_QUEUE_FILE, 'r') as f:
            return json.load(f)

    def _save_queue(self, data):
        with open(BLACKLIST_QUEUE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def submit_request(self, username, word):
        queue = self._load_queue()
        request_id = str(uuid.uuid4())
        queue[request_id] = {
            "user": username,
            "word": word,
            "status": "pending"
        }
        self._save_queue(queue)
        return request_id

    def get_pending_requests(self):
        queue = self._load_queue()
        return {rid: r for rid, r in queue.items() if r["status"] == "pending"}

    def resolve_request(self, request_id, approve):
        queue = self._load_queue()
        if request_id not in queue:
            return False, "Invalid request ID"

        if approve:
            blacklist = self._load_blacklist()
            if queue[request_id]["word"] not in blacklist:
                blacklist.append(queue[request_id]["word"])
                self._save_blacklist(blacklist)

        queue[request_id]["status"] = "approved" if approve else "rejected"
        self._save_queue(queue)
        return True, f"Request {'approved' if approve else 'rejected'}."
