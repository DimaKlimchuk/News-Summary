@echo off
chcp 65001 >nul
echo 🔧 Встановлення залежностей і запуск сервера...

REM Крок 1: запуск Python скрипта для створення venv і встановлення requirements
python install_dependencies.py

REM Крок 2: активація venv
call venv\Scripts\activate.bat

REM Крок 3: запуск Flask-сервера
echo Запуск Flask-сервера...
set FLASK_APP=webapp/app.py
set FLASK_ENV=development
flask run

pause
