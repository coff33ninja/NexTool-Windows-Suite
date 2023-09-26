# Ensure script is running as administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')
if (-not $IsAdmin) {
    # Relaunch script with admin rights
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Define directories
$NexToolDir = 'C:\NexTool'
$PSDir = 'C:\PS'

# Create directories if they don't exist and set permissions
if (-not (Test-Path $NexToolDir)) {
    New-Item -Path $NexToolDir -ItemType Directory | Out-Null
    Invoke-Command icacls $NexToolDir /grant 'Everyone:F'
}

if (-not (Test-Path $PSDir)) {
    New-Item -Path $PSDir -ItemType Directory | Out-Null
    Invoke-Command icacls $PSDir /grant 'Everyone:F'
}

# Ensure Chocolatey is installed or updated
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    $env:PATH += ";$env:ALLUSERSPROFILE\chocolatey\bin"
}

# Install or update necessary packages with Chocolatey
@('choco', 'aria2', 'wget', 'curl', 'powershell-core') | ForEach-Object {
    if (Get-Command $_ -ErrorAction SilentlyContinue) {
        choco upgrade $_ -y
    }
    else {
        choco install $_ -y
    }
}

# Check if winget is installed
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Output 'Winget is not detected, attempting installation...'
    $wingetURL = 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'
    $downloadPath = Join-Path $PSDir 'WinGet.ps1.msixbundle'

    # Use various methods to download
    try {
        Invoke-WebRequest -Uri $wingetURL -OutFile $downloadPath
    }
    catch {
        try {
            & pwsh -Command "Invoke-WebRequest -Uri '$wingetURL' -OutFile '$downloadPath'"
        }
        catch {
            try {
                & aria2c $wingetURL -d $PSDir -o 'WinGet.aria2.msixbundle'
            }
            catch {
                & Invoke-WebRequest -L -o (Join-Path $PSDir 'WinGet.curl.msixbundle') $wingetURL
            }
        }
    }

    # Attempt to install
    Get-ChildItem "$PSDir\WinGet.*.msixbundle" | ForEach-Object {
        Add-AppxPackage $_.FullName
    }

    # Cleanup
    Remove-Item "$PSDir\*.msixbundle" -Force

    # Verify installation
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Output "Please manually install 'App Installer' from the Microsoft Store."
        Start-Process 'https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1'
        exit
    }
}

# Print versions of installed software
Write-Output ('Winget version: ' + (winget --version))
Write-Output ('Chocolatey version: ' + (choco --version))
Write-Output ('Aria2 version: ' + (aria2c --version | Select-String 'aria2 version'))
Write-Output ('Wget version: ' + (Invoke-WebRequest --version | Select-String 'GNU Wget'))
Write-Output ('Curl version: ' + (Invoke-WebRequest --version | Select-String 'curl'))

Write-Output 'Packagemanagers are up to date!'
Pause

# Execute Python script
& python "$PSScriptRoot\NexTool.py"

# Cleanup directories
Remove-Item $NexToolDir -Recurse -Force
Remove-Item $PSDir -Recurse -Force

Pause
