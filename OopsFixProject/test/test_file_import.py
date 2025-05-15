# test_file_import.py

from services.file_loader import load_text_from_file

def test_import():
    filepath = input("Enter path to .txt file: ").strip()
    success, result = load_text_from_file(filepath)
    
    if success:
        print("\n--- File Content ---")
        print(result)
    else:
        print("Failed to load file:", result)

if __name__ == "__main__":
    test_import()