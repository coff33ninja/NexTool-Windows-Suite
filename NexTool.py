import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ttkthemes import ThemedTk
from datetime import datetime
import psutil
import platform
import wmi
import urllib.request
import webbrowser
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


def button_action(sub_item):
    function_mapping = {
        "Basic Computer Report": run_quick_info,
        "Advanced Hardware Info": run_hwinfo32,
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
        "Network Setup",
        "Defender Toolbox",
        "Telemetry",
        "Microsoft Activation",
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
