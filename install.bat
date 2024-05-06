@echo off
setlocal

REM Path to your Python interpreter
set PYTHON=python

REM Name of your virtual environment directory
set VENV_DIR=venv

REM Check if the virtual environment already exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    %PYTHON% -m venv %VENV_DIR%
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate

REM Install requirements from requirements.txt
echo Installing requirements...
pip install -r requirements.txt

REM Deactivate the virtual environment
deactivate

echo Requirements installation completed.
pause
