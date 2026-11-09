
import tkinter as tk
from tkinter import ttk, messagebox
import re

from database import login_user, register_user, email_exists
from user_dashboard import UserDashboard
from admin_dashboard import AdminDashboard

# Colours
BG = "#F5F1F7"
PURPLE = "#76558F"
DARK = "#3D3147"
WHITE = "#FFFFFF"
GREEN = "#267347"
RED = "#B42332"
GREY = "#666666"

EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def is_valid_email(email):
    return bool(re.fullmatch(EMAIL_PATTERN, email.strip()))


class LoginWindow:
    def __init__(self, root, show_login):
        self.root = root
        self.show_login = show_login

        self.window = tk.Toplevel(root)
        self.window.title("Path to Peace - Login")
        self.window.geometry("900x580")
        self.window.minsize(800, 530)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", root.destroy)

        self.create_login()

    def create_login(self):
        left = tk.Frame(
            self.window, bg=PURPLE, width=350
        )
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(
            left,
            text="🌿",
            font=("Segoe UI", 55),
            bg=PURPLE,
            fg=WHITE
        ).pack(pady=(85, 10))

        tk.Label(
            left,
            text="Path to Peace",
            font=("Segoe UI", 27, "bold"),
            bg=PURPLE,
            fg=WHITE
        ).pack()

        tk.Label(
            left,
            text="A safe space to pause,\nconnect and seek support.",
            font=("Segoe UI", 12),
            bg=PURPLE,
            fg=WHITE,
            justify="center"
        ).pack(pady=20)

        tk.Label(
            left,
            text="It is okay to ask for help.",
            font=("Segoe UI", 11, "italic"),
            bg=PURPLE,
            fg=WHITE
        ).pack(side="bottom", pady=45)

        right = tk.Frame(
            self.window,
            bg=WHITE,
            padx=50,
            pady=45
        )
        right.pack(
            side="right",
            fill="both",
            expand=True
        )

        tk.Label(
            right,
            text="Welcome Back",
            font=("Segoe UI", 24, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w")

        tk.Label(
            right,
            text="Log in to continue to Path to Peace",
            font=("Segoe UI", 10),
            bg=WHITE,
            fg=GREY
        ).pack(anchor="w", pady=(5, 25))

        tk.Label(
            right,
            text="Email Address",
            font=("Segoe UI", 10, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w")

        self.email_var = tk.StringVar()

        self.email = ttk.Entry(
            right,
            textvariable=self.email_var
        )
        self.email.pack(fill="x", pady=(5, 3))

        tk.Label(
            right,
            text="Example: student@gmail.com",
            font=("Segoe UI", 9),
            bg=WHITE,
            fg=GREY
        ).pack(anchor="w")

        self.email_feedback = tk.Label(
            right,
            text="",
            font=("Segoe UI", 9),
            bg=WHITE,
            fg=RED
        )
        self.email_feedback.pack(
            anchor="w", pady=(3, 12)
        )

        self.email_var.trace_add(
            "write",
            lambda *args: self.validate_login_email()
        )

        tk.Label(
            right,
            text="Password",
            font=("Segoe UI", 10, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(anchor="w")

        self.password = ttk.Entry(
            right, show="*"
        )
        self.password.pack(
            fill="x", pady=(5, 8)
        )

        self.show_password = tk.BooleanVar(value=False)

        tk.Checkbutton(
            right,
            text="Show password",
            variable=self.show_password,
            command=self.toggle_password,
            bg=WHITE,
            fg=DARK,
            activebackground=WHITE
        ).pack(anchor="w", pady=(0, 15))

        tk.Button(
            right,
            text="LOGIN",
            command=self.login,
            bg=PURPLE,
            fg=WHITE,
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            pady=10,
            cursor="hand2"
        ).pack(fill="x")

        tk.Button(
            right,
            text="Create a User Account",
            command=self.open_register,
            bg=WHITE,
            fg=PURPLE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=10,
            cursor="hand2"
        ).pack(fill="x", pady=10)

        tk.Label(
            right,
            text="Counsellor? Use your existing admin login.",
            font=("Segoe UI", 9),
            bg=WHITE,
            fg=GREY
        ).pack(pady=5)

        self.email.focus_set()

        self.window.bind(
            "<Return>",
            lambda event: self.login()
        )

    def validate_login_email(self):
        email = self.email_var.get().strip()

        if not email:
            self.email_feedback.config(text="")
            return

        if email.lower() == "admin":
            self.email_feedback.config(
                text="✓ Counsellor login",
                fg=GREEN
            )
        elif is_valid_email(email):
            self.email_feedback.config(
                text="✓ Valid email format",
                fg=GREEN
            )
        else:
            self.email_feedback.config(
                text="Enter a valid email, e.g. student@gmail.com",
                fg=RED
            )

    def toggle_password(self):
        self.password.config(
            show="" if self.show_password.get() else "*"
        )

    def login(self):
        email = self.email_var.get().strip()
        password = self.password.get()

        if not email or not password:
            messagebox.showwarning(
                "Login",
                "Please enter your email and password.",
                parent=self.window
            )
            return

        if email.lower() != "admin" and not is_valid_email(email):
            messagebox.showerror(
                "Invalid Email",
                "Please enter a valid email address.",
                parent=self.window
            )
            return

        user = login_user(email, password)

        if not user:
            messagebox.showerror(
                "Login Failed",
                "Invalid email or password.",
                parent=self.window
            )
            self.password.delete(0, tk.END)
            return

        self.window.destroy()

        if user["role"] == "admin":
            AdminDashboard(
                self.root, user, self.show_login
            )
        else:
            UserDashboard(
                self.root, user, self.show_login
            )

    def open_register(self):
        self.window.withdraw()
        RegisterWindow(self.window)


class RegisterWindow:
    def __init__(self, parent):
        self.parent = parent

        self.window = tk.Toplevel(parent)
        self.window.title("Path to Peace - Registration")
        self.window.geometry("570x750")
        self.window.minsize(520, 690)
        self.window.configure(bg=WHITE)

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.go_back
        )

        self.variables = {}
        self.entries = {}
        self.feedback = {}
        self.touched = set()

        self.create_form()

    def create_form(self):
        tk.Label(
            self.window,
            text="Create User Account",
            font=("Segoe UI", 22, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(pady=(25, 5))

        tk.Label(
            self.window,
            text="Register to access Path to Peace.",
            font=("Segoe UI", 10),
            bg=WHITE,
            fg=GREY
        ).pack(pady=(0, 12))

        form = tk.Frame(
            self.window, bg=WHITE
        )
        form.pack(fill="x", padx=50)

        fields = [
            ("Full Name", "name"),
            ("Email Address", "email"),
            ("Password", "password"),
            ("Confirm Password", "confirm")
        ]

        for label, key in fields:
            tk.Label(
                form,
                text=label,
                bg=WHITE,
                fg=DARK,
                font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", pady=(8, 4))

            variable = tk.StringVar()
            self.variables[key] = variable

            entry = ttk.Entry(
                form,
                textvariable=variable,
                show="*" if key in ("password", "confirm") else ""
            )
            entry.pack(fill="x")
            self.entries[key] = entry

            # Email example displayed below the field
            if key == "email":
                tk.Label(
                    form,
                    text="Example: student@gmail.com",
                    bg=WHITE,
                    fg=GREY,
                    font=("Segoe UI", 9)
                ).pack(anchor="w", pady=(2, 2))

            feedback = tk.Label(
                form,
                text="",
                bg=WHITE,
                fg=GREY,
                font=("Segoe UI", 9),
                anchor="w",
                justify="left",
                wraplength=430
            )
            feedback.pack(
                fill="x", pady=(3, 5)
            )
            self.feedback[key] = feedback

            variable.trace_add(
                "write",
                lambda *args, field=key:
                self.on_field_change(field)
            )

            entry.bind(
                "<FocusOut>",
                lambda event, field=key:
                self.on_field_change(field, True)
            )

        self.show_password = tk.BooleanVar(value=False)

        tk.Checkbutton(
            form,
            text="Show passwords",
            variable=self.show_password,
            command=self.toggle_password,
            bg=WHITE,
            fg=DARK,
            activebackground=WHITE
        ).pack(anchor="w", pady=(5, 5))

        tk.Label(
            form,
            text="Password: 8+ characters, uppercase, "
                 "lowercase and a number.",
            bg=WHITE,
            fg=GREY,
            font=("Segoe UI", 9),
            wraplength=430
        ).pack(anchor="w", pady=(0, 10))

        self.create_button = tk.Button(
            self.window,
            text="CREATE ACCOUNT",
            command=self.create_account,
            bg="#D7CEDD",
            fg=WHITE,
            disabledforeground="#555555",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=10,
            state="disabled"
        )
        self.create_button.pack(
            fill="x", padx=50, pady=(10, 5)
        )

        tk.Button(
            self.window,
            text="Back to Login",
            command=self.go_back,
            bg=WHITE,
            fg=PURPLE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=8
        ).pack(fill="x", padx=50)

        self.entries["name"].focus_set()

    def validate_field(self, key):
        name = self.variables["name"].get().strip()
        email = self.variables["email"].get().strip()
        password = self.variables["password"].get()
        confirm = self.variables["confirm"].get()

        if key == "name":
            if not name:
                return False, "Full name is required."

            if len(name) < 2:
                return False, "Enter at least 2 characters."

            if not all(
                c.isalpha() or c in " '-"
                for c in name
            ):
                return False, "Use letters and spaces only."

            if not any(c.isalpha() for c in name):
                return False, "Name must contain letters."

            return True, "✓ Valid full name"

        if key == "email":
            if not email:
                return False, "Email address is required."

            if not is_valid_email(email):
                return False, (
                    "Invalid email. Example: student@gmail.com"
                )

            return True, "✓ Valid email format"

        if key == "password":
            if len(password) < 8:
                return False, "At least 8 characters required."

            if not any(c.isupper() for c in password):
                return False, "Add an uppercase letter."

            if not any(c.islower() for c in password):
                return False, "Add a lowercase letter."

            if not any(c.isdigit() for c in password):
                return False, "Add a number."

            return True, "✓ Password meets requirements"

        if key == "confirm":
            if not confirm:
                return False, "Confirm your password."

            if password != confirm:
                return False, "Passwords do not match."

            return True, "✓ Passwords match"

        return False, "Invalid field."

    def on_field_change(self, key, mark_touched=False):
        if mark_touched:
            self.touched.add(key)

        value = self.variables[key].get()

        if value:
            self.touched.add(key)

        valid, message = self.validate_field(key)

        if key not in self.touched and not value:
            self.feedback[key].config(text="")
        else:
            self.feedback[key].config(
                text=message,
                fg=GREEN if valid else RED
            )

        if key == "password":
            if self.variables["confirm"].get():
                valid, message = self.validate_field("confirm")
                self.feedback["confirm"].config(
                    text=message,
                    fg=GREEN if valid else RED
                )

        self.update_button()

    def update_button(self):
        all_valid = all(
            self.validate_field(key)[0]
            for key in (
                "name", "email", "password", "confirm"
            )
        )

        self.create_button.config(
            state="normal" if all_valid else "disabled",
            bg=PURPLE if all_valid else "#D7CEDD",
            cursor="hand2" if all_valid else "arrow"
        )

    def toggle_password(self):
        symbol = "" if self.show_password.get() else "*"

        self.entries["password"].config(show=symbol)
        self.entries["confirm"].config(show=symbol)

    def create_account(self):
        for key in (
            "name", "email", "password", "confirm"
        ):
            valid, message = self.validate_field(key)

            if not valid:
                messagebox.showerror(
                    "Validation Error",
                    message,
                    parent=self.window
                )
                self.entries[key].focus_set()
                return

        name = self.variables["name"].get().strip()
        email = self.variables["email"].get().strip().lower()
        password = self.variables["password"].get()

        if email_exists(email):
            messagebox.showerror(
                "Email Already Registered",
                "This email is already registered. "
                "Please use another email or log in.",
                parent=self.window
            )
            self.entries["email"].focus_set()
            return

        success, message = register_user(
            name, email, password
        )

        if success:
            messagebox.showinfo(
                "Registration Successful",
                message,
                parent=self.window
            )
            self.go_back()
        else:
            messagebox.showerror(
                "Registration Failed",
                message,
                parent=self.window
            )

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()
        self.parent.lift()
        self.parent.focus_force()
