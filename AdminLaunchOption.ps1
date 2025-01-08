# Define the path for the log file
$LOGFILE = "$env:USERPROFILE\Desktop\install-log.txt"
Write-Output "$(Get-Date) - Script started" | Out-File $LOGFILE -Append

# Function to write log entries to the log file and console
Function LogWrite {
    Param ([string]$logEntry)
    "$(Get-Date) - $logEntry" | Out-File $LOGFILE -Append
    Write-Host $logEntry
}

# Function to test if a command exists
Function Test-Command {
    Param ([string]$command)
    return Get-Command $command -ErrorAction SilentlyContinue
}

# Function to test Windows version compatibility
Function Test-WindowsVersion {
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
Test-WindowsVersion

# Check and Install Chocolatey
LogWrite 'Checking Chocolatey installation...'
if (-not (Test-Command choco)) {
    LogWrite 'Chocolatey not detected. Attempting installation...'
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    RefreshEnv
    LogWrite 'Chocolatey installed successfully.'
} else {
    LogWrite 'Chocolatey is already installed.'
}

# Check and Install Winget
LogWrite 'Checking Winget installation...'
if (-not (Test-Command winget)) {
    LogWrite 'Winget not detected. Attempting installation...'
    choco install winget -y
} else {
    LogWrite 'Winget is already installed.'
}

# Check and Install aria2c
LogWrite 'Checking aria2c installation...'
if (-not (Test-Command aria2c)) {
    LogWrite 'aria2c not detected. Installing...'
    choco install aria2 -y
} else {
    LogWrite 'aria2c is already installed.'
}

# Check and Install PowerShell Core
LogWrite 'Checking PowerShell Core installation...'
if (-not (Test-Command pwsh)) {
    LogWrite 'PowerShell Core not detected. Installing...'
    choco install powershell-core -y
} else {
    LogWrite 'PowerShell Core is already installed.'
}

# Check for Python, download and install if necessary
$pythonPath = 'C:\Python311\python.exe'
if (-not (Test-Path $pythonPath)) {
    LogWrite 'Python not detected. Attempting download...'
    Invoke-WebRequest 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe' -OutFile 'C:\NexTool\python-3.11.6-amd64.exe'
    LogWrite 'Installing Python...'
    Start-Process 'C:\NexTool\python-3.11.6-amd64.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python311' -Wait
    LogWrite 'Python installed successfully.'
} else {
    LogWrite "Python found at $pythonPath."
}

# Upgrade pip
LogWrite 'Upgrading pip...'
& $pythonPath -m pip install --upgrade pip

# Install required Python packages
$packages = @('setuptools', 'pyqt5-tools', 'PyQt5-stubs', 'pyqtgraph', 'requests', 'psutil', 'pywin32')
foreach ($package in $packages) {
    LogWrite "Installing/upgrading $package..."
    & $pythonPath -m pip install --upgrade $package
}

# Download NexTool.py
LogWrite 'Downloading NexTool.py...'
Invoke-WebRequest 'https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py' -OutFile 'C:\NexTool\NexTool.py'

# Launch NexTool.py
LogWrite 'Launching NexTool.py...'
Start-Process $pythonPath 'C:\NexTool\NexTool.py'

# Script complete
LogWrite 'Script completed.'
