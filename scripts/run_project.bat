@echo off
cd /d %~dp0
echo Activating virtual environment...
call ..\venv\Scripts\activate

echo Running main.py...
py ..\src\main.py

echo.
echo Done. Press any key to close.
pause
