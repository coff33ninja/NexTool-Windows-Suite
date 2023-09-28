:: Main script initialization and admin privilege check
@ECHO ON
:SelfAdminTest
ECHO.
ECHO =============================
ECHO Running Admin shell
ECHO =============================

:init
rem -- Set local variables and create the VBScript for UAC privilege escalation
setlocal DisableDelayedExpansion
set "batchPath=%~0"
for %%k in (%0) do set batchName=%%~nk
set "vbsGetPrivileges=%temp%\OEgetPriv_%batchName%.vbs"
setlocal EnableDelayedExpansion

:checkPrivileges
rem -- Check if the script is running with admin privileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )

:getPrivileges
rem -- If not running with admin privileges, try to elevate permissions using VBScript
if '%1'=='ELEV' (echo ELEV & shift /1 & goto gotPrivileges)
ECHO.
ECHO **************************************
ECHO Invoking UAC for Privilege Escalation
ECHO **************************************
:: Writing the VBScript to elevate permissions
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%vbsGetPrivileges%"
ECHO args = "ELEV " >> "%vbsGetPrivileges%"
ECHO For Each strArg in WScript.Arguments >> "%vbsGetPrivileges%"
ECHO args = args ^& strArg ^& " "  >> "%vbsGetPrivileges%"
ECHO Next >> "%vbsGetPrivileges%"
ECHO UAC.ShellExecute "!batchPath!", args, "", "runas", 1 >> "%vbsGetPrivileges%"
"%SystemRoot%\System32\WScript.exe" "%vbsGetPrivileges%" %*
"%SystemRoot%\System32\WScript.exe" "%vbsGetPrivileges%" %*
if %errorlevel% neq 0 (
   echo Error during privilege escalation. Error level: %errorlevel%
   pause
   exit /B
)

:gotPrivileges
rem -- At this point, the script is running with admin privileges
setlocal & pushd .
cd /d %~dp0
if '%1'=='ELEV' (del "%vbsGetPrivileges%" 1>nul 2>nul  &  shift /1)

:: Begin the main package checking and installation routines

rem ---- Start of Install/Update section ----
SET WINGET_PYTHON_INSTALLED=0

rem -- Create the directories necessary for the tool if they don't already exist
IF NOT EXIST C:\NexTool mkdir C:\NexTool
icacls C:\NexTool /grant Everyone:F

rem Create the PS directory if it doesn't exist
IF NOT EXIST C:\PS mkdir C:\PS
icacls C:\PS /grant Everyone:F

:: Main script flow starts here
:: Execute the function to check for Chocolatey's presence
CALL :CheckChoco
GOTO CheckAria2c

:: ---------------------
:: FUNCTION DEFINITIONS
:: ---------------------

:: ----------------------------------------------
:: Function: CheckChoco
:: Purpose:  Check if Chocolatey is installed.
::           If not, attempts to install it.
::           If installation fails, script exits.
:: ----------------------------------------------

:CheckChoco
rem  Function to ensure Chocolatey is installed to manage packages
FOR /F "delims=" %i in ('choco --version 2^>^&1') do set CHOCO_VERSION=%%i

rem If Chocolatey is not detected, attempt installation
IF NOT DEFINED CHOCO_VERSION (
    echo Chocolatey not detected, attempting installation...
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"

    rem Re-check after installation to ensure Chocolatey is installed
    FOR /F "delims=" %i in ('choco --version 2^>^&1') do set CHOCO_VERSION=%%i
    IF NOT DEFINED CHOCO_VERSION (
        echo Error: Failed to install Chocolatey!
        exit /B
    )
) ELSE (
    echo Chocolatey version: %CHOCO_VERSION%
)
GOTO :EOF

:CheckAria2c
rem Ensure aria2c is installed for concurrent downloads
FOR /F "delims=" %i in ('aria2c --version ^| findstr "aria2 version"') do set ARIA2C_VERSION=%%i
IF NOT DEFINED ARIA2C_VERSION (
    echo aria2c not detected, installing...
    choco install aria2 -y
) ELSE (
    echo aria2c version: %ARIA2C_VERSION%
)
GOTO CheckWget

:CheckWget
rem Ensure wget is available for web operations
FOR /F "delims=" %i in ('wget --version ^| findstr "GNU Wget"') do set WGET_VERSION=%%i
IF NOT DEFINED WGET_VERSION (
    echo wget not detected, installing...
    choco install wget -y
) ELSE (
    echo wget version: %WGET_VERSION%
)
GOTO CheckCurl

:CheckCurl
rem Ensure curl is available for web requests
FOR /F "tokens=2" %i in ('curl --version ^| findstr "curl"') do set CURL_VERSION=%%i
IF NOT DEFINED CURL_VERSION (
    echo curl not detected, installing...
    choco install curl -y
) ELSE (
    echo curl version: %CURL_VERSION%
)
GOTO CheckPowershellCore

:CheckPowershellCore
rem Ensure PowerShell Core is present for advanced scripting
FOR /F "delims=" %i in ('pwsh --version 2^>^&1') do set POWERSHELLCORE_VERSION=%%i
IF NOT DEFINED POWERSHELLCORE_VERSION (
    echo powershell-core not detected, installing...
    choco install powershell-core -y
) ELSE (
    echo powershell-core version: %POWERSHELLCORE_VERSION%
    choco upgrade powershell-core -y
)
GOTO CheckPython

rem ---- Start of Python Setup section ----
rem ---- Using this approach to ensure Python is installed, and to avoid issues with Winget compatibility for older gen Windows ----

:CheckPython
rem Checking if Python is installed
python --version >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
   echo Python is not detected, attempting installation...

   rem Retrieving Windows version
   FOR /F "tokens=2 delims==" %I IN ('wmic os get version /value') DO SET "winver=%%I"
   SET winver=%winver:~0,2%

   rem Only proceed if Windows version is 10 or 11
   IF "%winver%"=="10" OR "%winver%"=="11" (
      rem Trying to install Python using winget
      winget install python --exact >NUL 2>&1
      IF %ERRORLEVEL% NEQ 0 (
         echo Winget method failed. Would you like to:
         echo 1. Attempt installation using Chocolatey?
         echo 2. Install manually?
         SET /P UserChoice=Enter your choice (1/2):
         IF /I "%UserChoice%"=="1" (
            choco install python -y
         ) ELSE IF /I "%UserChoice%"=="2" (
            echo Please manually install Python from the official website: "https://www.python.org/downloads/"
            pause
            exit
         )
      )
   ) ELSE (
      echo This system is not Windows 10 or 11. Using Chocolatey to install Python...
      choco install python -y
   )
) ELSE (
   echo Python is already installed.
)
GOTO InstallPythonPackages

:InstallPythonPackages
rem Ensure pip is updated
python -m pip install --upgrade pip

rem Install Python packages
python -m pip install tk
python -m pip install ttkthemes
python -m pip install psutil
python -m pip install wmi
python -m pip install urllib3
python -m pip install pywin32
python -m pip install pypiwin32
python -m pip install ctypes
python -m pip install zipfile

python -m pip3 install tk
python -m pip3 install ttkthemes
python -m pip3 install psutil
python -m pip3 install wmi
python -m pip3 install urllib3
python -m pip3 install pywin32
python -m pip3 install pypiwin32
python -m pip3 install ctypes
python -m pip3 install zipfile
GOTO CheckWinget

rem ---- End of Python Setup section ----
rem ---- This is the start of a horrible mess for Winget due to no actual possible way to check for the installed version of winget or to even Install it ----

:CheckWinget
rem Check if winget is installed
IF %WINGET_PYTHON_INSTALLED% NEQ 1 (
    IF "%winver%"=="10" OR "%winver%"=="11" (
        echo Winget is not detected.
        SET /P UserChoice=Would you like to install the winget package manager manually from the Microsoft Store? (Y/N):
        IF /I "%UserChoice%"=="Y" (
            start "https://aka.ms/winget-install"
            echo Please install winget and then re-run this script.
            pause
            exit
        )
        rem If user declines, or if the system lacks Microsoft Store, attempt the lengthy auto-installation

winget --version >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
   echo Winget is not detected, attempting installation...

   echo [Method 1] Trying to install using latest release link with PowerShell...
   powershell -Command "Invoke-WebRequest -Uri 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle' -OutFile 'C:\PS\WinGet.ps1.msixbundle'"

   IF NOT EXIST 'C:\PS\WinGet.ps1.msixbundle' (
      echo [Method 1.1] Trying to install using latest release link with PowerShell 7...
      pwsh -Command "Invoke-WebRequest -Uri 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle' -OutFile 'C:\PS\WinGet.pwsh1.msixbundle'"
   ) ELSE (
      GOTO InstallWinget
   )

   IF NOT EXIST 'C:\PS\WinGet.pwsh1.msixbundle' (
      echo [Method 1.2] PowerShell method failed. Trying with aria2...
      aria2c "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle" -d C:\PS -o WinGet.aria2.msixbundle
   ) ELSE (
      GOTO InstallWinget
   )

   IF NOT EXIST 'C:\PS\WinGet.aria2.msixbundle' (
      echo [Method 1.3] aria2 method failed. Trying with curl...
      curl -L -o C:\PS\WinGet.curl.msixbundle "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
   ) ELSE (
      GOTO InstallWinget
   )

   :InstallWinget
   powershell -Command "Get-ChildItem 'C:\PS\WinGet.*.msixbundle' | ForEach-Object { Add-AppxPackage $_.FullName }"

   rem Cleanup .msixbundle files
   del /Q C:\PS\*.msixbundle

   winget --version >NUL 2>&1
   IF %ERRORLEVEL% NEQ 0 (
      echo [Method 2] Please manually install "App Installer" from the Microsoft Store.
      echo Opening the Microsoft Store page for "App Installer"...
      start "https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1"
      pause
      exit
   )
)

cls

:Last-double-check
rem -- A final check for validations
rem -- Display installed versions of tools to verify successful installations

for /f "delims=" %i in ('winget --version') do set WINGET_VERSION=%%i
echo Winget version: %WINGET_VERSION%

for /f "delims=" %i in ('choco --version 2^>^&1') do set CHOCO_VERSION=%%i
echo Chocolatey version: %CHOCO_VERSION%

for /f "delims=" %i in ('aria2c --version ^| findstr "aria2 version"') do set ARIA2C_VERSION=%%i
echo %ARIA2C_VERSION%

for /f "delims=" %i in ('wget --version ^| findstr "GNU Wget"') do set WGET_VERSION=%%i
echo %WGET_VERSION%

for /f "delims=" %i in ('curl --version ^| findstr "curl"') do set CURL_VERSION=%%i
echo %CURL_VERSION%

for /f "delims=" %i in ('python --version ^| findstr "python"') do set python_VERSION=%%i
echo %python_VERSION%

echo Packagemanagers are up to date!
GOTO END

rem ---- End of Install/Update section ----

:END
rem -- Cleanup and end of the script
cls
python %~dp0\NexTool.py
cls
goto Cleanup

:CleanUp
rem -- Clean directories post operations to leave no traces behind
echo Clearing out C:\NexTool...
del /Q C:\NexTool\*.*
for /D %%i in (C:\NexTool\*) do rmdir /S /Q "%%i"
rmdir /S /Q C:\NexTool

echo Clearing out C:\PS...
del /Q C:\PS\*.*
for /D %%i in (C:\PS\*) do rmdir /S /Q "%%i"
rmdir /S /Q C:\PS

pause
exit
@echo off
