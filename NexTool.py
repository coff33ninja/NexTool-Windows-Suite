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
import ctypes
import win32service
import winreg as reg
import json
import tempfile

app = ThemedTk(theme="breeze-dark")
app.title("NexTool Windows Suite")
app.geometry("1000x700")


def is_admin():
    try:
        # Attempt to read the system file which is only readable by admin
        with open(
            os.path.join(os.environ["SystemRoot"],
                         "system32", "config", "system"), "r"
        ):
            return True
    except PermissionError:
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
    Downloads a file from the provided URL to the given destination path and updates a progress bar.
    """
    try:

        def download_progress(blocknum, blocksize, totalsize):
            downloaded = blocknum * blocksize
            progress = int((downloaded / totalsize) * 100)
            progress_bar["value"] = progress
            app.update_idletasks()
            print_to_terminal(f"Downloading: {progress}% complete")

        urllib.request.urlretrieve(
            url, destination, reporthook=download_progress)
    except Exception as e:
        print_to_terminal(f"Error downloading {url} to {destination}: {e}")


def extract_zip(zip_path, destination_folder):
    """
    Extract a zip file to a specified folder and update the progress bar.
    """

    def extract_progress(zip_file):
        files = zip_file.namelist()
        total_files = len(files)

        for i, file in enumerate(files, 1):
            zip_file.extract(file, destination_folder)
            percent_complete = int(i * 100 / total_files)
            progress_bar["value"] = percent_complete
            app.update_idletasks()
            print_to_terminal(f"Extracting: {percent_complete}%")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        extract_progress(zip_ref)


def msg_box(message, title, style):
    return ctypes.windll.user32.MessageBoxW(0, message, title, style)


def run_winget_check(action_type):
    if is_winget_installed():
        terminal.insert(tk.END, "Winget is available!\n")
        terminal.see(tk.END)  # Auto-scroll to the end

        if action_type == "gui":
            # Specific functionality for Winget GUI
            run_winget_gui()
        elif action_type == "pre_set_selections":
            # Specific functionality for Winget Pre-Set Selections
            install_winget_packages()
    else:
        prompt_winget_installation()

    def is_winget_installed():
        try:
            result = subprocess.run(
                ["winget", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def prompt_winget_installation():
        # Message to guide user
        msg = ("Winget is not detected on this machine. Please follow the instructions below:\n\n"
               "Method 1: Install winget via Microsoft Store\n"
               "1. Open the Microsoft Store app.\n"
               "2. Search for 'winget' and select the App Installer application.\n"
               "3. Click Get to install.\n\n"
               "Alternatively, you can [Click Here](https://aka.ms/winget-install) to directly open the Microsoft Store page for Winget.\n\n"
               "Method 2: Install winget via GitHub\n"
               "1. Navigate to the [Winget GitHub page](https://github.com/microsoft/winget-cli/releases).\n"
               "2. Download the latest .msixbundle file and install.\n\n"
               "After installation, please re-run this tool.")

        info_window = tk.Toplevel(app)
        info_window.title("Winget Installation Guide")

        text_widget = tk.Text(info_window, wrap=tk.WORD, height=20, width=60)
        text_widget.pack(padx=20, pady=20)

        # Make links clickable
        text_widget.insert(tk.END, msg)
        text_widget.tag_configure("hyper", foreground="blue", underline=True)
        text_widget.tag_bind("hyper", "<Enter>",
                             lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind("hyper", "<Leave>",
                             lambda e: text_widget.config(cursor="arrow"))

        # Open Microsoft Store link
        start_link = msg.find("[Click Here]")
        end_link = start_link + len("[Click Here]")
        text_widget.tag_add("hyper", f"1.{start_link}", f"1.{end_link}")
        text_widget.tag_bind(
            "hyper", "<Button-1>", lambda e: webbrowser.open("https://aka.ms/winget-install"))

        # Open GitHub link
        start_link_gh = msg.find("[Winget GitHub page]")
        end_link_gh = start_link_gh + len("[Winget GitHub page]")
        text_widget.tag_add("hyper", f"1.{start_link_gh}", f"1.{end_link_gh}")
        text_widget.tag_bind("hyper", "<Button-1>", lambda e: webbrowser.open(
            "https://github.com/microsoft/winget-cli/releases"))

        # Prompt for Winget PowerShell installation
        response = tk.messagebox.askyesno("Install using PowerShell?",
                                          "Do you want to attempt the installation using a PowerShell script?")
        if response:
            install_winget_powershell()

    def install_winget_powershell():
        os.system("cls")
        base_dir = "C:\\NexTool"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        destination = os.path.join(base_dir, "winget-install.ps1")
        download_file(
            "https://raw.githubusercontent.com/asheroto/winget-install/master/winget-install.ps1",
            destination
        )

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

        # Clean up the downloaded script
        os.remove(destination)

        return


def run_quick_info():
    os.system("cls")
    print_to_terminal("Running Basic Computer Report...")

    # Define the base directory and ensure it exists
    print_to_terminal("Running Basic Computer Report...")
    base_dir = "C:\\NexTool\\System\\Basic Computer Report"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    destination = os.path.join(base_dir, "ComputerInfo.ps1")
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/ComputerInfo.ps1",
        destination,
    )

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

    # Downloading the executable and its configuration
    base_dir = "C:\\NexTool\\System\\Advanced Hardware Info"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    exe_destination = os.path.join(base_dir, "HWiNFO32.exe")
    ini_destination = os.path.join(base_dir, "HWiNFO32.INI")
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/HWiNFO32.exe",
        exe_destination,
    )
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/HWiNFO32.INI",
        ini_destination,
    )
    subprocess.run([exe_destination], check=True)

    # Show the messagebox to notify user
    messagebox.showinfo("Notice", "Press OK to continue.")
    return


def run_speed_test():
    print_to_terminal(
        "THIS SECTION WILL RUN A CLI BASED SPEED TEST TO DETECT INTERNET STABILITY"
    )

    # Define the base directory and ensure it exists
    base_dir = "C:\\NexTool\\Configuration\\Network"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    exe_destination = os.path.join(base_dir, "speedtest.exe")
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/1.INFORMATION/speedtest.exe",
        exe_destination,
    )

    try:
        with subprocess.Popen(
            [exe_destination],
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        ) as proc:
            if proc.stdout:  # Check if stdout is not None
                for line in proc.stdout:
                    print_to_terminal(line.strip())
        proc.wait()
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def list_adapters():
    print_to_terminal(
        "Listing all network configurations registered on the device...")
    try:
        output = subprocess.check_output(
            ["netsh", "interface", "ip", "show", "config"])
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

        print_to_terminal(
            "Wi-Fi configured successfully for automatic IP and DNS.")
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
    driveletter = simpledialog.askstring(
        "Input", "Enter a letter to use for map:")
    computer_name = simpledialog.askstring(
        "Input", "Enter an IP address or hostname for map:"
    )
    share_name = simpledialog.askstring(
        "Input", "Enter a folder share name for map:")
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
        subprocess.run(cmd_str, shell=True, check=True,
                       capture_output=True, text=True)
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
        subprocess.run(
            ["net", "use", f"{drive_letter}:", "/delete"], check=True)
        print_to_terminal(
            f"{drive_letter}: drive mapping removed successfully.")
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
                    print_to_terminal(
                        f"SSID: {profile}  |  Password: {wifi_lines[0]}")
                except subprocess.CalledProcessError as e:
                    print_to_terminal(
                        f"Encountered an error while fetching details of {profile}. {e}"
                    )
                    continue

        print_to_terminal("Completed fetching WiFi details.")
    except subprocess.CalledProcessError as e:
        print_to_terminal(f"Error occurred: {e}")


def disable_windows_defender():
    os.system("cls")
    print_to_terminal("DISABLING WINDOWS DEFENDER...")

    cmd_list_base = [
        "Powershell",
        "-ExecutionPolicy",
        "Bypass",
    ]

    # List of commands to run
    cmd_options = [
        "Set-MpPreference -DisableRealtimeMonitoring $true",
        "Set-MpPreference -DisableBehaviorMonitoring $true",
        "Set-MpPreference -DisableOnAccessProtection $true",
        "Set-MpPreference -DisableIOAVProtection $true",
        "Set-MpPreference -DisableIntrusionPreventionSystem $true",
        "Set-MpPreference -DisablePrivacyMode $true",
    ]

    for option in cmd_options:
        try:
            cmd_list = cmd_list_base + [option]
            with subprocess.Popen(cmd_list, stdout=subprocess.PIPE, text=True) as proc:
                if proc.stdout:  # Check if stdout is not None
                    for line in proc.stdout:
                        print_to_terminal(line.strip())
        except Exception as e:
            print_to_terminal(f"Error occurred: {e}")

    # Disable Tamper Protection
    disable_tamper_protection()

    # Download and run Defender_Tools.exe
    base_dir = "C:\\NexTool\\Configuration\\SECURITY"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    exe_destination = os.path.join(base_dir, "Defender_Tools.exe")
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/Defender_Tools.exe",
        exe_destination,
    )
    subprocess.run([exe_destination], check=True)

    print_to_terminal("WINDOWS DEFENDER DISABLED SUCCESSFULLY.")


def disable_tamper_protection():
    print_to_terminal("ATTEMPTING TO DISABLE TAMPER PROTECTION...")

    cmd = (
        "powershell -Command "
        "'Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows Defender\\Features -Name TamperProtection -Value 0'"
    )

    try:
        subprocess.run(cmd, check=True)
        print_to_terminal("Tamper Protection disabled successfully.")
    except subprocess.CalledProcessError as e:
        print_to_terminal(
            f"Error occurred during command execution:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def remove_windows_defender():
    print_to_terminal("REMOVING WINDOWS DEFENDER...")
    try:
        # Downloading install_wim_tweak.exe
        base_dir = "C:\\NexTool\\Configuration\\SECURITY"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        exe_destination = os.path.join(base_dir, "install_wim_tweak.exe")
        download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/install_wim_tweak.exe",
            exe_destination,
        )

        # Run the downloaded executable
        subprocess.run([exe_destination, "/o", "/l", "SHOWCLI"], check=True)
        subprocess.run(
            [exe_destination, "/o", "/c", "Windows-Defender", "/r", "SHOWCLI"],
            check=True,
        )
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
            r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",  # Note the 'r' prefix
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
        base_dir = r"C:\NexTool\Configuration\TELEMETRY"  # Note the 'r' prefix
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        telemetry_script_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/block-telemetry.ps1"
        telemetry_script_path = os.path.join(base_dir, "block-telemetry.ps1")
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
        exe_path = os.path.join(base_dir, "ooshutup10.exe")
        cfg_path = os.path.join(base_dir, "ooshutup10.cfg")

        download_file(exe_url, exe_path)
        download_file(cfg_url, cfg_path)

        command = [exe_path, cfg_path, "/quiet"]
        subprocess.run(command, check=True)

        # Show success message box
        messagebox.showinfo(
            "COMPLETE", "Telemetry blocked successfully. Press OK to continue."
        )

    except subprocess.CalledProcessError as e:
        print_to_terminal(
            f"Error occurred during command execution:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def run_MAS():
    print_to_terminal("Executing Microsoft Activation Script...")
    try:
        # Execute the PowerShell command
        command = ["powershell.exe", "-Command",
                   "irm https://massgrave.dev/get | iex"]
        result = subprocess.run(
            command, text=True, capture_output=True, check=True)
        print_to_terminal(result.stdout)
    except subprocess.CalledProcessError as e:
        print_to_terminal(
            f"Error occurred during command execution:\n{e.stderr}")
    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def start_windows_update():
    print_to_terminal("Starting Windows Manual Updater...")

    # Define the base directory and ensure it exists
    base_dir = "C:\\NexTool\\UPDATES"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Define the URL for WUpdater.exe and its intended destination
    download_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/WUpdater.exe"
    exe_destination = os.path.join(base_dir, "WUpdater.exe")

    try:
        # Download WUpdater.exe
        download_file(download_url, exe_destination)
        print_to_terminal("Downloaded WUpdater.exe successfully.")

        # Execute the WUpdater.exe and wait until it completes
        subprocess.run(exe_destination, check=True)

        # After the execution, delete the exe (you can keep this if you want to reuse without downloading again)
        os.remove(exe_destination)
        print_to_terminal("Deleted WUpdater.exe.")

    except Exception as e:
        print_to_terminal(f"Error occurred: {e}")


def pause_windows_update():
    # Check if we have elevated permissions
    if not is_admin():
        # If not, re-run the script with elevated permissions
        subprocess.run(["pythonw", __file__, "--elevated"], shell=True)
        return

    # Disable and stop the Windows Update service
    try:
        scm = win32service.OpenSCManager(
            None, None, win32service.SC_MANAGER_ALL_ACCESS)
        handle = win32service.OpenService(
            scm, "wuauserv", win32service.SERVICE_ALL_ACCESS)
        win32service.StopService(handle)  # type: ignore
        win32service.ChangeServiceConfig(handle, win32service.SERVICE_NO_CHANGE, win32service.SERVICE_DISABLED,
                                         win32service.SERVICE_NO_CHANGE, None, None, False, None, None, None, None)
    except Exception as e:
        print(f"Error stopping or disabling Windows Update service: {e}")

    # Prompt the user for the number of days
    number_of_days = int(
        input("Enter the number of days to pause updates for: "))
    trigger_time = datetime.now() + timedelta(days=number_of_days)

    # Create a scheduled task to re-enable the Windows Update service
    try:
        scheduler = win32com.client.Dispatch("Schedule.Service")
        scheduler.Connect()

        root_folder = scheduler.GetFolder("\\")
        task_def = scheduler.NewTask(0)

        # Create a time-based trigger that fires at the specified date/time
        start_time = trigger_time.strftime("%Y-%m-%dT%H:%M:%S")
        trigger = task_def.Triggers.Create(
            win32com.client.constants.TASK_TRIGGER_TIME)
        trigger.StartBoundary = start_time
        trigger.Enabled = True

        # Define the action to restart the Windows Update service
        action = task_def.Actions.Create(
            win32com.client.constants.TASK_ACTION_EXEC)
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
    base_dir = "C:\\NexTool\\Updater\\PRE-SELECT"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    exe_destination = os.path.join(base_dir, "PatchMyPC.exe")
    ini_destination = os.path.join(base_dir, "PatchMyPC.ini")

    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/PRE-SELECT/PatchMyPC.exe",
        exe_destination,
    )
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/PRE-SELECT/PatchMyPC.ini",
        ini_destination,
    )

    subprocess.run([exe_destination, "/auto", "switch"], check=True)


def run_patchmypc_own_selections():
    base_dir = "C:\\NexTool\\Updater\\SELF-SELECT"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    exe_destination = os.path.join(base_dir, "PatchMyPC.exe")
    ini_destination = os.path.join(base_dir, "PatchMyPC.ini")

    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/SELF-SELECT/PatchMyPC.exe",
        exe_destination,
    )
    download_file(
        "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/SELF-SELECT/PatchMyPC.ini",
        ini_destination,
    )

    subprocess.run([exe_destination], check=True)


def install_choco_packages():
    response = msg_box(
        "Warning: This script will install a collection of hand-picked applications using Chocolatey. "
        "If you don't want to proceed, please consider another method to install applications. "
        "Do you want to continue?",
        "Chocolatey Installation Warning",
        4,
    )

    # If the user clicks 'No' in the MessageBox
    if response == 7:
        return

    progress_label.config(text="Preparing installations...")
    app.update()

    packages = [
        "googlechrome",
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
        "python3",
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
    total_packages = len(packages)
    installed_packages = []
    failed_packages = []

    if not is_chocolatey_installed():
        install_chocolatey()

    for index, package in enumerate(packages, start=1):
        progress_label.config(
            text=f"Installing {index} of {total_packages} applications: {package}"
        )
        progress_bar["value"] = (
            index / total_packages
        ) * 100  # Update progress bar value
        app.update()

        print(f"Attempting to install {package}...")

        try:
            subprocess.run(["choco", "install", package, "-y"], check=True)
            print(f"{package} installed successfully!")
            installed_packages.append(package)
        except subprocess.CalledProcessError:
            progress_label.config(text=f"Error installing {package}.")
            app.update()
            failed_packages.append(package)
        except Exception as e:
            progress_label.config(text=f"An unexpected error occurred: {e}")
            app.update()
            failed_packages.append(package)

    progress_label.config(text="Installations complete.")
    app.update()

    # Generate a log file on the user's desktop
    user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    log_file_path = os.path.join(user_desktop, "choco_installation_log.txt")

    with open(log_file_path, "w") as log_file:
        log_file.write("Chocolatey Installation Log\n")
        log_file.write("=" * 40 + "\n\n")

        log_file.write("Installed Packages:\n")
        for package in installed_packages:
            log_file.write(f"- {package}\n")

        log_file.write("\nFailed Packages:\n")
        for package in failed_packages:
            log_file.write(f"- {package}\n")

    print(
        f"Installation complete. A log file has been saved to: {log_file_path}")
    inform_about_choco_gui()


def is_chocolatey_installed():
    choco_path = os.path.join(os.environ["ProgramData"], "Chocolatey")
    return os.path.exists(choco_path)


def install_chocolatey():
    install_cmd = (
        "Set-ExecutionPolicy Bypass -Scope Process -Force; "
        "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
        "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    )
    subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", install_cmd],
        check=True,
    )


def inform_about_choco_gui():
    response = msg_box(
        "Installation process completed. If you wish to manage your applications in a GUI, "
        "consider using Chocolatey's GUI. Do you want to install and open Chocolatey GUI now?",
        "Chocolatey GUI Information",
        4,
    )

    if response == 6:  # If the user clicks 'Yes'
        run_chocolatey_gui()


def run_chocolatey_gui():
    try:
        print("Installing Chocolatey GUI...")
        subprocess.run(["choco", "install", "chocolateygui", "-y"], check=True)
        print("Chocolatey GUI installed successfully. Launching...")
        subprocess.run(
            ["chocolateygui"], check=True
        )  # Assuming 'chocolateygui' is the correct command to launch the GUI. Modify if needed.
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during installation or launch:\n{e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def install_adobe_reader():
    architecture = platform.architecture()[0]

    if architecture == "32bit":
        package_id = "Adobe.Acrobat.Reader.32-bit"
    elif architecture == "64bit":
        package_id = "Adobe.Acrobat.Reader.64-bit"
    else:
        print(
            f"Unknown system architecture: {architecture}. Cannot install Adobe Acrobat Reader."
        )
        return

    print(f"Installing Adobe Acrobat Reader for {architecture}...")
    try:
        subprocess.run(["winget", "install", "--id=" +
                       package_id, "-e"], check=True)
        print(
            f"Adobe Acrobat Reader for {architecture} installed successfully!")
    except subprocess.CalledProcessError:
        print(f"Error installing Adobe Acrobat Reader for {architecture}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def install_winget_packages():
    response = msg_box(
        "Warning: This script will install a collection of hand-picked applications using Winget. "
        "If you don't want to proceed, please use the Winget GUI which will be the next menu option in the GUI. "
        "Do you want to continue?",
        "Winget Installation Warning",
        4,
    )

    # If the user clicks 'No' in the MessageBox
    if response == 7:
        return

        # Before the loop:
    progress_label.config(text="Preparing installations...")
    app.update()

    install_adobe_reader()

    packages = [
        "Mozilla.Firefox",
        "VideoLAN.VLC",
        "7zip.7zip",
        "AnyDeskSoftwareGmbH.AnyDesk",
        "Twilio.Authy",
        "Gyan.FFmpeg.Shared",
        "Gyan.FFmpeg",
        "Google.Chrome",
        "Oracle.JavaRuntimeEnvironment",
        "Oracle.JDK.19",
        "Oracle.JDK.18",
        "Oracle.JDK.17",
        "CodecGuide.K-LiteCodecPack.Full",
        "Microsoft.DotNet.Runtime.3_1",
        "Microsoft.DotNet.Runtime.5",
        "Microsoft.DotNet.Runtime.6",
        "Microsoft.DotNet.Runtime.7",
        "Microsoft.DotNet.Runtime.Preview",
        "Microsoft.dotnet",
        "Microsoft.DotNet.DesktopRuntime.3_1",
        "Microsoft.DotNet.DesktopRuntime.5",
        "Microsoft.DotNet.DesktopRuntime.6",
        "Microsoft.DotNet.DesktopRuntime.7",
        "Microsoft.Edge",
        "Microsoft.VCRedist.2005.x86",
        "Microsoft.VCRedist.2005.x64",
        "Microsoft.VCRedist.2008.x64",
        "Microsoft.VCRedist.2008.x86",
        "Microsoft.VCRedist.2010.x64",
        "Microsoft.VCRedist.2010.x86",
        "Microsoft.VCRedist.2012.x64",
        "Microsoft.VCRedist.2012.x86",
        "Microsoft.VCRedist.2013.x64",
        "Microsoft.VCRedist.2013.x86",
        "Microsoft.VCRedist.2015+.x64",
        "Microsoft.VCRedist.2015+.x86",
        "Microsoft.dotnetRuntime.3-x64",
        "Microsoft.dotnetRuntime.3-x86",
        "Microsoft.dotnetRuntime.5-x64",
        "Microsoft.dotnetRuntime.5-x86",
        "Microsoft.dotnetRuntime.6-x64",
        "Microsoft.dotnetRuntime.6-x86",
        "Microsoft.XNARedist",
        "Nvidia.PhysX",
        "Microsoft.PowerShell",
        "Python.Python.3.11",
        "VinaySajip.PythonLauncher",
        "qBittorrent.qBittorrent",
        "Ookla.Speedtest.CLI",
        "Ookla.Speedtest.Desktop",
        "TeamViewer.TeamViewer",
        "ClockworkMod.UniversalADBDriver",
        "WinSCP.WinSCP",
    ]
    total_packages = len(packages)
    installed_packages = []
    failed_packages = []

    for index, package in enumerate(packages, start=1):
        progress_label.config(
            text=f"Installing {index} of {total_packages} applications: {package}"
        )
        progress_bar["value"] = (
            index / total_packages
        ) * 100  # Update progress bar value
        app.update()  # This will update the GUI for each iteration

        print(f"Attempting to install {package}...")

        try:
            subprocess.run(["winget", "install", "--id=" +
                           package, "-e"], check=True)
            print(f"{package} installed successfully!")
            installed_packages.append(package)
        except subprocess.CalledProcessError:
            progress_label.config(text=f"Error installing {package}.")
            app.update()
            failed_packages.append(package)
        except Exception as e:
            progress_label.config(text=f"An unexpected error occurred: {e}")
            app.update()
            failed_packages.append(package)

    progress_label.config(text="Installations complete.")
    app.update()

    # Generate a log file on the user's desktop
    user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    log_file_path = os.path.join(user_desktop, "winget_installation_log.txt")

    with open(log_file_path, "w") as log_file:
        log_file.write("Winget Installation Log\n")
        log_file.write("=" * 40 + "\n\n")

        log_file.write("Installed Packages:\n")
        for package in installed_packages:
            log_file.write(f"- {package}\n")

        log_file.write("\nFailed Packages:\n")
        for package in failed_packages:
            log_file.write(f"- {package}\n")

    print(
        f"Installation complete. A log file has been saved to: {log_file_path}")
    # Inform the user about the Winget GUI
    inform_about_winget_gui()


def inform_about_winget_gui():
    response = msg_box(
        "Installation process completed. If you wish to install or update other applications, "
        "or manage your existing installations, consider using the Winget GUI which offers a user-friendly interface "
        "with features such as updates, installation tracking, and more. Do you want to install and open Winget GUI now?",
        "Winget GUI Information",
        4,
    )

    if response == 6:  # If the user clicks 'Yes'
        run_winget_gui()  # This will attempt to install the WingetUI Store if it's not already
        print_to_terminal("Winget GUI installed successfully.")


def run_winget_gui():
    try:
        # Install the WingetUI Store
        subprocess.run(
            ["winget", "install", "-e", "--id", "SomePythonThings.WingetUIStore"],
            check=True,
        )
        print(f"WingetUI Store installed successfully.")

        # Launch the WingetUI
        subprocess.run(
            ["WingetUI"], check=True
        )  # replace "WingetUI" with the actual command or path to the executable
        print(f"WingetUI Store launched successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred during installation or launch:\n{e.stderr}")
    except Exception as e:
        print(f"Error occurred: {e}")


def run_driver_updater():
    print_to_terminal("RUNNING DRIVER UPDATER...")
    try:
        # Setting base directory and paths
        base_dir = "C:\\NexTool\\Updater"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Download the Snappy Driver zip file
        snappy_zip_path = os.path.join(base_dir, "SNAPPY_DRIVER.zip")
        snappy_extract_path = os.path.join(base_dir, "SNAPPY_DRIVER")

        download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SNAPPY_DRIVER.zip",
            snappy_zip_path,
        )

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


def download_and_setup_office():
    print_to_terminal("INITIATING OFFICE TOOL PLUS SETUP...")

    try:
        # Determine system architecture
        arch = platform.architecture()[0]
        if arch == "64bit":
            architecture = "64"
        elif arch == "32bit":
            architecture = "32"
        else:
            print_to_terminal(f"Unsupported architecture: {arch}")
            return

        # Fetch the correct URL from TRUSTED_URLS based on architecture
        url = TRUSTED_URLS.get(architecture)
        if not url:
            print_to_terminal("Invalid architecture specified.")
            return

        # Setting base directory and paths
        office_dir = os.path.join(BASE_DIR, f"Office_Tool_{architecture}")
        if not os.path.exists(office_dir):
            os.makedirs(office_dir)

        destination_zip = os.path.join(office_dir, "Office_Tool.zip")
        destination_folder = office_dir
        destination_xml = os.path.join(office_dir, "office_config.xml")

        # Download
        print_to_terminal("Attempting to download Office Tool Plus...")
        download_file(url, destination_zip)
        print_to_terminal("Downloaded Office Tool Plus.")

        # Extract
        print_to_terminal("Attempting to extract Office Tool Plus...")
        with zipfile.ZipFile(destination_zip, "r") as zip_ref:
            zip_ref.extractall(destination_folder)
        print_to_terminal("Extracted Office Tool Plus.")

        # Create XML
        create_office_config(architecture, destination_xml)

        # Show popup
        message = (
            f"The Office Tool Plus (x{architecture}) has been set up at {destination_folder}."
            "\n\nAn XML configuration preset is available for you to import, making the setup process easier."
            "\n\nYou can find the import option under the 'Deploy Office' menu. Navigate to the 'Deploy' main menu, select the dropdown, and choose 'import configuration'."
        )

        messagebox.showinfo("Office Setup", message)

        # Execute Office Tool Plus with XML configuration
        otp_exe_path = os.path.join(
            destination_folder, "Office Tool", "Office Tool Plus.exe"
        )
        subprocess.run([otp_exe_path, "-xml", destination_xml], check=True)
        print_to_terminal("Office Tool Plus launched with XML configuration!")

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


# Services, Startup and Tasks Manager
RECOMMENDED_DISABLE = [
    "bits", "BDESVC", "BcastDVRUserService_7c360", "GoogleChromeElevationService",
    "gupdate", "gupdatem", "vmickvpexchange", "vmicguestinterface", "vmicshutdown"
]


def list_all_services():
    command = ["sc", "query", "type=", "service"]
    output = subprocess.check_output(command, text=True).splitlines()
    services = [line.split(":")[1].strip()
                for line in output if "SERVICE_NAME" in line]
    return services


def backup_services():
    services = list_all_services()
    service_status = {}
    for service in services:
        status_cmd = ["sc", "qc", service]
        status_output = subprocess.check_output(
            status_cmd, text=True).splitlines()
        status = [line.split(":", 1)[1].strip()
                  for line in status_output if "START_TYPE" in line][0]
        service_status[service] = status

    with open("backup_services.json", "w") as file:
        json.dump(service_status, file)


def restore_services():
    with open("backup_services.json", "r") as file:
        backup_statuses = json.load(file)

    for service, status in backup_statuses.items():
        set_service_start_type(service, status)


def get_service_start_type(service):
    status_cmd = ["sc", "qc", service]
    status_output = subprocess.check_output(status_cmd, text=True).splitlines()
    status = [line.split(":", 1)[1].strip()
              for line in status_output if "START_TYPE" in line]
    return status[0] if status else None


def set_service_start_type(service, start_type):
    subprocess.run(
        ["sc", "config", service, f"start= {start_type}"], text=True)


def control_service(service, action):
    if action in ["start", "stop", "pause", "continue"]:
        result = subprocess.run(["sc", action, service],
                                capture_output=True, text=True)
    elif action in ["auto", "demand", "disabled"]:
        result = subprocess.run(
            ["sc", "config", service, f"start= {action}"], capture_output=True, text=True)
    else:
        return f"Invalid action: {action}"

    output = result.stdout + result.stderr
    if "Access is denied" in output:
        return f"Cannot control '{service}' due to system restrictions."
    elif "Pending" in output:
        return f"Changes to '{service}' will take effect after system restart."
    elif "FAILED" in output:
        return f"Failed to perform action '{action}' on '{service}'."
    else:
        return f"Successfully performed action '{action}' on '{service}'."


def disable_recommended_services():
    results = []
    for service in RECOMMENDED_DISABLE:
        result = control_service(service, "disabled")
        results.append(result)
    return results


def disable_selected_services(service_list):
    results = []
    for service in service_list:
        result = control_service(service, "disabled")
        results.append(result)
    return results


def list_startup_applications():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    startup_apps = {}
    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ) as key:
        index = 0
        while True:
            try:
                name, value, _ = reg.EnumValue(key, index)
                startup_apps[name] = value
                index += 1
            except WindowsError:
                break
    return startup_apps


def add_startup_application(name, path):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as key:
        reg.SetValueEx(key, name, 0, reg.REG_SZ, path)


def remove_startup_application(name):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as key:
        reg.DeleteValue(key, name)


def list_scheduled_tasks():
    tasks = subprocess.check_output(
        ["schtasks", "/query", "/fo", "LIST"]).decode()
    return tasks


def create_scheduled_task(name, command, time="12:00", frequency="daily"):
    subprocess.run(["schtasks", "/create", "/sc", frequency,
                   "/tn", name, "/tr", command, "/st", time])


def delete_scheduled_task(name):
    subprocess.run(["schtasks", "/delete", "/tn", name, "/f"])


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
        "Winget Pre-Set Selections": lambda: run_winget_check("pre_set_selections"),
        "Winget GUI": lambda: run_winget_check("gui"),
        "Driver Updater": run_winget_check,
        "Office Installations": download_and_setup_office,
    }
    print(f"Button Action Called for: {sub_item}")  # Debug print
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
        main_button.grid(row=idx, column=0, sticky="nsew", padx=10, pady=5)
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
    back_button.grid(row=len(sub_items), column=0,
                     sticky="ew", padx=10, pady=10)


def show_sub_sub_menu(main_item, sub_category):
    for child in left_frame.winfo_children():
        child.grid_forget()

    sub_sub_items = tabs[main_item][sub_category]
    for idx, sub_sub_item in enumerate(sub_sub_items):
        sub_sub_button = ttk.Button(
            left_frame,
            text=sub_sub_item,
            command=lambda sub_sub_item=sub_sub_item: button_action(
                sub_sub_item),
        )
        sub_sub_button.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)

    back_button = ttk.Button(
        left_frame,
        text=f"Back to {main_item}",
        command=lambda: show_sub_menu(main_item),
    )
    back_button.grid(row=len(sub_sub_items), column=0,
                     sticky="ew", padx=10, pady=10)


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
    # This is added based on your 'tabs' structure.
    "Additional Tool": "Access more tools to enhance your system.",
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
left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# Creating right frame for the terminal
right_frame = ttk.Frame(app)
right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=3)
app.grid_rowconfigure(0, weight=1)

# Embedded Terminal
terminal = scrolledtext.ScrolledText(
    right_frame,
    undo=True,
    wrap=tk.WORD,
    bg="black",
    fg="white",
    font=("Consolas", 12),
    width=80,
    height=15,  # Adjust width and height values as needed
)
terminal.pack(fill="both", expand=True, padx=10, pady=10)

# Create a global progress bar
progress_frame = tk.Frame(right_frame)
progress_frame.pack(pady=10)
progress_label = ttk.Label(right_frame, text="", font=("Consolas", 12))
progress_label.pack(pady=5)
progress_bar = ttk.Progressbar(
    progress_frame, orient=tk.HORIZONTAL, length=300, mode="determinate"
)
progress_bar.pack()

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

info_text = "\n".join(
    [f"{key}: {value}" for key, value in system_info.items()])
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
        "Services Management",
        "Startup Applications",
        "Scheduled Tasks",
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
