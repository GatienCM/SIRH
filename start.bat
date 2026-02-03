@echo off
REM Script de démarrage du SIRH

echo Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Running migrations...
python manage.py migrate

echo Creating superuser...
python manage.py createsuperuser

echo Starting Django server...
python manage.py runserver

pause
