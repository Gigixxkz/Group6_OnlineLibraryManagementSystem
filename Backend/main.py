from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import os
import sqlite3
from passlib.hash import bcrypt

app = FastAPI()

#this allows the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database connection ---
def get_db_connection():
    #this finds the database path relative to this file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #this actually builds the path to the database
    db_path = os.path.join(BASE_DIR, "../Database/library.db")
    #this connects to the database
    conn = sqlite3.connect(db_path)
    #this makes the
    conn.row_factory = sqlite3.Row
    return conn


# --- Registration endpoint ---
@app.post("/register")
#Reads form data from the frontend request
def register_user(
    name: str = Form(...),
    surname: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...)
):
    #Connects to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if username or email already exists
    cursor.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    #this checks if a user with the same username or email already exists end returns an error if so
    if cursor.fetchone():
        conn.close()
        return JSONResponse(content={"success": False, "message": "Username or email already exists."})

    #this hashes the password before storing it in the database
    hashed_password = bcrypt.hash(password)

    #this inserts the new user into the database
    cursor.execute("""
        INSERT INTO users (name, surname, username, email, phone_number, password)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, surname, username, email, phone_number, hashed_password))
    #this saves the changes and closes the database connection
    conn.commit()
    conn.close()
    #this returns a success message to the frontend
    return JSONResponse(content={"success": True, "message": "User registered successfully!"})