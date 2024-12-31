@echo off
echo Building Expapyrus...

:: Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Install requirements
pip install -r requirements.txt

:: Run build script
python build.py

:: Check if build was successful
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build completed successfully!
pause