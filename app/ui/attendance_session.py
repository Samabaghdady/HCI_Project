import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import cv2
from PIL import Image, ImageTk

from app.recognition.face_recognizer import FaceRecognizer


# =========================
# THEME
# =========================
BG_COLOR = "#0f172a"
PANEL_COLOR = "#020617"
PRIMARY = "#38bdf8"
SUCCESS = "#22c55e"
DANGER = "#ef4444"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_TEXT = ("Segoe UI", 11)


class AttendanceSession(tk.Toplevel):

    def __init__(self, master, db, lectures):
        super().__init__(master)

        self.db = db
        self.lectures = lectures
        self.face_rec = FaceRecognizer(self.db, tolerance=0.50)

        self.active = False
        self.recognized_students = set()
        self.face_recognition_history = {}

        # ✅ NEW (delay fix)
        self.frame_count = 0
        self.recog_every = 5
        self.last_boxes = []
        self.last_results = []

        self.title("Attendance Session")
        self.geometry("1100x720")
        self.configure(bg=BG_COLOR)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        if not self.face_rec.known_students:
            messagebox.showwarning(
                "No Students Found",
                "No students found in database.\n\n"
                "Please train the dataset first."
            )

        self._setup_ui()

    # =========================
    # UI SETUP
    # =========================
    def _setup_ui(self):

        left = tk.Frame(self, bg=PANEL_COLOR, width=320)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(
            left, text="Attendance Control",
            font=FONT_TITLE, fg=PRIMARY, bg=PANEL_COLOR
        ).pack(pady=20)

        tk.Label(left, text="Select Lecture", fg=TEXT, bg=PANEL_COLOR)\
            .pack(anchor="w", padx=20)

        self.lecture_var = tk.StringVar()
        self.lecture_map = {
            f"{l['id']} - {l['course_name']}": l['id']
            for l in self.lectures
        }

        self.lecture_cb = ttk.Combobox(
            left,
            textvariable=self.lecture_var,
            values=list(self.lecture_map.keys()),
            state="readonly",
            width=35
        )
        self.lecture_cb.pack(padx=20, pady=8)

        btn_frame = tk.Frame(left, bg=PANEL_COLOR)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame, text="Start Session",
            bg=SUCCESS, fg="black",
            width=14, relief="flat",
            command=self.start_session
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = tk.Button(
            btn_frame, text="Stop Session",
            bg=DANGER, fg="white",
            width=14, relief="flat",
            command=self.stop_session,
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.status_label = tk.Label(
            left, text="Status: Idle",
            fg=MUTED, bg=PANEL_COLOR
        )
        self.status_label.pack(pady=10)

        tk.Label(left, text="Attendance Log", fg=TEXT, bg=PANEL_COLOR)\
            .pack(anchor="w", padx=20, pady=(15, 0))

        self.listbox = tk.Listbox(
            left, bg="#020617", fg=TEXT,
            height=20, width=40, relief="flat"
        )
        self.listbox.pack(padx=20, pady=8, fill="both", expand=True)

        right = tk.Frame(self, bg=BG_COLOR)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            right, text="Live Camera Preview",
            font=FONT_TITLE, fg=PRIMARY, bg=BG_COLOR
        ).pack(pady=15)

        self.canvas = tk.Label(right, bg="black", bd=2, relief="solid")
        self.canvas.pack(padx=20, pady=10, fill="both", expand=True)

    # =========================
    # SESSION CONTROL
    # =========================
    def start_session(self):
        if self.active:
            return

        if not self.lecture_cb.get():
            messagebox.showerror("Error", "Please select a lecture first.")
            return

        self.lecture_id = self.lecture_map[self.lecture_cb.get()]
        self.active = True
        self.recognized_students.clear()
        self.face_recognition_history.clear()

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Status: Running", fg=SUCCESS)

        threading.Thread(target=self._camera_loop, daemon=True).start()

    def stop_session(self):
        self.active = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped", fg=DANGER)

    def on_close(self):
        self.active = False
        self.after(100, self.destroy)

    # =========================
    # CAMERA LOOP (OPTIMIZED)
    # =========================
    def _camera_loop(self):
        try:
            cap = self.face_rec.start_video_capture()
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        except Exception as e:
            self._safe_log(f"Camera error: {e}")
            return

        try:
            while self.active:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (640, 480))
                self.frame_count += 1

                # 🧠 HEAVY PART (every N frames)
                if self.frame_count % self.recog_every == 0:
                    boxes, results = self.face_rec.recognize_faces(frame)
                    self.last_boxes = boxes
                    self.last_results = results
                    now = time.time()

                    for r in results:
                        sid = r["student_id"]
                        name = r["name"]

                        if sid:
                            history = self.face_recognition_history.setdefault(
                                sid, {"count": 0, "last": now}
                            )
                            history["count"] += 1
                            history["last"] = now

                            if history["count"] >= 6 and sid not in self.recognized_students:
                                self.db.mark_attendance(self.lecture_id, sid)
                                self.recognized_students.add(sid)
                                ts = datetime.now().strftime("%H:%M:%S")
                                self._safe_log(f"✓ {name} marked present at {ts}")

                # 🖼️ FAST DISPLAY
                self._update_preview(frame, self.last_boxes, self.last_results)
                time.sleep(0.01)

        finally:
            cap.release()

    # =========================
    # UI HELPERS
    # =========================
    def _safe_log(self, text):
        def safe():
            if self.listbox.winfo_exists():
                self.listbox.insert(tk.END, text)
                self.listbox.yview_moveto(1)
        self.after(0, safe)

    def _update_preview(self, frame, boxes, results):
        if not self.active:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        for (top, right, bottom, left), r in zip(boxes, results):
            color = (0, 255, 0) if r["student_id"] else (255, 0, 0)
            label = r["name"] if r["student_id"] else "Unknown"
            cv2.rectangle(rgb, (left, top), (right, bottom), color, 2)
            cv2.putText(
                rgb, label, (left, top - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

        img = Image.fromarray(rgb)
        tkimg = ImageTk.PhotoImage(img)

        def safe_update():
            if self.canvas.winfo_exists():
                self.canvas.configure(image=tkimg)
                self.canvas.image = tkimg

        self.after(0, safe_update)
