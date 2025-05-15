from services.user_manager import load_user
from services.statistics import get_user_statistics

user = load_user("Khalid")
stats = get_user_statistics(user)

print("\n--- Usage Statistics ---")
for key, value in stats.items():
    print(f"{key}: {value}")