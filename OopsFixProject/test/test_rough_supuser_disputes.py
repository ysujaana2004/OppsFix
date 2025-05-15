from services.complaint_handler import ComplaintHandler

ch = ComplaintHandler()
all_c = ch.get_all_complaints()
for cid, record in all_c.items():
    if record['status'] == 'responded':
        print(f"{cid}: from {record['complainant']} vs {record['defendant']}, response = {record['response']}")
