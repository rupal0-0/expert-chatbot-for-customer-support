@echo off
REM Quick launcher for the Support Chatbot GUI
echo Starting Support Chatbot...
python chatbot_gui.py
if errorlevel 1 (
    echo.
    echo Error: Failed to start the chatbot.
    echo Please make sure Python and dependencies are installed.
    echo Run: pip install -r requirements.txt
    pause
)
