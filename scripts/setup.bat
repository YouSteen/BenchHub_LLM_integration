@echo off
echo Navigating to project root...
cd ..

echo Creating virtual environment...
py -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies from requirements.txt...
py -m pip install -r requirements.txt

echo.
echo ✅ Setup complete. Your virtual environment is ready.
pause
