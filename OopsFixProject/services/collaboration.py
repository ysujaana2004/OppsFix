# services/collaboration.py

import json
import os

COLLAB_FILE = "data/collabs.json"

class CollaborationService:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(COLLAB_FILE) or os.path.getsize(COLLAB_FILE) == 0:
            with open(COLLAB_FILE, 'w') as f:
                json.dump({}, f)

    def _load_data(self):
        with open(COLLAB_FILE, 'r') as f:
            return json.load(f)

    def _save_data(self, data):
        with open(COLLAB_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def invite_user(self, text_id, inviter, invitee):
        data = self._load_data()
        if text_id not in data:
            data[text_id] = {'owner': inviter, 'collaborators': []}

        # Check for existing invitation or collaboration
        for entry in data[text_id]['collaborators']:
            if entry['username'] == invitee:
                return False, f"{invitee} is already invited or a collaborator."

        data[text_id]['collaborators'].append({'username': invitee, 'status': 'pending'})
        self._save_data(data)
        return True, f"Invitation sent to {invitee}."


    def respond_to_invite(self, text_id, invitee, accept):
        data = self._load_data()
        if text_id not in data:
            return False, "Invalid text ID."

        collab_list = data[text_id]['collaborators']
        for entry in collab_list:
            if entry['username'] == invitee and entry['status'] == 'pending':
                if accept:
                    entry['status'] = 'accepted'
                    self._save_data(data)
                    return True, "Invitation accepted."
                else:
                    collab_list.remove(entry)
                    self._save_data(data)
                    return False, "Invitation rejected. Token penalty applies."

        return False, "No pending invitation found."

    def get_collaborators(self, text_id):
        data = self._load_data()
        if text_id not in data:
            return []

        seen = set()
        accepted = []
        for entry in data[text_id]['collaborators']:
            if entry['status'] == 'accepted' and entry['username'] not in seen:
                accepted.append(entry['username'])
                seen.add(entry['username'])
        return accepted


    def is_collaborator(self, text_id, username):
        return username in self.get_collaborators(text_id)
