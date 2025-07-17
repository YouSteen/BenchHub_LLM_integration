@echo off
echo Cloning BenchHub LLM Integration...
git clone https://github.com/YouSteen/BenchHub_LLM_integration.git

cd BenchHub_LLM_integration

echo Creating virtual environment...
py -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo.
echo ✅ Setup complete. You can now run your app.
pause
