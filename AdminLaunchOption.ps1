# Path for our flag/temporary file
$flagFilePath = 'C:\temp\script_ran.txt'
$exitFilePath = 'C:\temp\exit.txt'

if (-not (Test-Path $flagFilePath)) {
    # Set the execution policies
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process -Force

    # Create the flag file to indicate the script has been run once
    New-Item -Path $flagFilePath -ItemType File -Force

    # Restart the shell and rerun the script
    Start-Process powershell -ArgumentList '-File', $PSCommandPath -Wait

    # Check for the exit.txt after the restarted shell closes
    if (Test-Path $exitFilePath) {
        # Delete the exit.txt file
        Remove-Item -Path $exitFilePath -Force

        Clear-Host

        # Exit the current session after the restarted shell has been closed
        Write-Host 'INFORMATION:' -ForegroundColor Green -NoNewline
        Write-Host ' If the script does not close on its own you may close it manually' -ForegroundColor Yellow -BackgroundColor DarkBlue
        Start-Sleep -Seconds 5  # Pauses the script for 5 seconds
        exit
    }
}
Clear-Host

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {
    Write-Warning 'You need to run this script as an Administrator!'
    Start-Process powershell.exe -Verb RunAs -ArgumentList ("-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"")
    exit
}

# Retrieve current execution policies
$currentUserPolicy = Get-ExecutionPolicy -Scope CurrentUser
$localMachinePolicy = Get-ExecutionPolicy -Scope LocalMachine

# Adjust execution policies if necessary
if ($currentUserPolicy -ne 'RemoteSigned') {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

if ($localMachinePolicy -ne 'Unrestricted') {
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope LocalMachine -Force
}

# Initialization
$batchPath = $MyInvocation.MyCommand.Definition
$batchName = [System.IO.Path]::GetFileNameWithoutExtension($batchPath)

# Ensure directories exist and set permissions
$directories = @('C:\NexTool', 'C:\PS', 'C:\temp')
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
        icacls $dir /grant 'Everyone:F'
    }
}

# Check and Install Chocolatey if not present
try {
    $chocoVersion = choco --version
    Write-Output "Chocolatey version: $chocoVersion"
}
catch {
    Write-Output 'Chocolatey not detected, attempting installation...'
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    $env:Path += ";$env:ALLUSERSPROFILE\chocolatey\bin"

    # Re-check Chocolatey version after installation
    try {
        $chocoVersion = choco --version
        Write-Output "Chocolatey version after installation: $chocoVersion"
    }
    catch {
        Write-Output 'Failed to install Chocolatey. Exiting...'
        exit
    }
}

# Check and install/upgrade Aria2
try {
    $aria2Version = aria2c --version | Select-Object -First 1
    Write-Output $aria2Version
    choco upgrade aria2 -y
}
catch {
    Write-Output 'Aria2 not detected, installing...'
    choco install aria2 -y
}

# Check and install/upgrade Wget
try {
    $wgetVersion = cmd /c wget -h | Select-Object -First 1
    Write-Output $wgetVersion
    choco upgrade wget -y
}
catch {
    Write-Output 'Wget not detected, installing...'
    choco install wget -y
}

# Check and install/upgrade Curl
try {
    $wgetVersion = cmd /c curl -h | Select-Object -First 1
    Write-Output $curlVersion
    choco upgrade curl -y
}
catch {
    Write-Output 'Curl not detected, installing...'
    choco install curl -y
}

# Check and install/upgrade PowerShell Core
try {
    $pwshVersion = pwsh --version
    Write-Output "powershell-core version: $pwshVersion"
    choco upgrade powershell-core -y
}
catch {
    Write-Output 'powershell-core not detected, installing...'
    choco install powershell-core -y
}

# Check and install Python
try {
    $pythonVersion = python --version 2>&1
    Write-Output "$pythonVersion"
}
catch {
    Write-Output 'Python is not detected, attempting installation...'
    $winver = (Get-CimInstance Win32_OperatingSystem).Version.Split('.')[0]

    if ($winver -eq '10' -or $winver -eq '11') {
        winget install python --exact 2>&1 | Out-Null
    }
    else {
        Write-Output 'This system is not Windows 10 or 11. Using Chocolatey to install Python...'
        choco install python -y
    }
}

# Enviroment Temporary reset after Aria2, Curl, Wget, Powershell-Core and Python installations...
$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User')
# This will be changed if certain specific issues occure on diffrent windows versions that does not support this method

# Update pip and install Python packages
$pythonPackages = @('tk', 'ttkthemes', 'psutil', 'wmi', 'urllib3', 'pywin32', 'pypiwin32')
pip install --upgrade pip
foreach ($package in $pythonPackages) {
    pip install $package
}

# Check and install Winget
function Get-Winget {
    param (
        [string]$wingetDownloadURL = 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle',
        [string]$destination = 'C:\PS\WinGet.msixbundle'
    )

    try {
        $wingetVersion = winget --version
        Write-Output "Winget version: $wingetVersion"
        # Attempt to write the version to a text file without the `-Path` parameter
        $wingetVersion | Out-File 'C:\temp\winget-available.txt' -Force
        return $true
    }
    catch {
        # If an error occurred, attempt writing to the file using the `-Path` parameter
        try {
            $wingetVersion | Out-File -Path 'C:\temp\winget-available.txt' -Force
        }
        catch {
            # If both attempts fail, then output an error
            Write-Output "Error occurred: $_"
            Write-Output 'Winget is not detected, attempting installation...'
        }
    }
    # Check Windows version
    $winver = (Get-CimInstance Win32_OperatingSystem).Version.Split('.')[0]
    if ($winver -eq '10' -or $winver -eq '11') {
        $userChoice = Read-Host 'Would you like to install the winget package manager manually from the Microsoft Store? (Y/N)'
        if ($userChoice -eq 'Y') {
            Start-Process 'https://aka.ms/winget-install'
            Write-Output 'Please install winget from the Microsoft Store and then re-run this script.'
            exit
        }
    }

    $downloadMethods = @(
        { Invoke-WebRequest -Uri $wingetDownloadURL -OutFile $destination },
        { cmd /c wget $wingetDownloadURL -O $destination },
        { aria2c $wingetDownloadURL -d 'C:\PS' -o 'WinGet.msixbundle' },
        { cmd /c curl -L -o $destination $wingetDownloadURL },
        { pwsh -Command "Invoke-WebRequest -Uri '$wingetDownloadURL' -OutFile '$destination'" }
    )

    $downloaded = $false
    foreach ($method in $downloadMethods) {
        try {
            & $method
            $downloaded = $true
            break
        }
        catch {
            continue
        }
    }

    if ($downloaded) {
        try {
            Add-AppxPackage $destination
            $wingetVersion = winget --version
            Write-Output "Successfully installed Winget version: $wingetVersion"
            return $true
        }
        catch {
            Write-Output "Failed to install winget. Please try manually or ensure 'App Installer' is available from the Microsoft Store."
            Start-Process 'https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1'
            exit
        }
    }
    else {
        Write-Output 'Failed to download winget using all methods.'
        return $false
    }
}

# Call Winget Installation
Get-Winget

# Display specific installed Chocolatey packages
Clear-Host
Write-Output 'Listing Specific Installed Chocolatey Packages...'

# Check Chocolatey version
try {
    $chocoVersion = choco --version
    Write-Output "Chocolatey version: $chocoVersion"
}
catch {
    Write-Output 'Chocolatey is not installed.'
}

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Output "$pythonVersion"
}
catch {
    Write-Output 'Python is not installed.'
}

# Check wget version
try {
    $wgetVersion = cmd /c wget -h | Select-Object -First 1
    Write-Output $wgetVersion
}
catch {
    Write-Output 'wget is not installed.'
}

# Check curl version
try {
    $curlVersion = cmd /c curl --version | Select-Object -First 1
    Write-Output $curlVersion
}
catch {
    Write-Output 'curl is not installed.'
}

# Check aria2 version
try {
    $aria2Version = aria2c --version | Select-Object -First 1
    Write-Output $aria2Version
}
catch {
    Write-Output 'aria2 is not installed.'
}

# Check powershell-core version
try {
    $pwshVersion = pwsh --version
    Write-Output $pwshVersion
}
catch {
    Write-Output 'powershell-core is not installed.'
}

# Display winget version
try {
    $wingetVersion = winget --version
    Write-Output "Winget version: $wingetVersion"
}
catch {
    Write-Output 'Winget is not detected.'
}

# Attempt to download NexTool.py using multiple methods
function Get-NexTool {
    param (
        [string[]]$downloadURLs = @(
            'https://github.com/coff33ninja/NexTool-Windows-Suite/blob/23efbe6160e74b5c6b149493fbded3ef33ee53fb/NexTool.py',
            'https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/master/NexTool.py'
        ),
        [string]$destination = 'C:\NexTool\NexTool.py'
    )

    $downloadMethods = @(
        { cmd /c wget $args[0] -O $args[1] },
        { cmd /c curl -L -o $args[1] $args[0] },
        { aria2c $args[0] -d 'C:\NexTool' -o 'NexTool.py' },
        { Invoke-WebRequest -Uri $args[0] -OutFile $args[1] },
        { pwsh -Command "Invoke-WebRequest -Uri '$args[0]' -OutFile '$args[1]'" }
    )

    foreach ($url in $downloadURLs) {
        $downloaded = $false
        foreach ($method in $downloadMethods) {
            try {
                & $method $url $destination
                $downloaded = $true
                break
            }
            catch {
                continue
            }
        }

        if ($downloaded) {
            Write-Output "Successfully downloaded NexTool.py from $url"
            return $true
        }
    }

    Write-Output 'Failed to download NexTool.py from all URLs.'
    return $false
}


# Call NexTool Download
Get-NexTool

# Launch Python NexTool.py
& python "$PSScriptRoot\NexTool.py"

# Cleanup
Write-Output 'Clearing out C:\NexTool and C:\PS...'
Remove-Item 'C:\NexTool' -Recurse -Force
Remove-Item 'C:\PS' -Recurse -Force

# Now, reset the execution policies at the end of the script and cleanup
Set-ExecutionPolicy -ExecutionPolicy Default -Force
Set-ExecutionPolicy -ExecutionPolicy Default -Scope Process -Force
Remove-Item $flagFilePath
New-Item -Path $exitFilePath -ItemType File -Force

exit
