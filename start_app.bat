@echo off
echo ========================================
echo   ProScout AI - Starting Application
echo ========================================
echo.

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [ERROR] Streamlit is not installed!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [INFO] Starting Streamlit application...
echo [INFO] The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run streamlit_app.py

pause

