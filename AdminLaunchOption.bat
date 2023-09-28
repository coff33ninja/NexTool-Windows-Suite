@ECHO OFF
:SelfAdminTest
ECHO.
ECHO =============================
ECHO Running Admin shell
ECHO =============================

:init
setlocal DisableDelayedExpansion
set "batchPath=%~0"
for %%k in (%0) do set batchName=%%~nk
set "vbsGetPrivileges=%temp%\OEgetPriv_%batchName%.vbs"
setlocal EnableDelayedExpansion

:checkPrivileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )

:getPrivileges
if '%1'=='ELEV' (echo ELEV & shift /1 & goto gotPrivileges)
ECHO.
ECHO **************************************
ECHO Invoking UAC for Privilege Escalation
ECHO **************************************

ECHO Set UAC = CreateObject^("Shell.Application"^) > "%vbsGetPrivileges%"
ECHO args = "ELEV " >> "%vbsGetPrivileges%"
ECHO For Each strArg in WScript.Arguments >> "%vbsGetPrivileges%"
ECHO args = args ^& strArg ^& " "  >> "%vbsGetPrivileges%"
ECHO Next >> "%vbsGetPrivileges%"
ECHO UAC.ShellExecute "!batchPath!", args, "", "runas", 1 >> "%vbsGetPrivileges%"
"%SystemRoot%\System32\WScript.exe" "%vbsGetPrivileges%" %*
exit /B

:gotPrivileges
setlocal & pushd .
cd /d %~dp0
if '%1'=='ELEV' (del "%vbsGetPrivileges%" 1>nul 2>nul  &  shift /1)

rem ---- Start of Install/Update section ----

rem Create the NexTool directory if it doesn't exist
IF NOT EXIST C:\NexTool mkdir C:\NexTool
icacls C:\NexTool /grant Everyone:F

rem Create the PS directory if it doesn't exist
IF NOT EXIST C:\PS mkdir C:\PS
icacls C:\PS /grant Everyone:F

rem Ensure Chocolatey is installed or updated
choco -v || (
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
)
rem Install or update packages
choco install choco -y || choco upgrade choco -y
choco install aria2 -y || choco upgrade aria2 -y
choco install wget -y || choco upgrade wget -y
choco install curl -y || choco upgrade curl -y
choco install powershell-core || choco upgrade powershell-core -y

rem Check if winget is installed
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

for /f "delims=" %%i in ('winget --version') do set WINGET_VERSION=%%i
echo Winget version: %WINGET_VERSION%

for /f "delims=" %%i in ('choco --version 2^>^&1') do set CHOCO_VERSION=%%i
echo Chocolatey version: %CHOCO_VERSION%

for /f "delims=" %%i in ('aria2c --version ^| findstr "aria2 version"') do set ARIA2C_VERSION=%%i
echo %ARIA2C_VERSION%

for /f "delims=" %%i in ('wget --version ^| findstr "GNU Wget"') do set WGET_VERSION=%%i
echo %WGET_VERSION%

for /f "delims=" %%i in ('curl --version ^| findstr "curl"') do set CURL_VERSION=%%i
echo %CURL_VERSION%

echo Packagemanagers are up to date!

rem ---- End of Install/Update section ----

rem ---- Start of Python Setup section ----

rem Checking if Python is installed
python --version >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
   echo Python is not detected, attempting installation...

   rem Trying to install Python using winget
   winget install python --exact >NUL 2>&1
   IF %ERRORLEVEL% NEQ 0 (
      echo Winget method failed. Trying Chocolatey...
      choco install python -y
   )
)

rem Ensure pip is updated
python -m pip install --upgrade pip

rem Install Python packages
python -m pip install tk ttkthemes psutil wmi urllib3 pywin32 pypiwin32 ctypes zipfile

rem ---- End of Python Setup section ----

cls
python NexTool.py

echo Clearing out C:\NexTool...
del /Q C:\NexTool\*.*
for /D %%i in (C:\NexTool\*) do rmdir /S /Q "%%i"
rmdir /S /Q C:\NexTool

echo Clearing out C:\PS...
del /Q C:\PS\*.*
for /D %%i in (C:\PS\*) do rmdir /S /Q "%%i"
rmdir /S /Q C:\PS

pause
