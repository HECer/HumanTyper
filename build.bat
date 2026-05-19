@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
:: --onefile creates a single .exe file
:: --windowed hides the console window when running the .exe
:: --collect-all customtkinter ensures all UI assets are included
pyinstaller --noconfirm --onefile --windowed --collect-all customtkinter main.py

echo.
echo Build finished! 
echo You can find your HumanTyper.exe inside the "dist" folder.
pause
