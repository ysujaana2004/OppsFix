from user import PaidUser, SuperUser
from collaboration import CollaborationSession
from payment import purchase_tokens
from complaint import Complaint
import database

def main():
    # Initialize the database (creates the .db file if it doesn't exist)
    database.init_db()

    # Create some test users
    alice = PaidUser("Alice", tokens=10)
    bob = PaidUser("Bob", tokens=5)
    su = SuperUser("RootAdmin")
    
    # Token purchase
    print("\n🛒 Purchasing tokens...")
    purchase_tokens(alice, 15)  # Alice buys 15 tokens
    print(f"{alice.name} now has {alice.tokens} tokens.")

    # Collaboration test
    print("\n🤝 Starting a collaboration...")
    doc = "The quick brown fox jumps over the lazy dog."
    session = CollaborationSession(alice, bob, doc)
    session.send_invitation()
    session.accept()
    session.add_edit(alice, "The QUICK brown fox.")
    session.add_edit(bob, "The quick brown fox jumps HIGH.")
    print(f"\n📄 Final document content: {session.document}")

    # Complaint test
    print("\n⚖️ Filing a complaint...")
    complaint = Complaint(complainant=alice, accused=bob, description="Bob made unwanted edits!")
    complaint.resolve(su, valid=True)

    # Persist user balances
    print("\n💾 Saving user balances...")
    database.upsert_user(alice.name, alice.tokens)
    database.upsert_user(bob.name, bob.tokens)
    print("✅ Users saved to database.")

    # Retrieve and print current balances
    print("\n📊 Current user balances:")
    for username in [alice.name, bob.name]:
        tokens = database.get_tokens(username)
        print(f"{username}: {tokens} tokens")

if __name__ == "__main__":
    main()

