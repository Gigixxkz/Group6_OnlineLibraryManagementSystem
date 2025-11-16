from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
from ..main import get_db_connection   # this imports DB function from the main.py file

# this defines the prefix for all routes in this file as /registration, in other words, all routes here will start with /registration
router = APIRouter(prefix="/registration", tags=["Registration"])

# this is the registration endpoint that the frontend will call to register a new user
@router.post("/register")
def register_user(
    # The Form(...) parameters tell FastAPI to read these values from form-data
    # submitted by fetch() or an HTML form
    name: str = Form(...),
    surname: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    password: str = Form(...)
):
    # this establishes a connection to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # This sends a query to the database check if the username or email already exist
    cursor.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    # If a record is found, returns an error response
    if cursor.fetchone():
        conn.close()
        return JSONResponse(
            content={"success": False, "message": "Username or email already exists."}
        )

    # this hashes the password using bcrypt before storing it in the database for security
    hashed_password = bcrypt.hash(password)

    # this is the query that inserts the new user into the users table
    cursor.execute("""
        INSERT INTO users (name, surname, username, email, phone_number, password)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, surname, username, email, phone_number, hashed_password))

    conn.commit()
    conn.close()
    # returns a success response
    return JSONResponse(content={"success": True, "message": "User registered successfully!"})
