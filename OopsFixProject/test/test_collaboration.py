# test_collaboration.py

from services.collaboration import CollaborationService
import os

def test_collaboration():
    cs = CollaborationService()

    text_id = "text_123"
    inviter = "alice"
    invitee1 = "bob"
    invitee2 = "carol"

    print("\n[Invite User]")
    success, msg = cs.invite_user(text_id, inviter, invitee1)
    print("Invite bob:", success, "|", msg)

    success, msg = cs.invite_user(text_id, inviter, invitee2)
    print("Invite carol:", success, "|", msg)

    print("\n[Respond to Invite: Accept]")
    success, msg = cs.respond_to_invite(text_id, invitee1, accept=True)
    print("bob response:", success, "|", msg)

    print("\n[Respond to Invite: Reject]")
    success, msg = cs.respond_to_invite(text_id, invitee2, accept=False)
    print("carol response:", success, "|", msg)

    print("\n[Get Collaborators]")
    collaborators = cs.get_collaborators(text_id)
    print("Collaborators on text_123:", collaborators)

    print("\n[Invite Existing Collaborator Again]")
    success, msg = cs.invite_user(text_id, inviter, invitee1)
    print("Invite bob again:", success, "|", msg)

if __name__ == "__main__":
    test_collaboration()
