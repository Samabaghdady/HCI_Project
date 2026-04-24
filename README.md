# 🎓 Face Recognition–Based Attendance Management System

## 1. Project Overview

This project is a multi-face recognition–based attendance management system designed for academic environments such as universities and training institutes.
The system automatically detects and recognizes multiple faces in real time, records attendance for lecture sessions, and generates detailed attendance reports.

The primary goal of the project is to reduce manual attendance effort, increase accuracy, and improve usability through a clear Human–Computer Interaction (HCI) design.

## 2. Key Features

Multi-Face Recognition

Detects and recognizes multiple students simultaneously using a camera.

Works in real time during lecture sessions.

Automatic Attendance Recording

Marks attendance automatically once a student is recognized.

Prevents duplicate attendance for the same session.

Lecture & Session Management

Create lecture sessions with:

Instructor

Course name

Room number

Date and time slot

Instructor Integration

Each lecture session is linked to a specific instructor.

Attendance Reports

Generate attendance reports per lecture.

Export reports in:

CSV format

PDF format

User-Friendly Interface (HCI Focused)

Simple dashboard for navigation.

Clear feedback during attendance sessions.

Minimal user interaction required during operation.

## 3. Technologies Used

Programming Language: Python

GUI Framework: Tkinter

Computer Vision:

OpenCV

face_recognition library

Database: MySQL

Reporting:

CSV

PDF (FPDF)

## 4. System Architecture

The system follows a modular and layered architecture:

```
app/
├── database/
│   ├── db.py          # Database access & SQL logic
│   └── models.py      # Data models
│
├── recognition/
│   ├── face_recognizer.py   # Multi-face recognition logic
│   └── train_model.py       # Model training utilities
│
├── ui/
│   ├── dashboard.py         # Main navigation
│   ├── lecture_form.py      # Create lecture sessions
│   ├── attendance_session.py # Live attendance capture
│   └── report_viewer.py     # Report viewing & export
│
├── reports/
│   └── report_generator.py  # CSV & PDF report generation
│
├── utils/
│   ├── camera.py            # Camera utilities
│   └── helpers.py           # Helper functions
│
└── main.py                  # Application entry point
```

## 5. How the System Works

Instructor creates a lecture session

Selects instructor, room, date, and time slot.

Attendance session starts

Camera captures live video.

Multiple faces are detected and recognized simultaneously.

Attendance is recorded

Each recognized student is marked present once per session.

Attendance is stored in the database.

Reports are generated

Attendance data can be exported as CSV or PDF.

Reports can be viewed directly from the application.

## 6. Human–Computer Interaction (HCI) Considerations

Minimal Interaction:
Students do not need to interact with the system manually.

Immediate Feedback:
Recognized students are shown live during attendance sessions.

Error Prevention:
Duplicate attendance is automatically prevented.

Consistency:
All user interfaces follow a unified layout and navigation pattern.

## 7. Installation & Setup

### Requirements

- Python 3.9+
- MySQL Server
- Webcam

### Python Dependencies

Install all required packages using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Note:** On Windows with Python 3.13+, `dlib-bin` is used instead of `dlib` to avoid compilation issues. The `requirements.txt` file is already configured for this.

### Database Setup

1. Create a MySQL database:

```sql
CREATE DATABASE attendance_system;
```

2. Update database credentials in `app/database/db.py`:

```python
self.conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
    database="attendance_system"
)
```

The database tables will be created automatically when you first run the application.

## 8. Running the Application

```bash
python main.py
```

## 9. Future Enhancements

Role-based access (Admin / Instructor)

Attendance analytics and statistics

Cloud database support

Face spoofing detection

Mobile or web-based interface

## 10. Conclusion

This project demonstrates how computer vision, database systems, and HCI principles can be combined to build a practical and efficient attendance management solution.
The system improves accuracy, reduces workload, and provides a smooth user experience suitable for real academic environments.