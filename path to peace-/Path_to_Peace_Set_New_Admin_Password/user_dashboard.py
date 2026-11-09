
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
import webbrowser

from database import (
    add_counselling_request,
    get_user_requests,
    get_booked_times
)

BG = "#F5F1F7"
PURPLE = "#76558F"
DARK = "#3D3147"
WHITE = "#FFFFFF"
GREEN = "#4D8B68"
RED = "#B85C5C"
YELLOW = "#B38B2E"


class UserDashboard:
    def __init__(self, root, user, show_login):
        self.root = root
        self.user = user
        self.show_login = show_login

        self.window = tk.Toplevel(root)
        self.window.title("Path to Peace - User Dashboard")
        self.window.geometry("1100x700")
        self.window.configure(bg=BG)
        self.window.minsize(950, 620)
        self.window.protocol("WM_DELETE_WINDOW", self.logout)

        self.build()

    def build(self):
        sidebar = tk.Frame(self.window, bg=PURPLE, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="🌿", font=("Segoe UI", 35),
            bg=PURPLE, fg=WHITE
        ).pack(pady=(35, 5))

        tk.Label(
            sidebar, text="Path to Peace",
            font=("Segoe UI", 17, "bold"),
            bg=PURPLE, fg=WHITE
        ).pack()

        buttons = [
            ("🏠  Dashboard", self.show_home),
            ("📝  Book Counselling", self.show_booking),
            ("📚  Resources", self.show_resources),
            ("☎  Emergency Help", self.show_emergency)
        ]

        for index, (text, command) in enumerate(buttons):
            tk.Button(
                sidebar,
                text=text,
                command=command,
                bg=PURPLE,
                fg=WHITE,
                relief="flat",
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                padx=25,
                pady=12
            ).pack(
                fill="x",
                pady=(35, 2) if index == 0 else 0
            )

        tk.Button(
            sidebar,
            text="Logout",
            command=self.logout,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            padx=25,
            pady=12
        ).pack(side="bottom", fill="x", pady=20)

        self.content = tk.Frame(self.window, bg=BG)
        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.show_home()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def title(self, heading, subtitle=""):
        tk.Label(
            self.content,
            text=heading,
            font=("Segoe UI", 25, "bold"),
            bg=BG,
            fg=DARK
        ).pack(anchor="w", padx=35, pady=(30, 2))

        if subtitle:
            tk.Label(
                self.content,
                text=subtitle,
                font=("Segoe UI", 10),
                bg=BG,
                fg="#777777"
            ).pack(
                anchor="w",
                padx=35,
                pady=(0, 20)
            )

    def card(self, parent, text, value, color=PURPLE):
        frame = tk.Frame(
            parent,
            bg=WHITE,
            padx=20,
            pady=18
        )
        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        tk.Label(
            frame,
            text=text,
            bg=WHITE,
            fg="#777777",
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        tk.Label(
            frame,
            text=value,
            bg=WHITE,
            fg=color,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", pady=(5, 0))

        return frame

    def show_home(self):
        self.clear_content()

        self.title(
            f"Welcome, {self.user['full_name']} 🌿",
            "Your private space to seek support and find helpful resources."
        )

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x", padx=30, pady=10)

        requests = get_user_requests(self.user["id"])

        pending = len([
            r for r in requests if r[5] == "Pending"
        ])

        accepted = len([
            r for r in requests if r[5] == "Accepted"
        ])

        self.card(
            cards, "MY REQUESTS", str(len(requests))
        )

        self.card(
            cards, "PENDING", str(pending), YELLOW
        )

        self.card(
            cards, "ACCEPTED", str(accepted), GREEN
        )

        welcome = tk.Frame(
            self.content,
            bg=WHITE,
            padx=25,
            pady=25
        )
        welcome.pack(
            fill="x",
            padx=36,
            pady=20
        )

        tk.Label(
            welcome,
            text="A gentle reminder",
            font=("Segoe UI", 16, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w")

        tk.Label(
            welcome,
            text=(
                "You do not have to deal with everything alone. "
                "If you would like to talk to a counsellor, "
                "you can send a private request."
            ),
            wraplength=700,
            justify="left",
            font=("Segoe UI", 11),
            bg=WHITE,
            fg="#555555"
        ).pack(anchor="w", pady=10)

        tk.Button(
            welcome,
            text="Request Counselling",
            command=self.show_booking,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=9
        ).pack(anchor="w", pady=5)

        self.show_recent_requests()

    def show_recent_requests(self):
        box = tk.Frame(
            self.content,
            bg=WHITE,
            padx=20,
            pady=15
        )
        box.pack(
            fill="both",
            expand=True,
            padx=36,
            pady=(0, 20)
        )

        tk.Label(
            box,
            text="Recent Counselling Requests",
            font=("Segoe UI", 14, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w", pady=(0, 10))

        columns = (
            "ID", "Concern", "Date", "Time", "Status"
        )

        tree = ttk.Treeview(
            box,
            columns=columns,
            show="headings",
            height=7
        )

        for col in columns:
            tree.heading(col, text=col)

        tree.column("ID", width=50, anchor="center")
        tree.column("Concern", width=330)
        tree.column("Date", width=110, anchor="center")
        tree.column("Time", width=100, anchor="center")
        tree.column("Status", width=110, anchor="center")

        for row in get_user_requests(self.user["id"]):
            tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[2],
                    row[3],
                    row[4],
                    row[5]
                )
            )

        tree.pack(fill="both", expand=True)

    def show_booking(self):
        self.clear_content()

        self.title(
            "Book a Counselling Session",
            "Choose an available date and time to request a session."
        )

        form = tk.Frame(
            self.content,
            bg=WHITE,
            padx=30,
            pady=22
        )
        form.pack(
            fill="x",
            padx=36,
            pady=10
        )

        tk.Label(
            form,
            text="Name shown to counsellor",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        anonymous_var = tk.BooleanVar(value=False)

        self.name_entry = ttk.Entry(form)
        self.name_entry.insert(
            0, self.user["full_name"]
        )
        self.name_entry.pack(
            fill="x",
            pady=(5, 8)
        )

        tk.Checkbutton(
            form,
            text="Submit anonymously",
            variable=anonymous_var,
            bg=WHITE,
            fg=DARK,
            activebackground=WHITE,
            command=lambda: self.toggle_anonymous(
                anonymous_var
            )
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            form,
            text="What would you like support with?",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        concern = tk.Text(
            form,
            height=5,
            font=("Segoe UI", 10)
        )
        concern.pack(
            fill="x",
            pady=(5, 14)
        )

        row = tk.Frame(form, bg=WHITE)
        row.pack(fill="x")

        left = tk.Frame(row, bg=WHITE)
        left.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8)
        )

        tk.Label(
            left,
            text="Preferred date",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        date_entry = DateEntry(
            left,
            background=PURPLE,
            foreground=WHITE,
            date_pattern="yyyy-mm-dd",
            mindate=date.today(),
            state="readonly"
        )
        date_entry.pack(fill="x", pady=5)

        right = tk.Frame(row, bg=WHITE)
        right.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0)
        )

        tk.Label(
            right,
            text="Available time",
            bg=WHITE,
            fg=DARK,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        # 24 hourly slots, including midnight.
        all_times = tuple(
            f"{(hour % 12) or 12}:00 "
            f"{'AM' if hour < 12 else 'PM'}"
            for hour in range(24)
        )

        time_entry = ttk.Combobox(
            right,
            state="readonly",
            values=all_times
        )
        time_entry.pack(fill="x", pady=5)

        availability = tk.Label(
            form,
            text="",
            bg=WHITE,
            fg=GREEN,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left"
        )
        availability.pack(
            fill="x",
            pady=(8, 5)
        )

        def refresh_times(event=None):
            chosen_date = date_entry.get_date()

            reserved = get_booked_times(
                chosen_date.isoformat()
            )

            available = [
                t for t in all_times
                if t not in reserved
                and datetime.combine(
                    chosen_date,
                    datetime.strptime(
                        t, "%I:%M %p"
                    ).time()
                ) > datetime.now()
            ]

            previous = time_entry.get()

            time_entry["values"] = available

            if previous not in available:
                time_entry.set("")

            if not available:
                availability.config(
                    text=(
                        "No available time slots on this date. "
                        "Please choose another date."
                    ),
                    fg=RED
                )

            elif reserved:
                availability.config(
                    text=(
                        "Booked times are hidden. "
                        "Please select an available time."
                    ),
                    fg=GREEN
                )

            else:
                availability.config(
                    text=(
                        "Select an available time "
                        "from the dropdown."
                    ),
                    fg=GREEN
                )

        date_entry.bind(
            "<<DateEntrySelected>>",
            refresh_times
        )

        refresh_times()

        def submit():
            display_name = (
                self.name_entry.get().strip()
            )

            message = concern.get(
                "1.0", "end"
            ).strip()

            chosen_date = date_entry.get_date()
            selected_time = time_entry.get().strip()

            if not anonymous_var.get():
                valid_name = (
                    display_name
                    and all(
                        c.isalpha() or c in " -'"
                        for c in display_name
                    )
                )

                if not valid_name:
                    messagebox.showwarning(
                        "Name",
                        "Enter a valid name or choose "
                        "anonymous submission.",
                        parent=self.window
                    )
                    return

            if not selected_time:
                messagebox.showwarning(
                    "Time Unavailable",
                    "Please choose an available time "
                    "or another date.",
                    parent=self.window
                )
                refresh_times()
                return

            appointment_datetime = datetime.combine(
                chosen_date,
                datetime.strptime(
                    selected_time, "%I:%M %p"
                ).time()
            )

            if appointment_datetime <= datetime.now():
                messagebox.showwarning(
                    "Date and time",
                    "Please choose a future date and time.",
                    parent=self.window
                )
                refresh_times()
                return

            if not message:
                messagebox.showwarning(
                    "Request",
                    "Please describe what you need support with.",
                    parent=self.window
                )
                return

            if anonymous_var.get():
                display_name = "Anonymous"

            # Database checks the slot again before saving.
            saved = add_counselling_request(
                self.user["id"],
                display_name,
                message,
                chosen_date.isoformat(),
                selected_time
            )

            if not saved:
                messagebox.showwarning(
                    "Time Slot Unavailable",
                    "This date and time have already "
                    "been requested. Please choose "
                    "another slot.",
                    parent=self.window
                )
                refresh_times()
                return

            messagebox.showinfo(
                "Request Submitted",
                "Your counselling request was submitted "
                "and is pending review.",
                parent=self.window
            )

            self.show_home()

        tk.Button(
            form,
            text="SUBMIT COUNSELLING REQUEST",
            command=submit,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10
        ).pack(anchor="w", pady=(12, 0))

    def toggle_anonymous(self, var):
        self.name_entry.delete(0, "end")

        if var.get():
            self.name_entry.insert(0, "Anonymous")
        else:
            self.name_entry.insert(
                0, self.user["full_name"]
            )

    def show_resources(self):
        self.clear_content()

        self.title(
            "Student Wellbeing Resources",
            "Motivational videos, research and helpful information."
        )

        container = tk.Frame(self.content, bg=BG)
        container.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 15)
        )

        canvas = tk.Canvas(
            container,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )

        page = tk.Frame(canvas, bg=BG)

        page.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=page,
            anchor="nw"
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        def heading(text):
            tk.Label(
                page,
                text=text,
                font=("Segoe UI", 17, "bold"),
                bg=BG,
                fg=DARK
            ).pack(
                anchor="w",
                pady=(18, 10)
            )

        def resource_card(
            title,
            description,
            button_text=None,
            url=None
        ):
            card = tk.Frame(
                page,
                bg=WHITE,
                padx=22,
                pady=16
            )
            card.pack(
                fill="x",
                pady=6
            )

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 13, "bold"),
                bg=WHITE,
                fg=PURPLE
            ).pack(anchor="w")

            tk.Label(
                card,
                text=description,
                font=("Segoe UI", 10),
                bg=WHITE,
                fg="#555555",
                wraplength=650,
                justify="left"
            ).pack(
                anchor="w",
                pady=(8, 10)
            )

            if url:
                tk.Button(
                    card,
                    text=button_text or "OPEN RESOURCE",
                    command=lambda link=url: webbrowser.open(
                        link
                    ),
                    bg=PURPLE,
                    fg=WHITE,
                    relief="flat",
                    font=("Segoe UI", 9, "bold"),
                    padx=14,
                    pady=8,
                    cursor="hand2"
                ).pack(anchor="w")

        heading("Welcome to Your Wellbeing Space")

        resource_card(
            "Your Wellbeing Matters",
            "College life can bring academic pressure, "
            "personal challenges and new responsibilities. "
            "These resources provide useful information "
            "about motivation, stress management, healthy "
            "habits and seeking support."
        )

        heading("Motivational Videos")

        resource_card(
            "Student Motivation",
            "Explore talks about staying focused, "
            "building confidence and continuing "
            "through academic challenges.",
            "WATCH ON YOUTUBE",
            "https://www.youtube.com/results?search_query=TEDx+student+motivation"
        )

        resource_card(
            "Overcoming Procrastination",
            "Learn why people delay important tasks "
            "and explore ways to develop better habits.",
            "WATCH ON YOUTUBE",
            "https://www.youtube.com/results?search_query=TED+Ed+procrastination"
        )

        resource_card(
            "Building Self-Confidence",
            "Explore educational talks about "
            "self-belief, personal growth and "
            "learning from mistakes.",
            "WATCH ON YOUTUBE",
            "https://www.youtube.com/results?search_query=TEDx+self+confidence+students"
        )

        resource_card(
            "Managing Exam Stress",
            "Find educational videos about "
            "preparing for examinations and "
            "managing academic pressure.",
            "WATCH ON YOUTUBE",
            "https://www.youtube.com/results?search_query=TED+Ed+exam+stress"
        )

        heading("Research and Important Information")

        resource_card(
            "World Health Organization (WHO)",
            "Read evidence-based information about "
            "mental health, wellbeing and the importance "
            "of appropriate support.",
            "READ WHO INFORMATION",
            "https://www.who.int/health-topics/mental-health"
        )

        resource_card(
            "UNICEF - Mental Health",
            "Explore information about young people's "
            "mental health, emotional wellbeing "
            "and supportive environments.",
            "EXPLORE UNICEF",
            "https://www.unicef.org/mental-health"
        )

        resource_card(
            "National Institute of Mental Health",
            "Find information about stress, "
            "mental health research and "
            "professional support.",
            "READ INFORMATION",
            "https://www.nimh.nih.gov/health"
        )

        resource_card(
            "Healthy Sleep - CDC",
            "Learn about the importance of sleep "
            "for health, concentration and "
            "daily functioning.",
            "LEARN ABOUT SLEEP",
            "https://www.cdc.gov/sleep/"
        )

        heading("Practical Tips for Students")

        resource_card(
            "Study and Time Management",
            "Create a realistic timetable, divide "
            "assignments into smaller tasks and "
            "take regular study breaks."
        )

        resource_card(
            "Managing Stress",
            "Take short breaks when overwhelmed, "
            "practise relaxation and talk to "
            "someone you trust."
        )

        resource_card(
            "Healthy Daily Habits",
            "Maintain regular sleep habits, eat "
            "regularly, drink enough water and "
            "make time for enjoyable activities."
        )

        resource_card(
            "Seeking Support",
            "Consider talking with a trusted "
            "friend, family member, teacher "
            "or qualified counsellor when needed."
        )

        heading("Counselling Support")

        resource_card(
            "Book a Counselling Session",
            "You can request a private counselling "
            "appointment through Path to Peace. "
            "Select Book Counselling from the sidebar "
            "and choose an available date and time. "
            "Requests remain pending until reviewed "
            "by the counsellor."
        )

        tk.Label(
            page,
            text=(
                "Note: External resources require an "
                "internet connection. This information "
                "does not replace professional advice."
            ),
            font=("Segoe UI", 9),
            bg=BG,
            fg="#777777",
            wraplength=650,
            justify="left"
        ).pack(
            anchor="w",
            pady=(18, 20)
        )

    def show_emergency(self):
        self.clear_content()

        self.title(
            "Emergency Support",
            "Find appropriate help when urgent support is needed."
        )

        card = tk.Frame(
            self.content,
            bg=WHITE,
            padx=30,
            pady=30
        )
        card.pack(
            fill="x",
            padx=36,
            pady=15
        )

        tk.Label(
            card,
            text="☎ Emergency / Immediate Help",
            font=("Segoe UI", 17, "bold"),
            bg=WHITE,
            fg=RED
        ).pack(anchor="w")

        tk.Label(
            card,
            text=(
                "If you need urgent assistance, "
                "contact local emergency services, "
                "a healthcare professional, your "
                "college counsellor or a trusted person."
            ),
            font=("Segoe UI", 11),
            bg=WHITE,
            fg="#555555",
            wraplength=720,
            justify="left"
        ).pack(
            anchor="w",
            pady=15
        )

        tk.Label(
            card,
            text=(
                "Use your college's verified emergency "
                "and counselling contact information."
            ),
            font=("Segoe UI", 11, "bold"),
            bg=WHITE,
            fg=PURPLE,
            wraplength=720,
            justify="left"
        ).pack(anchor="w")

    def logout(self):
        self.window.destroy()
        self.show_login()
