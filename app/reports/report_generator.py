import csv
import os
from fpdf import FPDF
from datetime import datetime


class ReportGenerator:
    def __init__(self, db):
        """
        db: instance of Database (from app.database.db)
        """
        self.db = db

    # =========================
    # Helper to get lecture details (course name, instructor name)
    # =========================
    def _get_lecture_details(self, lecture_id):
        """Fetch course_name and instructor name for the lecture"""
        try:
            cursor = self.db.conn.cursor()
            # Common column patterns – adjust based on your lectures table
            # Usually: course_name, instructor_id → join with instructors table
            # Or direct instructor name if stored in lectures
            query = """
                SELECT l.course_name, i.name 
                FROM lectures l
                LEFT JOIN instructors i ON l.instructor_id = i.id
                WHERE l.id = %s
            """
            cursor.execute(query, (lecture_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result[0] or "N/A", result[1] or "N/A"
            else:
                return "N/A", "N/A"
        except Exception as e:
            print(f"Error fetching lecture details: {e}")
            # Fallback simple query if join fails
            try:
                cursor = self.db.conn.cursor()
                cursor.execute("SELECT course_name FROM lectures WHERE id = %s", (lecture_id,))
                course = cursor.fetchone()
                cursor.close()
                return course[0] if course else "N/A", "N/A"
            except:
                return "N/A", "N/A"

    # =========================
    # Helper to get all registered students from DB
    # =========================
    def _get_all_students(self):
        """Fetch all students from the database (code, name)"""
        try:
            cursor = self.db.conn.cursor()
            
            possible_queries = [
                "SELECT student_id, name FROM students ORDER BY student_id",
                "SELECT student_code, name FROM students ORDER BY student_code",
                "SELECT code, name FROM students ORDER BY code",
                "SELECT id, name FROM students ORDER BY id",
            ]
            
            for query in possible_queries:
                try:
                    cursor.execute(query)
                    students = cursor.fetchall()
                    if students:
                        return [(str(code), str(name or "")) for code, name in students]
                except:
                    continue
            
            print("None of the common column names worked. Table structure:")
            cursor.execute("DESCRIBE students")
            columns = cursor.fetchall()
            print("Columns in 'students' table:", [col[0] for col in columns])
            
            return []
            
        except Exception as e:
            print(f"Error accessing students table: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    # =========================
    # CSV REPORT
    # =========================
    def generate_csv(self, lecture_id, out_folder="reports"):
        os.makedirs(out_folder, exist_ok=True)

        # Get lecture details
        course_name, instructor_name = self._get_lecture_details(lecture_id)

        # Get present students
        present_rows = self.db.get_lecture_report(lecture_id)
        present_codes = {str(code) for code, _, _, _ in present_rows if code is not None}

        # Get all students
        all_students = self._get_all_students()

        total_students = len(all_students)
        total_present = len(present_codes)
        total_absent = total_students - total_present

        filename = os.path.join(
            out_folder,
            f"lecture_{lecture_id}{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        )

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Header Section with Instructor & Course
            writer.writerow(["Attendance Management System"])
            writer.writerow([])
            writer.writerow(["Course Name:", course_name])
            writer.writerow(["Instructor Name:", instructor_name])
            writer.writerow(["Lecture ID:", lecture_id])
            writer.writerow(["Generated on:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])

            # Table Header
            writer.writerow(["Student Code", "Student Name", "Status", "Attendance Time"])

            # All students
            for code, name in all_students:
                if code in present_codes:
                    ts = next((t for c, _, _, t in present_rows if str(c) == code), "")
                    writer.writerow([code, name, "Present", ts or ""])
                else:
                    writer.writerow([code, name, "Absent", ""])

            # Summary
            writer.writerow([])
            writer.writerow(["Attendance Summary"])
            writer.writerow(["Total Registered Students:", total_students])
            writer.writerow(["Total Present:", total_present])
            writer.writerow(["Total Absent:", total_absent])
            writer.writerow([])
            writer.writerow(["End of Report"])

        return filename

    # =========================
    # PDF REPORT
    # =========================
    def generate_pdf(self, lecture_id, out_folder="reports"):
        os.makedirs(out_folder, exist_ok=True)

        # Get lecture details
        course_name, instructor_name = self._get_lecture_details(lecture_id)

        # Get present students
        present_rows = self.db.get_lecture_report(lecture_id)
        present_codes = {str(code) for code, _, _, _ in present_rows if code is not None}

        # Get all students
        all_students = self._get_all_students()

        total_students = len(all_students)
        total_present = len(present_codes)
        total_absent = total_students - total_present

        filename = os.path.join(
            out_folder,
            f"lecture_{lecture_id}{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        )

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 15, "Attendance Management System", ln=True, align="C")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Attendance Report", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.ln(8)

        # Lecture Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Course: {course_name}", ln=True)
        pdf.cell(0, 8, f"Instructor: {instructor_name}", ln=True)
        pdf.cell(0, 8, f"Lecture ID: {lecture_id}", ln=True)
        pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)

        # Description
        pdf.set_font("Arial", size=11)
        pdf.ln(10)

        if total_students == 0:
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, "No registered students found in database.", ln=True)
            pdf.output(filename)
            return filename

        # Table Header
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 10, "Code", border=1, align="C")
        pdf.cell(60, 10, "Name", border=1, align="C")
        pdf.cell(30, 10, "Status", border=1, align="C")
        pdf.cell(60, 10, "Time", border=1, align="C", ln=True)

        # Table Rows
        pdf.set_font("Arial", size=10)
        for code, name in all_students:
            if code in present_codes:
                ts = next((t for c, _, _, t in present_rows if str(c) == code), "-")
                status = "Present"
            else:
                ts = "-"
                status = "Absent"
            pdf.cell(40, 8, str(code), border=1)
            pdf.cell(60, 8, str(name), border=1)
            pdf.cell(30, 8, status, border=1)
            pdf.cell(60, 8, str(ts), border=1, ln=True)

        # Summary
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Attendance Summary", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 8, f"Total Registered Students: {total_students}", ln=True)
        pdf.cell(0, 8, f"Total Present: {total_present}", ln=True)
        pdf.cell(0, 8, f"Total Absent: {total_absent}", ln=True)

        # Footer
        pdf.ln(15)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "End of Report | Automated Face Recognition Attendance System", align="C")

        pdf.output(filename)
        return filename