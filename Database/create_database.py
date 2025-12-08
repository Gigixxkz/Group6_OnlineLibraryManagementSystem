# UPDATED DATABASE CREATION SCRIPT (MIGRATION SAFE)

import sqlite3

DB_PATH = "library.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def column_exists(table, column):
    """Check if a column exists in a given table."""
    cursor.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols

def table_exists(table):
    """Check if a table already exists."""
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?;
    """, (table,))
    return cursor.fetchone() is not None


# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('user', 'librarian', 'admin')) DEFAULT 'user'
);
""")

# BOOKS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    publisher TEXT,
    year INTEGER,
    description TEXT,
    isbn TEXT UNIQUE,
    language TEXT,
    cover_image TEXT,
    available BOOLEAN DEFAULT 1
);
""")

# GENRES + BOOK_GENRES TABLES
cursor.execute("""
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS book_genres (
    book_id INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);
""")

# BORROWED BOOKS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS borrowed_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    return_date TEXT,
    due_date TEXT, 
    status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue')) DEFAULT 'borrowed',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);
""")

# Add missing due_date column safely
if not column_exists("borrowed_books", "due_date"):
    print("Adding missing column: borrowed_books.due_date")
    cursor.execute("ALTER TABLE borrowed_books ADD COLUMN due_date TEXT;")


# FINES TABLE (Automatic rebuild if outdated)

# If no fines table exists → create correct version
if not table_exists("fines"):
    print("Creating fines table...")
    cursor.execute("""
    CREATE TABLE fines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        borrowed_book_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT CHECK(status IN ('unpaid', 'paid')) DEFAULT 'unpaid',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (borrowed_book_id) REFERENCES borrowed_books(id)
    );
    """)
else:
    # Check if old columns exist (issued_date or paid_date)
    cursor.execute("PRAGMA table_info(fines);")
    columns = [row[1] for row in cursor.fetchall()]

    if "issued_date" in columns or "paid_date" in columns:

        cursor.execute("""
        CREATE TABLE fines_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            borrowed_book_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT CHECK(status IN ('unpaid', 'paid')) DEFAULT 'unpaid',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (borrowed_book_id) REFERENCES borrowed_books(id)
        );
        """)

        # Copy valid data (ignore old columns)
        cursor.execute("""
        INSERT INTO fines_new (id, user_id, borrowed_book_id, amount, status)
        SELECT id, user_id, borrowed_book_id, amount, status
        FROM fines;
        """)

        # Replace old table
        cursor.execute("DROP TABLE fines;")


conn.commit()
conn.close()

print("Database migration completed successfully.")
