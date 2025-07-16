@echo off
cd /d %~dp0
echo Activating virtual environment...
call ..\venv\Scripts\activate

echo Changing to build directory...
cd ..\build

echo Running build.py...
py build.py

echo.
echo Build complete. Press any key to close.
pause
