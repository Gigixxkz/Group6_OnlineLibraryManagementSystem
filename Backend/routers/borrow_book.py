from fastapi import APIRouter, HTTPException
import sqlite3, os
from datetime import datetime, timedelta

router = APIRouter()

def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "../../Database/library.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@router.post("/borrow")
def borrow_book(data: dict):
    user_id = data.get("user_id")
    book_id = data.get("book_id")

    if not user_id or not book_id:
        raise HTTPException(status_code=400, detail="Missing user_id or book_id.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Check user exists ---
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found.")

    # --- Check book exists ---
    cursor.execute("SELECT id, available FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found.")

    # --- Check availability ---
    if book["available"] == 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Book is already borrowed.")

    # --- Insert into borrowed_books ---
    borrow_date = datetime.now().isoformat()
    due_date = datetime.now()+timedelta(days=20)
    due_date = due_date.isoformat()

    cursor.execute("""
        INSERT INTO borrowed_books (user_id, book_id, borrow_date, due_date, status)
        VALUES (?, ?, ?, ?, 'borrowed')
    """, (user_id, book_id, borrow_date, due_date))

    # --- Mark book as unavailable ---
    cursor.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Book borrowed successfully."}