import os
import cv2
import numpy as np
import pickle
import face_recognition
from app.database.db import Database


def train_dataset(dataset_path=None):
    """
    Offline training script.
    Reads images and stores face encodings directly in the database.
    Folder name must be the student_code.
    Uses multiple encodings per student and averages them for better accuracy.
    """
    
    # Auto-detect dataset path if not provided
    if dataset_path is None:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to app directory, then to dataset
        app_dir = os.path.dirname(script_dir)
        dataset_path = os.path.join(app_dir, "dataset")
    
    # Convert to absolute path
    dataset_path = os.path.abspath(dataset_path)

    db = Database()

    # Check if dataset path exists
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset path not found: {dataset_path}")
        print(f"[INFO] Please ensure the dataset folder exists at: {os.path.abspath(dataset_path)}")
        db.close()
        return

    student_dirs = [d for d in os.listdir(dataset_path) 
                   if os.path.isdir(os.path.join(dataset_path, d))]

    if not student_dirs:
        print(f"[WARNING] No student directories found in {dataset_path}")
        db.close()
        return

    print(f"[INFO] Found {len(student_dirs)} students in dataset")
    print(f"[INFO] Processing dataset at: {os.path.abspath(dataset_path)}\n")

    for student_code in student_dirs:
        student_dir = os.path.join(dataset_path, student_code)

        print(f"[INFO] Processing student: {student_code}")

        encodings = []
        processed_images = 0

        image_files = [f for f in os.listdir(student_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            print(f"[WARNING] No image files found for {student_code}")
            continue

        for img_name in image_files:
            img_path = os.path.join(student_dir, img_name)

            image = cv2.imread(img_path)
            if image is None:
                print(f"[SKIP] Could not read image: {img_name}")
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            
            if not boxes:
                print(f"[SKIP] No face detected in: {img_name}")
                continue

            faces = face_recognition.face_encodings(rgb, boxes)

            if faces:
                # Use the first face found in the image
                encodings.append(faces[0])
                processed_images += 1
                print(f"[OK] Encoded: {img_name} (face detected)")

        if encodings:
            # Average all encodings for better accuracy
            if len(encodings) > 1:
                avg_encoding = np.mean(encodings, axis=0)
                print(f"[INFO] Averaged {len(encodings)} encodings for {student_code}")
            else:
                avg_encoding = encodings[0]

            # Check if student already exists
            db.cursor.execute("SELECT id FROM students WHERE student_code = %s", (student_code,))
            existing = db.cursor.fetchone()

            if existing:
                # Update existing student
                blob = pickle.dumps(avg_encoding)
                db.cursor.execute("""
                    UPDATE students 
                    SET face_encoding = %s 
                    WHERE student_code = %s
                """, (blob, student_code))
                db.conn.commit()
                print(f"[UPDATED] Student {student_code} encoding updated in database")
            else:
                # Add new student
                db.add_student(
                    student_code=student_code,
                    name=student_code,
                    face_encoding=avg_encoding
                )
                print(f"[SAVED] Student {student_code} added to database")
        else:
            print(f"[ERROR] No valid face encodings found for {student_code}")

        print()  # Empty line for readability

    db.close()
    print("[DONE] Training completed successfully.")


if __name__ == "__main__":
    train_dataset()
