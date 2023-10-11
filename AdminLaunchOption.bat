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
    FOR /F "delims=" %%i in ('choco --version 2^>^&1') do set CHOCO_VERSION=%%i
    IF NOT DEFINED CHOCO_VERSION (
        echo %date% %time% - Error: Failed to install Chocolatey! >> %LOGFILE%
        exit /B
    ) ELSE (
        echo Chocolatey version: %CHOCO_VERSION% >> %LOGFILE%
    )
) ELSE (
    FOR /F "delims=" %%i in ('choco --version 2^>^&1') do set CHOCO_VERSION=%%i
    echo Chocolatey version: %CHOCO_VERSION% already installed >> %LOGFILE%
)

:: Note: From here, we follow a pattern for checking/installing each tool.

:CheckAria2c
echo %date% %time% - Checking aria2c installation >> %LOGFILE%
FOR /F "delims=" %%i in ('aria2c --version ^| findstr "aria2 version"') do set ARIA2C_VERSION=%%i
IF NOT DEFINED ARIA2C_VERSION (
    echo aria2c not detected. Installing... >> %LOGFILE%
    choco install -y -n
) ELSE (
    echo aria2c version: %ARIA2C_VERSION% already installed >> %LOGFILE%
)

:CheckWget
echo %date% %time% - Checking wget installation >> %LOGFILE%
FOR /F "delims=" %%i in ('wget --version ^| findstr "GNU Wget"') do set WGET_VERSION=%%i
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

:CheckforPython3.11
echo %date% %time% - Checking for Python 3.11 installation >> %LOGFILE%
choco list --local-only | find "python 3.11" > nul
if errorlevel 1 (
    echo Python 3.11 not detected. Installing... >> %LOGFILE%
    choco install python --version 3.11.0 -y -n
) ELSE (
    echo Python 3.11 already installed >> %LOGFILE%
)

:CheckforPython3.12
echo %date% %time% - Checking for Python 3.12 installation >> %LOGFILE%
choco list --local-only | find "python 3.12" > nul
if errorlevel 1 (
    echo Python 3.12 not detected. Installing... >> %LOGFILE%
    choco install python --version 3.12.0 -y -n
) ELSE (
    echo Python 3.12 already installed >> %LOGFILE%
)

:CheckfornewerversionsofPython
echo %date% %time% - Checking for the latest version of Python >> %LOGFILE%
choco list --local-only | find "python" > nul
if errorlevel 1 (
    echo Latest version of Python not detected. Installing... >> %LOGFILE%
    choco install python -y -n
) ELSE (
    echo The latest version of Python already installed >> %LOGFILE%
)
:: You can add newer versions in a similar manner...

cls

:Beginactualscriptcommands

echo Installing/upgrading pip... >> %LOGFILE%
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
if errorlevel 1 (
    echo Error: Failed to install/upgrade pip >> %LOGFILE%
) else (
    rem Ensure pip is updated
    python -m pip install --upgrade pip
    if errorlevel 1 (
        echo Error: Failed to upgrade pip >> %LOGFILE%
    )
)

echo Installing/upgrading setuptools... >> %LOGFILE%
pip install --upgrade setuptools
if errorlevel 1 (
    echo Error: Failed to install/upgrade setuptools >> %LOGFILE%
)

echo Upgrading pip... >> %LOGFILE%
pip install --upgrade pip
if errorlevel 1 (
    echo Error: Failed to upgrade pip again >> %LOGFILE%
)

echo Installing/upgrading PyQt5 tools for Python 3.12... >> %LOGFILE%
C:\Python312\python.exe -m pip install --upgrade pyqt5-tools
if errorlevel 1 (
    echo Error: Failed to install/upgrade PyQt5 tools using Python 3.12 >> %LOGFILE%

    echo Attempting to install/upgrade PyQt5 tools with Python 3.11... >> %LOGFILE%
    C:\Python311\python.exe -m pip install --upgrade pyqt5-tools
    if errorlevel 1 (
        echo Error: Failed to install/upgrade PyQt5 tools using Python 3.11 as well >> %LOGFILE%
        echo You might have issues using the tool. Please consult the documentation or support. >> %LOGFILE%
    ) else (
        echo Success: PyQt5 tools installed/upgraded successfully using Python 3.11 >> %LOGFILE%
        echo Please use Python 3.11 for running the NexTool script. >> %LOGFILE%
    )
) ELSE (
    echo Success: PyQt5 tools installed/upgraded successfully using Python 3.12 >> %LOGFILE%
)

echo Installing/upgrading PyQt5 tools... >> %LOGFILE%
pip install --upgrade pyqt5-tools
if errorlevel 1 (
    echo Error: Failed to install/upgrade PyQt5 tools >> %LOGFILE%
)

echo Installing/upgrading PyQt5 stubs for SVG support... >> %LOGFILE%
pip install --upgrade PyQt5-stubs
if errorlevel 1 (
    echo Error: Failed to install/upgrade PyQt5 stubs for SVG support >> %LOGFILE%
)

echo Installing/upgrading pyqtgraph... >> %LOGFILE%
pip install --upgrade pyqtgraph
if errorlevel 1 (
    echo Error: Failed to install/upgrade pyqtgraph >> %LOGFILE%
)

echo Installing/upgrading requests... >> %LOGFILE%
pip install --upgrade requests
if errorlevel 1 (
    echo Error: Failed to install/upgrade requests >> %LOGFILE%
)

echo Installing/upgrading psutil... >> %LOGFILE%
pip install --upgrade psutil
if errorlevel 1 (
    echo Error: Failed to install/upgrade psutil >> %LOGFILE%
)

echo Installing/upgrading pywin32... >> %LOGFILE%
pip install --upgrade pywin32
if errorlevel 1 (
    echo Error: Failed to install/upgrade pywin32 >> %LOGFILE%
)

echo Installation/Upgrade completed! >> %LOGFILE%

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

cls

:Prompt-User
echo Please choose a branch:
echo 1. Main branch
echo 2. Development branch
set /p branch_choice="Enter your choice (1 or 2): "

if "%branch_choice%"=="1" (
    set NexToolURL=https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py
    goto Download-NexTool
) else if "%branch_choice%"=="2" (
    set NexToolURL=https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/dev/NexTool-Dev.py
    goto Download-NexTool
) else (
    echo Invalid choice. Exiting.
    exit /B
)

:Download-NexTool
cls
set LOGFILE=%~dp0\download-log.txt

:: Initialize log
echo %date% %time% - Download Script started > %LOGFILE%

:: Define URL based on user's earlier choice of branch
set NexToolDestination=C:\NexTool\NexTool.py

:: Attempt download using pwsh (PowerShell)
echo %date% %time% - Attempting download using PowerShell >> %LOGFILE%
pwsh -Command "Invoke-WebRequest -Uri '%NexToolURL%' -OutFile '%NexToolDestination%'"
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with PowerShell >> %LOGFILE%
    goto :end
) else (
    echo %date% %time% - Download failed with PowerShell >> %LOGFILE%
)

:: Attempt download using curl
echo %date% %time% - Attempting download using curl >> %LOGFILE%
curl -L -o %NexToolDestination% %NexToolURL%
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with curl >> %LOGFILE%
    goto :end
) else (
    echo %date% %time% - Download failed with curl >> %LOGFILE%
)

:: Attempt download using aria2
echo %date% %time% - Attempting download using aria2 >> %LOGFILE%
aria2c -o %NexToolDestination% %NexToolURL%
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with aria2 >> %LOGFILE%
    goto :end
) else (
    echo %date% %time% - Download failed with aria2 >> %LOGFILE%
)

:: Attempt download using wget
echo %date% %time% - Attempting download using wget >> %LOGFILE%
wget -O %NexToolDestination% %NexToolURL%
if "%errorlevel%"=="0" (
    echo %date% %time% - Download successful with wget >> %LOGFILE%
    goto :end
) else (
    echo %date% %time% - Download failed with wget >> %LOGFILE%
)

:end
echo %date% %time% - Download process completed >> %LOGFILE%
echo Download complete!

goto Check-Python-Version

:Check-Python-Version
echo Checking for Python in PATH... >> %LOGFILE%
echo Checking for Python in PATH...
for %%i in (python.exe) do (
    set python_path=%%~$PATH:i
    if not "!python_path!"=="" (
        echo Found !python_path! >> %LOGFILE%
        echo Found !python_path!
        "!python_path!" --version >> %LOGFILE%
        "!python_path!" --version
        echo. >> %LOGFILE%
        echo.
    )
)

echo Checking common installation locations... >> %LOGFILE%
echo Checking common installation locations...
for %%i in (C:\Python*, C:\Users\%username%\AppData\Local\Programs\Python\Python*) do (
    if exist "%%i\python.exe" (
        echo Found %%i\python.exe >> %LOGFILE%
        echo Found %%i\python.exe
        "%%i\python.exe" --version >> %LOGFILE%
        "%%i\python.exe" --version
        echo. >> %LOGFILE%
        echo.
    )
)

cls

:: List all Python versions and let the user choose
echo Available Python versions:
set count=0

for /f "tokens=*" %%i in ('where /R C:\ python.exe') do (
    set /a count+=1
    set python!count!=%%i
    echo !count!. %%i
)

:choice
echo Please select the Python version by number (1-!count!):
set /p selected_python=
if not defined python%selected_python% goto choice

:: Run the chosen Python version for your script
if exist "%NexToolDestination%" (
    echo Launching NexTool.py
    !python%selected_python%! "%NexToolDestination%"
) else (
    echo Failed to download NexTool.py
)

pause
endlocal
