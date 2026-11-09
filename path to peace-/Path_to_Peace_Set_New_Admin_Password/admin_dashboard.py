import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import get_all_requests, update_request, request_counts

BG = "#F5F1F7"
PURPLE = "#76558F"
DARK = "#3D3147"
WHITE = "#FFFFFF"
GREEN = "#4D8B68"
RED = "#B85C5C"
YELLOW = "#B38B2E"

class AdminDashboard:
    def __init__(self, root, user, show_login):
        self.root = root
        self.user = user
        self.show_login = show_login

        self.window = tk.Toplevel(root)
        self.window.title("Path to Peace - Counsellor Dashboard")
        self.window.geometry("1200x720")
        self.window.configure(bg=BG)
        self.window.minsize(1000, 620)
        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        self.build()

    def build(self):
        top = tk.Frame(self.window, bg=PURPLE, height=85)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top, text="🌿 Path to Peace",
            font=("Segoe UI", 22, "bold"),
            bg=PURPLE, fg=WHITE
        ).pack(side="left", padx=30)

        tk.Label(
            top, text="Counsellor / Admin Dashboard",
            font=("Segoe UI", 11),
            bg=PURPLE, fg=WHITE
        ).pack(side="left", padx=10)

        tk.Button(
            top, text="Logout", command=self.logout,
            bg=PURPLE, fg=WHITE, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15
        ).pack(side="right", padx=25)

        body = tk.Frame(self.window, bg=BG)
        body.pack(fill="both", expand=True, padx=25, pady=20)

        self.stats = tk.Frame(body, bg=BG)
        self.stats.pack(fill="x", pady=(0, 15))

        self.make_stats()

        toolbar = tk.Frame(body, bg=BG)
        toolbar.pack(fill="x", pady=(0, 10))

        tk.Label(
            toolbar, text="Counselling Requests",
            font=("Segoe UI", 18, "bold"),
            bg=BG, fg=DARK
        ).pack(side="left")

        tk.Button(
            toolbar, text="↻ Refresh",
            command=self.refresh,
            bg=WHITE, fg=PURPLE, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=12, pady=7
        ).pack(side="right")

        table_box = tk.Frame(body, bg=WHITE, padx=15, pady=15)
        table_box.pack(fill="both", expand=True)

        columns = (
            "ID", "User", "Concern", "Date",
            "Time", "Status", "Created"
        )

        self.tree = ttk.Treeview(
            table_box, columns=columns,
            show="headings", selectmode="browse"
        )

        widths = {
            "ID": 50,
            "User": 130,
            "Concern": 350,
            "Date": 100,
            "Time": 90,
            "Status": 110,
            "Created": 130
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(
                col, width=widths[col],
                anchor="center" if col != "Concern" else "w"
            )

        scroll = ttk.Scrollbar(
            table_box, orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.tag_configure("Pending", foreground=YELLOW)
        self.tree.tag_configure("Accepted", foreground=GREEN)
        self.tree.tag_configure("Cancelled", foreground=RED)

        buttons = tk.Frame(body, bg=BG)
        buttons.pack(fill="x", pady=(12, 0))

        tk.Button(
            buttons, text="✓ ACCEPT REQUEST",
            command=lambda: self.change_status("Accepted"),
            bg=GREEN, fg=WHITE, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=9
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="✕ CANCEL REQUEST",
            command=lambda: self.change_status("Cancelled"),
            bg=RED, fg=WHITE, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=9
        ).pack(side="left", padx=5)

        tk.Button(
            buttons, text="View Details",
            command=self.view_details,
            bg=WHITE, fg=PURPLE, relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=9
        ).pack(side="left", padx=5)

        self.refresh()

    def make_stats(self):
        for widget in self.stats.winfo_children():
            widget.destroy()

        total, pending, accepted, cancelled = request_counts()

        stats = [
            ("TOTAL REQUESTS", total, PURPLE),
            ("PENDING", pending, YELLOW),
            ("ACCEPTED", accepted, GREEN),
            ("CANCELLED", cancelled, RED)
        ]

        for title, value, color in stats:
            card = tk.Frame(self.stats, bg=WHITE, padx=20, pady=15)
            card.pack(side="left", fill="both", expand=True, padx=5)

            tk.Label(
                card, text=title,
                bg=WHITE, fg="#777777",
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")

            tk.Label(
                card, text=str(value),
                bg=WHITE, fg=color,
                font=("Segoe UI", 22, "bold")
            ).pack(anchor="w", pady=(4, 0))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in get_all_requests():
            self.tree.insert(
                "", "end",
                values=(
                    row[0], row[1], row[2],
                    row[3], row[4], row[5], row[7]
                ),
                tags=(row[5],)
            )

        self.make_stats()

    def selected_request(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Request",
                "Please select a counselling request first."
            )
            return None

        item = selected[0]
        return self.tree.item(item, "values")

    def change_status(self, status):
        values = self.selected_request()

        if not values:
            return

        request_id = values[0]
        current_status = values[5]

        if current_status == status:
            messagebox.showinfo(
                "Request",
                f"This request is already {status.lower()}."
            )
            return

        action = "accept" if status == "Accepted" else "cancel"

        confirm = messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to {action} request #{request_id}?"
        )

        if not confirm:
            return

        note = simpledialog.askstring(
            "Counsellor Note",
            "Optional note for the user:"
        )

        update_request(request_id, status, note or "")
        messagebox.showinfo(
            "Updated",
            f"Request #{request_id} has been marked as {status}."
        )
        self.refresh()

    def view_details(self):
        values = self.selected_request()

        if not values:
            return

        request_id = values[0]

        rows = get_all_requests()
        selected_row = None

        for row in rows:
            if str(row[0]) == str(request_id):
                selected_row = row
                break

        if not selected_row:
            return

        row = selected_row

        detail = (
            f"Request ID: {row[0]}\n\n"
            f"User: {row[1]}\n\n"
            f"Concern:\n{row[2]}\n\n"
            f"Preferred Date: {row[3] or 'Not specified'}\n"
            f"Preferred Time: {row[4] or 'Not specified'}\n\n"
            f"Status: {row[5]}\n\n"
            f"Counsellor Note: {row[6] or 'None'}\n\n"
            f"Submitted: {row[7]}"
        )

        messagebox.showinfo("Counselling Request Details", detail)

    def logout(self):
        self.window.destroy()
        self.show_login()
