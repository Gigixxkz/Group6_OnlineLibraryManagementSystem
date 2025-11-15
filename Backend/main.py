from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import os
import sqlite3
from passlib.hash import bcrypt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database connection ---
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "../Database/library.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# --- Registration endpoint ---
@app.post("/register")
def register_user(
    name: str = Form(...),
    surname: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if username or email already exists
    cursor.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    if cursor.fetchone():
        conn.close()
        return JSONResponse(content={"success": False, "message": "Username or email already exists."})

    # Hash password
    hashed_password = bcrypt.hash(password)

    # Insert user
    cursor.execute("""
        INSERT INTO users (name, surname, username, email, phone_number, password)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, surname, username, email, phone_number, hashed_password))

    conn.commit()
    conn.close()

    return JSONResponse(content={"success": True, "message": "User registered successfully!"})