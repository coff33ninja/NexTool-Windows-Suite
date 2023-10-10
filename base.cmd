:BACKUP_CONFIG
color 0f
mode con cols=98 lines=32
title  BACKUP NETWORK CONFIGURATION
cls

echo:
echo:
echo                  ^|===============================================================^|
echo                  ^|                                                               ^|
echo                  ^|                                                               ^|
echo                  ^|      [1] BACKUP WIFI CONFIGURATION                            ^|
echo                  ^|                                                               ^|
echo                  ^|      [2] RESTORE WIFI CONFIGURATION                           ^|
echo                  ^|                                                               ^|
echo                  ^|                                                               ^|
echo                  ^|      [3] NETWORK INTERFACES CONFIGURATION BACKUP              ^|
echo                  ^|                                                               ^|
echo                  ^|      [4] NETWORK INTERFACES CONFIGURATION RESTORE             ^|
echo                  ^|                                                               ^|
echo                  ^|                                                               ^|
echo                  ^|      [5] BACKUP DRIVERS                                       ^|
echo                  ^|                                                               ^|
echo                  ^|      [6] RESTORE DRIVERS                                      ^|
echo                  ^|                                                               ^|
echo                  ^|      [7] USER DATA BACKUP                                     ^|
echo                  ^|                                                               ^|
echo                  ^|                                                 [8] Go back   ^|
echo                  ^|                                                               ^|
echo                  ^|===============================================================^|
echo:
choice /C:12345678 /N /M ">                   Enter Your Choice in the Keyboard [1,2,3,4,5,6,7,8] : "

if errorlevel  8 goto:end_COMPUTER_CONFIGURATION
if errorlevel  7 goto:USER_DATA
if errorlevel  6 goto:RESTORE_DRIVERS
if errorlevel  5 goto:BACHUP_DRIVERS
if errorlevel  4 goto:RESTORE_IP
if errorlevel  3 goto:Backup_IP
if errorlevel  2 goto:RESTORE_WIFI
if errorlevel  1 goto:BACKUP_WIFI
cls

::========================================================================================================================================

:BACKUP_WIFI
color 0f
Title WIFI BACKUP
mode con cols=98 lines=32
cls
echo
md C:\AIO_BACKUP\NETWORK\WIFI
cd C:\AIO_BACKUP\NETWORK\WIFI
echo This will backup the WiFi config to C:\AIO_BACKUP\NETWORK\WIFI
netsh wlan export profile key=clear folder=C:\AIO_BACKUP\NETWORK\WIFI
start .
pause & goto end_COMPUTER_CONFIGURATION

::========================================================================================================================================

:RESTORE_WIFI
color 0f
Title WIFI RESTORE
mode con cols=98 lines=32
cls
echo
cd C:\AIO_BACKUP\NETWORK\WIFI
dir
netsh wlan add profile filename="C:\AIO_BACKUP\NETWORK\WIFI\%WIFINAME%.xml" user=all
echo Enter complete file name excluding .xml
echo exapmle: WIFI-TSUNAMI
echo the .xml will be added automatically
Set /P %WIFINAME%=ENTER PEVIEWED WIFI NAME TO ADD WIFI BACK:
pause & goto end_COMPUTER_CONFIGURATION

::========================================================================================================================================

:Backup_IP
color 0f
Title NETWORK INTERFACES CONFIGURATION BACKUP
mode con cols=98 lines=32
cls
echo
md C:\AIO_BACKUP\NETWORK\Interfaces
cd C:\AIO_BACKUP\NETWORK\Interfaces
echo This section will backupp all the network interfaces confiuration to C:\AIO_BACKUP\NETWORK\Interfaces
netsh interface dump > C:\AIO_BACKUP\NETWORK\Interfaces\netcfg.txt
start .
pause & goto end_COMPUTER_CONFIGURATION

::========================================================================================================================================

:RESTORE_IP
color 0f
Title NETWORK INTERFACES CONFIGURATION RESTORE
mode con cols=98 lines=32
cls
echo
cd C:\AIO_BACKUP\NETWORK\Interfaces
dir
echo This section will restore all the network interfaces confiuration from C:\AIO_BACKUP\NETWORK\Interfaces
netsh exec C:\AIO_BACKUP\NETWORK\Interfaces\netcfg.txt
start .
pause & goto end_COMPUTER_CONFIGURATION

::========================================================================================================================================

:BACHUP_DRIVERS
color 0f
Title DRIVERS BACKUP
mode con cols=98 lines=32
cls
echo
md C:\AIO_BACKUP\DRIVERS_EXPORT
cd C:\AIO_BACKUP\DRIVERS_EXPORT
powershell.exe Dism /Online /Export-Driver /Destination:C:\AIO_BACKUP\DRIVERS_EXPORT
echo.The operation completed successfully.
pause & goto end_COMPUTER_CONFIGURATION

::========================================================================================================================================

:RESTORE_DRIVERS
color 0f
Title DRIVERS RESTORE
mode con cols=98 lines=32
cls
echo
cd C:\AIO_BACKUP\DRIVERS_EXPORT
dir
powershell.exe Dism /Online /Add-Driver /Driver:C:\AIO_BACKUP\DRIVERS_EXPORT
echo.The operation completed successfully.
pause & goto end_COMPUTER_CONFIGURATION

::========================================================================================================================================

:USER_DATA
color 0f
Title USER DATA BACKUP AND RESTORE
mode con cols=98 lines=32
cls
echo
echo This section is still a work in progress, STAY TUNED!
@echo off
Powershell -ExecutionPolicy Bypass Set-MpPreference -DisableRealtimeMonitoring 1
powershell Invoke-WebRequest "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/6.EXTRAS/User_profile_Backup_and_Restore.ps1" -O "%USERPROFILE%\AppData\Local\Temp\AIO\User_profile_Backup_and_Restore.ps1"
Powershell -ExecutionPolicy Bypass -File "%USERPROFILE%\AppData\Local\Temp\AIO\User_profile_Backup_and_Restore.ps1"  -verb runas
echo.The operation completed successfully.
pause & goto end_COMPUTER_CONFIGURATION
::========================================================================================================================================

::========================================================================================================================================


::========================================================================================================================================

::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================

:CLEANER
cls
color 0f
mode con cols=98 lines=40
TITLE PC Cleanup Utility
ECHO                THIS OPTION WILL GIVE OPTIONS TO CLEAN UP TEMPORARY ITEMS FROM WINDOWS
echo                     ASWELL AS DEBLOAT A FEW OF WINDOWS PREINSTALLED APPLICATIONS
ECHO                        THERE ARE 2 OTHER REPAIR TOOLS AS A LAST RESORT REPAIR.
ECHO                                    PLEASE READ BEFORE PROCEEDING
echo                  ^|===============================================================^|
echo                  ^|                                                               ^|
echo                  ^|                                                               ^|
echo                  ^|      [1] Disk Cleanup                                         ^|
echo                  ^|                                                               ^|
echo                  ^|      [2] Disk Defragment                                      ^|
echo                  ^|                                                               ^|
echo                  ^|      [3] DISK CHECK                                           ^|
echo                  ^|                                                               ^|
echo                  ^|      [4] DISM AND SFC WINDOWS REPAIR                          ^|
echo                  ^|                                                               ^|
echo                  ^|      [5] Windows Debloater                                    ^|
echo                  ^|                                                               ^|
echo                  ^|      [6] Group Policy Reset - USE AT OWN RISK                 ^|
echo                  ^|                                                               ^|
echo                  ^|      [7] WMI RESET - USE AT OWN RISK                          ^|
echo                  ^|                                                               ^|
echo                  ^|      ___________________________________________________      ^|
echo                  ^|                                                               ^|
echo                  ^|                          [8] GO BACK            [9] EXIT      ^|
echo                  ^|                                                               ^|
echo                  ^|===============================================================^|
echo:
choice /C:123456789 /N /M ">                   Enter Your Choice in the Keyboard [1,2,3,4,5,6,7,8,9] : "
CLS
if errorlevel 9 goto :EXIT
if errorlevel 8 goto :end_BACKMENU
if errorlevel 7 goto :WMI_RESET_AGREEMENT
if errorlevel 6 goto :GROUP_POLICY_RESET_AGREEMENT
if errorlevel 5 goto :Windows_Debloater
if errorlevel 4 goto :DISM_and_SFC
if errorlevel 3 goto :DISK_CHECK
if errorlevel 2 goto :Disk_Defragment
if errorlevel 1 goto :Disk_Cleanup
goto error

:Disk_Cleanup
cls
echo.
title DISK CLEANUP
echo.
del /f /q "%userprofile%\Cookies\*.*"
del /f /q "%userprofile%\AppData\Local\Microsoft\Windows\Temporary Internet Files\*.*"
del /f /q "%userprofile%\AppData\Local\Temp\*.*"
del /s /f /q "c:\windows\temp\*.*"
rd /s /q "c:\windows\temp"
md "c:\windows\temp"
del /s /f /q "C:\WINDOWS\Prefetch"
del /s /f /q "%temp%\*.*"
rd /s /q "%temp%"
md %temp%
deltree /y "c:\windows\tempor~1"
deltree /y "c:\windows\temp"
deltree /y "c:\windows\tmp"
deltree /y "c:\windows\ff*.tmp"
deltree /y "c:\windows\history"
deltree /y "c:\windows\cookies"
deltree /y "c:\windows\recent"
deltree /y "c:\windows\spool\printers"
del c:\WIN386.SWP
del /f /s /q "%systemdrive%\*.tmp"
del /f /s /q "%systemdrive%\*._mp"
del /f /s /q "%systemdrive%\*.log"
del /f /s /q "%systemdrive%\*.gid"
del /f /s /q "%systemdrive%\*.chk"
del /f /s /q "%systemdrive%\*.old"
del /f /s /q "%systemdrive%\recycled\*.*"
del /f /s /q "%windir%\*.bak"
del /f /s /q "%windir%\prefetch\*.*"
rd /s /q "%windir%\temp & md %windir%\temp"
del /f /q "%userprofile%\cookies\*.*"
del /f /q "%userprofile%\recent\*.*"
del /f /s /q "%userprofile%\Local Settings\Temporary Internet Files\*.*"
del /f /s /q "userprofile%\Local Settings\Temp\*.*"
del /f /s /q "%userprofile%\recent\*.*"
if exist "C:\WINDOWS\temp"del /f /q "C:WINDOWS\temp\*.*"
if exist "C:\WINDOWS\tmp" del /f /q "C:\WINDOWS\tmp\*.*"
if exist "C:\tmp" del /f /q "C:\tmp\*.*"
if exist "C:\temp" del /f /q "C:\temp\*.*"
if exist "%temp%" del /f /q "%temp%\*.*"
if exist "%tmp%" del /f /q "%tmp%\*.*"
if exist "C:\WINDOWS\Users\*.zip" del "C:\WINDOWS\Users\*.zip" /f /q
if exist "C:\WINDOWS\Users\*.exe" del "C:\WINDOWS\Users\*.exe" /f /q
if exist "C:\WINDOWS\Users\*.gif" del "C:\WINDOWS\Users\*.gif" /f /q
if exist "C:\WINDOWS\Users\*.jpg" del "C:\WINDOWS\Users\*.jpg" /f /q
if exist "C:\WINDOWS\Users\*.png" del "C:\WINDOWS\Users\*.png" /f /q
if exist "C:\WINDOWS\Users\*.bmp" del "C:\WINDOWS\Users\*.bmp" /f /q
if exist "C:\WINDOWS\Users\*.avi" del "C:\WINDOWS\Users\*.avi" /f /q
if exist "C:\WINDOWS\Users\*.mpg" del "C:\WINDOWS\Users\*.mpg" /f /q
if exist "C:\WINDOWS\Users\*.mpeg" del "C:\WINDOWS\Users\*.mpeg" /f /q
if exist "C:\WINDOWS\Users\*.ra" del "C:\WINDOWS\Users\*.ra" /f /q
if exist "C:\WINDOWS\Users\*.ram" del "C:\WINDOWS\Users\*.ram"/f /q
if exist "C:\WINDOWS\Users\*.mp3" del "C:\WINDOWS\Users\*.mp3" /f /q
if exist "C:\WINDOWS\Users\*.mov" del "C:\WINDOWS\Users\*.mov" /f /q
if exist "C:\WINDOWS\Users\*.qt" del "C:\WINDOWS\Users\*.qt" /f /q
if exist "C:\WINDOWS\Users\*.asf" del "C:\WINDOWS\Users\*.asf" /f /q
if exist "C:\WINDOWS\Users\AppData\Temp\*.zip" del "C:\WINDOWS\Users\Users\*.zip /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.exe" del "C:\WINDOWS\Users\Users\*.exe /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.gif" del "C:\WINDOWS\Users\Users\*.gif /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.jpg" del "C:\WINDOWS\Users\Users\*.jpg /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.png" del "C:\WINDOWS\Users\Users\*.png /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.bmp" del "C:\WINDOWS\Users\Users\*.bmp /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.avi" del "C:\WINDOWS\Users\Users\*.avi /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.mpg" del "C:\WINDOWS\Users\Users\*.mpg /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.mpeg" del "C:\WINDOWS\Users\Users\*.mpeg /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.ra" del "C:\WINDOWS\Users\Users\*.ra /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.ram" del "C:\WINDOWS\Users\Users\*.ram /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.mp3" del "C:\WINDOWS\Users\Users\*.mp3 /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.asf" del "C:\WINDOWS\Users\Users\*.asf /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.qt" del "C:\WINDOWS\Users\Users\*.qt /f /q"
if exist "C:\WINDOWS\Users\AppData\Temp\*.mov" del "C:\WINDOWS\Users\Users\*.mov /f /q"
if exist "C:\WINDOWS\ff*.tmp" del "C:\WINDOWS\ff*.tmp /f /q"
if exist "C:\WINDOWS\ShellIconCache" del /f /q "C:\WINDOWS\ShellI~1\*.*"
DEL /S /Q "%TMP%\*.*"
DEL /S /Q "%TEMP%\*.*"
DEL /S /Q "%WINDIR%\Temp\*.*"
DEL /S /Q "%USERPROFILE%\Local Settings\Temp\*.*"
DEL /S /Q "%USERPROFILE%\Appdata\Local\BraveSoftware\Brave-Browser\User Data\Default\Cache"
DEL /S /Q "%LocalAppData%\Temp"

DEL /S /Q "C:\Program Files (x86)\Google\Temp"
DEL /S /Q "C:\Program Files (x86)\Steam\steamapps\temp"
DEL /S /Q "U:\Games\steamapps\temp"
DEL /S /Q "C:\ProgramData\Microsoft\Windows\WER\Temp"
DEL /S /Q "C:\Users\All Users\Microsoft\Windows\WER\Temp"
DEL /S /Q "C:\Windows\Temp"
DEL /S /Q "C:\Windows\System32\DriverStore\Temp"
DEL /S /Q "C:\Windows\WinSxS\Temp"

cleanmgr /VERYLOWDISK /sagerun:0
ipconfig /flushdns
echo.
cls
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Disk Cleanup successfully. Press OK to continue.', 'COMPLETE', 'OK', [System.Windows.Forms.MessageBoxIcon]::Information);}"
echo.
cls & goto end_CLEANER

:Disk_Defragment
cls
color 0f
mode con cols=98 lines=32
cls
echo --------------------------------------------------------------------------------
echo Disk Defragment
echo --------------------------------------------------------------------------------
echo.
echo Defragmenting hard disks...
ping localhost -n 3 >nul
defrag -c -v
cls
echo --------------------------------------------------------------------------------
echo Disk Defragment
echo --------------------------------------------------------------------------------
echo.
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Disk defrag completed successfully. Press OK to continue.', 'COMPLETE', 'OK', [System.Windows.Forms.MessageBoxIcon]::Information);}"
echo.
pause & goto end_CLEANER

:DISK_CHECK
color 0f
mode con cols=98 lines=32
TITLE DISK CHECK
Set /P %DLETTER%=ENTER DRIVE LETTER THAT NEEDS ATTENTION:
CHKDSK %DLETTER%: /R /I /F /X
pause & goto end_CLEANER

:DISM_and_SFC
color 0f
mode con cols=98 lines=32
TITLE DISM
cls
echo ------------------------------------------------
echo Windows component files check - procedure 1 of 3
echo ------------------------------------------------
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase
echo --------------------------------------------------
echo Phase 1 of 2 completed
echo --------------------------------------------------
Dism.exe /online /Cleanup-Image /SPSuperseded
echo --------------------------------------------------
echo Phase 2 of 2 completed
echo PRESS ANY KEY TO CONTINUE.
pause >null
del null
cls
echo --------------------------------------------------------------
echo Checking the integrity of the Windows image - procedure 2 of 3
echo --------------------------------------------------------------
DISM /Online /Cleanup-Image /CheckHealth
echo --------------------------------------------------
echo Phase 1 of 3 completed
echo --------------------------------------------------
DISM /Online /Cleanup-Image /ScanHealth
echo --------------------------------------------------
echo Phase 2 of 3 completed
echo --------------------------------------------------
DISM /Online /Cleanup-Image /RestoreHealth
echo --------------------------------------------------
echo Phase 3 of 3 completed
echo PRESS ANY KEY TO CONTINUE.
pause >null
del null
cls
echo -------------------------------------------------
echo Running System file check - procedure 3 of 3
echo -------------------------------------------------
sfc /scannow
echo --------------------------------------------------------------------------------
echo If SFC found some errors and could not repair, re-run the script after a reboot.
echo --------------------------------------------------------------------------------
del null
pause & cls & goto end_CLEANER

:Windows_Debloater
color 0f
mode con cols=98 lines=32
TITLE DEBLOATER
ECHO THIS OPTION WILL DEBLOAT WINDOWS 10 + 11
timeout 2 >nul
powershell Invoke-WebRequest "https://github.com/coff33ninja/AIO/blob/92e827cb6a57ef688d1f87f0635aa91a337e7a68/TOOLS/4.CLEANER_REPAIR/DEBLOATER.ps1" -O "%USERPROFILE%\AppData\Local\Temp\AIO\Debloater.ps1"
Powershell -ExecutionPolicy Bypass -File "%USERPROFILE%\AppData\Local\Temp\AIO\Debloater.ps1"  -verb runas
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('This device has been successfully debloated. Press OK to continue.', 'COMPLETE', 'OK', [System.Windows.Forms.MessageBoxIcon]::Information);}"
cls & goto end_CLEANER

:GROUP_POLICY_RESET_AGREEMENT
cls
color 0f
mode con cols=98 lines=32
TITLE GROUP POLICY RESET
echo GROUP POLICY AGREEMENT
timeout 2 >nul
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('The Group Policy Editor is an important tool for Windows OS using which System Administrators can fine-tune system settings. It has several infrastructural configuration options that allow you to make adjustments to the specific performance and security settings for users and computers. Sometimes you might end up tweaking your Group Policy Editor a bit further down the line here your computer starts behaving in an unwanted way. This is when you know that its time to reset all Group Policy settings to default and save yourself the pain of reinstalling Windows again. This section is Pre-Setup so that you wont have to look through forums to find a solution. Please reboot once the cleanup is complete. Press YES if you understand. Press NO to go back to the previous section.', 'GROUP POLICY RESET AGREEMENT', 'YesNo', [System.Windows.Forms.MessageBoxIcon]::Warning);}" > %TEMP%\out.tmp
set /p OUT=<%TEMP%\out.tmp
if %OUT%==Yes cls & GOTO GROUP_POLICY_RESET
if %OUT%==No cls & goto CLEANER

:GROUP_POLICY_RESET
cls
color 0f
mode con cols=98 lines=32
TITLE GROUP POLICY RESET
ECHO The Group Policy Editor is an important tool for Windows OS using which
ECHO System Administrators can fine-tune system settings.
ECHO It has several infrastructural configuration options that allow you to make
ECHO adjustments to the specific performance and security settings for users and computers.
ECHO Sometimes you might end up tweaking your Group Policy Editor a bit further down the
ECHO line where your computer starts behaving in an unwanted way. This is when you
ECHO know that its time to reset all Group Policy settings to default
ECHO and save yourself the pain of reinstalling Windows again. This section is Pre-Setup
ECHO so that you won't have to look through forums to find a solution.
ECHO Please reboot once the cleanup is complete.
ECHO.
RD /S /Q "%WinDir%\System32\GroupPolicyUsers"
RD /S /Q "%WinDir%\System32\GroupPolicy"
gpupdate /force
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies" /f
reg delete "HKCU\Software\Microsoft\WindowsSelfHost" /f
reg delete "HKCU\Software\Policies" /f
reg delete "HKLM\Software\Microsoft\Policies" /f
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies" /f
reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\WindowsStore\WindowsUpdate" /f
reg delete "HKLM\Software\Microsoft\WindowsSelfHost" /f
reg delete "HKLM\Software\Policies" /f
reg delete "HKLM\Software\WOW6432Node\Microsoft\Policies" /f
reg delete "HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Policies" /f
reg delete "HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\WindowsStore\WindowsUpdate" /f
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('GroupPolicy has been successfully reset. Press OK to continue.', 'COMPLETE', 'OK', [System.Windows.Forms.MessageBoxIcon]::Information);}"
cls & goto end_CLEANER

:WMI_RESET_AGREEMENT
cls
color 0f
mode con cols=98 lines=32
TITLE WINDOWS MANAGEMENT INSTRUMENTATION RESET
echo WINDOWS MANAGEMENT INSTRUMENTATION RESET AGREEMENT
timeout 2 >nul
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Full WMI reset to the state when the operating system was installed is a serious measurement that should be well thought about, if needed at all. After the reset, you will need to reinstall any software that uses WMI repository. If, for example, your Server is System Center Configuration Manager Distribution Point or Pull Distribution Point, then you should not have any problem resetting though you will need to reinstall SCCM Client. However, keep in mind that if there are other uses for the server, you might need to check it afterwards. If youre in a case, when you need to reset WMI and it fixed your system to the state when you can boot â?? backup your content and better reinstall. It should not be an escape solution. Press YES if you understand. Press NO to go back to the previous section.', 'WINDOWS MANAGEMENT INSTRUMENTATION RESET AGREEMENT', 'YesNo', [System.Windows.Forms.MessageBoxIcon]::Warning);}" > %TEMP%\out.tmp
set /p OUT=<%TEMP%\out.tmp
if %OUT%==Yes cls & GOTO WMI_RESET
if %OUT%==No cls & goto CLEANER

:WMI_RESET
cls
color 0f
mode con cols=98 lines=32
TITLE WINDOWS MANAGEMENT INSTRUMENTATION RESET
ECHO Full WMI reset (to the state when the operating system was installed)
ECHO is a serious measurement that should be well thought about, if needed
ECHO at all. After the reset, you will need to reinstall any software that
ECHO uses WMI repository. If, for example, your Server is System Center
ECHO Configuration Manager Distribution Point or Pull Distribution Point,
ECHO then you should not have any problem resetting (though you will need
ECHO to reinstall SCCM Client). However, keep in mind that if there are
ECHO other uses for the server, you might need to check it afterwards.
ECHO If youâ??re in a case, when you need to reset WMI and it fixed your
ECHO system to the state when you can boot â?? backup your content and better
ECHO reinstall. It should not be an escape solution.
PAUSE
ECHO FULL WMI REPOSITORY RESET
echo:
ECHO To merge current WMI repository with factory defaults
winmgmt /salvagerepository
PAUSE
rem need if command here

ECHO If this still doesnâ??t help, make full reset of the WMI respository:
winmgmt /resetrepository
PAUSE
rem need if command here

:-----------------------------------------------------------------------------

ECHO If previous attempt failed, then we must make use of an older method:
REM Turn winmgmt service Startup type to Disabled
sc config winmgmt start = disabled
REM Stop winmgmt service
net stop winmgmt /y

REM Register / Reregister Service DLLs
regsvr32 /s %systemroot%\system32\scecli.dll
regsvr32 /s %systemroot%\system32\userenv.dll

REM Enter WBEM folder
cd /d %systemroot%\system32\wbem
REM Remove â??repositoryâ?? folder
rd /S /Q repository
REM Register / Reregister Service DLLs
for /f %%s in ('dir /b /s *.dll') do regsvr32 /s %%s
for /f %%s in ('dir /b /s *.exe') do regsvr32 /s %%s
for /f %%s in ('dir /b *.mof') do mofcomp %%s
for /f %%s in ('dir /b *.mfl') do mofcomp %%s

REM Register / Reregister wmiprvse Service
wmiprvse /regserver
REM Register / Reregister winmgmt Service
winmgmt /regserver

REM Enter WBEM folder in SysWOW64
cd /d %systemroot%\SysWOW64\wbem\
REM Remove â??repositoryâ?? folder
rd /S /Q repository
REM Register / Reregister Service DLLs
for /f %%s in ('dir /b /s *.dll') do regsvr32 /s %%s
for /f %%s in ('dir /b /s *.exe') do regsvr32 /s %%s
for /f %%s in ('dir /b *.mof') do mofcomp %%s
for /f %%s in ('dir /b *.mfl') do mofcomp %%s

REM Turn winmgmt service Startup type to Automatic
sc config winmgmt start = auto
REM Stop winmgmt service
net start winmgmt

echo After you run it, there might be â??Manageabilityâ?? errors
echo on Servers (maybe even clients), so you need to run again:
winmgmt /resetrepository
powershell -Command "& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Windows Management interface has been successfully reset. Press OK to continue.', 'COMPLETE', 'OK', [System.Windows.Forms.MessageBoxIcon]::Information);}"
cls & goto end_CLEANER
::========================================================================================================================================
::========================================================================================================================================

:WIN_INSTALL
cls
color 0f
mode con cols=98 lines=32
Title AIO PRE-SETUP
ECHO STILL BLANK
PAUSE GOTO end_BACKMENU

::========================================================================================================================================
::========================================================================================================================================

:EXTRAS
cls
color 0f
mode con cols=98 lines=32
Title EXTRA ITEMS
ECHO STILL BLANK
PAUSE GOTO end_BACKMENU

::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================
::========================================================================================================================================

::========================================================================================================================================

REM THIS SECTION RESERVED FOR PROGRESS BAR ANIMATION

::========================================================================================================================================

:end_WIN_INSTALL
cls & goto end_BACKMENU

::========================================================================================================================================
::========================================================================================================================================

:end_CLEANER
cls & goto CLEANER

::========================================================================================================================================
::========================================================================================================================================

:end_UPDATER
cls & goto UPDATER

::========================================================================================================================================
::========================================================================================================================================

:end_BACKMENU
cls & goto MainMenu

::========================================================================================================================================
::========================================================================================================================================

:end_NETWORK_CONFIGURATION
cls & goto NETWORK_CONFIGURATION

::========================================================================================================================================
::========================================================================================================================================

:end_COMPUTER_CONFIGURATION
cls & goto COMPUTER_CONFIGURATION

::========================================================================================================================================
::========================================================================================================================================

:EXIT
cls & exit
::========================================================================================================================================
::========================================================================================================================================



::========================================================================================================================================
::========================================================================================================================================
REM THIS SECTION RESERVED FOR A FEW INTRESTING ITEMS
::========================================================================================================================================
:EASTER
cls
mode con cols=41 lines=24
echo [41m                                         [0m
echo [41m                                         [0m
echo [41m                                         [0m
echo [41m     [0m                               [41m     [0m
echo [41m     [0m  ###########################  [41m     [0m
echo [41m     [0m  ###########################  [41m     [0m
echo [41m     [0m  ##########   ##   #########  [41m     [0m
echo [41m     [0m  #########    #    #########  [41m     [0m
echo [41m     [0m  ##########  ###   #########  [41m     [0m
echo [41m     [0m  ########### #### ##########  [41m     [0m
echo [41m     [0m  #########    #    #########  [41m     [0m
echo [41m     [0m  ##########   ##   #########  [41m     [0m
echo [41m     [0m  ###########################  [41m     [0m
echo [41m     [0m  ######   ##    #  ##  #####  [41m     [0m
echo [41m     [0m          #  #   # #  #        [41m     [0m
echo [41m     [0m         ######  # #  #        [41m     [0m
echo [41m     [0m        ##    ## #  ##         [41m     [0m
echo [41m                    [0m  [41m                   [0m
echo [41m                  [0m      [41m                 [0m
echo [41m              [0m              [41m             [0m
echo [41m                                         [0m
echo [41m                                         [0m
echo [41m                                         [0m
pause & cls & goto MainMenu
::========================================================================================================================================




























































::========================================================================================================================================
::========================================================================================================================================
REM THIS SECTION DOES NOT NEED ANY EDITING
::========================================================================================================================================
::========================================================================================================================================

:SHUTDOWN_OPTIONS
title Shutdown Script
mode con cols=98 lines=32
set seconds=1

:start
cls
echo.
echo.
echo.
echo                    Select a number:
echo                  ^|===============================================================^|
echo                  ^|                                                               ^|
echo                  ^|                                                               ^|
echo                  ^|      [1] Restart (Default Setting)                            ^|
echo                  ^|                                                               ^|
echo                  ^|      [2] Restart Reregister Applications                      ^|
echo                  ^|                                                               ^|
echo                  ^|      [3] Restart UEFI/BIOS                                    ^|
echo                  ^|                                                               ^|
echo                  ^|      [4] Restart Advanced Boot Options                        ^|
echo                  ^|      ___________________________________________________      ^|
echo                  ^|                                                               ^|
echo                  ^|      [5] Shutdown (Default Setting)                           ^|
echo                  ^|                                                               ^|
echo                  ^|      [6] Shutdown Reregister Applications                     ^|
echo                  ^|      ___________________________________________________      ^|
echo                  ^|                                                               ^|
echo                  ^|      [7] Sign Out User                                        ^|
echo                  ^|      ___________________________________________________      ^|
echo                  ^|                                                               ^|
echo                  ^|                                              [8] GO BACK      ^|
echo                  ^|                                                               ^|
echo                  ^|===============================================================^|
echo.
choice /c 12345678 /m "Enter your choice:"
if errorlevel 8 goto :end_BACKMENU
if errorlevel 7 (
cls
echo.
echo Sign out
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /l
goto error
)

if errorlevel 6 (
cls
echo.
echo Shutdown PC and Re-register any applications on next boot
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /sg /t %seconds%
goto error
)

if errorlevel 5 (
cls
echo.
echo Shutdown PC ^(Default Setting^)
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /s /t %seconds%
goto error
)

if errorlevel 4 (
cls
echo.
echo Restart PC and load the advanced boot options menu
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /r /o /t %seconds%
goto error
)

if errorlevel 3 (
cls
echo.
echo Restart PC to UEFI/BIOS menu
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /r /fw /t %seconds%
goto error
)

if errorlevel 2 (
cls
echo.
echo Restart PC and Re-register any applications
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /g /t %seconds%
goto error
)

if errorlevel 1 (
cls
echo.
echo Restart PC ^(Default Setting^)
choice /c yne /m "Are you sure you want to continue Y or N or [E]xit?"
if errorlevel 3 goto end
if errorlevel 2 goto startover
if errorlevel 1 shutdown /r /t %seconds%
goto error
)

:startover
cls
echo.
echo Restarting script
timeout 2 >nul
goto start

:error
cls
echo.
echo You might be here because of a bad input selection
timeout 2 >nul
echo.
echo Perhaps try another input
endlocal
exit /b

::========================================================================================================================================
::========================================================================================================================================
