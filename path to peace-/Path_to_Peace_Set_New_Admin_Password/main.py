import tkinter as tk
from tkinter import simpledialog, messagebox
from database import init_db, create_default_admin, admin_exists
from login import LoginWindow


def main():
    # Create database and default counsellor account
    init_db()

    root = tk.Tk()
    root.withdraw()
    if not admin_exists():
        messagebox.showinfo("First-time setup", "Create a password for the counsellor account (username: admin).")
        while True:
            password = simpledialog.askstring("Admin setup", "Choose an admin password (8+ characters, uppercase, lowercase and number):", show="*", parent=root)
            if password is None:
                root.destroy()
                return
            try:
                create_default_admin(password)
                break
            except ValueError as exc:
                messagebox.showerror("Password requirements", str(exc))

    def show_login():
        LoginWindow(root, show_login)

    show_login()

    root.mainloop()


if __name__ == "__main__":
    main()