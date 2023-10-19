@echo off
setlocal enabledelayedexpansion
cls

set LOGFILE=%~dp0\install-log.txt
echo %date% %time% - Script started > %LOGFILE%

:: Check if running as administrator and, if not, elevate permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges... >> %LOGFILE%
    goto UACPrompt
) else (
    echo Running with administrative privileges... >> %LOGFILE%
    goto gotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
if exist "%temp%\getadmin.vbs" (
    del "%temp%\getadmin.vbs"
)
pushd "%CD%"
CD /D "%~dp0"

:: Create the C:\NexTool directory
if not exist "C:\NexTool\" (
    mkdir "C:\NexTool"
)

:: Set full permissions for the directory
icacls "C:\NexTool" /grant Everyone:F /T /C /Q

:: Check and Install Chocolatey
echo %date% %time% - Checking Chocolatey installation >> %LOGFILE%
choco --version > nul 2>&1
if errorlevel 1 (
    echo Chocolatey not detected. Attempting installation... >> %LOGFILE%
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex (((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1')))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    FOR /F "tokens=*" %%i in ('choco --version') do set CHOCO_VERSION=%%i
    IF NOT DEFINED CHOCO_VERSION (
        echo %date% %time% - Error: Failed to install Chocolatey! >> %LOGFILE%
        exit /B
    ) ELSE (
        echo Chocolatey version: %CHOCO_VERSION% >> %LOGFILE%
    )
) ELSE (
    FOR /F "tokens=*" %%i in ('choco --version') do set CHOCO_VERSION=%%i
    echo Chocolatey version: %CHOCO_VERSION% already installed >> %LOGFILE%
)

:: Note: From here, we follow a pattern for checking/installing each tool.

:CheckAria2c
echo %date% %time% - Checking aria2c installation >> %LOGFILE%
FOR /F "tokens=3" %%i in ('aria2c --version ^| findstr "aria2 version"') do set ARIA2C_VERSION=%%i
IF NOT DEFINED ARIA2C_VERSION (
    echo aria2c not detected. Installing... >> %LOGFILE%
    choco install aria2 -y -n
) ELSE (
    echo aria2c version: %ARIA2C_VERSION% already installed >> %LOGFILE%
)

:CheckWget
echo %date% %time% - Checking wget installation >> %LOGFILE%
FOR /F "tokens=3" %%i in ('wget --version ^| findstr "GNU Wget"') do set WGET_VERSION=%%i
IF NOT DEFINED WGET_VERSION (
    echo wget not detected. Installing... >> %LOGFILE%
    choco install wget -y -n
) ELSE (
    echo wget version: %WGET_VERSION% already installed >> %LOGFILE%
)

:CheckCurl
echo %date% %time% - Checking curl installation >> %LOGFILE%
FOR /F "tokens=2" %%i in ('curl --version ^| findstr "curl"') do set CURL_VERSION=%%i
IF NOT DEFINED CURL_VERSION (
    echo curl not detected. Installing... >> %LOGFILE%
    choco install curl -y -n
) ELSE (
    echo curl version: %CURL_VERSION% already installed >> %LOGFILE%
)

:CheckPowershellCore
echo %date% %time% - Checking PowerShell Core installation >> %LOGFILE%
FOR /F "delims=" %%i in ('pwsh --version 2^>^&1') do set POWERSHELLCORE_VERSION=%%i
IF NOT DEFINED POWERSHELLCORE_VERSION (
    echo PowerShell Core not detected. Installing... >> %LOGFILE%
    choco install powershell-core -y -n
) ELSE (
    echo PowerShell Core version: %POWERSHELLCORE_VERSION% already installed >> %LOGFILE%
    choco upgrade powershell-core -y -n
)

:Check-Python311
echo Checking for Python in C:\Python311... >> %LOGFILE%
if exist "C:\Python311\python.exe" (
    echo Found C:\Python311\python.exe >> %LOGFILE%
    "C:\Python311\python.exe" --version >> %LOGFILE%
) else (
    echo Python not found in C:\Python311! >> %LOGFILE%
    set /p user_input="Do you want to download and install Python 3.11? (yes/no): "
    if /i "%user_input%"=="yes" (
:: Define Python URL and destination
set PythonURL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe
set PythonDestination=C:\Temp\python-3.11.6-amd64.exe

:: Attempt download using curl
echo %date% %time% - Attempting Python download using curl >> %LOGFILE%
curl -L -o %PythonDestination% %PythonURL%
if "%errorlevel%"=="0" (
    goto InstallPython
) else (
    echo %date% %time% - Python download failed with curl >> %LOGFILE%
    goto TryPythonDownloadPowerShell
)

:TryPythonDownloadPowerShell
:: Attempt download using pwsh (PowerShell)
echo %date% %time% - Attempting Python download using PowerShell >> %LOGFILE%
pwsh -Command "Invoke-WebRequest -Uri '%PythonURL%' -OutFile '%PythonDestination%'"
if "%errorlevel%"=="0" (
    goto InstallPython
) else (
    echo %date% %time% - Python download failed with PowerShell >> %LOGFILE%
    goto TryPythonDownloadAria2
)

:TryPythonDownloadAria2
:: Attempt download using aria2
echo %date% %time% - Attempting Python download using aria2 >> %LOGFILE%
aria2c -o %PythonDestination% %PythonURL%
if "%errorlevel%"=="0" (
    goto InstallPython
) else (
    echo %date% %time% - Python download failed with aria2 >> %LOGFILE%
    goto TryPythonDownloadWget
)

:TryPythonDownloadWget
:: Attempt download using wget
echo %date% %time% - Attempting Python download using wget >> %LOGFILE%
wget -O %PythonDestination% %PythonURL%
if "%errorlevel%"=="0" (
    goto InstallPython
) else (
    echo %date% %time% - Python download failed with wget >> %LOGFILE%
    echo Failed to download Python 3.11.6. Please check your internet connection or try again later. >> %LOGFILE%
    exit /b
)

:InstallPython
echo Installing Python 3.11... >> %LOGFILE%
C:\Temp\python-3.11.6-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
del /f "C:\Temp\python-3.11.6-amd64.exe"
echo Python 3.11 installation completed >> %LOGFILE%
        echo Installing Python 3.11... >> %LOGFILE%
        C:\Temp\python-3.11.6-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
        del /f "C:\Temp\python-3.11.6-amd64.exe"
        echo Python 3.11 installation completed >> %LOGFILE%
    ) else (
        echo Skipping Python installation >> %LOGFILE%
    )
)

cls

:Beginactualscriptcommands

echo Installing/upgrading pip... >> %LOGFILE%
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Error: Failed to upgrade pip. Attempting to reinstall pip... >> %LOGFILE%

    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    if errorlevel 1 (
        echo Error: Failed to install/upgrade pip >> %LOGFILE%
        exit /b
    )
)

echo Installing/upgrading setuptools for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade setuptools
if errorlevel 1 (
    echo Error: Failed to install/upgrade setuptools >> %LOGFILE%
) else (
    echo Success: setuptools installed/upgraded successfully>> %LOGFILE%
)


echo Installing/upgrading pyqt5-tools for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade pyqt5-tools
if errorlevel 1 (
    echo Error: Failed to install/upgrade pyqt5-tools >> %LOGFILE%
) else (
    echo Success: pyqt5-tools installed/upgraded successfully >> %LOGFILE%
)


echo Installing/upgrading PyQt5-stubs for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade PyQt5-stubs
if errorlevel 1 (
    echo Error: Failed to install/upgrade PyQt5-stubs >> %LOGFILE%
) else (
    echo Success: PyQt5-stubs installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading pyqtgraph for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade pyqtgraph
if errorlevel 1 (
    echo Error: Failed to install/upgrade pyqtgraph >> %LOGFILE%
) else (
    echo Success: pyqtgraph installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading requests for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade requests
if errorlevel 1 (
    echo Error: Failed to install/upgrade requests >> %LOGFILE%
) else (
    echo Success: requests installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading psutil for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade psutil
if errorlevel 1 (
    echo Error: Failed to install/upgrade psutil >> %LOGFILE%
) else (
    echo Success: psutil installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading pywin32 for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade pywin32
if errorlevel 1 (
    echo Error: Failed to install/upgrade pywin32l >> %LOGFILE%
) else (
    echo Success: pywin32 installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading pywinauto for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade pywinauto
if errorlevel 1 (
    echo Error: Failed to install/upgrade pywinauto >> %LOGFILE%
) else (
    echo Success: pywinauto installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading pywinpty for Python 3.11... >> %LOGFILE%
"C:\Python311\python.exe" -m pip install --upgrade pywinpty
if errorlevel 1(
    echo Error: Failed to install/upgrade pywinpty >> %LOGFILE%
) else (
    echo Success: pywinpty installed/upgraded successfully >> %LOGFILE%
)



:LoggPreview
echo. >> %LOGFILE%
echo Installation Summary: >> %LOGFILE%
echo --------------------- >> %LOGFILE%
type %LOGFILE% | find "Failed" >nul
if errorlevel 1 (
    echo All installations were successful! >> %LOGFILE%
    echo All installations were successful!
) else (
    echo Some installations failed. Check the log for details. >> %LOGFILE%
    echo Some installations failed. Check the log for details.
)
pause

set /p user_input="Do you want to review the log? (yes/no): "
if /i "%user_input%"=="yes" (
    start notepad %LOGFILE%
)

cls && goto :Download-NexTool

:Download-NexTool
cls
set LOGFILE=%~dp0\download-log.txt
set NexToolURL=https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py

:: Initialize log
echo %date% %time% - Download Script started > %LOGFILE%

:: Define URL based on user's earlier choice of branch
set NexToolDestination=C:\NexTool\NexTool.py

:: Attempt download using curl
echo %date% %time% - Attempting download using curl >> %LOGFILE%
curl -L -o %NexToolDestination% %NexToolURL%
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with curl >> %LOGFILE% && goto :TryPowerShell
) else (
    echo %date% %time% - Download failed with curl >> %LOGFILE%
    goto TryPowerShell
)

:TryPowerShell
:: Attempt download using pwsh (PowerShell)
echo %date% %time% - Attempting download using PowerShell >> %LOGFILE%
pwsh -Command "Invoke-WebRequest -Uri '%NexToolURL%' -OutFile '%NexToolDestination%'"
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with PowerShell >> %LOGFILE% && goto :TryAria2
) else (
    echo %date% %time% - Download failed with PowerShell >> %LOGFILE%
    goto TryAria2
)

:TryAria2
:: Attempt download using aria2
echo %date% %time% - Attempting download using aria2 >> %LOGFILE%
aria2c -o %NexToolDestination% %NexToolURL%
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with aria2 >> %LOGFILE% && goto :TryWget
) else (
    echo %date% %time% - Download failed with aria2 >> %LOGFILE%
    goto TryWget
)

:TryWget
:: Attempt download using wget
echo %date% %time% - Attempting download using wget >> %LOGFILE%
wget -O %NexToolDestination% %NexToolURL%
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with wget >> %LOGFILE% && goto :end
) else (
    echo %date% %time% - Download failed with wget >> %LOGFILE%
)

C:\Python311\python.exe "%NexToolDestination%"

pause
endlocal
