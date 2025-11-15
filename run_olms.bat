@echo off
title Starting OLMS Backend
echo     Activating virtual environment...
call venv\Scripts\activate
echo     Starting FastAPI backend...
uvicorn Backend.main:app --reload
echo     Backend stopped. Press any key to exit.
pause
