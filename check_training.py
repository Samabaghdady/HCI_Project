"""
Quick script to check if the dataset has been trained.
Run this to verify students are in the database.
"""
from app.database.db import Database

def check_training():
    db = Database()
    
    students = db.get_all_students()
    
    print("=" * 50)
    print("TRAINING STATUS CHECK")
    print("=" * 50)
    
    if len(students) == 0:
        print("\n❌ NO STUDENTS FOUND IN DATABASE!")
        print("\nYou need to train the dataset first.")
        print("\nTo train:")
        print("  1. Open the main application")
        print("  2. Click 'Train Dataset' button")
        print("  OR")
        print("  3. Run: python -m app.recognition.train_model")
    else:
        print(f"\n✅ Found {len(students)} students in database:")
        print("\nStudent List:")
        for sid, name, encoding in students:
            encoding_status = "✓ Has encoding" if encoding is not None else "✗ No encoding"
            print(f"  - {name} (ID: {sid}) - {encoding_status}")
    
    print("\n" + "=" * 50)
    db.close()

if __name__ == "__main__":
    check_training()

