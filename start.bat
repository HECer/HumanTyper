@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting HumanTyper...
python main.py
pause
