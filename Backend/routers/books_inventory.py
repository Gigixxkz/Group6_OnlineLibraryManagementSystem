
 #File:books_inventory.py
  #Created by: Andreas Andreou
  #Course: Software Engineering II
  #Project: Online Library Management System (Group 6)
  #Description: Homepage for the Archive of Light Library.
  #Date Created: 9 November 2025
  #Last Updated: 19 November 2025

#from fastapi import FastAPI, UploadFile, Form, HTTPException, File
#from fastapi.middleware.cors import CORSMiddleware
#from fastapi.responses import FileResponse
#import sqlite3, os, uuid, shutil
#app = FastAPI()

#--------------------------------------------------------------
#Georgia
#This file originally used FastAPI(), but our project must only
#have one main FastAPI app (in main.py). 
#To include Andreas' books API correctly, we need to convert this file 
#into a router.
from fastapi import APIRouter, UploadFile, Form, HTTPException, File
router = APIRouter(prefix="/books", tags=["Books"])
#--------------------------------------------------------------

#--------------------------------------------------------------
#Georgia:
#These imports were originally part of the FastAPI app block.
#Since that block is commented out now, we need to import them again
#because they are used for DB access, image saving, and file paths.
#--------------------------------------------------------------
import os
import sqlite3
import uuid
import shutil
from fastapi.responses import FileResponse

#--------------------------------------------------------------
#Georgia:
#This CORS middleware was originally used when this file was a
#full FastAPI app. After converting it into a router, it can no
#longer use app.add_middleware(), because only main.py is allowed
#to add middleware. main.py already handles CORS for the whole
#project, so we disable this block to avoid errors.
#--------------------------------------------------------------
#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)


DB_PATH = os.path.join("Database", "library.db")
IMAGE_DIR = "Images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# DB helper
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# GET all books

#Georgia change: using router instead of app
@router.get("/all") 

def get_all_books():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, author, publisher, year,
               description, isbn, language,
               cover_image, available
        FROM books
    """)
    books = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"books": books}

# Serve book image

#Georgia change: using router instead of app
@router.get("/image/{filename}")

def serve_image(filename: str):
    filepath = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)

# Add new book

#Georgia change:
@router.post("/add")

def add_book(
    title: str = Form(...),
    author: str = Form(...),
    publisher: str = Form(...),
    year: int = Form(...),
    description: str = Form(...),
    isbn: str = Form(...),
    language: str = Form(...),
    cover_image: UploadFile = File(...)  
):
    # Save image
    image_ext = cover_image.filename.split(".")[-1]
    image_name = f"{uuid.uuid4()}.{image_ext}"
    image_path = os.path.join(IMAGE_DIR, image_name)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(cover_image.file, buffer)

    # Insert into DB
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO books
        (title, author, publisher, year, description,
         isbn, language, cover_image,available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
    """, (title, author, publisher, year, description,
          isbn, language, image_name,1))
    conn.commit()
    conn.close()

    return {"message": "Book added successfully"}

# Remove / mark book unavailable

#Georgia change:
@router.post("/remove/{book_id}") 

def remove_book(book_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    cur.execute("UPDATE books SET available = 0 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return {"message": "Book removed"}

#undo remove 

#Georgia change:
@router.post("/restore/{book_id}")

def restore_book(book_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")

    cur.execute("UPDATE books SET available = 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    return {"message": "Book restored successfully"}

