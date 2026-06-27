@echo off
REM Quick start script for Windows
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -q -r requirements.txt
if not exist instance\shop.db (
    echo Seeding database with sample data...
    python seed.py
)
echo.
echo ============================================
echo  Starting %STORE_NAME% on http://127.0.0.1:5000
echo  Admin: admin@shophub.com / admin123
echo ============================================
echo.
python app.py
