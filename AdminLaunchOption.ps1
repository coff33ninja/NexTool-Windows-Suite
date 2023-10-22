$LOGFILE = "$env:USERPROFILE\Desktop\install-log.txt"
$pythonPath = "C:\Python311\python.exe"
$NexToolPath = "C:\NexTool\NexTool.py"

Function LogWrite {
    Param ([string]$logEntry)
    "$(Get-Date) - $logEntry" | Out-File $LOGFILE -Append
    Write-Host $logEntry
}

function MinimizeWindow {
    Add-Type -TypeDefinition @"
        using System;
        using System.Runtime.InteropServices;

        public class Window {
            [DllImport("user32.dll")]
            public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

            [DllImport("kernel32.dll")]
            public static extern IntPtr GetConsoleWindow();

            public const int SW_MINIMIZE = 6;
            public const int SW_RESTORE = 9;
        }
"@

    [void][Window]::ShowWindow([Window]::GetConsoleWindow(), [Window]::SW_MINIMIZE)
}

function RestoreWindow {
    [void][Window]::ShowWindow([Window]::GetConsoleWindow(), [Window]::SW_RESTORE)
}

Function Install-Chocolatey {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    RefreshEnv
}

Function Download-File {
    Param ([string]$url, [string]$destination)
    $downloadSuccess = $false

    if (Get-Command aria2c -ErrorAction SilentlyContinue) {
        try {
            aria2c --disable-ipv6 -x 4 -o (Split-Path -Leaf $destination) -d (Split-Path -Parent $destination) --allow-overwrite=true $url
            $downloadSuccess = $true
        } catch {
            LogWrite "Failed to download using aria2c. Trying PowerShell..."
        }
    }

    if (-not $downloadSuccess) {
        try {
            Invoke-WebRequest -Uri $url -OutFile $destination
            $downloadSuccess = $true
        } catch {
            LogWrite "Failed to download using PowerShell."
        }
    }

    if (-not $downloadSuccess) {
        Throw "Failed to download using both aria2c and PowerShell."
    }
}

LogWrite "Script started"

# Check for administrative rights
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    LogWrite "Requesting administrative privileges..."
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}
LogWrite "Running with administrative privileges..."

# Create NexTool directory if it doesn't exist
if (-not (Test-Path C:\NexTool)) {
    New-Item -Path C:\NexTool -ItemType Directory
}

# Set full permissions for the NexTool directory
icacls 'C:\NexTool' /grant 'Everyone:F' /T /C /Q

# Install Chocolatey if not already installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    try {
        LogWrite "Chocolatey not detected. Attempting installation..."
        Install-Chocolatey
    } catch {
        LogWrite "Error installing Chocolatey!"
        exit
    }
}

# Check for Aria2c and install if necessary
if (-not (Get-Command aria2c -ErrorAction SilentlyContinue)) {
    try {
        LogWrite "Aria2c not detected. Attempting installation..."
        choco install aria2 -y
    } catch {
        LogWrite "Error installing Aria2c!"
        exit
    }
}

# Check for PowerShell Core and install/upgrade if necessary
if (-not (Get-Command pwsh -ErrorAction SilentlyContinue)) {
    try {
        LogWrite "PowerShell Core not detected. Attempting installation..."
        choco install powershell-core -y
    } catch {
        LogWrite "Error installing PowerShell Core!"
        exit
    }
} else {
    choco upgrade powershell-core -y
}

# Check for Python, download and install if necessary
if (-not (Test-Path $pythonPath)) {
    try {
        LogWrite "Python not detected. Attempting download..."
        Download-File "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" "C:\NexTool\python-3.11.6-amd64.exe"
        LogWrite "Installing Python..."
        Start-Process -FilePath "C:\NexTool\python-3.11.6-amd64.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\Python311" -Wait
    } catch {
        LogWrite "Error installing Python!"
        exit
    }
}

# Download NexTool.py using Aria2c, then PowerShell if Aria2c fails
try {
    LogWrite "Downloading NexTool.py..."
    Download-File "https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py" $NexToolPath
} catch {
    LogWrite "Error downloading NexTool.py"
    exit
}

# Launch NexTool.py if it exists
if (Test-Path $NexToolPath) {
    LogWrite "Launching NexTool.py"
    MinimizeWindow
    Start-Process -Wait -FilePath $pythonPath -ArgumentList $NexToolPath
    RestoreWindow
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
