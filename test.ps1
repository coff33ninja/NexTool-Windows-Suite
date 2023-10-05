$url = 'https://raw.githubusercontent.com/asheroto/winget-install/master/winget-install.ps1'
$downloadPath = 'C:\temp\winget-install.ps1'

# Make sure the directory exists
if (-not (Test-Path 'C:\temp\')) {
    New-Item -Path 'C:\temp\' -ItemType Directory
}

Invoke-WebRequest -Uri $url -OutFile $downloadPath
. $downloadPath


# Function to check Winget Compatibility
function IsWingetCompatible {
    $osInfo = Get-CimInstance Win32_OperatingSystem
    $major = $osInfo.Version.Split('.')[0]
    $build = $osInfo.BuildNumber

    # Check for Windows 10 with build 19041 or later
    if ($major -eq '10' -and $build -ge 19041) {
        return $true
    }
    # Check for Windows 11
    elseif ($major -eq '11') {
        return $true
    }
    return $false
}

# Auto-execute the alternative Winget installation method upon invocation
$url = 'https://raw.githubusercontent.com/asheroto/winget-install/master/winget-install.ps1'
$downloadPath = 'C:\temp\winget-install.ps1'

# Make sure the directory exists
if (-not (Test-Path 'C:\temp\')) {
    New-Item -Path 'C:\temp\' -ItemType Directory
}

Invoke-WebRequest -Uri $url -OutFile $downloadPath
. $downloadPath

# Function to detect Winget installation
function IsWingetInstalled {
    try {
        $wingetVersion = winget --version
        Write-Output "Winget version detected: $wingetVersion"
        return $true
    }
    catch {
        Write-Output 'Winget not detected.'
        return $false
    }
}

# Call functions based on compatibility and Winget detection
if (IsWingetCompatible) {
    if (-not (IsWingetInstalled)) {
        Get-Winget
    }
}
else {
    Write-Output 'Your Windows version is not compatible with winget. It is only available on newer versions of Windows 10 or 11.'
    Write-Output 'Consider updating to a newer version or use the Chocolatey package manager as an alternative.'
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
        $wingetVersion | Out-File 'C:\temp\winget-available.txt' -Force
        return $true
    }
    catch {
        # If error occurred, attempt writing to the file
        try {
            $wingetVersion | Out-File -Path 'C:\temp\winget-available.txt' -Force
        }
        catch {
            Write-Output "Error occurred: $_"
            Write-Output 'Winget is not detected, attempting installation...'
            "$_" | Out-File $errorLog -Append

        }
    }

    # User confirmation to install manually from the store
    $userChoice = Read-Host 'Would you like to install the winget package manager manually from the Microsoft Store? (Y/N)'
    if ($userChoice -eq 'Y') {
        Start-Process 'https://apps.microsoft.com/store/detail/app-installer/9NBLGGH4NNS1'
        Start-Process 'ms-windows-store://pdp/?PFN=Microsoft.DesktopAppInstaller_8wekyb3d8bbwe'

        Read-Host 'Press ENTER after you have attempted the manual installation of winget.'

        # Check winget version again
        try {
            $wingetVersion = winget --version
            Write-Output "Successfully detected Winget version: $wingetVersion"
        }
        catch {
            Write-Output "Still unable to detect winget. Please ensure it's installed and available in the system path."
            "$_" | Out-File $errorLog -Append
            exit
        }
    }

    # Download methods for winget
    $downloadMethods = @(
        { Invoke-WebRequest -Uri $wingetDownloadURL -OutFile $destination },
        { cmd /c wget $wingetDownloadURL -O $destination },
        { aria2c $wingetDownloadURL -d 'C:\PS' -o 'WinGet.msixbundle' },
        { cmd /c curl -L -o $destination $wingetDownloadURL },
        { pwsh -Command "Invoke-WebRequest -Uri '$wingetDownloadURL' -OutFile '$destination'" }
    )

    # Try downloading using available methods
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
        Add-AppxPackage $destination
        $wingetVersion = winget --version
        Write-Output "Successfully installed Winget version: $wingetVersion"
        return $true
    }
    else {
        Write-Output 'Failed to download winget using all methods.'
        return $false
    }
}

# Call functions based on compatibility
if (IsWingetCompatible) {
    Get-Winget
}
else {
    Write-Output 'Your Windows version is not compatible with winget. It is only available on newer versions of Windows 10 or 11.'
    Write-Output 'Consider updating to a newer version or use the Chocolatey package manager as an alternative.'
}
