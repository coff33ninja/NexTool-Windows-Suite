# Define the path for the log file
$LOGFILE = "$env:USERPROFILE\Desktop\install-log.txt"
Write-Output "$(Get-Date) - Script started" | Out-File $LOGFILE -Append

# Function to write log entries to the log file and console
Function LogWrite {
    Param ([string]$logEntry)
    "$(Get-Date) - $logEntry" | Out-File $LOGFILE -Append
    Write-Host $logEntry
}

# Function to check if a command exists
Function Check-Command {
    Param ([string]$command)
    return Get-Command $command -ErrorAction SilentlyContinue
}

# Function to install Chocolatey
Function Install-Chocolatey {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    RefreshEnv
}

# Function to download a file from a URL to a destination
Function DownloadFile {
    Param ([string]$url, [string]$destination)
    $wc = New-Object System.Net.WebClient
    $wc.DownloadFile($url, $destination)
}

# Function to check Windows version
Function Check-WindowsVersion {
    $version = [System.Environment]::OSVersion.Version
    if ($version.Major -lt 10) {
        LogWrite 'Winget is only available for Windows 10 and later. Exiting script.'
        exit
    }
}

# Start of the main script
LogWrite 'Script started'

# Check for administrative rights and elevate if necessary
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    LogWrite 'Requesting administrative privileges...'
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}
LogWrite 'Running with administrative privileges...'

# Create the C:\NexTool directory
if (-not (Test-Path 'C:\NexTool')) {
    New-Item -Path 'C:\NexTool' -ItemType Directory | Out-Null
}

# Set full permissions for the directory
icacls 'C:\NexTool' /grant Everyone:F /T /C /Q
if ($LASTEXITCODE -ne 0) {
    LogWrite 'Error setting permissions for C:\NexTool'
    exit
}

# Check Windows version
Check-WindowsVersion

# Check and Install Chocolatey
LogWrite 'Checking Chocolatey installation'
if (-not (Check-Command choco)) {
    LogWrite 'Chocolatey not detected. Attempting installation...'
    Install-Chocolatey
    if (-not (Check-Command choco)) {
        LogWrite 'Error: Failed to install Chocolatey!'
        exit
    }
    LogWrite 'Chocolatey installed successfully.'
}
else {
    LogWrite 'Chocolatey is already installed.'
}

# Check and Install Winget
LogWrite 'Checking Winget installation'
if (-not (Check-Command winget)) {
    LogWrite 'Winget not detected. Attempting installation...'
    choco install winget -y
}
else {
    LogWrite 'Winget is already installed. Checking for updates...'
    choco upgrade winget -y
}

# Check and Install aria2c
LogWrite 'Checking aria2c installation'
if (-not (Check-Command aria2c)) {
    LogWrite 'aria2c not detected. Installing...'
    choco install aria2 -y
}
else {
    LogWrite 'aria2c is already installed.'
}

# Check and Install PowerShell Core
LogWrite 'Checking PowerShell Core installation'
if (-not (Check-Command pwsh)) {
    LogWrite 'PowerShell Core not detected. Installing...'
    choco install powershell-core -y
}
else {
    LogWrite 'PowerShell Core is already installed. Checking for updates...'
    choco upgrade powershell-core -y
}

# Check for Python, download and install if necessary
$pythonPath = 'C:\Python311\python.exe'
if (-not (Test-Path $pythonPath)) {
    LogWrite 'Python not detected. Attempting download...'
    DownloadFile 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe' 'C:\NexTool\python-3.11.6-amd64.exe'
    if ($LASTEXITCODE -eq 0) {
        LogWrite 'Downloaded Python installer successfully.'
        LogWrite 'Installing Python...'
        Start-Process 'C:\NexTool\python-3.11.6-amd64.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python311' -Wait
        if ($LASTEXITCODE -ne 0) {
            LogWrite 'Failed to install Python.'
            exit
        }
        LogWrite 'Python installed successfully.'
    }
    else {
        LogWrite 'Failed to download Python installer.'
        exit
    }
}
else {
    LogWrite "Python found at $pythonPath."
}

# Upgrade pip
LogWrite 'Upgrading pip...'
& $pythonPath -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    LogWrite 'Error: Failed to upgrade pip.'
    exit
}
else {
    LogWrite 'Successfully upgraded pip.'
}

# Install required Python packages
$packages = @('setuptools', 'pyqt5-tools', 'PyQt5-stubs', 'pyqtgraph', 'requests', 'psutil', 'pywin32')
foreach ($package in $packages) {
    LogWrite "Installing/upgrading $package..."
    & $pythonPath -m pip install --upgrade $package
    if ($LASTEXITCODE -ne 0) {
        LogWrite "Error: Failed to install/upgrade $package."
    }
    else {
        LogWrite "Success: $package installed/upgraded successfully."
    }
}

# Download NexTool.py
LogWrite 'Attempting to download NexTool.py...'
DownloadFile 'https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py' 'C:\NexTool\NexTool.py'
if ($LASTEXITCODE -eq 0) {
    LogWrite 'Downloaded NexTool.py successfully.'
    LogWrite 'Launching NexTool.py...'
    Start-Process $pythonPath 'C:\NexTool\NexTool.py'
}
else {
    LogWrite 'Failed to download NexTool.py.'
}

# Summary of installations
LogWrite 'Installation Summary:'
$logContent = Get-Content $LOGFILE
if ($logContent -match 'Error') {
    LogWrite 'Some installations failed. Check the log for details.'
}
else {
    LogWrite 'All installations were successful!'
}

# Prompt user to review the log
$userInput = Read-Host 'Do you want to review the log? (yes/no)'
if ($userInput -eq 'yes') {
    Start-Process notepad.exe $LOGFILE
}

# Cleanup logic
LogWrite 'Cleaning up...'
if (Test-Path 'C:\NexTool') {
    Remove-Item 'C:\NexTool\*' -Recurse -Force
    Remove-Item 'C:\NexTool' -Force
    LogWrite 'Cleanup complete.'
}
else {
    LogWrite 'C:\NexTool does not exist. No cleanup necessary.'
}

LogWrite 'Script completed.'
