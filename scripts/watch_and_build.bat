@echo off
cd /d %~dp0
echo Activating virtual environment...
call ..\venv\Scripts\activate

echo Changing to root project folder...
cd ..

echo Running watch_and_build.py...
py watch_and_build.py

echo.
echo Done watching. Press any key to close.
pause
