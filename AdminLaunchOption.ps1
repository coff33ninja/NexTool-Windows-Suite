$baseTranscriptLog = 'C:\temp\transcript_log'
$errorLog = 'C:\temp\error_log.txt'

if (Test-Path "${baseTranscriptLog}_2.txt") {
    Remove-Item "${baseTranscriptLog}_2.txt"
}

if (Test-Path "${baseTranscriptLog}_1.txt") {
    Rename-Item "${baseTranscriptLog}_1.txt" "${baseTranscriptLog}_2.txt"
}

if (Test-Path "${baseTranscriptLog}.txt") {
    Rename-Item "${baseTranscriptLog}.txt" "${baseTranscriptLog}_1.txt"
}

Start-Transcript -Path "${baseTranscriptLog}.txt"

# Path for our flag/temporary file
$flagFilePath = 'C:\temp\script_ran.txt'

if (-not (Test-Path $flagFilePath)) {
    Start-Transcript -Path "${baseTranscriptLog}.txt" -Append
    # Set the execution policies
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process -Force

    # Create the flag file to indicate the script has been run once
    New-Item -Path $flagFilePath -ItemType File -Force

    # Restart the shell and rerun the script
    Start-Process powershell -ArgumentList '-File', $PSCommandPath -Wait
    exit

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
# $batchPath = $MyInvocation.MyCommand.Definition
# $batchName = [System.IO.Path]::GetFileNameWithoutExtension($batchPath)

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
        "$_" | Out-File $errorLog -Append
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
    "$_" | Out-File $errorLog -Append
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
    "$_" | Out-File $errorLog -Append
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
    "$_" | Out-File $errorLog -Append
    choco install curl -y
}

# Check and install/upgrade PowerShell Core
try {
    $pwshVersion = pwsh --version
    Write-Output "powershell-core version: $pwshVersion"
    "$_" | Out-File $errorLog -Append
    choco upgrade powershell-core -y
}
catch {
    Write-Output 'powershell-core not detected, installing...'
    "$_" | Out-File $errorLog -Append
    choco install powershell-core -y
}

# Check and install Python 3.11
try {
    $python311Version = & 'C:\Python311\python.exe' --version 2>&1
    Write-Output "Python 3.11 version: $python311Version"
    "$python311Version" | Out-File $errorLog -Append
}
catch {
    Write-Output 'Python 3.11 not detected, installing...'
    "$_" | Out-File $errorLog -Append
    choco install python --version=3.11.0 -y
}

# Check and install Python 3.12
try {
    $python312Version = & 'C:\Python312\python.exe' --version 2>&1
    Write-Output "Python 3.12 version: $python312Version"
    "$python312Version" | Out-File $errorLog -Append
}
catch {
    Write-Output 'Python 3.12 not detected, installing...'
    "$_" | Out-File $errorLog -Append
    choco install python --version=3.12.0 -y
}

# Enviroment Temporary reset after Aria2, Curl, Wget, Powershell-Core and Python installations...
$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path', 'User')
# This will be changed if certain specific issues occure on diffrent windows versions that does not support this method

# Update pip and install Python packages
$pythonPackages = @('tk', 'ttkthemes', 'psutil', 'wmi', 'urllib3', 'pywin32', 'pypiwin32')
pip install --upgrade pip
foreach ($package in $pythonPackages) {
    pip install $package
    pip3 install $package
}

# Display specific installed Chocolatey packages
Clear-Host
Write-Output 'Listing Specific Installed Chocolatey Packages...'
function Get-ChocolateyInstalledPackage {
    # Check Chocolatey version
    try {
        $chocoVersion = choco --version
        Write-Output "Chocolatey version: $chocoVersion"
    }
    catch {
        Write-Output 'Chocolatey is not installed.'
        "$_" | Out-File $errorLog -Append

    }

    # Check Python 3.11 version
    try {
        $python311Version = & 'C:\Python311\python.exe' --version 2>&1
        Write-Output "Python 3.11: $python311Version"
    }
    catch {
        Write-Output 'Python 3.11 is not installed or not found at C:\Python311\.'
        "$_" | Out-File $errorLog -Append
    }

    # Check Python 3.12 version
    try {
        $python312Version = & 'C:\Python312\python.exe' --version 2>&1
        Write-Output "Python 3.12: $python312Version"
    }
    catch {
        Write-Output 'Python 3.12 is not installed or not found at C:\Python312\.'
        "$_" | Out-File $errorLog -Append
    }

    # Check wget version
    try {
        $wgetVersion = cmd /c wget -h | Select-Object -First 1
        Write-Output $wgetVersion
    }
    catch {
        Write-Output 'wget is not installed.'
        "$_" | Out-File $errorLog -Append
    }

    # Check curl version
    try {
        $curlVersion = cmd /c curl --version | Select-Object -First 1
        Write-Output $curlVersion
    }
    catch {
        Write-Output 'curl is not installed.'
        "$_" | Out-File $errorLog -Append
    }

    # Check aria2 version
    try {
        $aria2Version = aria2c --version | Select-Object -First 1
        Write-Output $aria2Version
    }
    catch {
        Write-Output 'aria2 is not installed.'
        "$_" | Out-File $errorLog -Append
    }

    # Check powershell-core version
    try {
        $pwshVersion = pwsh --version
        Write-Output $pwshVersion
    }
    catch {
        Write-Output 'powershell-core is not installed.'
        "$_" | Out-File $errorLog -Append
    }
}

function Test-If-WingetInstalled {
    try {
        $wingetVersion = winget --version
        Write-Output "Winget version detected: $wingetVersion"
        Set-Content -Path 'C:\temp\winget-installed.txt' -Value $wingetVersion
    }
    catch {
        Write-Output 'Winget not detected.'
        New-Item -Path 'C:\temp\winget-not-installed.txt' -ItemType File -Force
    }
}

# Call the function
Check-WingetInstalled

# Attempt to download NexTool.py using multiple methods
function Get-NexTool {
    param (
        [string[]]$downloadURLs = @(
            'https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/master/NexTool.py',
            'https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/main/NexTool.py',
            'https://github.com/coff33ninja/NexTool-Windows-Suite/blob/main/AdminLaunchOption.ps1'
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
if ($null -ne $python311Version) {
    & 'C:\Python311\python.exe' 'C:\NexTool\NexTool.py'
}
else {
    python 'C:\NexTool\NexTool.py'
}

# Cleanup
Write-Output 'Clearing out C:\NexTool and C:\PS...'
Remove-Item 'C:\NexTool' -Recurse -Force
Remove-Item 'C:\PS' -Recurse -Force

# Now, reset the execution policies at the end of the script and cleanup
Set-ExecutionPolicy -ExecutionPolicy Default -Force
Set-ExecutionPolicy -ExecutionPolicy Default -Scope Process -Force
Stop-Transcript
exit
