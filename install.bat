@echo off
REM RTK - Installation Script for Windows
REM This script sets up the Django project with all dependencies

echo ========================================
echo RTK - Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo [1/6] Python found:
python --version

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo [2/6] Upgrading pip...
python -m pip install --upgrade pip

echo [3/6] Installing dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)

echo [4/6] Creating .env file from template...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo Created .env file. Please edit it with your settings.
    ) else (
        echo WARNING: .env.example not found, creating basic .env
        echo SECRET_KEY=django-insecure-change-this-in-production > .env
        echo DEBUG=True >> .env
        echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env
        echo DATABASE_URL=sqlite:///db.sqlite3 >> .env
    )
) else (
    echo .env file already exists, skipping.
)

echo [5/6] Running migrations...
python manage.py migrate

echo [6/6] Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Create a superuser: python manage.py createsuperuser
echo 3. Run the server: start.bat
echo.
pause