
import sqlite3
import hashlib
import hmac
import re
from datetime import datetime

DB_NAME = "path_to_peace.db"

EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def connect():
    return sqlite3.connect(DB_NAME)


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def valid_email(email):
    return bool(re.fullmatch(
        EMAIL_PATTERN, email.strip()
    ))


def validate_registration(full_name, email, password, confirm=None):
    full_name = full_name.strip()
    email = email.strip()

    if len(full_name) < 2:
        return False, "Enter your full name."

    if not all(c.isalpha() or c in " '-" for c in full_name):
        return False, "Full name must contain letters only."

    if not valid_email(email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must have at least 8 characters."

    if not any(c.isupper() for c in password):
        return False, "Add at least one uppercase letter."

    if not any(c.islower() for c in password):
        return False, "Add at least one lowercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Add at least one number."

    if confirm is not None and password != confirm:
        return False, "Passwords do not match."

    return True, "All fields are valid."


def init_db():
    conn = connect()
    cur = conn.cursor()

    # Keep the existing username column for compatibility.
    # New student accounts store email addresses in this column.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS counselling_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            display_name TEXT NOT NULL,
            concern TEXT NOT NULL,
            preferred_date TEXT,
            preferred_time TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            admin_note TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_default_admin(password):
    """Create the counsellor account on first launch, without a default password."""
    if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("Use 8+ characters with uppercase, lowercase and a number.")
    conn = connect()
    try:
        existing = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
        if not existing:
            conn.execute("INSERT INTO users (full_name, username, password, role) VALUES (?, ?, ?, ?)",
                         ("Path to Peace Counsellor", "admin", hash_password(password), "admin"))
            conn.commit()
    finally:
        conn.close()


def email_exists(email):
    conn = connect()
    row = conn.execute("""
        SELECT id FROM users
        WHERE LOWER(username) = ?
    """, (email.strip().lower(),)).fetchone()
    conn.close()
    return row is not None


def register_user(full_name, email, password):
    valid, message = validate_registration(
        full_name, email, password
    )

    if not valid:
        return False, message

    email = email.strip().lower()

    conn = connect()

    try:
        conn.execute("""
            INSERT INTO users
            (full_name, username, password, role)
            VALUES (?, ?, ?, 'user')
        """, (
            full_name.strip(),
            email,
            hash_password(password)
        ))

        conn.commit()
        return True, "Account created successfully. Please log in."

    except sqlite3.IntegrityError:
        return False, "This email is already registered."

    finally:
        conn.close()


def verify_password(password, stored):
    """Check legacy PBKDF2 accounts and newer SHA-256 accounts."""
    if stored.startswith("pbkdf2$"):
        try:
            _, salt_hex, digest_hex = stored.split("$")
            calculated = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"),
                bytes.fromhex(salt_hex), 200000
            )
            return hmac.compare_digest(calculated, bytes.fromhex(digest_hex))
        except (ValueError, TypeError):
            return False
    return hmac.compare_digest(hash_password(password), stored)


def login_user(email, password):
    email = email.strip().lower()
    conn = connect()
    try:
        row = conn.execute("""
            SELECT id, full_name, username, role, password
            FROM users WHERE LOWER(username) = ?
        """, (email,)).fetchone()
    finally:
        conn.close()
    if row and verify_password(password, row[4]):
        return {"id": row[0], "full_name": row[1],
                "username": row[2], "email": row[2], "role": row[3]}
    return None


def get_booked_times(preferred_date):
    """Return times held by pending or accepted requests, without student details."""
    conn = connect()
    try:
        rows = conn.execute("""
            SELECT preferred_time FROM counselling_requests
            WHERE preferred_date = ? AND status IN ('Pending', 'Accepted')
        """, (preferred_date,)).fetchall()
        return {row[0] for row in rows if row[0]}
    finally:
        conn.close()


def is_slot_available(preferred_date, preferred_time):
    return preferred_time not in get_booked_times(preferred_date)


def add_counselling_request(user_id, display_name, concern, date, time):
    """Atomically reserve a slot. Returns True if saved, False if unavailable."""
    conn = connect()
    try:
        # A write transaction prevents two simultaneous requests taking the same slot.
        conn.execute("BEGIN IMMEDIATE")
        occupied = conn.execute("""
            SELECT 1 FROM counselling_requests
            WHERE preferred_date = ? AND preferred_time = ?
              AND status IN ('Pending', 'Accepted') LIMIT 1
        """, (date, time)).fetchone()
        if occupied:
            conn.rollback()
            return False
        conn.execute("""
            INSERT INTO counselling_requests
            (user_id, display_name, concern, preferred_date, preferred_time,
             status, created_at)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?)
        """, (user_id, display_name, concern, date, time,
              datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_user_requests(user_id):
    conn = connect()

    rows = conn.execute("""
        SELECT id, display_name, concern,
               preferred_date, preferred_time,
               status, admin_note, created_at
        FROM counselling_requests
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    conn.close()
    return rows


def get_all_requests():
    conn = connect()

    rows = conn.execute("""
        SELECT id, display_name, concern,
               preferred_date, preferred_time,
               status, admin_note, created_at
        FROM counselling_requests
        ORDER BY id DESC
    """).fetchall()

    conn.close()
    return rows


def update_request(request_id, status, admin_note=""):
    conn = connect()

    conn.execute("""
        UPDATE counselling_requests
        SET status = ?, admin_note = ?
        WHERE id = ?
    """, (
        status, admin_note, request_id
    ))

    conn.commit()
    conn.close()


def add_mood_entry(user_id, mood, note):
    conn = connect()

    conn.execute("""
        INSERT INTO mood_entries
        (user_id, mood, note, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        mood,
        note,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()


def get_mood_entries(user_id, limit=10):
    conn = connect()

    rows = conn.execute("""
        SELECT mood, note, created_at
        FROM mood_entries
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()

    conn.close()
    return rows


def request_counts():
    conn = connect()

    total = conn.execute(
        "SELECT COUNT(*) FROM counselling_requests"
    ).fetchone()[0]

    pending = conn.execute("""
        SELECT COUNT(*) FROM counselling_requests
        WHERE status = 'Pending'
    """).fetchone()[0]

    accepted = conn.execute("""
        SELECT COUNT(*) FROM counselling_requests
        WHERE status = 'Accepted'
    """).fetchone()[0]

    cancelled = conn.execute("""
        SELECT COUNT(*) FROM counselling_requests
        WHERE status = 'Cancelled'
    """).fetchone()[0]

    conn.close()

    return total, pending, accepted, cancelled
def admin_exists():
    conn = connect()
    row = conn.execute(
        "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
    ).fetchone()
    conn.close()
    return row is not None

