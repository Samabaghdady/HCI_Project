import mysql.connector
import pickle
import numpy as np


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_system"
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    # =========================
    # TABLE CREATION
    # =========================
    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_code VARCHAR(50) UNIQUE,
            name VARCHAR(255),
            face_encoding LONGBLOB
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            email VARCHAR(255)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS lectures (
            id INT AUTO_INCREMENT PRIMARY KEY,
            instructor_id INT,
            course_name VARCHAR(255),
            room VARCHAR(100),
            session_date DATE,
            start_time TIME,
            end_time TIME,
            FOREIGN KEY (instructor_id) REFERENCES instructors(id)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lecture_id INT,
            student_id INT,
            attendance_time DATETIME,
            status ENUM('Present','Late') DEFAULT 'Present',
            UNIQUE (lecture_id, student_id),
            FOREIGN KEY (lecture_id) REFERENCES lectures(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        );
        """)

        self.conn.commit()

    # =========================
    # STUDENT METHODS
    # =========================
    def add_student(self, student_code, name, face_encoding):
        blob = pickle.dumps(face_encoding)
        self.cursor.execute("""
            INSERT INTO students (student_code, name, face_encoding)
            VALUES (%s, %s, %s)
        """, (student_code, name, blob))
        self.conn.commit()

    def get_all_students(self):
        """
        Used by FaceRecognizer
        Returns: (id, name, face_encoding)
        """
        self.cursor.execute("""
            SELECT id, name, face_encoding FROM students
        """)

        students = []

        for sid, name, blob in self.cursor.fetchall():
            if blob is None:
                continue  # تجاهل أي طالب ملوش Face Encoding

            try:
                encoding = pickle.loads(blob)
                # Ensure encoding is a numpy array
                if not isinstance(encoding, np.ndarray):
                    encoding = np.array(encoding)
            except Exception as e:
                print(f"[WARNING] Failed to load encoding for student {name} (ID: {sid}): {e}")
                continue  # أمان إضافي لو البيانات بايظة

            students.append((sid, name, encoding))

        return students

    # =========================
    # INSTRUCTOR METHODS
    # =========================
    def add_instructor(self, name, email):
        self.cursor.execute("""
            INSERT INTO instructors (name, email)
            VALUES (%s, %s)
        """, (name, email))
        self.conn.commit()

    def get_instructors(self):
        self.cursor.execute("""
            SELECT id, name FROM instructors
        """)
        return [
            {"id": i, "name": n}
            for i, n in self.cursor.fetchall()
        ]

    # =========================
    # LECTURE METHODS
    # =========================
    def create_lecture(self, instructor_id, course_name, room,
                       session_date, start_time, end_time):
        self.cursor.execute("""
            INSERT INTO lectures
            (instructor_id, course_name, room, session_date, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            instructor_id,
            course_name,
            room,
            session_date,
            start_time,
            end_time
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def list_lectures(self):
        self.cursor.execute("""
            SELECT id, course_name, session_date, start_time
            FROM lectures
            ORDER BY session_date DESC, start_time DESC
        """)
        return [
            {
                "id": i,
                "course_name": c,
                "session_date": d,
                "start_time": t
            }
            for i, c, d, t in self.cursor.fetchall()
        ]

    # =========================
    # ATTENDANCE METHODS
    # =========================
    def mark_attendance(self, lecture_id, student_id, status="Present"):
        self.cursor.execute("""
            INSERT IGNORE INTO attendance
            (lecture_id, student_id, attendance_time, status)
            VALUES (%s, %s, NOW(), %s)
        """, (lecture_id, student_id, status))
        self.conn.commit()

    # =========================
    # REPORT METHODS
    # =========================
    def get_student_report(self, student_id):
        self.cursor.execute("""
            SELECT l.course_name, l.session_date, a.status
            FROM attendance a
            JOIN lectures l ON a.lecture_id = l.id
            WHERE a.student_id = %s
            ORDER BY l.session_date
        """, (student_id,))
        return self.cursor.fetchall()

    def get_lecture_report(self, lecture_id):
        self.cursor.execute("""
            SELECT s.student_code, s.name, a.status, a.attendance_time
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.lecture_id = %s
        """, (lecture_id,))
        return self.cursor.fetchall()

    # =========================
    # CLEANUP
    # =========================
    def close(self):
        self.cursor.close()
        self.conn.close()
