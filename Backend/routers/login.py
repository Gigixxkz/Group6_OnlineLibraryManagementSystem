#----------------------------------------------------------------------------
# File: login.py
#  Created by: Georgia Kazara
#  Course: Software Engineering II
#  Project: Online Library Management System (Group 6)
#  Description: It handles the user login by checking the provided credentials.
#  Date Created: 19 November 2025
#  Last Updated: 19 November 2025
#----------------------------------------------------------------------------
from fastapi import APIRouter, HTTPException
import sqlite3, os
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

#The login endpoint:
@router.post("/login")
def login_user(data: dict):

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
    return {"message": "success"}
#----------------------------------------------------------------------------
