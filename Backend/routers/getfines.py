from fastapi import APIRouter, Depends, HTTPException
import sqlite3, os
from .login import get_current_user  

router = APIRouter()

# DATABASE CONNECTION
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "../../Database/library.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn



#   GET UNPAID FINES FOR USER
@router.get("/getfines")
def get_fines(current_user = Depends(get_current_user)):

    user_id = current_user["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT 
                f.id,
                f.amount,
                f.status,
                b.title AS book_title,
                bb.due_date
            FROM fines f
            JOIN borrowed_books bb ON f.borrowed_book_id = bb.id
            JOIN books b ON bb.book_id = b.id
            WHERE f.user_id = ? AND f.status = 'unpaid'
        """, (user_id,))

        rows = cursor.fetchall()

        fines = []
        for r in rows:
            fines.append({
                "id": r["id"],
                "amount": r["amount"],
                "status": r["status"],
                "book_title": r["book_title"],
                "due_date": r["due_date"]
            })

        return fines

    finally:
        conn.close()