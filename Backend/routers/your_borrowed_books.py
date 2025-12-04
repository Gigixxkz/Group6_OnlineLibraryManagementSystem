from fastapi import APIRouter, HTTPException, Depends
from .login import get_current_user
import sqlite3, os

router = APIRouter()

def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "../../Database/library.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint to get the list of borrowed books for the current user
@router.get("/borrowed_books")
def get_borrowed_books(current_user = Depends(get_current_user)):
    userid = current_user["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check user exists 
    cursor.execute("SELECT id FROM users WHERE id = ?", (userid,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found.")

    # Fetch borrowed books
    cursor.execute("""
        SELECT bb.id AS borrow_id, b.id AS book_id, b.title, b.author, bb.borrow_date, bb.status
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.id
        WHERE bb.user_id = ?
    """, (userid,))

    borrowed_books = cursor.fetchall()
    conn.close()

    # Convert the rows of borrowed books to JSON format
    books_list = [dict(book) for book in borrowed_books]

    return {"borrowed_books": books_list}