import tkinter as tk
from tkinter import ttk, messagebox

from app.ui.lecture_form import LectureForm
from app.ui.attendance_session import AttendanceSession
from app.ui.report_viewer import ReportViewer
from app.database.db import Database


# =========================
# THEME
# =========================
BG_COLOR = "#0f172a"
CARD_COLOR = "#020617"
PRIMARY = "#38bdf8"
SUCCESS = "#22c55e"
WARNING = "#facc15"
TEXT_COLOR = "#e5e7eb"
MUTED = "#94a3b8"

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_CARD = ("Segoe UI", 14, "bold")
FONT_TEXT = ("Segoe UI", 11)


class Dashboard(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.pack(fill="both", expand=True)

        self.db = Database()

        self._create_widgets()
        self._set_status("Ready")

        self.master.protocol("WM_DELETE_WINDOW", self._on_close)

    # =========================
    # UI SETUP
    # =========================
    def _create_widgets(self):

        # ===== Header =====
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", pady=20)

        tk.Label(
            header,
            text="Lecture Attendance Dashboard",
            font=FONT_TITLE,
            fg=PRIMARY,
            bg=BG_COLOR
        ).pack()

        tk.Label(
            header,
            text="Face Recognition Based Attendance System",
            font=FONT_TEXT,
            fg=MUTED,
            bg=BG_COLOR
        ).pack(pady=5)

        # ===== Cards Area =====
        cards = tk.Frame(self, bg=BG_COLOR)
        cards.pack(pady=40)

        self._create_card(
            cards,
            title="Create / Edit Lecture",
            desc="Add lectures, instructors and schedules",
            color=PRIMARY,
            command=self.open_lecture_form,
            col=0
        )

        self._create_card(
            cards,
            title="Start Attendance",
            desc="Run face recognition attendance session",
            color=SUCCESS,
            command=self.open_session,
            col=1
        )

        self._create_card(
            cards,
            title="View Reports",
            desc="Generate CSV & PDF attendance reports",
            color=WARNING,
            command=self.open_reports,
            col=2
        )

        # ===== Status Bar =====
        self.status = tk.Label(
            self,
            text="",
            bg="#020617",
            fg=MUTED,
            anchor="w",
            padx=10
        )
        self.status.pack(side="bottom", fill="x")

    # =========================
    # CARD CREATOR
    # =========================
    def _create_card(self, parent, title, desc, color, command, col):
        card = tk.Frame(
            parent,
            bg=CARD_COLOR,
            width=260,
            height=160,
            relief="flat"
        )
        card.grid(row=0, column=col, padx=20)
        card.grid_propagate(False)

        tk.Label(
            card,
            text=title,
            font=FONT_CARD,
            fg=color,
            bg=CARD_COLOR
        ).pack(pady=(25, 10))

        tk.Label(
            card,
            text=desc,
            font=FONT_TEXT,
            fg=MUTED,
            bg=CARD_COLOR,
            wraplength=220,
            justify="center"
        ).pack(pady=5)

        tk.Button(
            card,
            text="Open",
            font=("Segoe UI", 11, "bold"),
            bg=color,
            fg="black",
            relief="flat",
            width=12,
            command=command
        ).pack(pady=20)

    # =========================
    # STATUS
    # =========================
    def _set_status(self, text):
        self.status.config(text=f"  {text}")

    # =========================
    # ACTIONS
    # =========================
    def open_lecture_form(self):
        self._set_status("Opening lecture form...")
        LectureForm(self.master, self.db)

    def open_session(self):
        lectures = self.db.list_lectures()

        if not lectures:
            messagebox.showinfo(
                "No Lectures",
                "No lectures found. Please create a lecture first."
            )
            self._set_status("No lectures available")
            return

        self._set_status("Attendance session started")
        AttendanceSession(self.master, self.db, lectures)

    def open_reports(self):
        self._set_status("Opening reports viewer...")
        ReportViewer(self.master, self.db)

    # =========================
    def _on_close(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.master.destroy()
