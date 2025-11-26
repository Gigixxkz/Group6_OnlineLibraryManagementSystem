import argparse, os, sqlite3, sys
from passlib.hash import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "Database", "library.db")

def upsert_user(username, email, role, password=None, update_password=False):
    if role not in {"user", "librarian", "admin"}:
        raise ValueError("Invalid role")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    row = cur.fetchone()

    if row:
        cur.execute("UPDATE users SET role = ? WHERE id = ?", (role, row["id"]))
        if password and update_password:
            cur.execute("UPDATE users SET password = ? WHERE id = ?", (bcrypt.hash(password), row["id"]))
        conn.commit()
        msg = f"Updated user {username} (id={row['id']}) to role {role}" + (" and password" if password and update_password else "")
    else:
        if not password:
            conn.close()
            raise ValueError("Password required to create new user")
        cur.execute(
            """INSERT INTO users (name, surname, username, email, phone_number, password, role)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("Admin", "User", username, email, "", bcrypt.hash(password), role),
        )
        conn.commit()
        msg = f"Created user {username} (id={cur.lastrowid}) with role {role}"

    conn.close()
    return msg

def main():
    ap = argparse.ArgumentParser(description="Create/update users with roles.")
    ap.add_argument("--username", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--role", required=True, choices=["user", "librarian", "admin"])
    ap.add_argument("--password", help="Required when creating; optional on update")
    ap.add_argument("--update-password", action="store_true", help="Also reset password if provided")
    args = ap.parse_args()
    try:
        print(upsert_user(args.username, args.email, args.role, args.password, args.update_password))
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
