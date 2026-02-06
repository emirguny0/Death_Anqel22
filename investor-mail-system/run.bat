@echo off
echo Yatirimci Mail Sistemi Baslatiliyor...
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
    echo Virtual environment bulunamadi veya aktif edilemedi.
    echo Lutfen once kurulumu yapin.
)
streamlit run app.py
pause
