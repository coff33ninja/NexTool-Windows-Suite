# Define the path for the log file
$LOGFILE = "$env:USERPROFILE\Desktop\install-log.txt"

# Define the paths for Python and NexTool
$pythonPath = "C:\Python311\python.exe"
$NexToolPath = "C:\NexTool\NexTool.py"

# Function to write log entries to the log file and console
Function LogWrite {
    Param ([string]$logEntry)
    "$(Get-Date) - $logEntry" | Out-File $LOGFILE -Append
    Write-Host $logEntry
}

# Function to install Chocolatey package manager
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

# Start of the main script
LogWrite "Script started"

# Check for administrative rights and elevate if necessary
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    LogWrite "Requesting administrative privileges..."
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}
LogWrite "Running with administrative privileges..."

# Create NexTool directory if it doesn't exist
if (-not (Test-Path C:\NexTool)) {
    New-Item -Path C:\NexTool -ItemType Directory | Out-Null
}

# Set full permissions for the NexTool directory
icacls 'C:\NexTool' /grant 'Everyone:F' /T /C /Q | Out-Null

# Install Chocolatey if not already installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    try {
        LogWrite "Chocolatey not detected. Attempting installation..."
        Install-Chocolatey
    }
    catch {
        LogWrite "Error installing Chocolatey!"
        exit
    }
}

# Check for Aria2c and install if necessary
if (-not (Get-Command aria2c -ErrorAction SilentlyContinue)) {
    try {
        LogWrite "Aria2c not detected. Attempting installation..."
        choco install aria2 -y
    }
    catch {
        LogWrite "Error installing Aria2c!"
        exit
    }
}

# Check for PowerShell Core and install/upgrade if necessary
if (-not (Get-Command pwsh -ErrorAction SilentlyContinue)) {
    try {
        LogWrite "PowerShell Core not detected. Attempting installation..."
        choco install powershell-core -y
    }
    catch {
        LogWrite "Error installing PowerShell Core!"
        exit
    }
}
else {
    choco upgrade powershell-core -y
}

# Check for Python, download and install if necessary
if (-not (Test-Path $pythonPath)) {
    try {
        LogWrite "Python not detected. Attempting download..."
        DownloadFile "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" "C:\NexTool\python-3.11.6-amd64.exe"
        LogWrite "Installing Python..."
        Start-Process -FilePath "C:\NexTool\python-3.11.6-amd64.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python311" -Wait
    }
    catch {
        LogWrite "Error installing Python!"
        exit
    }
}

# Download NexTool.py using WebClient
try {
    LogWrite "Downloading NexTool.py..."
    DownloadFile "https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py" $NexToolPath
}
catch {
    LogWrite "Error downloading NexTool.py"
    exit
}

# Launch NexTool.py if it exists
if (Test-Path $NexToolPath) {
    LogWrite "Launching NexTool.py"
    Start-Process -Wait -FilePath $pythonPath -ArgumentList $NexToolPath
}

# Check if the user wants to clean up
Clear-Host
$response = $null
while ($response -notmatch '^[yn]$') {
    $response = Read-Host "Do you wish to clean up and remove C:\NexTool? (Y/N)"
}
if ($response -eq 'y') {
    # Cleanup
    Remove-Item "C:\NexTool" -Recurse
    LogWrite "Cleanup completed. Removed C:\NexTool directory."
}

LogWrite "Script completed."