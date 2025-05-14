# test_complaint_handler.py

from services.complaint_handler import ComplaintHandler

def test_complaints():
    ch = ComplaintHandler()

    complainant = "alice"
    defendant = "bob"
    text_id = "text_123"
    reason = "Edited the file without asking"

    # Step 1: File complaint
    print("\n[Filing Complaint]")
    cid = ch.file_complaint(complainant, defendant, text_id, reason)
    print("Complaint ID:", cid)

    # Step 2: Fetch pending complaints for defendant
    print("\n[Pending Complaints for bob]")
    pending = ch.get_pending_complaints_for_user(defendant)
    for cid, c in pending.items():
        print(f"Complaint: {cid} | Reason: {c['reason']} | Status: {c['status']}")

    # Step 3: Respond to complaint
    print("\n[Responding to Complaint]")
    response_text = "I thought I had permission."
    success, msg = ch.respond_to_complaint(cid, response_text)
    print(msg)

    # Step 4: Review complaint (super user action)
    print("\n[Super User Review]")
    punished_user = "bob"
    penalty = 5
    success, msg = ch.review_complaint(cid, punished_user, penalty)
    print(msg)

    # Step 5: Show full complaint record
    print("\n[Final Complaint Record]")
    all_data = ch.get_all_complaints()
    print(all_data[cid])

if __name__ == "__main__":
    test_complaints()
