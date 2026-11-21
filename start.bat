@echo off
REM Kernify - Start Script for Windows
REM Runs the Django development server

echo ========================================
echo Kernify - Starting Development Server
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found. Run install.bat first.
    echo.
)

REM Check if virtual environment exists and activate it
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python.
)

REM Run migrations (in case new ones were added)
echo Checking for new migrations...
python manage.py migrate --check >nul 2>&1
if %errorlevel% neq 0 (
    echo New migrations found. Applying...
    python manage.py migrate
)

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput >nul

REM Start the server
echo.
echo Starting server at http://127.0.0.1:8000
echo Press CTRL+C to stop
echo ========================================
echo.

python manage.py runserver 127.0.0.1:8000