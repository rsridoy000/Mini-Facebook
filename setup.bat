@echo off
title Mini-Facebook Automated Setup
echo ===================================================
echo       MINI-FACEBOOK AUTOMATED SETUP SYSTEM
echo ===================================================
echo.

:: Check if Python is installed
echo [1/6] Checking for Python installation...
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [!] Python is NOT installed or NOT in your system PATH.
        echo Attempting to install Python 3.11 automatically using winget...
        echo Please wait, this may take a few minutes...
        
        winget install -e --id Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
        
        if %errorlevel% neq 0 (
            echo.
            echo [X] ERROR: Automatic Python installation failed.
            echo Please download and install Python manually from: https://www.python.org/downloads/
            echo Make sure to check the box "Add Python to PATH" during installation.
            echo.
            pause
            exit /b 1
        )
        echo.
        echo [^o^] Python installed successfully!
        echo.
        echo [!] IMPORTANT: You MUST restart this command prompt window/VS Code
        echo     so the system recognizes the newly installed Python in your PATH.
        echo     After restarting, run setup.bat again.
        echo.
        pause
        exit /b 0
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo [OK] Python is available.
echo.

:: Setup Virtual Environment
echo [2/6] Setting up virtual environment...
if not exist .venv (
    echo Virtual environment (.venv) not found. Creating it now...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [X] ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)
echo.

:: Activate Virtual Environment
echo [3/6] Activating virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [X] ERROR: Activation script not found. Virtual environment might be corrupted.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.
echo.

:: Install Dependencies
echo [4/6] Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [X] ERROR: Failed to install packages from requirements.txt.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully.
) else (
    echo [!] WARNING: requirements.txt not found. Skipping dependency installation.
)
echo.

:: Run Migrations
echo [5/6] Creating database schemas and running migrations...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% neq 0 (
    echo [X] ERROR: Migrations failed.
    pause
    exit /b 1
)
echo [OK] Database migrations completed.
echo.

:: Create default superuser if not exists
echo [6/6] Checking default admin user...
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin user already exists.')"
echo [OK] Default credentials: Username [admin], Password [admin123]
echo.

echo ===================================================
echo     SETUP COMPLETE! Launching Mini-Facebook...
echo ===================================================
echo.
echo Launching your default browser to http://127.0.0.1:8000/
start http://127.0.0.1:8000/
echo.
echo Starting Django development server...
python manage.py runserver
pause
