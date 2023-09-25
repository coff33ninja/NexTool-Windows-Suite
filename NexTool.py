import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk
from datetime import datetime, timedelta
from tkinter import simpledialog
from tkinter import messagebox
import psutil
import platform
import wmi
import urllib.request
import webbrowser
import os
import subprocess
import win32serviceutil
import win32api
import win32con
import win32com.client
import zipfile

app = ThemedTk(theme="arc")
app.title("NexTool Windows Suite")
app.geometry("1000x700")


def is_admin():
    try:
        # Attempt to read the system file which is only readable by admin
        with open(
            os.path.join(os.environ["SystemRoot"], "system32", "config", "system"), "r"
        ):
            return True
    except:
        return False


def print_to_terminal(msg):
    terminal.insert(tk.END, f"{msg}\n")
    terminal.see(tk.END)  # Auto-scroll to the end


BASE_DIR = "C:\\NexTool"
TRUSTED_URLS = {
    "64": "https://github.com/YerongAI/Office-Tool/releases/download/v10.1.10.1/Office_Tool_with_runtime_v10.1.10.1_x64.zip",
    "32": "https://github.com/YerongAI/Office-Tool/releases/download/v10.1.10.1/Office_Tool_with_runtime_v10.1.10.1_x86.zip",
}


def verify_path(basedir, path):
    return os.path.realpath(path).startswith(basedir)


def download_file(url, destination):
    """
    Downloads a file from the provided URL to the given destination path.
    """
    try:
        urllib.request.urlretrieve(url, destination, reporthook=download_progress)
    except Exception as e:
        print_to_terminal(f"Error downloading {url} to {destination}: {e}")


def download_progress(blocknum, blocksize, totalsize):
    """Callback for displaying download progress."""
    downloaded = blocknum * blocksize
    progress_percentage = int(downloaded / totalsize * 100)
    print_to_terminal(
        f"Downloaded {downloaded} of {totalsize} bytes ({progress_percentage}%)"
    )


def run_quick_info():
    os.system("cls")
    print_to_terminal("Running Basic Computer Report...")

    # Define the base directory and ensure it exists
    base_dir = "C:\\NexTool\\System\\Basic Computer Report"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Downloading the PowerShell script
    ps_script_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/ComputerInfo.ps1"
    destination = os.path.join(base_dir, "ComputerInfo.ps1")

    urllib.request.urlretrieve(ps_script_url, destination, reporthook=download_progress)

    # Execute the PowerShell script
    subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            destination,
            "-verb",
            "runas",
        ],
        check=True,
    )

    # Show messagebox using tkinter
    messagebox.showinfo("Notice", "Press OK to continue.")

    # Open the report in default browser
    report_path = "C:\\Windows\\Temp\\Basic-Computer-Information-Report.html"
    webbrowser.open(report_path)

    # Clean up the downloaded script
    os.remove(destination)

    return


def run_hwinfo32():
    os.system("cls")

    # Check for administrative privileges
    if not is_admin():
        user_response = messagebox.askyesno(
            "Elevation Required",
            "The upcoming operation requires elevated privileges. Do you wish to continue and elevate?",
        )

        if not user_response:  # If the user says 'no', then return
            return

    # Define the base directory and ensure it exists
    base_dir = "C:\\NexTool\\System\\Advanced Hardware Info"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Downloading the executable and its configuration
    exe_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/HWiNFO32.exe"
    ini_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/HWiNFO32.INI"

    exe_destination = os.path.join(base_dir, "HWiNFO32.exe")
    ini_destination = os.path.join(base_dir, "HWiNFO32.INI")

    urllib.request.urlretrieve(exe_url, exe_destination, reporthook=download_progress)
    urllib.request.urlretrieve(ini_url, ini_destination, reporthook=download_progress)

    # Run the downloaded executable
    subprocess.run([exe_destination], check=True)

    # Show the messagebox to notify user
    messagebox.showinfo("Notice", "Press OK to continue.")

    # Clean up after executing
    os.remove(exe_destination)
    os.remove(ini_destination)

    return


# Call the functions based on your requirements
# run_quick_info()
# run_hwinfo32()


def run_speed_test():
    print_to_terminal(
        "THIS SECTION WILL RUN A CLI BASED SPEED TEST TO DETECT INTERNET STABILITY"
    )

    # Setting the paths
    url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/speedtest.exe"
    destination = "c:\\NexTool\\speedtest.exe"

    # Downloading the speedtest executable using the download_file() method
    download_file(url, destination)

    # Running the speedtest and capturing its output
    try:
        result = subprocess.run(
            [destination], text=True, capture_output=True, check=True
        )
        print_to_terminal(result.stdout)

    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred during command execution:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def list_adapters():
    print_to_terminal("Listing all network configurations registered on the device...")
    try:
        output = subprocess.check_output(["netsh", "interface", "ip", "show", "config"])
        print_to_terminal(output.decode())
    except Exception as e:
        print_to_terminal(f"Failed to list adapters: {e}")


def auto_config_wifi():
    print_to_terminal("Configuring Wi-Fi for automatic IP and DNS...")
    try:
        # Set IP to DHCP
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "set",
                "address",
                "name=Wi-Fi",
                "source=dhcp",
            ],
            check=True,
        )

        # Set DNS to DHCP
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "set",
                "dnsservers",
                "name=Wi-Fi",
                "source=dhcp",
            ],
            check=True,
        )

        print_to_terminal("Wi-Fi configured successfully for automatic IP and DNS.")
    except subprocess.CalledProcessError:
        print_to_terminal(
            "Failed to configure Wi-Fi. Ensure you have the necessary permissions and that Wi-Fi is a valid interface name."
        )


def auto_config_ethernet():
    print_to_terminal("Configuring Ethernet for automatic settings...")

    try:
        # Set IP configuration for Ethernet to DHCP
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "set",
                "address",
                "name=Ethernet",
                "source=dhcp",
            ]
        )
        # Set DNS for Ethernet to DHCP
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "set",
                "dnsservers",
                "name=Ethernet",
                "source=dhcp",
            ]
        )

        print_to_terminal("Ethernet set up successfully.")
        response = subprocess.run(
            ["ping", "google.com"], capture_output=True, text=True
        )
        print_to_terminal(response.stdout)

    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def manual_config_wifi():
    # Getting the details from the user
    wifi_ip = simpledialog.askstring("Input", "Enter Wi-Fi IP Address:")
    wifi_subnet = simpledialog.askstring("Input", "Enter Wi-Fi Subnet Mask:")
    wifi_gateway = simpledialog.askstring("Input", "Enter Wi-Fi Gateway:")
    wifi_dns = simpledialog.askstring("Input", "Enter Wi-Fi DNS:")

    # Applying the configurations
    print_to_terminal("Applying Wi-Fi configurations...")

    try:
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "set",
                "address",
                'name="Wi-Fi"',
                f"static {wifi_ip} {wifi_subnet} {wifi_gateway}",
            ]
        )
        subprocess.run(
            [
                "netsh",
                "interface",
                "ipv4",
                "set",
                "dns",
                'name="Wi-Fi"',
                f"{wifi_dns}",
                "primary",
            ]
        )

        print_to_terminal("Wi-Fi configurations applied successfully.")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def ping_host():
    user_input = simpledialog.askstring(
        "Input", "Enter an IP address or hostname to ping (e.g., 8.8.8.8 for GOOGLE):"
    )

    if user_input:  # Check if user provided input and didn't cancel the dialog
        print_to_terminal(f"Pinging {user_input}...")

        try:
            response = subprocess.run(
                ["ping", user_input], capture_output=True, text=True
            )
            print_to_terminal(response.stdout)
            if response.returncode != 0:
                print_to_terminal("Ping operation failed.")
        except Exception as e:
            print_to_terminal(f"Error occurred: {e}")
    else:
        print_to_terminal("Ping operation cancelled by user.")


def traceroute():
    print_to_terminal("Please enter the IP address or hostname to trace:")
    host = simpledialog.askstring("Input", "Enter the IP address or hostname:")

    if host:
        print_to_terminal(f"Tracing route to {host}...\n")
        try:
            output = subprocess.check_output(
                ["tracert", "-d", "-h", "64", host], text=True, stderr=subprocess.STDOUT
            )
            print_to_terminal(output)
        except Exception as e:
            print_to_terminal(f"Error occurred: {e}")
    else:
        print_to_terminal("No input provided. Operation cancelled.")


def setup_network_share():
    print_to_terminal("NETWORK SHARE MAP SETUP")
    driveletter = simpledialog.askstring("Input", "Enter a letter to use for map:")
    computer_name = simpledialog.askstring(
        "Input", "Enter an IP address or hostname for map:"
    )
    share_name = simpledialog.askstring("Input", "Enter a folder share name for map:")
    persistent_choice = simpledialog.askstring(
        "Input", "Type ONLY YES or NO to make it permanent:"
    )
    username = simpledialog.askstring(
        "Input", "Enter USER ACCOUNT SHARE NAME (Leave blank if none):"
    )
    password = simpledialog.askstring(
        "Input", "Enter USER ACCOUNT PASSWORD (Leave blank if none):", show="*"
    )

    cmd_str = f"net use {driveletter}: \\\\{computer_name}\\{share_name} /user:{username} {password} /PERSISTENT:{persistent_choice}"

    try:
        subprocess.run(cmd_str, shell=True, check=True, capture_output=True, text=True)
        print_to_terminal(
            f"Successfully mapped drive {driveletter}: to {computer_name}\\{share_name}"
        )
    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred: {e.stdout}")


def remove_network_map():
    print_to_terminal("REMOVE NETWORK MAP")

    # Prompt the user for a drive letter
    drive_letter = input("ENTER MAPPED DRIVE LETTER TO REMOVE:")

    try:
        # Attempt to remove the network map
        subprocess.run(["net", "use", f"{drive_letter}:", "/delete"], check=True)
        print_to_terminal(f"{drive_letter}: drive mapping removed successfully.")
    except subprocess.CalledProcessError:
        print_to_terminal(f"Failed to remove {drive_letter}: drive mapping.")


def wifi_configuration():
    print_to_terminal(
        "This section will display all registered WIFI networks on this device."
    )

    # Show registered Wi-Fi networks
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "profile"])
        print_to_terminal(result.decode("utf-8"))

        # Ask user if they want to view passwords of saved networks
        answer = messagebox.askyesno(
            "WiFi Passwords", "Do you want to view the WiFi passwords?"
        )

        if answer:
            profiles = [
                line.split(":")[1][1:-1]
                for line in result.decode("utf-8").split("\n")
                if "All User Profile" in line
            ]
            for profile in profiles:
                try:
                    wifi_result = subprocess.check_output(
                        [
                            "netsh",
                            "wlan",
                            "show",
                            "profile",
                            "name={}".format(profile),
                            "key=clear",
                        ]
                    )
                    wifi_lines = wifi_result.decode("utf-8").split("\n")
                    wifi_lines = [
                        line.split(":")[1][1:-1]
                        for line in wifi_lines
                        if "Key Content" in line
                    ]
                    print_to_terminal(f"SSID: {profile}  |  Password: {wifi_lines[0]}")
                except subprocess.CalledProcessError as e:
                    print_to_terminal(
                        f"Encountered an error while fetching details of {profile}. {e}"
                    )
                    continue

        print_to_terminal("Completed fetching WiFi details.")
    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred: {e}")


def disable_windows_defender():
    print_to_terminal("DISABLING WINDOWS DEFENDER...")
    try:
        # Disable real-time monitoring
        subprocess.run(
            [
                "Powershell",
                "-ExecutionPolicy",
                "Bypass",
                "Set-MpPreference",
                "-DisableRealtimeMonitoring",
                "1",
            ],
            check=True,
        )

        # Download the PowerShell script and run it
        ps_script_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/disable-windows-defender.ps1"
        destination = "C:\\NexTool\\WINDOWS_DEFENDER\\disable-windows-defender.ps1"
        subprocess.run(
            [
                "aria2c",
                ps_script_url,
                "-d,",
                "--dir=C:\\NexTool\\WINDOWS_DEFENDER\\",
                "--allow-overwrite=true",
                "--disable-ipv6",
            ],
            check=True,
        )
        subprocess.run(
            [
                "Powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                destination,
                "-verb",
                "runas",
            ],
            check=True,
        )

        # Add Threat ID exceptions
        threat_ids = [
            "2147685180",
            "2147735507",
            "2147736914",
            "2147743522",
            "2147734094",
            "2147743421",
            "2147765679",
            "251873",
            "213927",
            "2147722906",
        ]
        for tid in threat_ids:
            subprocess.run(
                [
                    "Powershell",
                    "-nologo",
                    "-noninteractive",
                    "-windowStyle",
                    "hidden",
                    "-noprofile",
                    "-command",
                    "Add-MpPreference",
                    "-ThreatIDDefaultAction_Ids",
                    tid,
                    "-ThreatIDDefaultAction_Actions",
                    "Allow",
                    "-Force",
                ],
                check=True,
            )

        # Add path exclusions
        paths = [
            "C:\\Windows\\KMSAutoS",
            "C:\\Windows\\System32\\SppExtComObjHook.dll",
            "C:\\Windows\\System32\\SppExtComObjPatcher.exe",
            "C:\\Windows\\AAct_Tools",
            "C:\\Windows\\AAct_Tools\\AAct_x64.exe",
            "C:\\Windows\\AAct_Tools\\AAct_files\\KMSSS.exe",
            "C:\\Windows\\AAct_Tools\\AAct_files",
            "C:\\Windows\\KMS",
            "C:\\WINDOWS\\Temp\\_MAS",
            "C:\\WINDOWS\\Temp\\__MAS",
            "C:\\ProgramData\\Online_KMS_Activation",
            "C:\\ProgramData\\Online_KMS_Activation\\BIN\\cleanosppx64.exe",
            "C:\\ProgramData\\Online_KMS_Activation\\BIN\\cleanosppx86.exe",
            "C:\\ProgramData\\Online_KMS_Activation\\Activate.cmd",
            "C:\\ProgramData\\Online_KMS_Activation\\Info.txt",
            "C:\\ProgramData\\Online_KMS_Activation\\Activate.cmd",
        ]
        for path in paths:
            subprocess.run(
                [
                    "Powershell",
                    "-nologo",
                    "-noninteractive",
                    "-windowStyle",
                    "hidden",
                    "-noprofile",
                    "-command",
                    "Add-MpPreference",
                    "-ExclusionPath",
                    path,
                    "-Force",
                ],
                check=True,
            )

        # Download and run Defender_Tools.exe
        defender_tools_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/Defender_Tools.exe"
        destination = "C:\\NexTool\\WINDOWS_DEFENDER\\Defender_Tools.exe"
        subprocess.run(
            [
                "aria2c",
                defender_tools_url,
                "-d,",
                "--dir=C:\\NexTool\\WINDOWS_DEFENDER\\",
                "--allow-overwrite=true",
                "--disable-ipv6",
            ],
            check=True,
        )
        subprocess.run([destination], check=True)

        print_to_terminal("WINDOWS DEFENDER DISABLED SUCCESSFULLY.")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def remove_windows_defender():
    print_to_terminal("REMOVING WINDOWS DEFENDER...")
    try:
        # Downloading install_wim_tweak.exe
        tweak_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/install_wim_tweak.exe"
        destination = "C:\\NexTool\\install_wim_tweak.exe"

        # Use the download_file method to download the executable
        download_file(tweak_url, destination)

        # Run the downloaded executable
        subprocess.run([destination, "/o", "/l", "SHOWCLI"], check=True)
        subprocess.run(
            [destination, "/o", "/c", "Windows-Defender", "/r", "SHOWCLI"], check=True
        )

        # Other commands...

        print_to_terminal("WINDOWS DEFENDER REMOVED SUCCESSFULLY.")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


# Placeholder function for the additional tool
def additional_tool():
    print_to_terminal("RUNNING ADDITIONAL TOOL...")
    # Add the commands or functionalities for the additional tool here
    print_to_terminal("ADDITIONAL TOOL COMPLETED.")


def run_TELEMETRY():
    print_to_terminal("Blocking telemetry...")
    try:
        # Set the registry key
        command = [
            "reg",
            "add",
            "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "/v",
            "AllowTelemetry",
            "/t",
            "REG_DWORD",
            "/d",
            "0",
            "/F",
        ]
        subprocess.run(command, check=True)

        # Download and run the PowerShell telemetry blocker
        telemetry_script_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/block-telemetry.ps1"
        telemetry_script_path = "C:\\NexTool\\block-telemetry.ps1"
        download_file(telemetry_script_url, telemetry_script_path)
        command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            telemetry_script_path,
            "-verb",
            "runas",
        ]
        subprocess.run(command, check=True)

        # Download and run ooshutup10 with its configuration
        exe_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/ooshutup10.exe"
        cfg_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/ooshutup10.cfg"
        exe_path = "C:\\NexTool\\ooshutup10.exe"
        cfg_path = "C:\\NexTool\\ooshutup10.cfg"
        download_file(exe_url, exe_path)
        download_file(cfg_url, cfg_path)
        command = [exe_path, cfg_path, "/quiet"]
        subprocess.run(command, check=True)

        # Show success message box
        messagebox.showinfo(
            "COMPLETE", "Telemetry blocked successfully. Press OK to continue."
        )

    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred during command execution:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def run_MAS():
    print_to_terminal("Executing Microsoft Activation Script...")
    try:
        # Execute the PowerShell command
        command = ["powershell.exe", "-Command", "irm https://massgrave.dev/get | iex"]
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        print_to_terminal(result.stdout)
    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred during command execution:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def start_windows_update():
    print_to_terminal("Starting Windows Manual Updater...")

    # Define the URL for WUpdater.exe and its intended destination
    download_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/WUpdater.exe"
    destination = "C:\\NexTool\\WUpdater.exe"

    try:
        # Download WUpdater.exe
        urllib.request.urlretrieve(download_url, destination)
        print_to_terminal("Downloaded WUpdater.exe successfully.")

        # Execute the WUpdater.exe and wait until it completes
        subprocess.run(destination, check=True)

        # After the execution, delete the exe (you can keep this if you want to reuse without downloading again)
        os.remove(destination)
        print_to_terminal("Deleted WUpdater.exe.")

    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def pause_windows_update():
    # Check if we have elevated permissions
    if not win32api.IsUserAnAdmin():
        # If not, re-run the script with elevated permissions
        subprocess.run(["pythonw", __file__, "--elevated"], shell=True)
        return

    # Disable and stop the Windows Update service
    try:
        win32serviceutil.StopService("wuauserv")
        win32serviceutil.ChangeStartType("wuauserv", win32serviceutil.SERVICE_DISABLED)
    except Exception as e:
        print(f"Error stopping or disabling Windows Update service: {e}")

    # Prompt the user for the number of days
    number_of_days = int(input("Enter the number of days to pause updates for: "))
    trigger_time = datetime.now() + timedelta(days=number_of_days)

    # Create a scheduled task to re-enable the Windows Update service
    try:
        scheduler = win32com.client.Dispatch("Schedule.Service")
        scheduler.Connect()

        root_folder = scheduler.GetFolder("\\")
        task_def = scheduler.NewTask(0)

        # Create a time-based trigger that fires at the specified date/time
        start_time = trigger_time.strftime("%Y-%m-%dT%H:%M:%S")
        trigger = task_def.Triggers.Create(win32com.client.constants.TASK_TRIGGER_TIME)
        trigger.StartBoundary = start_time
        trigger.Enabled = True

        # Define the action to restart the Windows Update service
        action = task_def.Actions.Create(win32com.client.constants.TASK_ACTION_EXEC)
        action.Path = "powershell.exe"
        action.Arguments = '-c "Start-Service wuauserv"'

        # Register the task (no password needed as we are already running as an admin)
        root_folder.RegisterTaskDefinition(
            "PauseWinUpdates",
            task_def,
            win32com.client.constants.TASK_CREATE_OR_UPDATE,
            "",  # No user
            "",  # No password
            win32com.client.constants.TASK_LOGON_INTERACTIVE_TOKEN,
        )
        print(f"Windows Update paused. It will be resumed on {trigger_time}.")
    except Exception as e:
        print(f"Error creating scheduled task: {e}")


def run_patchmypc():
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/PRE-SELECT/PatchMyPC.exe",
        "C:\\NexTool\\PatchMyPC.exe",
    )
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/PRE-SELECT/PatchMyPC.ini",
        "C:\\NexTool\\PatchMyPC.ini",
    )
    subprocess.run(["C:\\NexTool\\PatchMyPC.exe", "/auto", "switch"], check=True)


def run_patchmypc_own_selections():
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/SELF-SELECT/PatchMyPC.exe",
        "C:\\NexTool\\PatchMyPC.exe",
    )
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/SELF-SELECT/PatchMyPC.ini",
        "C:\\NexTool\\PatchMyPC.ini",
    )
    subprocess.run(["C:\\NexTool\\PatchMyPC.exe"], check=True)


def install_choco_packages():
    packages = [
        "googlechrome",
        "git",
        "adobeair",
        "adobeshockwaveplayer",
        "javaruntime",
        "netfx-repair-tool",
        "dogtail.dotnet3.5sp1",
        "dotnet4.0",
        "dotnet4.5",
        "dotnet4.6.1",
        "netfx-4.7.1",
        "netfx-4.8",
        "dotnetfx",
        "silverlight",
        "vcredist-all",
        "python2",
        "python3",
        "googlechrome",
        "firefox",
        "edgedeflector",
        "k-litecodecpackfull",
        "k-litecodecpackmega",
        "vlc",
        "7zip",
        "adobereader",
        "cdburnerxp",
        "skype",
        "winaero-tweaker",
        "anydesk.install",
        "teamviewer",
    ]

    choco_path = os.path.join(os.environ["ProgramData"], "Chocolatey")

    if os.path.exists(choco_path):
        for package in packages:
            subprocess.run(["choco", "install", package, "-y"], check=True)
    else:
        install_cmd = "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", install_cmd],
            check=True,
        )

        for package in packages:
            subprocess.run(["choco", "install", package, "-y"], check=True)


def run_chocolatey_gui():
    subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "[System.Net.ServicePointManager]::SecurityProtocol = 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
        ]
    )
    subprocess.run(["powershell", "choco", "upgrade", "all", "--noop"], check=True)
    subprocess.run(["powershell", "choco", "install", "chocolateygui"], check=True)
    # subprocess.run(["powershell", "choco", "install", "hot-chocolatey"], check=True) # Uncomment if needed.


def install_winget_packages():
    packages = [
        "microsoftedge",  # 'googlechrome' - Microsoft Edge is a direct analog to Chrome in Winget
        "git.git",  # 'git'
        # 'adobeair',  # There's no direct Adobe AIR package in Winget
        # 'adobeshockwaveplayer',  # No direct Adobe Shockwave Player package in Winget
        # 'javaruntime',  # No direct Java Runtime package in Winget, but there are OpenJDK variants
        # .NET framework installations might be better handled outside of package managers for more control
        "vlc.vlc",  # 'vlc'
        "7zip.7zip",  # '7zip'
        # 'adobereader',  # Adobe Reader has licensing issues, consider using other PDF readers like Foxit
        # 'cdburnerxp',  # No direct CD Burner XP package in Winget
        "microsoft.skypeapp",  # 'skype'
        # 'winaero-tweaker',  # No direct WinAero Tweaker package in Winget
        # 'anydesk.install',  # No direct AnyDesk package in Winget, but there are alternatives like TeamViewer
        "teamviewer.teamviewer",  # 'teamviewer'
    ]

    for package in packages:
        subprocess.run(["winget", "install", package], check=True)


def run_winget_gui():
    try:
        # Install the WingetUI Store
        subprocess.run(
            ["winget", "install", "-e", "--id", "SomePythonThings.WingetUIStore"],
            check=True,
        )
        print_to_terminal("WingetUI Store installed successfully.")
    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred during installation:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def run_driver_updater():
    try:
        # Download the Snappy Driver zip file
        snappy_driver_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SNAPPY_DRIVER.zip"
        snappy_zip_path = "C:\\NexTool\\SNAPPY_DRIVER.zip"
        snappy_extract_path = "C:\\NexTool\\SNAPPY_DRIVER"

        # Download using urllib (make sure to import it at the top of your script)
        import urllib.request

        urllib.request.urlretrieve(snappy_driver_url, snappy_zip_path)

        # Extract the downloaded zip
        with zipfile.ZipFile(snappy_zip_path, "r") as zip_ref:
            zip_ref.extractall(snappy_extract_path)

        # Execute the appropriate Snappy Driver Installer based on the system's architecture
        arch = platform.architecture()[0]
        if arch == "64bit":
            subprocess.run(
                [
                    os.path.join(snappy_extract_path, "SDI_x64_R2111.exe"),
                    "-checkupdates",
                    "-autoupdate",
                    "-autoclose",
                ],
                check=True,
            )
        elif arch == "32bit":
            subprocess.run(
                [
                    os.path.join(snappy_extract_path, "SDI_R2111.exe"),
                    "-checkupdates",
                    "-autoupdate",
                    "-autoclose",
                ],
                check=True,
            )
        else:
            raise Exception(f"Unsupported architecture: {arch}")

        print_to_terminal("Driver update completed!")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def download_and_setup_office(architecture):
    print_to_terminal("Starting the Office Installation process...")

    url = TRUSTED_URLS.get(architecture)
    if not url:
        print_to_terminal("Invalid architecture specified.")
        return

    destination_zip = os.path.join(BASE_DIR, f"office_tool_{architecture}.zip")
    destination_folder = os.path.join(BASE_DIR, "Office Tool")
    destination_xml = os.path.join(
        destination_folder, f"office_config_{architecture}.xml"
    )

    try:
        # Download
        print_to_terminal("Attempting to download Office Tool Plus...")
        urllib.request.urlretrieve(url, destination_zip)
        print_to_terminal("Downloaded Office Tool Plus.")

        # Verify and Extract
        if verify_path(BASE_DIR, destination_zip):
            print_to_terminal("Attempting to extract Office Tool Plus...")
            with zipfile.ZipFile(destination_zip, "r") as zip_ref:
                zip_ref.extractall(destination_folder)
            print_to_terminal("Extracted Office Tool Plus.")
        else:
            print_to_terminal("Invalid destination path.")

        # Execute Office Tool Plus with XML configuration
        otp_exe_path = os.path.join(destination_folder, "Office Tool Plus.exe")
        subprocess.run([otp_exe_path, "-xml", destination_xml], check=True)
        print_to_terminal("Office Tool Plus launched!")

        # Create XML
        create_office_config(architecture, destination_xml)

        # Show popup
        message = f"The Office Tool Plus (x{architecture}) has been set up at {destination_folder}. An XML configuration preset is available for you to import and make the setup process easier."
        messagebox.showinfo("Office Setup", message)

    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def create_office_config(architecture, destination):
    """Generate Office XML configuration for a given architecture."""

    if architecture not in ["64", "32"]:
        return

    # Define XML content
    xml_content = """
<Configuration>
  <Add OfficeClientEdition="{arch}" Channel="PerpetualVL2021" MigrateArch="true" AllowCdnFallback="true">
    <Product ID="ProPlus2021Volume">
      <Language ID="MatchPreviousMSI" />
      <ExcludeApp ID="Lync" />
      <ExcludeApp ID="OneDrive" />
      <ExcludeApp ID="OneNote" />
      <ExcludeApp ID="Teams" />
    </Product>
    <Product ID="ProofingTools">
      <Language ID="af-za" />
      <Language ID="en-us" />
    </Product>
  </Add>
  <Display AcceptEULA="True" />
  <Property Name="PinIconsToTaskbar" Value="True" />
  <Property Name="ForceAppShutdown" Value="True" />
  <Updates Enabled="false" />
  <RemoveMSI />
  <Extend DownloadFirst="true" CreateShortcuts="true" />
</Configuration>
    """.format(
        arch=architecture
    )

    # Write XML to file
    with open(destination, "w") as xml_file:
        xml_file.write(xml_content)


def button_action(sub_item):
    function_mapping = {
        "Basic Computer Report": run_quick_info,
        "Advanced Hardware Info": run_hwinfo32,
        "Test Connection": run_speed_test,
        "List Adapters": list_adapters,
        "Auto Config Wi-Fi": auto_config_wifi,
        "Ethernet Automatic Configuration": auto_config_ethernet,
        "Manual Wi-Fi Configuration": manual_config_wifi,
        "Ping Host": ping_host,
        "Trace Route": traceroute,
        "Setup Network Share": setup_network_share,
        "Remove Network Map": remove_network_map,
        "Wi-Fi Configuration": wifi_configuration,
        "Disable Windows Defender": disable_windows_defender,
        "Remove Windows Defender": remove_windows_defender,
        "Additional Tool": additional_tool,
        "Block Telemetry": run_TELEMETRY,
        "Microsoft Activation Script": run_MAS,
        "Windows Update": start_windows_update,
        "Pause Windows Update": pause_windows_update,
        "PatchMyPC Pre-Set Selections": run_patchmypc,
        "PatchMyPC GUI": run_patchmypc_own_selections,
        "Chocolatey Pre-Set Selections": install_choco_packages,
        "Chocolatey GUI": run_chocolatey_gui,
        "Winget Pre-Set Selections": install_winget_packages,
        "Winget GUI": run_winget_gui,
        "Driver Updater": run_driver_updater,
        "Download and Setup Office": download_and_setup_office,
    }
    function_to_run = function_mapping.get(sub_item)
    if function_to_run:
        function_to_run()
    else:
        terminal.insert(tk.END, f"Executing action for: {sub_item}\n")
        terminal.see(tk.END)  # Auto-scroll to the end


# Function to display the main menu
def show_main_menu():
    for child in left_frame.winfo_children():
        child.grid_forget()

    for idx, main_item in enumerate(tabs.keys()):
        main_button = ttk.Button(
            left_frame,
            text=main_item,
            command=lambda main_item=main_item: show_sub_menu(main_item),
        )
        main_button.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)
        tooltip_text = tabs_tooltips.get(main_item, default_tooltip)
        ToolTip(main_button, text=tooltip_text)


# Function to show sub-menus based on the main menu item
def show_sub_menu(main_item):
    for child in left_frame.winfo_children():
        child.grid_forget()

    sub_items = tabs[main_item]
    if isinstance(sub_items, dict):  # Check if it's a nested dictionary
        for idx, sub_category in enumerate(sub_items.keys()):
            sub_button = ttk.Button(
                left_frame,
                text=sub_category,
                command=lambda sub_category=sub_category: show_sub_sub_menu(
                    main_item, sub_category
                ),
            )
            sub_button.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)
    else:
        for idx, sub_item in enumerate(sub_items):
            sub_button = ttk.Button(
                left_frame,
                text=sub_item,
                command=lambda sub_item=sub_item: button_action(sub_item),
            )
            sub_button.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)

    back_button = ttk.Button(
        left_frame, text="Back to Main Menu", command=show_main_menu
    )
    back_button.grid(row=len(sub_items), column=0, sticky="ew", padx=10, pady=10)


def show_sub_sub_menu(main_item, sub_category):
    for child in left_frame.winfo_children():
        child.grid_forget()

    sub_sub_items = tabs[main_item][sub_category]
    for idx, sub_sub_item in enumerate(sub_sub_items):
        sub_sub_button = ttk.Button(
            left_frame,
            text=sub_sub_item,
            command=lambda sub_sub_item=sub_sub_item: button_action(sub_sub_item),
        )
        sub_sub_button.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)

    back_button = ttk.Button(
        left_frame,
        text=f"Back to {main_item}",
        command=lambda: show_sub_menu(main_item),
    )
    back_button.grid(row=len(sub_sub_items), column=0, sticky="ew", padx=10, pady=10)


class ToolTip:
    def __init__(self, widget, text="Widget Info"):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()


# Main Menu Tooltips
tabs_tooltips = {
    "System": "View and manage core system information.",
    "Configuration": "Modify various system settings and configurations.",
    "Software Management": "Manage software installations and updates.",
    "Maintenance": "Perform routine maintenance tasks on your system.",
    "Advanced": "Access advanced features and utilities.",
    "Extras": "Explore additional tools and features.",
    "Shutdown Options": "Choose different shutdown or restart options for the system.",
    "Additional Tool": "Access more tools to enhance your system.",  # This is added based on your 'tabs' structure.
}

# Sub Menu Tooltips
sub_tooltips = {
    "Basic Computer Report": "Get a quick overview of your computer's basic configuration.",
    "Advanced Hardware Info": "Dive deep into detailed hardware stats using HWINFO32.",
    "Test Connection": "Check your internet connection speed and quality.",
    "List Adapters": "View all network adapters on the system.",
    "Auto Config Wi-Fi": "Automatically configure Wi-Fi settings.",
    "Ethernet Automatic Configuration": "Set up Ethernet with automatic settings.",
    "Manual Wi-Fi Configuration": "Manually set up Wi-Fi connection parameters.",
    "Ping Host": "Ping a specific IP address or domain to check connectivity.",
    "Trace Route": "Trace the route packets take to reach a specific network target.",
    "Setup Network Share": "Establish a new network share mapping.",
    "Remove Network Map": "Disconnect and remove a network map.",
    "Wi-Fi Configuration": "Access and manage saved Wi-Fi networks on the system.",
    "Disable Windows Defender": "Turn off Windows Defender functionalities.",
    "Remove Windows Defender": "Completely remove Windows Defender from the system.",
    "Block Telemetry": "Restrict Windows from sending telemetry data.",
    "Microsoft Activation Script": "Manage Windows activation status.",
    "Windows Update": "Access and manage Windows updates.",
    "Windows Update Pauser": "Temporarily pause Windows updates.",
    "Software Updater": "Keep your software up-to-date.",
    "Driver Updater": "Automatically update drivers using the Snappy Driver Installer.",
    "Office Installations": "Manage your Microsoft Office installations.",
    "Disk Cleanup": "Free up storage space by cleaning unnecessary files.",
    "Disk Defragment": "Optimize your storage drives with defragmentation.",
    "Disk Check": "Scan your storage drives for errors.",
    "Backupper": "Backup important data to stay safe.",
    "Windows Install": "Manage and facilitate Windows installations.",
    "DISM and SFC Windows Repair": "Repair corrupted or damaged Windows files.",
    "Windows Debloater": "Remove unnecessary built-in software from Windows.",
    "Group Policy Reset": "Reset all system group policies to their defaults.",
    "WMI Reset": "Reset and refresh the Windows Management Instrumentation service.",
    "Disable Specific Services": "Turn off specific system services as needed.",
    "Services Manager": "Comprehensive control over all system services.",
    "Restart": "Reboot your computer.",
    "Restart and Re-register": "Reboot and re-register system components.",
    "Restart to UEFI/BIOS": "Directly reboot into the system UEFI or BIOS.",
    "Restart and Load Advanced Boot Options": "Reboot to the advanced startup options.",
    "Shutdown": "Completely turn off your computer.",
    "Shutdown and Re-register": "Shutdown and re-register system components.",
    "Sign Out": "Logout from the current user profile.",
}

default_tooltip = "This is the Main Menu For NexTool."

# Creating left frame for menu items
left_frame = ttk.Frame(app)
left_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)

# Creating right frame for the terminal
right_frame = ttk.Frame(app)
right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# Embedded Terminal
terminal = scrolledtext.ScrolledText(
    right_frame, undo=True, wrap=tk.WORD, bg="black", fg="white", font=("Consolas", 12)
)
terminal.pack(fill="both", expand=True, padx=10, pady=10)

# Fetch System Information
c = wmi.WMI()

os_info = c.Win32_OperatingSystem()[0]
proc_info = c.Win32_Processor()[0]
bios_info = c.Win32_BIOS()[0]
disk_info = c.Win32_DiskDrive()

system_info = {
    "CPU": proc_info.Name,
    "RAM (Total GB)": round(psutil.virtual_memory().total / (1024**3), 2),
    "BIOS Version": bios_info.Version,
    "Windows Version": f"{os_info.Version} ({os_info.BuildNumber})",
    "System Serial": bios_info.SerialNumber,
    "Disks": ", ".join([disk.Model for disk in disk_info]),
}

# Creating bottom frame for system info display
bottom_frame = ttk.Frame(app)
bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

info_text = "\n".join([f"{key}: {value}" for key, value in system_info.items()])
info_label = ttk.Label(bottom_frame, text=info_text, anchor="w")
info_label.pack(fill="both", expand=True, padx=10, pady=10)

tabs = {
    "System": ["Basic Computer Report", "Advanced Hardware Info"],
    "Configuration": {
        "Network": [
            "Test Connection",
            "List Adapters",
            "Auto Config Wi-Fi",
            "Ethernet Automatic Configuration",
            "Manual Wi-Fi Configuration",
            "Ping Host",
            "Trace Route",
            "Setup Network Share",
            "Remove Network Map",
            "Wi-Fi Configuration",
        ],
        "Security": [
            "Disable Windows Defender",
            "Remove Windows Defender",
            "Block Telemetry",
            "Microsoft Activation Script",
        ],
    },
    "Additional Tool": [],
    "Software Management": [
        "Windows Update",
        "Windows Update Pauser",
        "PatchMyPC Pre-Set Selections",
        "PatchMyPC GUI",
        "Chocolatey Pre-Set Selections",
        "Chocolatey GUI",
        "Winget Pre-Set Selections",
        "Winget GUI",
        "Driver Updater",
        "Office Installations",
    ],
    "Maintenance": ["Disk Cleanup", "Disk Defragment", "Disk Check", "Backupper"],
    "Advanced": [
        "Windows Install",
        "DISM and SFC Windows Repair",
        "Windows Debloater",
        "Group Policy Reset",
        "WMI Reset",
        "Disable Specific Services",
        "Services Manager",
    ],
    "Extras": [],
    "Shutdown Options": [
        "Restart",
        "Restart and Re-register",
        "Restart to UEFI/BIOS",
        "Restart and Load Advanced Boot Options",
        "Shutdown",
        "Shutdown and Re-register",
        "Sign Out",
    ],
}

# Display the main menu at startup
show_main_menu()

app.mainloop()
