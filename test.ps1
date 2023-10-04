$url = 'https://raw.githubusercontent.com/asheroto/winget-install/master/winget-install.ps1'
$downloadPath = 'C:\temp\winget-install.ps1'

# Make sure the directory exists
if (-not (Test-Path 'C:\temp\')) {
    New-Item -Path 'C:\temp\' -ItemType Directory
}

Invoke-WebRequest -Uri $url -OutFile $downloadPath
. $downloadPath
