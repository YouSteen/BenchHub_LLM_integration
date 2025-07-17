@echo off
cd ..

echo Creating virtual environment...
py -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo.
echo ✅ Setup complete. You can now run your app.
pause
