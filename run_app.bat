@echo off
echo Activating virtual environment...
call .\venv\Scripts\activate.bat

echo Starting Flask application...
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
python -m flask run

pause