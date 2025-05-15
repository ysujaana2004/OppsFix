# test_shared_files.py

from services.collaboration import get_shared_files_for_user

def test_shared_files():
    username = input("Enter a username to check shared files: ").strip()
    shared_files = get_shared_files_for_user(username)

    if not shared_files:
        print(f"No shared files found for {username}.")
    else:
        print(f"Shared files for {username}:")
        for f in shared_files:
            print(f"  - {f}")

if __name__ == "__main__":
    test_shared_files()
