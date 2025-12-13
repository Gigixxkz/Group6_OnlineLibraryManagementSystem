#----------------------------------------------------------------------------
# File: borrowedbooksmonitoring.py
# Created by: Andreas Andreou
# Course: Software Engineering II
# Project: Online Library Management System (OLMS)
# Description: Admin monitoring of borrowed books
# Date Created: 12 december 2025
#----------------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Depends
import sqlite3, os
from datetime import date
from .login import get_current_user
from datetime import datetime

router = APIRouter(prefix="/borrowedbooksmonitoring", tags=["Borrowed Books monitoring"])

# Database path
DB_PATH = os.path.join("Database", "library.db")

# DB helper
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------------------------------
# GET all borrowed books (ADMIN ONLY)
# -------------------------------------------------------------------------
@router.get("/all")
def get_all_borrowed_books(current_user=Depends(get_current_user)):

    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            bb.id,
            u.username AS user,
            b.title,
            b.isbn,
            bb.borrow_date,
            bb.due_date,
            bb.status
        FROM borrowed_books bb
        JOIN users u ON bb.user_id = u.id
        JOIN books b ON bb.book_id = b.id
        WHERE bb.return_date IS NULL
        ORDER BY bb.due_date ASC
    """)

    records = [dict(row) for row in cur.fetchall()]
    conn.close()

    today = date.today()

    # mark overdue in response (extra safety)
    for r in records:
        r["borrow_date"] = datetime.fromisoformat(r["borrow_date"]).strftime("%Y-%m-%d")
        r["due_date"] = datetime.fromisoformat(r["due_date"]).strftime("%Y-%m-%d")
        r["is_overdue"] = r["status"] == "overdue"

    return {"borrowed_books": records}


# -------------------------------------------------------------------------
# POST return a borrowed book (ADMIN ONLY)
# -------------------------------------------------------------------------
@router.post("/return/{borrowed_id}")
def return_book(borrowed_id: int, current_user=Depends(get_current_user)):

    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    conn = get_db()
    cur = conn.cursor()

    # Check if exists
    cur.execute("""
        SELECT book_id FROM borrowed_books
        WHERE id = ? AND return_date IS NULL
    """, (borrowed_id,))
    record = cur.fetchone()

    if not record:
        conn.close()
        raise HTTPException(status_code=404, detail="Borrow record not found")

    book_id = record["book_id"]

    # Mark as returned
    cur.execute("""
        UPDATE borrowed_books
        SET return_date = DATE('now'), status = 'returned'
        WHERE id = ?
    """, (borrowed_id,))

    # Make book available again
    cur.execute("""
        UPDATE books
        SET available = 1
        WHERE id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return {"message": "Book returned successfully"}
