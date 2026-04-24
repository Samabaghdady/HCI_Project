import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


# =========================
# THEME
# =========================
BG_COLOR = "#0f172a"
CARD_COLOR = "#020617"
PRIMARY = "#38bdf8"
SUCCESS = "#22c55e"
DANGER = "#ef4444"
TEXT = "#e5e7eb"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_TEXT = ("Segoe UI", 11)


class LectureForm(tk.Toplevel):

    def __init__(self, master, db):
        super().__init__(master)

        self.db = db
        self.title("Create Lecture Session")
        self.geometry("520x450")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self._load_instructors()
        self._setup_ui()

    # =========================
    # DATA
    # =========================
    def _load_instructors(self):
        self.instructors = self.db.get_instructors()

    # =========================
    # UI SETUP
    # =========================
    def _setup_ui(self):

        card = tk.Frame(self, bg=CARD_COLOR)
        card.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(
            card,
            text="Lecture Details",
            font=FONT_TITLE,
            fg=PRIMARY,
            bg=CARD_COLOR
        ).pack(pady=15)

        form = tk.Frame(card, bg=CARD_COLOR)
        form.pack(padx=20, pady=10, fill="x")

        # ---------- Instructor ----------
        self._field(
            form, "Instructor",
            self._create_instructor_cb(form)
        )

        # ---------- Course ----------
        self.course = self._field(
            form, "Course Name",
            tk.Entry(form)
        )

        # ---------- Room ----------
        self.room = self._field(
            form, "Room",
            tk.Entry(form)
        )

        # ---------- Buttons ----------
        btns = tk.Frame(card, bg=CARD_COLOR)
        btns.pack(pady=25)

        tk.Button(
            btns,
            text="Save Session",
            bg=SUCCESS,
            fg="black",
            relief="flat",
            width=16,
            command=self._save
        ).pack(side="left", padx=10)

        tk.Button(
            btns,
            text="Cancel",
            bg=DANGER,
            fg="white",
            relief="flat",
            width=16,
            command=self.destroy
        ).pack(side="left", padx=10)

    # =========================
    # FIELD HELPER
    # =========================
    def _field(self, parent, label, widget):
        container = tk.Frame(parent, bg=CARD_COLOR)
        container.pack(fill="x", pady=8)

        tk.Label(
            container,
            text=label,
            fg=TEXT,
            bg=CARD_COLOR,
            font=FONT_TEXT
        ).pack(anchor="w")

        widget.pack(fill="x", pady=4)
        return widget

    def _create_instructor_cb(self, parent):
        self.instructor_var = tk.StringVar()

        self.instructor_map = {
            ins["name"]: ins["id"]
            for ins in self.instructors
        }

        cb = ttk.Combobox(
            parent,
            textvariable=self.instructor_var,
            values=list(self.instructor_map.keys()),
            state="readonly"
        )
        return cb

    # =========================
    # SAVE LOGIC
    # =========================
    def _save(self):
        try:
            instructor_id = self.instructor_map[self.instructor_var.get()]
            course_name = self.course.get().strip()
            room = self.room.get().strip()

            if not course_name:
                raise ValueError

            # ✅ AUTO VALUES (no GUI input)
            session_date = datetime.today().date()
            start_time = datetime.now().time().replace(second=0, microsecond=0)
            duration_min = 90  # default duration
            end_time = (
                datetime.combine(session_date, start_time)
                + timedelta(minutes=duration_min)
            ).time()

        except Exception:
            messagebox.showerror(
                "Invalid Input",
                "Please fill all required fields."
            )
            return

        self.db.create_lecture(
            instructor_id,
            course_name,
            room,
            session_date,
            start_time,
            end_time
        )

        messagebox.showinfo(
            "Saved",
            "Lecture session created successfully."
        )
        self.destroy()
