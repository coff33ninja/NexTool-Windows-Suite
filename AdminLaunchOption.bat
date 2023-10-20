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
if "%errorlevel%" NEQ "0" (
    echo %date% %time% - Error setting permissions for C:\NexTool >> %LOGFILE%
    echo Failed to set permissions for C:\NexTool.
    pause
    exit /B
)
cd /D "C:\NexTool"

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
goto CheckPowershellCore

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
cls && goto CheckforPython3.11

:CheckforPython3.11
echo Checking for Python in PATH... >> %LOGFILE%
echo Checking for Python in PATH...
set python_path=C:\Python311\python.exe
if exist "!python_path!" (
    echo Found !python_path! >> %LOGFILE%
    echo Found !python_path!
    "!python_path!" --version >> %LOGFILE%
    "!python_path!" --version
    echo. >> %LOGFILE%
    echo.
    goto Beginactualscriptcommands
) else (
    echo Python 3.11.6 not found at expected location. >> %LOGFILE%
    goto DownloadPython
)


:: Refactored Download Function
:DownloadFile
:: Parameters: %1=URL, %2=Destination
setlocal
echo %date% %time% - Attempting download using aria2... >> %LOGFILE%
aria2c -o "%~2" "%~1"
if "%errorlevel%"=="0" (
    echo %date% %time% - Downloaded successfully with aria2 >> %LOGFILE%
    endlocal && set "DOWNLOAD_RESULT=0"
    goto :eof
) else (
    echo %date% %time% - Failed to download with aria2. Trying PowerShell... >> %LOGFILE%
    pwsh -Command "Invoke-WebRequest -Uri '%~1' -OutFile '%~2'"
    if "%errorlevel%"=="0" (
        echo %date% %time% - Downloaded successfully with PowerShell >> %LOGFILE%
        endlocal && set "DOWNLOAD_RESULT=0"
    ) else (
        echo %date% %time% - Download failed with both methods >> %LOGFILE%
        endlocal && set "DOWNLOAD_RESULT=1"
    )
    goto :eof
)

:DownloadPython
:: Direct link to Python 3.11.6 installer
set PYTHON_INSTALLER_PATH=python-3.11.6-amd64.exe
set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe

:: For Python installer
call :DownloadFile %PYTHON_INSTALLER_URL% %PYTHON_INSTALLER_PATH%
if "%DOWNLOAD_RESULT%"=="1" (
    echo All above methods failed. Proceeding to manual method >> %LOGFILE%
    goto PythonDownloadCheck
)
pause

:: Install Python
echo %date% %time% - Installing Python 3.11.6... >> %LOGFILE%
%PYTHON_INSTALLER_PATH% /quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python
if "%errorlevel%"=="0" (
    echo %date% %time% - Python 3.11.6 installed successfully >> %LOGFILE%
    goto CheckforPython3.11
) else (
    echo %date% %time% - Failed to install Python 3.11.6. Aborting... >> %LOGFILE%
    goto :PythonDownloadCheck
)


:PythonDownloadCheck
if not exist "!PYTHON_INSTALLER_PATH!" (
    echo %date% %time% - Python installer was not downloaded. Prompting user for manual installation... >> %LOGFILE%
    echo The Python 3.11.6 installer was not downloaded successfully.
    echo Please download and install it manually from:
    echo %PYTHON_INSTALLER_URL%
    echo Make sure to install it to C:\Python and select all default options.
    echo If you have installed it already, you can continue with the next steps.
    pause
    goto CheckforPython3.11
) else (
    :: Creating a shortcut to the installer on the Desktop if the download succeeded
    echo %date% %time% - Creating a shortcut to the Python installer on the Desktop... >> %LOGFILE%
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('$env:USERPROFILE\Desktop\Python 3.11.6 Installer.lnk'); $Shortcut.TargetPath = '!PYTHON_INSTALLER_PATH!'; $Shortcut.Save()"
    echo %date% %time% - Shortcut created. >> %LOGFILE%
    echo A shortcut to the Python installer has been placed on your desktop.
    echo Please run it and select all default options for installation.
    pause
)

cls && goto VerifyPython3.11

:VerifyPython3.11
echo Checking for Python in PATH... >> %LOGFILE%
echo Checking for Python in PATH...
set python_path=C:\Python311\python.exe
if exist "!python_path!" (
    echo Found !python_path! >> %LOGFILE%
    echo Found !python_path!
    "!python_path!" --version >> %LOGFILE%
    "!python_path!" --version
    echo. >> %LOGFILE%
    echo.
    goto Beginactualscriptcommands
) else (
    echo Python 3.11.6 not found at expected location. >> %LOGFILE%
    exit /B
)

:Beginactualscriptcommands

echo Installing/upgrading pip... >> %LOGFILE%
"!python_path!" -m pip install --upgrade pip
if errorlevel 1 (
    set get-pip=https://bootstrap.pypa.io/get-pip.py
    echo Error: Failed to upgrade pip. Attempting to reinstall pip... >> %LOGFILE%
    set get-pip-path=%~dp0\get-pip.py
    aria2c -o "!get-pip-path!" %get-pip%
    "!python_path!" "!get-pip-path!"
    if errorlevel 1 (
        echo Error: Failed to install/upgrade pip >> %LOGFILE%
        exit /b
    )
)

echo Installing/upgrading setuptools for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade setuptools
if errorlevel 1 (
    echo Error: Failed to install/upgrade setuptools >> %LOGFILE%
) else (
    echo Success: setuptools installed/upgraded successfully >> %LOGFILE%
)


echo Installing/upgrading pyqt5-tools for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade pyqt5-tools
if errorlevel 1 (
    echo Error: Failed to install/upgrade pyqt5-tools >> %LOGFILE%
) else (
    echo Success: pyqt5-tools installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading PyQt5-stubs for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade PyQt5-stubs
if errorlevel 1 (
    echo Error: Failed to install/upgrade PyQt5-stubs >> %LOGFILE%
) else (
    echo Success: PyQt5-stubs installed/upgraded >> %LOGFILE%
)

echo Installing/upgrading pyqtgraph for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade pyqtgraph
if errorlevel 1 (
    echo Error: Failed to install/upgrade pyqtgraph >> %LOGFILE%
) else (
    echo Success: pyqtgraph installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading requests for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade requests
if errorlevel 1 (
    echo Error: Failed to install/upgrade requests >> %LOGFILE%
) else (
    echo Success: requests installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading psutil for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade psutil
if errorlevel 1 (
    echo Error: Failed to install/upgrade psutil >> %LOGFILE%
) else (
    echo Success: psutil installed/upgraded successfully >> %LOGFILE%
)

echo Installing/upgrading pywin32 for Python 3.11... >> %LOGFILE%
"!python_path!" -m pip install --upgrade pywin32
if errorlevel 1 (
    echo Error: Failed to install/upgrade pywin32 >> %LOGFILE%
) else (
    echo Success: pywin32 installed/upgraded successfully >> %LOGFILE%
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

cls && goto :Links

:Links
:: For NexTool.py
set NexToolDestination=NexTool.py
set NexToolURL=https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py

call :DownloadFile %NexToolURL% %NexToolDestination%
if "%DOWNLOAD_RESULT%"=="1" (
    :: Handle error here for NexTool.py
    goto :Launch
)
:Launch
:: Run the chosen Python version for your script
if exist "%NexToolDestination%" (
    echo Launching NexTool.py
    start "" "!python_path!" "%NexToolDestination%"
) else (
    echo Failed to download NexTool.py
)

pause
endlocal
