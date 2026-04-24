import tkinter as tk
from app.ui.dashboard import Dashboard


def main():
    root = tk.Tk()
    root.title("Face Recognition Attendance System")
    root.geometry("900x600")
    root.eval('tk::PlaceWindow . center')

    Dashboard(root)

    root.mainloop()


if __name__ == "__main__":
    main()
