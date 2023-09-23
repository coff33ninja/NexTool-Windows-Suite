import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk
from datetime import datetime
from tkinter import simpledialog
import psutil
import platform
import wmi
import urllib.request
import webbrowser
from tkinter import messagebox
import os
import subprocess
import sys

app = ThemedTk(theme="arc")
app.title("AIO TOOLBOX ARIA VERSION")
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
        # Set Windows Defender's real-time monitoring to disabled
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

        # Downloading and executing the script to disable Windows Defender
        defender_script_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/disable-windows-defender.ps1"
        destination = "C:\\NexTool\\disable-windows-defender.ps1"

        # Use the download_file method to download the PowerShell script
        download_file(defender_script_url, destination)

        subprocess.run(
            ["Powershell", "-ExecutionPolicy", "Bypass", "-File", destination],
            check=True,
        )

        # Other commands...

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
        ToolTip(main_button, text=tabs_tooltips[main_item])  # Add this line


# Function to show sub-menus based on the main menu item
def show_sub_menu(main_item):
    for child in left_frame.winfo_children():
        child.grid_forget()

    sub_items = tabs[main_item]
    for idx, sub_item in enumerate(sub_items):
        sub_button = ttk.Button(
            left_frame,
            text=sub_item,
            command=lambda sub_item=sub_item: button_action(sub_item),
        )
        sub_button.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)
        if sub_item in sub_tooltips:  # Ensure there's a tooltip for the sub-item
            ToolTip(sub_button, text=sub_tooltips[sub_item])

    back_button = ttk.Button(
        left_frame, text="Back to Main Menu", command=show_main_menu
    )
    back_button.grid(row=len(sub_items), column=0, sticky="ew", padx=10, pady=10)


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
    "System": "View core system information and statuses.",
    "Configuration": "Modify key settings and configurations for the system.",
    "Software Management": "Manage software installations, updates, and related settings.",
    "Maintenance": "Carry out routine maintenance tasks to keep the system optimized.",
    "Advanced": "Advanced features and utilities for power users.",
    "Extras": "Additional features or functionalities not covered by the above categories.",
    "Shutdown Options": "Options to restart, shut down, or sign out of the computer.",
}

# Sub Menu Tooltips
sub_tooltips = {
    "Basic Computer Report": "Generate a basic informational report of your computer configuration. This will provide a quick overview of system details.",
    "Advanced Hardware Info": "View detailed hardware information using the HWINFO32 third-party application. This will provide an in-depth analysis of your device's hardware and system resources.",
    "Network Setup": "Configure network settings and connections.",
    "Defender Toolbox": "Manage and configure Windows Defender settings.",
    "Telemetry": "Control telemetry and data collection settings for Windows.",
    "Microsoft Activation": "Manage the activation status of your Windows installation.",
    "Windows Update": "Manage and apply Windows updates.",
    "Windows Update Pauser": "Pause automatic Windows updates for a certain period.",
    "Software Updater": "Update installed software to the latest versions.",
    "Driver Updater": "Update system drivers to the latest available versions.",
    "Office Installations": "Install or manage Microsoft Office installations.",
    "Disk Cleanup": "Clean unnecessary files from your storage drives.",
    "Disk Defragment": "Optimize and defragment your storage drives.",
    "Disk Check": "Check your storage drives for errors.",
    "Backupper": "Backup important system and user files.",
    "Windows Install": "Facilitate and manage Windows installations.",
    "DISM and SFC Windows Repair": "Repair corrupted Windows system files.",
    "Windows Debloater": "Remove unnecessary pre-installed Windows software.",
    "Group Policy Reset": "Reset all group policies to default settings.",
    "WMI Reset": "Reset the Windows Management Instrumentation service.",
    "Disable Specific Services": "Manage and disable specific Windows services as needed.",
    "Services Manager": "Comprehensive manager for all system services.",
    "Restart": "Restart the computer.",
    "Restart and Re-register": "Restart the computer and re-register its details.",
    "Restart to UEFI/BIOS": "Restart the computer directly to its UEFI/BIOS.",
    "Restart and Load Advanced Boot Options": "Restart the computer to the advanced boot options menu.",
    "Shutdown": "Completely turn off the computer.",
    "Shutdown and Re-register": "Turn off the computer and re-register its details.",
    "Sign Out": "Sign out of the current user profile.",
}

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
    "Configuration": [
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
        "Disable Windows Defender",
        "Remove Windows Defender",
        "Additional Tool",
        "Block Telemetry",
        "Microsoft Activation Script",
    ],
    "Software Management": [
        "Windows Update",
        "Windows Update Pauser",
        "Software Updater",
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
