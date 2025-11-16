from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sqlite3

app = FastAPI()

# This allows the frontend to communicate with the backend. We will use this only for current development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This connects the backend with the database
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "../Database/library.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# this routers are used to separate different functionalities/APIs of the backend.
# Every new functionality/API we make shoulb be in its own router file inside the routers folder and should be imported here
from .routers import registration

app.include_router(registration.router)

# This makes all paths work regardless of where the project is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This makes the frontend files be served by FastAPI as static files
STATIC_DIR = os.path.join(BASE_DIR, "../frontend")
HTML_DIR = os.path.join(STATIC_DIR, "HTML")

from fastapi.staticfiles import StaticFiles

# This is a custom StaticFiles class that disables caching, which i found usefull during development
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# This makes anything inside the frontend folder (HTML, CSS, JS, images)
# becomes accessible through URLs like: /static/HTML/SomePage.html
# We use NoCacheStaticFiles instead of StaticFiles to disable browser caching during development. Without this, browsers may show old versions of files
app.mount("/static", NoCacheStaticFiles(directory=STATIC_DIR), name="static")

# This makes our login page the root page, in other words, it serves UserLogin.html when someone accesses the base URL
@app.get("/")
def serve_login():
    file_path = os.path.join(HTML_DIR, "UserLogin.html")
    response = FileResponse(file_path)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# This serves the favicon.ico file when requested by browsers
@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))