#----------------------------------------------------------------------------
# File: login.py
#  Created by: Georgia Kazara
#  Course: Software Engineering II
#  Project: Online Library Management System (Group 6)
#  Description: It handles the user login by checking the provided credentials.
#  Date Created: 19 November 2025
#  Last Updated: 19 November 2025
#----------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Request, Depends
import sqlite3, os, datetime
from passlib.hash import bcrypt

#Creating a router for our login API
router = APIRouter()

#Connecting to the SQLite database
def get_db_connection():

    #Finding where this file is located
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    #Going to the database folder and opening library.db
    db_path = os.path.join(BASE_DIR, "../../Database/library.db")
    conn = sqlite3.connect(db_path)

    #Making rows act like dictionaries so that it is easier to use
    conn.row_factory = sqlite3.Row
    return conn

def update_fines():
    conn = get_db_connection()
    cursor = conn.cursor()

    current_date = datetime.date.today()

    # Get all borrowed books that have NOT been returned
    cursor.execute("""
        SELECT id, user_id, due_date, status
        FROM borrowed_books
        WHERE return_date IS NULL
    """)
    borrowed_books = cursor.fetchall()

    for record in borrowed_books:
        due_date = record["due_date"]
        borrowed_id = record["id"]
        user_id = record["user_id"]
        current_status = record["status"]

        due_date = datetime.datetime.fromisoformat(due_date).date()

        # Only apply fine if overdue
        if current_date > due_date:
            days_overdue = (current_date - due_date).days
            new_fine = days_overdue * 5

           # update status to 'overdue' if not already
            if current_status != "overdue":
                cursor.execute("""
                    UPDATE borrowed_books
                    SET status = 'overdue'
                    WHERE id = ?
                """, (borrowed_id,))
                print(f"[STATUS] Book record {borrowed_id} marked as OVERDUE.")

            # check if a fine for this already exists
            cursor.execute("""
                SELECT id FROM fines
                WHERE borrowed_book_id = ?
            """, (borrowed_id,))
            
            fine_record = cursor.fetchone()

            if fine_record:
                # update existing fine
                cursor.execute("""
                    UPDATE fines
                    SET amount = ?
                    WHERE borrowed_book_id = ?
                """, (new_fine, borrowed_id))

            else:
                # create a new fine
                cursor.execute("""
                    INSERT INTO fines (user_id, borrowed_book_id, amount, status)
                    VALUES (?, ?, ?, 'unpaid')
                """, (user_id, borrowed_id, new_fine))

        else:
            # If it's not overdue but status is 'overdue', correct it
            if current_status == "overdue":
                cursor.execute("""
                    UPDATE borrowed_books
                    SET status = 'borrowed'
                    WHERE id = ?
                """, (borrowed_id,))

    conn.commit()
    conn.close()

#The login endpoint:
@router.post("/login")
def login_user(request: Request, data: dict):

    #Getting the username/email and password that the user typed
    username_or_email = data.get("username_or_email")
    password = data.get("password")

    #Connecting to the database
    conn = get_db_connection()
    cur = conn.cursor()

    #Checking if there is a user with this username or this email
    cur.execute("""
        SELECT * FROM users
        WHERE username = ? OR email = ?
    """, (username_or_email, username_or_email))

    user = cur.fetchone()  #Getting the first user that matched
    conn.close()  #Closing the database

    #If no user was found then the login is incorrect!!!
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    #Getting the hashed password stored in the database
    hashed_password = user["password"]

    #Checking if the typed password matches the hashed one stored in the database
    if not bcrypt.verify(password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    #If the password is correct then the login is successful!!!!!!!!
    # Persist user identity/role in the signed session cookie
    request.session.clear()
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]
    request.session["role"] = user["role"] or "user"
    update_fines()
    return {"message": "success", "user": {"id": user["id"], "username": user["username"], "role": user["role"]}}
#----------------------------------------------------------------------------

#this helper function is used to get the current logged-in user based on the session cookie
def get_current_user(request: Request):
    # Helper used as a dependency to enforce authenticated access
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "user_id": user_id,
        "username": request.session.get("username"),
        "role": request.session.get("role") or "user",
    }

# this endpoint returns the current logged-in user based on the session cookie
@router.get("/session/me")
def session_me(request: Request):
    return get_current_user(request)

#this endpoint logs out the current user by clearing the session cookie
@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "logged out"}
