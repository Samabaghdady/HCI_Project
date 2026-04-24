import tkinter as tk
from tkinter import ttk, messagebox
import os

from app.reports.report_generator import ReportGenerator


# =========================
# THEME
# =========================
BG_COLOR = "#0f172a"
CARD_COLOR = "#020617"
PRIMARY = "#38bdf8"
SUCCESS = "#22c55e"
DANGER = "#ef4444"
TEXT = "#e5e7eb"
MUTED = "#94a3b8"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_TEXT = ("Segoe UI", 11)


class ReportViewer(tk.Toplevel):

    def __init__(self, master, db):
        super().__init__(master)

        self.db = db
        self.reporter = ReportGenerator(db)

        self.title("Attendance Reports")
        self.geometry("820x560")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self._setup_ui()

    # =========================
    # UI SETUP
    # =========================
    def _setup_ui(self):

        card = tk.Frame(self, bg=CARD_COLOR)
        card.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Label(
            card,
            text="Attendance Reports",
            font=FONT_TITLE,
            fg=PRIMARY,
            bg=CARD_COLOR
        ).pack(pady=15)

        form = tk.Frame(card, bg=CARD_COLOR)
        form.pack(fill="x", padx=20)

        tk.Label(
            form,
            text="Select Lecture",
            fg=TEXT,
            bg=CARD_COLOR
        ).grid(row=0, column=0, sticky="w")

        lectures = self.db.list_lectures()

        if not lectures:
            tk.Label(
                form,
                text="No lectures available",
                fg=DANGER,
                bg=CARD_COLOR
            ).grid(row=0, column=1, sticky="w")
            return

        self.lecture_map = {
    f"{l['course_name']} (ID {l['id']})": l['id']
    for l in lectures
}


        self.lecture_cb = ttk.Combobox(
            form,
            values=list(self.lecture_map.keys()),
            state="readonly",
            width=55
        )
        self.lecture_cb.grid(row=0, column=1, padx=10, pady=8)

        # ---------- Buttons ----------
        btns = tk.Frame(card, bg=CARD_COLOR)
        btns.pack(pady=10)

        tk.Button(
            btns,
            text="Generate CSV",
            bg=SUCCESS,
            fg="black",
            width=18,
            relief="flat",
            command=self._gen_csv
        ).pack(side="left", padx=10)

        tk.Button(
            btns,
            text="Generate PDF",
            bg=PRIMARY,
            fg="black",
            width=18,
            relief="flat",
            command=self._gen_pdf
        ).pack(side="left", padx=10)

        # ---------- Preview ----------
        tk.Label(
            card,
            text="CSV Preview",
            fg=MUTED,
            bg=CARD_COLOR
        ).pack(anchor="w", padx=20, pady=(15, 4))

        preview_frame = tk.Frame(card, bg=BG_COLOR)
        preview_frame.pack(padx=20, pady=(0, 15), fill="both", expand=True)

        self.text = tk.Text(
            preview_frame,
            bg="#020617",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            wrap="none"
        )
        self.text.pack(fill="both", expand=True)

    # =========================
    # ACTIONS
    # =========================
    def _gen_csv(self):
        key = self.lecture_cb.get()
        if not key:
            messagebox.showerror(
                "Select Lecture",
                "Please choose a lecture first."
            )
            return

        lecture_id = self.lecture_map[key]
        filename = self.reporter.generate_csv(lecture_id)

        messagebox.showinfo(
            "CSV Generated",
            f"CSV file saved to:\n{filename}"
        )

        self._show_csv(filename)

    def _gen_pdf(self):
        key = self.lecture_cb.get()
        if not key:
            messagebox.showerror(
                "Select Lecture",
                "Please choose a lecture first."
            )
            return

        lecture_id = self.lecture_map[key]
        filename = self.reporter.generate_pdf(lecture_id)

        messagebox.showinfo(
            "PDF Generated",
            f"PDF file saved to:\n{filename}"
        )

    # =========================
    # CSV PREVIEW
    # =========================
    def _show_csv(self, filename):
        if not filename or not os.path.exists(filename):
            return

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
