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
    Write-Output 'Attempting to download NexTool.py from GitHub...'

    $downloaded = $false

    foreach ($url in $downloadURLs) {
        try {
            wget $url -O $destination  # <-- Changed $downloadURL to $url
            Write-Output 'Downloaded using wget.'
            $downloaded = $true
            break
        }
        catch {
            try {
                curl -L $url -o $destination  # <-- Changed $downloadURL to $url
                Write-Output 'Downloaded using curl.'
                $downloaded = $true
                break
            }
            catch {
                try {
                    aria2c $url -d 'C:\NexTool' -o 'NexTool.py'  # <-- Changed $downloadURL to $url
                    Write-Output 'Downloaded using aria2c.'
                    $downloaded = $true
                    break
                }
                catch {
                    try {
                        Invoke-WebRequest -Uri $url -OutFile $destination  # <-- Changed $downloadURL to $url
                        Write-Output "Downloaded using default PowerShell's Invoke-WebRequest."
                        $downloaded = $true
                        break
                    }
                    catch {
                        try {
                            pwsh -Command "Invoke-WebRequest -Uri '$url' -OutFile '$destination'"  # <-- Changed $downloadURL to $url
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
}
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
    $wgetVersion = wget --version | Select-Object -First 1
    Write-Output $wgetVersion
}
catch {
    Write-Output 'wget is not installed.'
}

# Check curl version
try {
    $curlVersion = curl --version | Select-Object -First 1
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
