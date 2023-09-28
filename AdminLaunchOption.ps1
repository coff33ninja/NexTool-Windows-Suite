# Initialization
$batchPath = $MyInvocation.MyCommand.Definition
$batchName = [System.IO.Path]::GetFileNameWithoutExtension($batchPath)

# Ensure directories exist and set permissions
$directories = @('C:\NexTool', 'C:\PS')
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
        icacls $dir /grant 'Everyone:F'
    }
}

# Check Chocolatey
try {
    $chocoVersion = choco --version
    Write-Output "Chocolatey version: $chocoVersion"
}
catch {
    Write-Output 'Chocolatey not detected, attempting installation...'
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    $env:Path += ";$env:ALLUSERSPROFILE\chocolatey\bin"
}

# Check and install tools using Chocolatey
$tools = @('aria2', 'wget', 'curl', 'powershell-core')
foreach ($tool in $tools) {
    try {
        $version = & $tool --version
        Write-Output "$tool version: $version"
    }
    catch {
        Write-Output "$tool not detected, installing..."
        choco install $tool -y
    }
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

# Update pip and install Python packages
$pythonPackages = @('tk', 'ttkthemes', 'psutil', 'wmi', 'urllib3', 'pywin32', 'pypiwin32')
pip install --upgrade pip
foreach ($package in $pythonPackages) {
    pip install $package
}

# Check and install Winget
try {
    $wingetVersion = winget --version
    Write-Output "Winget version: $wingetVersion"
}
catch {
    Write-Output 'Winget is not detected, attempting multiple methods of installation...'

    # Method 1: Install using latest release link with PowerShell
    try {
        Invoke-WebRequest -Uri 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle' -OutFile 'C:\PS\WinGet.ps1.msixbundle'
        Add-AppxPackage 'C:\PS\WinGet.ps1.msixbundle'
    }
    catch {
        # Method 2: Using curl
        try {
            Invoke-WebRequest -L -o C:\PS\WinGet.curl.msixbundle 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'
            Add-AppxPackage 'C:\PS\WinGet.curl.msixbundle'
        }
        catch {
            # Method 3: Using aria2c
            try {
                aria2c 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle' -d C:\PS -o WinGet.aria2.msixbundle
                Add-AppxPackage 'C:\PS\WinGet.aria2.msixbundle'
            }
            catch {
                # Method 4: Using PowerShell Core
                pwsh -Command "Invoke-WebRequest -Uri 'https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle' -OutFile 'C:\PS\WinGet.pwsh1.msixbundle'"
                Add-AppxPackage 'C:\PS\WinGet.pwsh1.msixbundle'
            }
        }
    }

    # Cleanup .msixbundle files
    Remove-Item 'C:\PS\*.msixbundle' -Force
}

# Display installed Chocolatey packages
Clear-Host
Write-Output 'Listing Installed Chocolatey Packages...'
$chocoPackages = choco list --local-only
$chocoPackages | ForEach-Object { Write-Output $_ }
$wingetVersion = winget --version

# Attempt to download NexTool.py using multiple methods
$downloadURLs = @(
    'https://github.com/coff33ninja/NexTool-Windows-Suite/blob/23efbe6160e74b5c6b149493fbded3ef33ee53fb/NexTool.py',
    'https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/master/NexTool.py'
)

$destination = 'C:\NexTool\NexTool.py'

Write-Output 'Attempting to download NexTool.py from GitHub...'

$downloaded = $false

foreach ($url in $downloadURLs) {
    try {
        Invoke-WebRequest $url -O $destination  # Use $url not $downloadURLs
        Write-Output 'Downloaded using wget.'
        $downloaded = $true
        break
    }
    catch {
        try {
            Invoke-WebRequest -L $url -o $destination  # Use $url not $downloadURLs
            Write-Output 'Downloaded using curl.'
            $downloaded = $true
            break
        }
        catch {
            try {
                aria2c $url -d 'C:\NexTool' -o 'NexTool.py'  # Use $url not $downloadURLs
                Write-Output 'Downloaded using aria2c.'
                $downloaded = $true
                break
            }
            catch {
                try {
                    Invoke-WebRequest -Uri $url -OutFile $destination  # Use $url not $downloadURLs
                    Write-Output "Downloaded using default PowerShell's Invoke-WebRequest."
                    $downloaded = $true
                    break
                }
                catch {
                    try {
                        pwsh -Command "Invoke-WebRequest -Uri '$url' -OutFile '$destination'"  # Use $url not $downloadURLs
                        Write-Output "Downloaded using PowerShell Core's Invoke-WebRequest."
                        $downloaded = $true
                        break
                    }
                    catch {
                        continue
                    }
                }
            }
        }
    }
}

if (-not $downloaded) {
    Write-Output 'Failed to download NexTool.py from all URLs.'
    exit
}

# Launch Python NexTool.py
& python "$PSScriptRoot\NexTool.py"

# Cleanup
Write-Output 'Clearing out C:\NexTool and C:\PS...'
Remove-Item 'C:\NexTool' -Recurse -Force
Remove-Item 'C:\PS' -Recurse -Force
