import cv2
import numpy as np
import face_recognition


class FaceRecognizer:
    def __init__(self, db, tolerance=0.38):
        self.db = db
        self.tolerance = tolerance
        self.known_students = []
        self.known_encodings = []
        self._load_students()

    def _load_students(self):
        self.known_students.clear()
        self.known_encodings.clear()

        students = self.db.get_all_students()
        print(f"[FaceRecognizer] Loaded {len(students)} students from database")

        for sid, name, encoding in students:
            if isinstance(encoding, np.ndarray):
                self.known_students.append((sid, name, encoding))
                self.known_encodings.append(encoding)

    def start_video_capture(self, device=0):
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            raise RuntimeError("Cannot open camera")
        return cap

    def recognize_faces(self, frame):
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        results = []

        for encoding in encodings:
            name = "Unknown"
            student_id = None

            if self.known_encodings:
                distances = face_recognition.face_distance(
                    self.known_encodings, encoding
                )

                sorted_idx = np.argsort(distances)
                best = distances[sorted_idx[0]]

                print(f"[DEBUG] Best distance = {best:.3f}")

                # ✅ STRICT RULES
                if best < self.tolerance:
                    if len(sorted_idx) > 1:
                        second = distances[sorted_idx[1]]
                        if (second - best) >= 0.12:
                            student_id, name, _ = self.known_students[sorted_idx[0]]
                    else:
                        student_id, name, _ = self.known_students[sorted_idx[0]]

            results.append({
                "student_id": student_id,
                "name": name,
                "distance": float(best) if student_id else None
            })

        boxes = [(t*2, r*2, b*2, l*2) for (t, r, b, l) in boxes]
        return boxes, results
