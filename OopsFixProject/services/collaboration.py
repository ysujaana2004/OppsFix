# services/collaboration.py

import json
import os

from users.paid_user import PaidUser
from services.user_manager import load_user, save_user

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
    
def get_shared_files_for_user(username):
    data = CollaborationService()._load_data()
    shared = []
    for text_id, entry in data.items():
        for c in entry['collaborators']:
            if c['username'] == username and c['status'] == 'accepted':
                shared.append(text_id)
    return shared

def get_all_shared_files(username):
    """
    Returns all files shared with or by this user where the user is either:
    - the owner of the file, or
    - an accepted collaborator
    """
    cs = CollaborationService()
    data = cs._load_data()
    shared = []

    for text_id, entry in data.items():
        if entry['owner'] == username:
            shared.append(text_id)
            continue
        for c in entry['collaborators']:
            if c['username'] == username and c['status'] == 'accepted':
                shared.append(text_id)
                break

    return shared


def penalize_inviter_on_rejection(text_id):
    cs = CollaborationService()
    data = cs._load_data()
    if text_id in data:
        inviter = data[text_id]['owner']
        user = load_user(inviter)
        if isinstance(user, PaidUser):
            user.tokens = max(0, user.tokens - 3)
            save_user(user)  # Persist the penalty
        return inviter
    return None