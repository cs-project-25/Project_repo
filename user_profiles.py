import sqlite3

def init_db():
    """Create users table if not exists."""
    conn = sqlite3.connect("data/database.sqlite")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            preferences TEXT,
            calendar_link TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_user(name, email, preferences, calendar_link):
    """Add or update user with preferences and calendar link."""
    conn = sqlite3.connect("data/database.sqlite")
    c = conn.cursor()
    prefs_str = ",".join(preferences)
    c.execute("""
        INSERT OR REPLACE INTO users (name, email, preferences, calendar_link)
        VALUES (?, ?, ?, ?)
    """, (name, email, prefs_str, calendar_link))
    conn.commit()
    conn.close()


def get_users():
    """Return list of all users."""
    conn = sqlite3.connect("data/database.sqlite")
    c = conn.cursor()
    c.execute("SELECT id, name, email, preferences, calendar_link FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


def get_user_by_email(email):
    """Fetch single user by email."""
    conn = sqlite3.connect("data/database.sqlite")
    c = conn.cursor()
    c.execute("""
        SELECT id, name, email, preferences, calendar_link
        FROM users WHERE email = ?
    """, (email,))
    user = c.fetchone()
    conn.close()
    return user