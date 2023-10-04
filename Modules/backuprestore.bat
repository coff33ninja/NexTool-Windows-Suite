@echo off
:: Get the directory where the BAT file is located
set "script_dir=%~dp0"

:: Navigate to that directory
cd /d "%script_dir%"

:: Run the Python script using Python 3.11
C:\Python311\python.exe BACKUP_AND_RESTORE.py

exit
