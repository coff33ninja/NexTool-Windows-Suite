import sys
import os
import subprocess
import platform
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QHBoxLayout,
    QListWidget,
    QProgressBar,
    QGraphicsOpacityEffect,
    QStackedLayout,
    QAction,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QDialog,
    QLabel,
    QComboBox,
    QCheckBox,
    QTabWidget,
    QWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
)
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import (
    Qt,
    QPropertyAnimation,
    QRect,
    QEasingCurve,
    QThread,
    pyqtSignal,
    pyqtSlot,
    QObject,
    QTimer,
    QItemSelectionModel,
    pyqtSignal,
    QThread,
    QUrl,
)

# from PyQt5.QtGui import QGraphicsOpacityEffect
import logging
import traceback
import psutil
import datetime
import re
from typing import Any, Union, Dict, List
from functools import partial
import json
import winreg as reg
import urllib.request
import zipfile
import win32serviceutil
import win32api
import win32con
import win32com.client
import win32service


def is_admin():
    try:
        # Attempt to read the system file which is only readable by admin
        with open(
            os.path.join(os.environ["SystemRoot"], "system32", "config", "system"), "r"
        ):
            return True
    except PermissionError:
        return False


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.error("Error Caught: " + tb)  # Logging the error
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = excepthook


def get_system_information() -> Dict[str, Any]:
    def get_memory_details():
        details = {}
        commands = {
            "capacity": "wmic memorychip get devicelocator, capacity",
            "memorytype": "wmic memorychip get devicelocator, memorytype",
            "speed": "wmic memorychip get devicelocator, speed",
            "partnumber": "wmic memorychip get devicelocator, partnumber",
        }

        for key, command in commands.items():
            try:
                output = (
                    subprocess.check_output(command, stderr=subprocess.DEVNULL)
                    .decode("utf-8")
                    .split("\n")[1:]
                )
                details[key] = [line.strip() for line in output if line.strip()]
            except subprocess.CalledProcessError:
                details[key] = []

        return details

    info = {}

    # CPU details
    if platform.system() == "Windows":
        # Using wmic command to fetch CPU name
        cpu_name = (
            subprocess.check_output("wmic cpu get Name", stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
            .split("\n")[1]
        )
    else:
        cpu_name = platform.processor()

    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq().max
    cpu_info = (
        f"{cpu_name} @ {cpu_freq:.2f}GHz, Cores: {cpu_cores}, Threads: {cpu_threads}"
    )
    info["CPU Info"] = cpu_info

    # Disk Usage
    disk = psutil.disk_usage("/")
    hdd_ssd_usage = f"Total: {disk.total / (1024**3):.2f} GB, Used: {disk.used / (1024**3):.2f} GB, Free: {disk.free / (1024**3):.2f} GB, Percent Used: {disk.percent}%"
    info["Disk Info"] = hdd_ssd_usage

    # Network Info
    network_info = {}
    for interface, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == psutil.AF_LINK:
                continue
            network_info[interface] = address.address
    info["Network Adapters"] = network_info

    # System Uptime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    current_time = datetime.datetime.now()
    uptime = current_time - boot_time
    info["System Uptime"] = str(uptime).split(".")[0]

    # Current Logged-in Users
    users = [user.name for user in psutil.users()]
    info["Logged-in Users"] = ", ".join(users)

    # Battery Information
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
        if battery:
            info["Battery"] = {
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "secsleft": battery.secsleft,
            }

    # Disk Partitions
    partitions = psutil.disk_partitions()
    disk_partitions = {}
    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_partitions[part.device] = {
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total / (1024**3),
                "used": usage.used / (1024**3),
                "free": usage.free / (1024**3),
                "percent_used": usage.percent,
            }
        except PermissionError:
            # You can either log the error, ignore, or handle in a way you see fit
            print(f"PermissionError: Could not access {part.device}")

    # RAM details
    try:
        ram_type = {
            "0": "Unknown",
            "1": "Other",
            "2": "DRAM",
            "3": "Synchronous DRAM",
            "4": "Cache DRAM",
            "5": "EDO",
            "6": "EDRAM",
            "7": "VRAM",
            "8": "SRAM",
            "9": "RAM",
            "10": "ROM",
            "11": "Flash",
            "12": "EEPROM",
            "13": "FEPROM",
            "14": "EPROM",
            "15": "CDRAM",
            "16": "3DRAM",
            "17": "SDRAM",
            "18": "SGRAM",
            "19": "RDRAM",
            "20": "DDR",
            "21": "DDR2",
            "22": "DDR2 FB-DIMM",
            "24": "DDR3",
            "25": "FBD2",
            "26": "DDR4",
            "27": "DDR5",
        }
        ram_details_dict = get_memory_details()
        ram_details = []
        ram_total = 0

        for capacity, mem_type, speed in zip(
            ram_details_dict["capacity"],
            ram_details_dict["memorytype"],
            ram_details_dict["speed"],
        ):
            try:
                # Split by spaces and get the desired values
                capacity_parts = capacity.split()
                capacity_value = int(capacity_parts[0])

                mem_type_parts = mem_type.split()
                memory_type_value = mem_type_parts[1]  # Adjusted index

                speed_parts = speed.split()
                speed_mhz = speed_parts[1]  # Adjusted index

                capacity_gb = round(capacity_value / (1024**3), 2)
                ram_total += capacity_gb

                type_description = ram_type.get(memory_type_value, "Unknown")
                ram_details.append(
                    f"{capacity_gb}GB {type_description} @ {speed_mhz}MHz"
                )

            except ValueError as e:
                print(f"Error processing capacity: {capacity} -> {str(e)}")
                continue

        ram_info = {
            "Total GB": ram_total,
            "Details": ram_details,
            "Percent Used": psutil.virtual_memory().percent,
        }
        info["RAM Info"] = ram_info

        # Motherboard and BIOS details
        motherboard = (
            subprocess.check_output(
                "wmic baseboard get product", stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .split("\n")[-1]
        )

        manufacturer = (
            subprocess.check_output(
                "wmic baseboard get manufacturer", stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .split("\n")[-1]
        )

        bios_version = (
            subprocess.check_output(
                "wmic bios get smbiosbiosversion", stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .split("\n")[-1]
        )

        bios_date = (
            subprocess.check_output(
                "wmic bios get releasedate", stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .split("\n")[-1]
        )

        bios_serial = (
            subprocess.check_output(
                "wmic bios get serialnumber", stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
            .split("\n")[-1]
        )

        info["Motherboard"] = motherboard
        info["Manufacturer"] = manufacturer
        info["BIOS Version and Date"] = f"{bios_version} ({bios_date})"
        info["BIOS Serial Number"] = bios_serial

        # Graphics Card
        graphics_card = (
            subprocess.check_output(
                "wmic path win32_videocontroller get name",
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
            .split("\n")[-1]
        )

        info["Graphics Card"] = graphics_card

    except Exception as e:
        print(f"Error while fetching system info: {e}")

    return info


def consolidate_info(info: Dict[str, Any]) -> str:
    try:
        # Motherboard information
        manufacturer = info.get("Manufacturer", "N/A")
        motherboard_info = f"{manufacturer} {info.get('Motherboard', 'N/A')}"

        # CPU information
        cpu = info.get("CPU Info", "N/A")

        # RAM information
        ram_info = info.get("RAM Info", {})
        ram_total = ram_info.get("Total GB", "N/A")
        ram_details_list = ram_info.get("Details", [])

        # Construct a readable representation of each RAM stick
        ram_stick_details = "\n".join(ram_details_list)
        ram_details = f"Total: {ram_total}GB\n{ram_stick_details}"

        # GPU information
        gpu = info.get("Graphics Card", "N/A")

        # HDD/SSD information
        hdd_ssd = info.get("Disk Info", "N/A")

        # Network information
        network_adapters = info.get("Network Adapters", {})
        network_details = "\n".join(
            [f"   {k}: {v}" for k, v in network_adapters.items()]
        )

        # Uptime information
        uptime = info.get("System Uptime", "N/A")

        # Consolidating all information
        consolidated = (
            f"System Information:\n"
            f"----------------------\n"
            f"Motherboard: {motherboard_info}\n"
            f"CPU: {cpu}\n"
            f"RAM:\n{ram_details}\n"
            f"GPU: {gpu}\n"
            f"Storage: {hdd_ssd}\n"
            f"Network Adapters:\n{network_details}\n"
            f"Uptime: {uptime}"
        )

        return consolidated

    except Exception as e:
        print(f"Error while consolidating info: {e}")
        return ""


def is_dark_mode():
    if platform.system() == "Windows":  # For Windows
        try:
            # The registry key that indicates dark mode for apps
            reg_key = r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            reg_value = "AppsUseLightTheme"  # 0 means dark mode
            output = subprocess.check_output(
                ["reg", "query", reg_key, "/v", reg_value], stderr=subprocess.DEVNULL
            ).decode("utf-8")
            if "0x0" in output:  # Indicates dark mode
                return True
        except subprocess.CalledProcessError:
            return False
    return False  # Default to light theme


DARK_STYLE = """
QMainWindow {
    background-color: #333;
}
QListWidget, QPushButton, QTextEdit, QProgressBar {
    background-color: #444;
    color: #fff;
}
QListWidget::item {
    padding: 8px 16px;
}
QListWidget::item:selected {
    background-color: #555;
}
QPushButton:hover {
    background-color: #555;
}
QPushButton:pressed {
    background-color: #666;
}
QTextEdit {
    border: 2px solid #888;
    border-radius: 5px;
}
QProgressBar {
    background-color: #444;
    border: none;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #007ACC;
}
"""

LIGHT_STYLE = """
QMainWindow {
    background-color: #F5F5F5;
}
QListWidget, QPushButton, QTextEdit, QProgressBar {
    background-color: #FFFFFF;
    color: #555555;
}
QListWidget::item {
    padding: 8px 16px;
}
QListWidget::item:selected {
    background-color: #E1E1E1;
}
QPushButton:hover {
    background-color: #E1E1E1;
}
QPushButton:pressed {
    background-color: #C7C7C7;
}
QTextEdit {
    border: 2px solid #AAAAAA;
    border-radius: 5px;
}
QProgressBar {
    background-color: #FFFFFF;
    border: none;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #007ACC;
}
"""


class ManualConfigDialog(QDialog):
    def __init__(self, adapter_name: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Fetch current configurations
        current_configs = self.get_current_config(adapter_name)

        self.ip_input = QLineEdit(self)
        self.ip_input.setPlaceholderText(
            f"Current: {current_configs.get('IP Address', 'N/A')}"
        )
        layout.addWidget(QLabel("Enter IP Address:"))
        layout.addWidget(self.ip_input)

        self.subnet_mask_input = QLineEdit(self)
        self.subnet_mask_input.setPlaceholderText(
            f"Current: {current_configs.get('Subnet Mask', 'N/A')}"
        )
        layout.addWidget(QLabel("Enter Subnet Mask:"))
        layout.addWidget(self.subnet_mask_input)

        self.gateway_input = QLineEdit(self)
        self.gateway_input.setPlaceholderText(
            f"Current: {current_configs.get('Gateway', 'N/A')}"
        )
        layout.addWidget(QLabel("Enter Default Gateway (optional):"))
        layout.addWidget(self.gateway_input)

        self.dns_primary_input = QLineEdit(self)
        self.dns_primary_input.setPlaceholderText(
            f"Current: {current_configs.get('Primary DNS', 'N/A')}"
        )
        layout.addWidget(QLabel("Enter Primary DNS Server (optional):"))
        layout.addWidget(self.dns_primary_input)

        self.dns_secondary_input = QLineEdit(self)
        self.dns_secondary_input.setPlaceholderText(
            f"Current: {current_configs.get('Secondary DNS', 'N/A')}"
        )
        layout.addWidget(QLabel("Enter Secondary DNS Server (optional):"))
        layout.addWidget(self.dns_secondary_input)

        button_layout = QHBoxLayout()

        ok_button = QPushButton("Ok", self)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def get_current_config(self, adapter_name: str) -> dict:
        """Fetch current network configurations for the given adapter."""
        try:
            output = subprocess.check_output(
                ["netsh", "interface", "ipv4", "show", "config", f"name={adapter_name}"]
            ).decode()

            # Use regex to extract configurations
            ip_address = re.search(r"IP Address:\s+(\d+\.\d+\.\d+\.\d+)", output)
            subnet_mask = re.search(r"Subnet Prefix:\s+(\d+\.\d+\.\d+\.\d+)", output)
            gateway = re.search(r"Default Gateway:\s+(\d+\.\d+\.\d+\.\d+)", output)
            dns_primary = re.search(
                r"Statically Configured DNS Servers:\s+(\d+\.\d+\.\d+\.\d+)", output
            )
            dns_secondary = re.search(
                r"\n\s+(\d+\.\d+\.\d+\.\d+)",
                dns_primary.group(0) if dns_primary else "",
            )

            return {
                "IP Address": ip_address.group(1) if ip_address else "Not Found",
                "Subnet Mask": subnet_mask.group(1) if subnet_mask else "Not Found",
                "Gateway": gateway.group(1) if gateway else "Not Found",
                "Primary DNS": dns_primary.group(1) if dns_primary else "Not Found",
                "Secondary DNS": dns_secondary.group(1)
                if dns_secondary
                else "Not Found",
            }
        except Exception as e:
            return {
                "IP Address": "Error",
                "Subnet Mask": "Error",
                "Gateway": "Error",
                "Primary DNS": "Error",
                "Secondary DNS": "Error",
            }


class PingResultsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # ComboBox with common hosts and IP addresses
        self.host_combobox = QComboBox(self)
        common_hosts = ["8.8.8.8", "8.8.4.4", "www.google.com", "www.yahoo.com"]
        self.host_combobox.addItems(common_hosts)
        self.host_combobox.setEditable(True)  # Allow custom text input

        layout.addWidget(QLabel("Enter IP Address or Hostname:"))
        layout.addWidget(self.host_combobox)

        self.start_button = QPushButton("Start Pinging", self)
        self.start_button.clicked.connect(self.perform_ping)
        layout.addWidget(self.start_button)

        self.terminal_output = QTextEdit(self)
        layout.addWidget(self.terminal_output)
        self.setWindowTitle("Ping Results")
        self.resize(500, 400)

        self.stop_button = QPushButton("Stop Pinging", self)
        layout.addWidget(self.stop_button)

        # QTimer for continuous ping
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.perform_ping)

        self.stop_button.clicked.connect(self.stop_pinging)

    def perform_ping(self):
        host = self.host_combobox.currentText().strip()
        if not host:
            self.terminal_output.append("No input provided. Please provide a host.")
            return

        self.start_button.setDisabled(True)  # Disable start button after clicking
        self.terminal_output.clear()  # Clear terminal for new ping results

        try:
            response = subprocess.run(
                ["ping", "-n", "1", host], capture_output=True, text=True, timeout=10
            )
            self.timer.start(1000)
            self.terminal_output.append(response.stdout)
            if response.returncode != 0:
                self.terminal_output.append("Ping operation failed.")
        except Exception as e:
            self.terminal_output.append(f"Error occurred: {e}")

    def stop_pinging(self):
        self.timer.stop()
        self.start_button.setEnabled(True)  # Enable start button after stopping
        try:
            # Save the results to the desktop
            with open(os.path.expanduser("~/Desktop/ping_results.txt"), "w") as file:
                file.write(self.terminal_output.toPlainText())
                file.flush()
                os.fsync(file.fileno())
        except Exception as e:
            # Let's print out any exception that occurs to help diagnose the issue
            print(f"Error writing to file: {e}")
        self.accept()


class TracerouteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Combobox and line edit for hosts
        self.host_combobox = QComboBox(self)
        self.host_combobox.setEditable(True)
        # If you have predefined hosts, add them here
        predefined_hosts = ["8.8.8.8", "8.8.4.4"]  # Example
        self.host_combobox.addItems(predefined_hosts)
        layout.addWidget(QLabel("Select or enter IP Address/Hostname:"))
        layout.addWidget(self.host_combobox)

        self.start_button = QPushButton("Start Traceroute", self)
        self.start_button.clicked.connect(self.perform_traceroute)
        layout.addWidget(self.start_button)

        self.terminal_output = QTextEdit(self)
        layout.addWidget(self.terminal_output)
        self.setWindowTitle("Traceroute Results")
        self.resize(500, 400)

        self.stop_button = QPushButton("Stop Traceroute", self)
        layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_traceroute)

    def perform_traceroute(self):
        host = self.host_combobox.currentText().strip()
        if not host:
            self.terminal_output.append("No input provided. Please provide a host.")
            return

        self.terminal_output.append(f"Tracing route to {host}...\n")
        try:
            output = subprocess.run(
                ["tracert", "-d", "-h", "64", host],
                text=True,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,  # Ensure stdout is captured
                shell=True,  # Execute the command in a shell
            )
            if output.returncode != 0:
                self.terminal_output.append("Traceroute operation failed.")
                self.terminal_output.append(output.stderr)
            else:
                self.terminal_output.append(output.stdout)
        except Exception as e:
            self.terminal_output.append(f"Error occurred: {e}")

    def stop_traceroute(self):
        try:
            # Save the results to the desktop
            with open(
                os.path.expanduser("~/Desktop/traceroute_results.txt"), "w"
            ) as file:
                file.write(self.terminal_output.toPlainText())
        except Exception as e:
            # Let's print out any exception that occurs to help diagnose the issue
            self.terminal_output.append(f"Error writing to file: {e}")
        self.accept()


class NetworkShareDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Button to show current shares
        self.show_shares_button = QPushButton("Show Current Shares", self)
        layout.addWidget(self.show_shares_button)
        self.show_shares_button.clicked.connect(self.show_current_shares)

        # Drive letter
        self.drive_letter_input = QLineEdit(self)
        layout.addWidget(QLabel("Drive Letter:"))
        layout.addWidget(self.drive_letter_input)

        # Computer Name / IP
        self.computer_name_input = QLineEdit(self)
        layout.addWidget(QLabel("Computer Name/IP:"))
        layout.addWidget(self.computer_name_input)

        # Share name
        self.share_name_input = QLineEdit(self)
        layout.addWidget(QLabel("Share Name:"))
        layout.addWidget(self.share_name_input)

        # Persistent
        self.persistent_checkbox = QCheckBox("Persistent", self)
        layout.addWidget(self.persistent_checkbox)

        # Username
        self.username_input = QLineEdit(self)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)

        # Button to set up network share
        self.setup_button = QPushButton("Set Up Network Share", self)
        layout.addWidget(self.setup_button)
        self.setup_button.clicked.connect(self.setup_share)

        # Button to remove a network share
        self.remove_button = QPushButton("Remove Network Share", self)
        layout.addWidget(self.remove_button)
        self.remove_button.clicked.connect(self.remove_network_map)

        self.setWindowTitle("Network Share Setup")
        self.resize(400, 300)

    def show_current_shares(self):
        result = subprocess.run(["net", "use"], capture_output=True, text=True)

        shares = []
        lines = result.stdout.splitlines()
        for line in lines[4:]:
            parts = line.split()
            if len(parts) >= 2 and parts[1].endswith(":"):
                status = "Available" if parts[2] == "OK" else parts[2]
                shares.append((parts[1], status))

        shares_text = "\n".join(
            [f"Drive: {share[0]} - Status: {share[1]}" for share in shares]
        )
        QMessageBox.information(self, "Current Network Shares", shares_text)

    def setup_share(self):
        drive_letter = self.drive_letter_input.text().strip()
        computer_name = self.computer_name_input.text().strip()
        share_name = self.share_name_input.text().strip()
        persistent = "YES" if self.persistent_checkbox.isChecked() else "NO"
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        cmd_str = f"net use {drive_letter}: \\\\{computer_name}\\{share_name} /user:{username} {password} /PERSISTENT:{persistent}"

        try:
            subprocess.run(
                cmd_str, shell=True, check=True, capture_output=True, text=True
            )
            QMessageBox.information(
                self,
                "Success",
                f"Successfully mapped drive {drive_letter}: to {computer_name}\\{share_name}",
            )
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Error", f"Error occurred: {e.stdout}")

        self.accept()

    def remove_network_map(self):
        drive_letter, okPressed = QInputDialog.getText(
            self, "Input", "ENTER MAPPED DRIVE LETTER TO REMOVE:"
        )
        if okPressed:
            try:
                subprocess.run(
                    ["net", "use", f"{drive_letter}:", "/delete"], check=True
                )
                QMessageBox.information(
                    self,
                    "Success",
                    f"{drive_letter}: drive mapping removed successfully.",
                )
            except subprocess.CalledProcessError:
                QMessageBox.warning(
                    self, "Error", f"Failed to remove {drive_letter}: drive mapping."
                )


class WifiPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Button to extract passwords
        self.extract_button = QPushButton("Fetch WiFi Passwords", self)
        self.extract_button.clicked.connect(self.wifi_password_extract)
        layout.addWidget(self.extract_button)

        # Results
        self.results_output = QTextEdit(self)
        layout.addWidget(QLabel("WiFi Details:"))
        layout.addWidget(self.results_output)

        # Window properties
        self.setWindowTitle("WiFi Password Extraction")
        self.resize(400, 500)

    def wifi_password_extract(self):
        self.results_output.append(
            "This section will display all registered WIFI networks on this device."
        )

        # Show registered Wi-Fi networks
        try:
            result = subprocess.check_output(["netsh", "wlan", "show", "profile"])
            self.results_output.append(result.decode("utf-8"))

            # Ask user if they want to view passwords of saved networks
            answer = QMessageBox.question(
                self, "WiFi Passwords", "Do you want to view the WiFi passwords?"
            )

            wifi_details = []

            if answer == QMessageBox.Yes:
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
                        output_text = f"SSID: {profile}  |  Password: {wifi_lines[0]}"
                        self.results_output.append(output_text)
                        wifi_details.append(output_text)
                    except subprocess.CalledProcessError as e:
                        self.results_output.append(
                            f"Encountered an error while fetching details of {profile}. {e}"
                        )
                        continue

                self.results_output.append("Completed fetching WiFi details.")

                # Save to a text file on user's desktop
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                with open(os.path.join(desktop, "wifi_details.txt"), "w") as file:
                    file.write("\n".join(wifi_details))

        except subprocess.CalledProcessError as e:
            self.results_output.append(f"Error occurred: {e}")


class DefenderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Button to enable Windows Defender
        self.enable_button = QPushButton("Enable Windows Defender", self)
        self.enable_button.clicked.connect(self.enable_windows_defender)
        layout.addWidget(self.enable_button)

        # Button to disable Windows Defender
        self.disable_button = QPushButton("Disable Windows Defender", self)
        self.disable_button.clicked.connect(self.disable_windows_defender)
        layout.addWidget(self.disable_button)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Results output
        self.results_output = QTextEdit(self)
        layout.addWidget(self.results_output)

        # Window properties
        self.setWindowTitle("Windows Defender Control")
        self.resize(500, 500)

    def download_file(self, url, destination):
        """
        Download a file from a given URL to the specified destination.
        :param url: URL of the file to be downloaded.
        :param destination: Local path where the file should be saved.
        :return: Boolean indicating whether the download was successful.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            with open(destination, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True

        except requests.RequestException as e:
            print(f"Failed to download {url}. Error: {e}")
            return False

    def print_to_terminal(self, message):
        self.results_output.append(message)

    def disable_windows_defender(self):
        self.print_to_terminal("DISABLING WINDOWS DEFENDER...")
        total_steps = 6
        current_step = 0
        self.progress_bar.setMaximum(total_steps)
        self.progress_bar.setValue(current_step)

        cmd_list_base = [
            "Powershell",
            "-ExecutionPolicy",
            "Bypass",
        ]

        cmd_options = [
            "Set-MpPreference -DisableRealtimeMonitoring $true",
            "Set-MpPreference -DisableBehaviorMonitoring $true",
            "Set-MpPreference -DisableOnAccessProtection $true",
            "Set-MpPreference -DisableIOAVProtection $true",
            "Set-MpPreference -DisableIntrusionPreventionSystem $true",
            "Set-MpPreference -DisablePrivacyMode $true",
        ]

        for option in cmd_options:
            current_step += 1
            self.progress_bar.setValue(current_step)
            self.print_to_terminal(f"Step {current_step}: Executing {option}...")

            try:
                cmd_list = cmd_list_base + [option]
                with subprocess.Popen(
                    cmd_list, stdout=subprocess.PIPE, text=True
                ) as proc:
                    if proc.stdout:
                        for line in proc.stdout:
                            self.print_to_terminal(line.strip())
            except Exception as e:
                self.print_to_terminal(f"Error occurred: {e}")

        self.disable_tamper_protection()

        base_dir = "C:\\NexTool\\Configuration\\SECURITY"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        exe_destination = os.path.join(base_dir, "Defender_Tools.exe")
        downloaded = self.download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/Defender_Tools.exe",
            exe_destination,
        )

        if downloaded:
            subprocess.run([exe_destination], check=True)
            os.remove(exe_destination)
        else:
            print("Failed to download the executable. Not running it.")

        self.print_to_terminal("WINDOWS DEFENDER DISABLED SUCCESSFULLY.")

    def disable_tamper_protection(self):
        self.print_to_terminal("ATTEMPTING TO DISABLE TAMPER PROTECTION...")
        cmd = (
            "powershell -Command "
            "'Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows Defender\\Features -Name TamperProtection -Value 0'"
        )

        try:
            subprocess.run(cmd, check=True)
            self.print_to_terminal("Tamper Protection disabled successfully.")
        except subprocess.CalledProcessError as e:
            self.print_to_terminal(
                f"Error occurred during command execution:\n{e.stderr}"
            )
        except Exception as e:
            self.print_to_terminal(f"Error occurred: {e}")

    def enable_windows_defender(self):
        self.print_to_terminal("ENABLING WINDOWS DEFENDER...")
        total_steps = 6
        current_step = 0
        self.progress_bar.setMaximum(total_steps)
        self.progress_bar.setValue(current_step)

        cmd_list_base = [
            "Powershell",
            "-ExecutionPolicy",
            "Bypass",
        ]

        cmd_options = [
            "Set-MpPreference -DisableRealtimeMonitoring $false",
            "Set-MpPreference -DisableBehaviorMonitoring $false",
            "Set-MpPreference -DisableOnAccessProtection $false",
            "Set-MpPreference -DisableIOAVProtection $false",
            "Set-MpPreference -DisableIntrusionPreventionSystem $false",
            "Set-MpPreference -DisablePrivacyMode $false",
        ]

        for option in cmd_options:
            current_step += 1
            self.progress_bar.setValue(current_step)
            self.print_to_terminal(f"Step {current_step}: Executing {option}...")

            try:
                cmd_list = cmd_list_base + [option]
                with subprocess.Popen(
                    cmd_list, stdout=subprocess.PIPE, text=True
                ) as proc:
                    if proc.stdout:
                        for line in proc.stdout:
                            self.print_to_terminal(line.strip())
            except Exception as e:
                self.print_to_terminal(f"Error occurred: {e}")

        self.enable_tamper_protection()
        self.print_to_terminal("WINDOWS DEFENDER ENABLED SUCCESSFULLY.")

        base_dir = "C:\\NexTool\\Configuration\\SECURITY"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        exe_destination = os.path.join(base_dir, "Defender_Tools.exe")
        downloaded = self.download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/Defender_Tools.exe",
            exe_destination,
        )

        if downloaded:
            subprocess.run([exe_destination], check=True)
            os.remove(exe_destination)
        else:
            print("Failed to download the executable. Not running it.")

    def enable_tamper_protection(self):
        self.print_to_terminal("ATTEMPTING TO ENABLE TAMPER PROTECTION...")
        cmd = (
            "powershell -Command "
            "'Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows Defender\\Features -Name TamperProtection -Value 1'"
        )

        try:
            subprocess.run(cmd, check=True)
            self.print_to_terminal("Tamper Protection enabled successfully.")
        except subprocess.CalledProcessError as e:
            self.print_to_terminal(
                f"Error occurred during command execution:\n{e.stderr}"
            )
        except Exception as e:
            self.print_to_terminal(f"Error occurred: {e}")


class RemoveDefenderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Button to start the process
        self.remove_button = QPushButton("Remove Windows Defender", self)
        self.remove_button.clicked.connect(self.prompt_user)
        layout.addWidget(self.remove_button)

        # Results output
        self.results_output = QTextEdit(self)
        layout.addWidget(self.results_output)

        # Window properties
        self.setWindowTitle("Remove Windows Defender")
        self.resize(500, 500)

    def print_to_terminal(self, message):
        self.results_output.append(message)

    def prompt_user(self):
        choice = QMessageBox.warning(
            self,
            "Remove Windows Defender",
            "This action will permanently remove Windows Defender until Windows is either reset or updated to a new build. Are you sure you want to proceed?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if choice == QMessageBox.Yes:
            self.remove_windows_defender()
        else:
            self.close()

    def remove_windows_defender(self):
        self.print_to_terminal("REMOVING WINDOWS DEFENDER...")
        try:
            # Downloading install_wim_tweak.exe
            base_dir = "C:\\NexTool\\Configuration\\SECURITY"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            exe_destination = os.path.join(base_dir, "install_wim_tweak.exe")
            self.download_file(
                "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/install_wim_tweak.exe",
                exe_destination,
            )

            # Run the downloaded executable
            subprocess.run([exe_destination, "/o", "/l", "SHOWCLI"], check=True)
            subprocess.run(
                [exe_destination, "/o", "/c", "Windows-Defender", "/r", "SHOWCLI"],
                check=True,
            )
            os.remove(exe_destination)
            self.print_to_terminal("WINDOWS DEFENDER REMOVED SUCCESSFULLY.")
        except Exception as e:
            self.print_to_terminal(f"Error occurred: {e}")

    def download_file(self, url, destination):
        """
        Download a file from a given URL to the specified destination.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            with open(destination, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True

        except requests.RequestException as e:
            self.print_to_terminal(f"Failed to download {url}. Error: {e}")
            return False


class TelemetryManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Display the message about telemetry removal
        self.label = QLabel(
            "Telemetry removal is a necessary evil to keep Microsoft from spying. :)"
        )
        self.label.setWordWrap(True)  # To ensure the label wraps long text
        layout.addWidget(self.label)

        # Button to start the telemetry removal
        self.run_button = QPushButton("Start Telemetry Blocking", self)
        self.run_button.clicked.connect(self.run_TELEMETRY)
        layout.addWidget(self.run_button)

        self.terminal_output = QTextEdit(self)
        self.terminal_output.setReadOnly(True)
        layout.addWidget(self.terminal_output)

        self.setLayout(layout)
        self.setWindowTitle("Telemetry Management")
        self.resize(600, 400)

    def run_selected_script(self):
        selected_script = self.combo_box.currentText()
        if selected_script == "Run TELEMETRY Script":
            self.run_TELEMETRY()

    def print_to_terminal(self, message):
        self.terminal_output.append(message)

    def download_file(self, url, destination):
        """
        Download a file from a given URL to the specified destination.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(destination, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True

        except requests.RequestException as e:
            self.print_to_terminal(f"Failed to download {url}. Error: {e}")
            return False

    def run_TELEMETRY(self):
        self.print_to_terminal("Checking telemetry status...")

        # Check the current value of the AllowTelemetry registry key
        check_command = [
            "reg",
            "query",
            r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "/v",
            "AllowTelemetry",
        ]

        try:
            result = subprocess.run(
                check_command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if "0x0" in result.stdout:  # If the key's value is 0 (telemetry is off)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    "Your cunning plot has already been realized. Telemetry is already disabled!"
                )
                msg.setWindowTitle("ALREADY DISABLED")
                msg.exec_()
                return  # Exit the method early since telemetry is already turned off
        except subprocess.CalledProcessError:
            # The key might not exist yet. That's fine. We'll continue with the rest of the method.
            pass
            self.print_to_terminal("Blocking telemetry...")

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
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.print_to_terminal(result.stdout)
            self.print_to_terminal(result.stderr)

            # Download and run the PowerShell telemetry blocker
            base_dir = r"C:\NexTool\Configuration\TELEMETRY"
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            telemetry_script_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/block-telemetry.ps1"
            telemetry_script_path = os.path.join(base_dir, "block-telemetry.ps1")
            self.download_file(telemetry_script_url, telemetry_script_path)

            command = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                telemetry_script_path,
                "-verb",
                "runas",
            ]
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.print_to_terminal(result.stdout)
            self.print_to_terminal(result.stderr)

            # Download and run ooshutup10 with its configuration
            exe_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/ooshutup10.exe"
            cfg_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/2.COMPUTER_CONFIGURATION/ooshutup10.cfg"
            exe_path = os.path.join(base_dir, "ooshutup10.exe")
            cfg_path = os.path.join(base_dir, "ooshutup10.cfg")

            self.download_file(exe_url, exe_path)
            self.download_file(cfg_url, cfg_path)

            command = [exe_path, cfg_path, "/quiet"]
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.print_to_terminal(result.stdout)
            self.print_to_terminal(result.stderr)

            # Show success message using QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Telemetry blocked successfully. Press OK to continue.")
            msg.setWindowTitle("COMPLETE")
            msg.exec_()

        except subprocess.CalledProcessError as e:
            self.print_to_terminal(
                f"Error occurred during command execution:\n{e.stderr}"
            )
        except Exception as e:
            self.print_to_terminal(f"Error occurred: {e}")


class SystemManagerUI(QDialog):
    USER_PREFS_FILE = "C:\\temp\\user_prefs.json"
    DEFAULT_DISABLE_LIST = [
        "bits",
        "BDESVC",
        "BcastDVRUserService_7c360",
        "GoogleChromeElevationService",
        "gupdate",
        "gupdatem",
        "vmickvpexchange",
        "vmicguestinterface",
        "vmicshutdown",
        "vmicheartbeat",
        "vmcompute",
        "vmicvmsession",
        "vmicrdv",
        "vmictimesync",
        "vmicvss",
        "WdNisSvc",
        "WinDefend",
        "MicrosoftEdgeElevationServ",
        "edgeupdate",
        "edgeupdatem",
        "MozillaMaintenance",
        "SysMain",
        "TeamViewer",
        "Sense",
        "MixedRealityOpenXRSvc",
        "WSearch",
        "XboxGipSvc",
        "XblAuthManager",
        "XblGameSave",
        "XboxNetApiSvc",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        # Ensure the directory C:\temp exists
        if not os.path.exists("C:\\temp"):
            os.makedirs("C:\\temp")

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # Create tabs
        self.tab_widget.addTab(self.setup_services_ui(), "Services")
        self.tab_widget.addTab(self.setup_startup_ui(), "Startup Applications")
        self.tab_widget.addTab(self.setup_tasks_ui(), "Scheduled Tasks")
        self.tab_widget.addTab(self.setup_command_ui(), "Commands")

        main_layout.addWidget(self.tab_widget)
        main_layout.addStretch(1)
        # Buttons to save and load preferences
        self.save_prefs_button = QPushButton("Save Preferences")
        self.save_prefs_button.clicked.connect(self.save_preferences)
        main_layout.addWidget(self.save_prefs_button)

        self.setLayout(main_layout)
        self.setWindowTitle("System Manager")
        self.resize(800, 600)

        # Load user preferences if available or default list if not
        if not self.load_user_defined_list():
            self.load_default_disable_list()

    def save_preferences(self):
        """Save the current selected services to a config file."""
        selected_services = [item.text() for item in self.services_list.selectedItems()]
        with open(SystemManagerUI.USER_PREFS_FILE, "w") as file:
            json.dump(selected_services, file)

    def load_user_defined_list(self):
        if not os.path.exists(SystemManagerUI.USER_PREFS_FILE):
            return

        with open(SystemManagerUI.USER_PREFS_FILE, "r") as file:
            user_services = json.load(file)

        self.services_table.setRowCount(len(user_services))

        for row, service in enumerate(user_services):
            # Add service name to the table
            self.services_table.setItem(row, 0, QTableWidgetItem(service))
            # Again, using a dummy status for now
            self.services_table.setItem(row, 1, QTableWidgetItem("Running"))

    def setup_services_ui(self):
        layout = QVBoxLayout()

        # Use QTableWidget to display services in a tabular format
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(2)
        self.services_table.setHorizontalHeaderLabels(["Service Name", "Status"])
        self.refresh_services_button = QPushButton("Refresh Services")
        self.refresh_services_button.clicked.connect(self.refresh_services)

        self.backup_services_button = QPushButton("Backup Services")
        self.backup_services_button.clicked.connect(SystemManager.backup_services)

        self.restore_services_button = QPushButton("Restore Services")
        self.restore_services_button.clicked.connect(SystemManager.restore_services)

        self.control_service_combo = QComboBox()
        self.control_service_combo.addItems(
            ["start", "stop", "pause", "continue", "auto", "demand", "disabled"]
        )

        self.control_service_button = QPushButton("Control Selected Service")
        self.control_service_button.clicked.connect(self.control_service)

        layout.addWidget(QLabel("Services"))
        layout.addWidget(self.services_table)
        layout.addWidget(self.refresh_services_button)
        layout.addWidget(self.backup_services_button)
        layout.addWidget(self.restore_services_button)
        layout.addWidget(self.control_service_combo)
        layout.addWidget(self.control_service_button)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def setup_startup_ui(self):
        layout = QVBoxLayout()

        self.startup_list = QListWidget()
        self.refresh_startup_button = QPushButton("Refresh Startup Applications")
        self.refresh_startup_button.clicked.connect(self.refresh_startup_apps)

        self.add_startup_name = QLineEdit()
        self.add_startup_path = QLineEdit()
        self.add_startup_button = QPushButton("Add Startup Application")
        self.add_startup_button.clicked.connect(self.add_startup_app)

        self.remove_startup_button = QPushButton("Remove Selected Startup Application")
        self.remove_startup_button.clicked.connect(self.remove_startup_app)

        layout.addWidget(QLabel("Startup Applications"))
        layout.addWidget(self.startup_list)
        layout.addWidget(self.refresh_startup_button)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.add_startup_name)
        layout.addWidget(QLabel("Path"))
        layout.addWidget(self.add_startup_path)
        layout.addWidget(self.add_startup_button)
        layout.addWidget(self.remove_startup_button)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def setup_tasks_ui(self):
        layout = QVBoxLayout()

        self.tasks_list = QListWidget()
        self.refresh_tasks_button = QPushButton("Refresh Scheduled Tasks")
        self.refresh_tasks_button.clicked.connect(self.refresh_tasks)

        layout.addWidget(QLabel("Scheduled Tasks"))
        layout.addWidget(self.tasks_list)
        layout.addWidget(self.refresh_tasks_button)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def load_default_disable_list(self):
        self.services_table.setRowCount(len(SystemManagerUI.DEFAULT_DISABLE_LIST))

        for row, service in enumerate(SystemManagerUI.DEFAULT_DISABLE_LIST):
            # Add service name to the table
            self.services_table.setItem(row, 0, QTableWidgetItem(service))
            # For now, I'm just adding a dummy status, you should get the real status
            self.services_table.setItem(row, 1, QTableWidgetItem("Running"))

    def refresh_services(self):
        services = SystemManager.list_all_services()
        self.services_table.setRowCount(len(services))

        for row, service in enumerate(services):
            self.services_table.setItem(row, 0, QTableWidgetItem(service))
            # For now, I'm just adding a dummy status, you should get the real status
            self.services_table.setItem(row, 1, QTableWidgetItem("Running"))

    def control_service(self):
        selected_items = self.services_list.selectedItems()
        if not selected_items:
            return
        service = selected_items[0].text()
        action = self.control_service_combo.currentText()
        SystemManager.control_service(service, action)
        self.refresh_services()

    def refresh_startup_apps(self):
        self.startup_list.clear()
        apps = SystemManager.list_startup_applications()
        self.startup_list.addItems(apps.keys())

    def add_startup_app(self):
        name = self.add_startup_name.text()
        path = self.add_startup_path.text()
        SystemManager.add_startup_application(name, path)
        self.refresh_startup_apps()

    def remove_startup_app(self):
        selected_items = self.startup_list.selectedItems()
        if not selected_items:
            return
        name = selected_items[0].text()
        SystemManager.remove_startup_application(name)
        self.refresh_startup_apps()

    def refresh_tasks(self):
        self.tasks_list.clear()
        tasks = SystemManager.list_scheduled_tasks().split("\n")
        self.tasks_list.addItems(tasks)

    def setup_command_ui(self):
        layout = QVBoxLayout()
        self.command_list = QListWidget()
        self.command_list.addItem("Use Predetermined List")
        self.command_list.addItem("Use My List")

        self.run_command_button = QPushButton("Run Command")
        self.run_command_button.clicked.connect(self.run_command)

        layout.addWidget(QLabel("Choose Command"))
        layout.addWidget(self.command_list)
        layout.addWidget(self.run_command_button)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def run_command(self):
        selected_items = self.command_list.selectedItems()
        if not selected_items:
            return

        command = selected_items[0].text()
        services_to_disable = []

        if command == "Use Predetermined List":
            services_to_disable = SystemManagerUI.DEFAULT_DISABLE_LIST
        elif command == "Use My List":
            if os.path.exists(SystemManagerUI.USER_PREFS_FILE):
                with open(SystemManagerUI.USER_PREFS_FILE, "r") as file:
                    services_to_disable = json.load(file)

        # Disable services from the list
        for service in services_to_disable:
            # Disable the service
            success = SystemManager.disable_selected_services(service)

            # Find the service in the QTableWidget and update its status
            items = self.services_table.findItems(service, Qt.MatchExactly)
            if items:
                row = items[0].row()
                if success:
                    self.services_table.setItem(row, 1, QTableWidgetItem("Disabled"))
                else:
                    self.services_table.setItem(
                        row, 1, QTableWidgetItem("Failed to Disable")
                    )

            with open(SystemManagerUI.USER_PREFS_FILE, "r") as file:
                user_services = json.load(file)

            self.services_table.setRowCount(len(user_services))

            for row, service in enumerate(user_services):
                # Add service name to the table
                self.services_table.setItem(row, 0, QTableWidgetItem(service))
                # Again, using a dummy status for now
                self.services_table.setItem(row, 1, QTableWidgetItem("Running"))


class SystemManager:
    RECOMMENDED_DISABLE = [
        "bits",
        "BDESVC",
        "BcastDVRUserService_7c360",
        "GoogleChromeElevationService",
        "gupdate",
        "gupdatem",
        "vmickvpexchange",
        "vmicguestinterface",
        "vmicshutdown",
        "vmicheartbeat",
        "vmcompute",
        "vmicvmsession",
        "vmicrdv",
        "vmictimesync",
        "vmicvss",
        "WdNisSvc",
        "WinDefend",
        "MicrosoftEdgeElevationServ",
        "edgeupdate",
        "edgeupdatem",
        "MozillaMaintenance",
        "SysMain",
        "TeamViewer",
        "Sense",
        "MixedRealityOpenXRSvc",
        "WSearch",
        "XboxGipSvc",
        "XblAuthManager",
        "XblGameSave",
        "XboxNetApiSvc",
    ]

    @staticmethod
    def list_all_services():
        command = ["sc", "query", "type=", "service"]
        output = subprocess.check_output(command, text=True).splitlines()
        services = [
            line.split(":")[1].strip() for line in output if "SERVICE_NAME" in line
        ]
        return services

    @staticmethod
    def backup_services():
        services = SystemManager.list_all_services()  # Correct call
        # services = list_all_services()  <-- This line is redundant and should be removed
        service_status = {}
        for service in services:
            status_cmd = ["sc", "qc", service]
            status_output = subprocess.check_output(status_cmd, text=True).splitlines()
            status = [
                line.split(":", 1)[1].strip()
                for line in status_output
                if "START_TYPE" in line
            ][0]
            service_status[service] = status

        with open("backup_services.json", "w") as file:
            json.dump(service_status, file)

    @staticmethod
    def restore_services():
        with open("backup_services.json", "r") as file:
            backup_statuses = json.load(file)

        for service, status in backup_statuses.items():
            SystemManager.set_service_start_type(service, status)

    @staticmethod
    def get_service_start_type(service):
        status_cmd = ["sc", "qc", service]
        status_output = subprocess.check_output(status_cmd, text=True).splitlines()
        status = [
            line.split(":", 1)[1].strip()
            for line in status_output
            if "START_TYPE" in line
        ]
        return status[0] if status else None

    @staticmethod
    def set_service_start_type(service, start_type):
        subprocess.run(["sc", "config", service, f"start= {start_type}"], text=True)

    @staticmethod
    def control_service(service, action):
        if action in ["start", "stop", "pause", "continue"]:
            result = subprocess.run(
                ["sc", action, service], capture_output=True, text=True
            )
        elif action in ["auto", "demand", "disabled"]:
            result = subprocess.run(
                ["sc", "config", service, f"start= {action}"],
                capture_output=True,
                text=True,
            )
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

    @staticmethod
    def disable_recommended_services():
        results = []
        for service in SystemManager.RECOMMENDED_DISABLE:
            result = SystemManager.control_service(service, "disabled")
            results.append(result)
        return results

    @staticmethod
    def disable_selected_services(service_list):
        results = []
        for service in service_list:
            result = SystemManager.control_service(service, "disabled")
            results.append(result)
        return results

    @staticmethod
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

    @staticmethod
    def add_startup_application(name, path):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as key:
            reg.SetValueEx(key, name, 0, reg.REG_SZ, path)

    @staticmethod
    def remove_startup_application(name):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as key:
            reg.DeleteValue(key, name)

    @staticmethod
    def list_scheduled_tasks():
        tasks = subprocess.check_output(["schtasks", "/query", "/fo", "LIST"]).decode()
        return tasks

    @staticmethod
    def create_scheduled_task(name, command, time="12:00", frequency="daily"):
        subprocess.run(
            [
                "schtasks",
                "/create",
                "/sc",
                frequency,
                "/tn",
                name,
                "/tr",
                command,
                "/st",
                time,
            ]
        )

    @staticmethod
    def delete_scheduled_task(name):
        subprocess.run(["schtasks", "/delete", "/tn", name, "/f"])


class MASTool(QWidget):
    def __init__(self):
        super(MASTool, self).__init__()

        layout = QVBoxLayout(self)

        # Button to run the MAS script
        self.run_mas_button = QPushButton("Run MAS")
        self.run_mas_button.clicked.connect(self.run_MAS)

        # QTextEdit to act as a terminal
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)  # Make it read-only

        layout.addWidget(self.run_mas_button)
        layout.addWidget(self.terminal)

        self.setWindowTitle("MAS Tool")
        self.resize(400, 300)

    def print_to_terminal(self, message):
        self.terminal.append(message)

    def run_MAS(self):
        self.print_to_terminal("Executing Microsoft Activation Script...")
        try:
            # Execute the PowerShell command
            command = [
                "powershell.exe",
                "-Command",
                "irm https://massgrave.dev/get | iex",
            ]
            result = subprocess.run(command, text=True, capture_output=True, check=True)
            self.print_to_terminal(result.stdout)
        except subprocess.CalledProcessError as e:
            self.print_to_terminal(
                f"Error occurred during command execution:\n{e.stderr}"
            )
        except Exception as e:
            self.print_to_terminal(f"Error occurred: {e}")


class WindowsUpdaterTool:
    def run_update(self, callback=None):
        """Starts the Windows Manual Updater."""

        # Define the base directory and ensure it exists
        base_dir = "C:\\NexTool\\UPDATES"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Define the URL for WUpdater.exe and its intended destination
        download_url = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/WUpdater.exe"
        exe_destination = os.path.join(base_dir, "WUpdater.exe")

        try:
            # Download WUpdater.exe
            self.download_file(download_url, exe_destination)

            # Execute the WUpdater.exe and wait until it completes
            subprocess.run(exe_destination, check=True)

            # After the execution, delete the exe
            os.remove(exe_destination)

            if callback:
                callback("Windows Update process completed successfully.")

        except Exception as e:
            if callback:
                callback(f"Error occurred: {e}")

    def download_file(self, url, dest):
        """Method to download a file from the specified URL to the destination."""
        response = requests.get(url, stream=True)
        with open(dest, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)


class PatchMyPCTool(QWidget):
    BASE_DIR_PRESELECT = "C:\\NexTool\\Updater\\PRE-SELECT"
    BASE_DIR_SELFSELECT = "C:\\NexTool\\Updater\\SELF-SELECT"

    def __init__(self, progress_callback=None, completion_callback=None):
        super(PatchMyPCTool, self).__init__()

        # Assign callbacks
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback

        layout = QVBoxLayout(self)

        # Choice selection buttons
        self.preset_button = QPushButton("Use Preset")
        self.own_select_button = QPushButton("Make My Own Selection")

        self.preset_button.clicked.connect(self.run_preselected)
        self.own_select_button.clicked.connect(self.run_own_selections)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        layout.addWidget(self.preset_button)
        layout.addWidget(self.own_select_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle("PatchMyPC Tool")

    def download_file(self, url, dest):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024  # 1 Kibibyte
        with open(dest, "wb") as file:
            for data in response.iter_content(block_size):
                file.write(data)
                if self.progress_callback:
                    self.progress_callback(block_size, total_size)

    def run_preselected(self):
        if not os.path.exists(self.BASE_DIR_PRESELECT):
            os.makedirs(self.BASE_DIR_PRESELECT)

        exe_destination = os.path.join(self.BASE_DIR_PRESELECT, "PatchMyPC.exe")
        ini_destination = os.path.join(self.BASE_DIR_PRESELECT, "PatchMyPC.ini")

        self.download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/PRE-SELECT/PatchMyPC.exe",
            exe_destination,
        )
        self.download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/PRE-SELECT/PatchMyPC.ini",
            ini_destination,
        )

        subprocess.run([exe_destination, "/auto", "switch"], check=True)

        if self.completion_callback:
            self.completion_callback("Preselected PatchMyPC operation completed.")

    def run_own_selections(self):
        if not os.path.exists(self.BASE_DIR_SELFSELECT):
            os.makedirs(self.BASE_DIR_SELFSELECT)

        exe_destination = os.path.join(self.BASE_DIR_SELFSELECT, "PatchMyPC.exe")
        ini_destination = os.path.join(self.BASE_DIR_SELFSELECT, "PatchMyPC.ini")

        self.download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/SELF-SELECT/PatchMyPC.exe",
            exe_destination,
        )
        self.download_file(
            "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SOFTWARE/SELF-SELECT/PatchMyPC.ini",
            ini_destination,
        )

        subprocess.run([exe_destination], check=True)

        if self.completion_callback:
            self.completion_callback("Custom PatchMyPC operation completed.")

    def update_progress(self, value):
        # Update the progress bar value
        self.progress_bar.setValue(value)


class ChocolateyGUI(QWidget):
    def __init__(self):
        super(ChocolateyGUI, self).__init__()
        self.manager = ChocolateyManager()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Terminal-like display
        self.terminal_display = QTextEdit(self)
        layout.addWidget(self.terminal_display)

        # Install button
        self.install_button = QPushButton("Install Chocolatey Packages", self)
        self.install_button.clicked.connect(self.install_packages)
        layout.addWidget(self.install_button)

        # Set layout
        self.setLayout(layout)
        self.setWindowTitle("Chocolatey Manager GUI")

    def install_packages(self):
        installed, failed = self.manager.install_packages()

        self.terminal_display.append(f'Successfully installed: {", ".join(installed)}')
        self.terminal_display.append(f'Failed to install: {", ".join(failed)}')

        # Update progress bar
        self.progress_bar.setValue(
            int((len(installed) / len(self.manager.packages)) * 100)
        )

        response = self.manager.inform_about_choco_gui()
        reply = QMessageBox.question(
            self, "Message", response, QMessageBox.Yes, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.manager.run_chocolatey_gui()


class ChocolateyManager:
    def __init__(self):
        self.packages = [
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

    def is_chocolatey_installed(self):
        choco_path = os.path.join(os.environ["ProgramData"], "Chocolatey")
        return os.path.exists(choco_path)

    def install_chocolatey(self):
        install_cmd = (
            "Set-ExecutionPolicy Bypass -Scope Process -Force; "
            "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
            "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        )
        subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", install_cmd],
            check=True,
        )

    def install_packages(self):
        installed_packages = []
        failed_packages = []

        if not self.is_chocolatey_installed():
            self.install_chocolatey()

        for package in self.packages:
            try:
                subprocess.run(["choco", "install", package, "-y"], check=True)
                installed_packages.append(package)
            except subprocess.CalledProcessError:
                failed_packages.append(package)
            except Exception as e:
                failed_packages.append(package)

        return installed_packages, failed_packages

    def inform_about_choco_gui(self):
        message = (
            "Installation process completed. If you wish to manage your applications in a GUI, "
            "consider using Chocolatey's GUI. Do you want to install and open Chocolatey GUI now?"
        )
        return message

    def run_chocolatey_gui(self):
        try:
            subprocess.run(["choco", "install", "chocolateygui", "-y"], check=True)
            subprocess.run(["chocolateygui"], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error occurred during installation or launch:\n{e}"
        except Exception as e:
            return f"Unexpected error occurred: {e}"


class WingetGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = WingetManager()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Terminal-like display
        self.terminal_display = QTextEdit(self)
        layout.addWidget(self.terminal_display)

        # Install button
        self.install_button = QPushButton("Install Winget Packages", self)
        self.install_button.clicked.connect(self.install_packages)
        layout.addWidget(self.install_button)

        # Set layout
        self.setLayout(layout)
        self.setWindowTitle("Winget Manager GUI")

    def install_packages(self):
        installed, failed = self.manager.install_winget_packages()

        self.terminal_display.append(f'Successfully installed: {", ".join(installed)}')
        self.terminal_display.append(f'Failed to install: {", ".join(failed)}')

        # Update progress bar
        self.progress_bar.setValue(
            int((len(installed) / len(self.manager.packages)) * 100)
        )

        response = self.manager.inform_about_winget_gui()
        reply = QMessageBox.question(
            self, "Message", response, QMessageBox.Yes, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.manager.run_winget_gui()


class WingetManager:
    def __init__(self):
        self.packages = [
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

    def check_windows_version(self):
        version = sys.getwindowsversion().major
        if version < 10:  # Windows version less than Windows 10
            return False
        return True

    def check_winget_installed(self):
        try:
            result = subprocess.run(
                ["winget", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                return True
        except:
            pass
        return False

    def run_winget_check(self, action_type):
        is_windows_supported = self.check_windows_version()
        is_winget_installed = self.check_winget_installed()

        if not is_windows_supported or not is_winget_installed:
            self.show_guidance_window()
        else:
            # Winget is available, proceed with the desired action.
            if action_type == "gui":
                self.run_winget_gui()
            elif action_type == "pre_set_selections":
                self.install_winget_packages()

    def show_guidance_window(self):
        guidance_dialog = QDialog()
        layout = QVBoxLayout()

        guidance_msg = QLabel()
        guidance_msg.setWordWrap(True)
        guidance_msg.setText(
            "Winget is not detected on this machine. Please follow the instructions below:\n\n"
            "Method 1: Install winget via Microsoft Store\n"
            "1. Open the Microsoft Store app.\n"
            "2. Search for 'winget' and select the App Installer application.\n"
            "3. Click Get to install.\n\n"
            "Alternatively, you can Click Here to directly open the Microsoft Store page for Winget.\n\n"
            "Method 2: Install winget via GitHub\n"
            "1. Navigate to the Winget GitHub page.\n"
            "2. Download the latest .msixbundle file and install.\n\n"
            "After installation, please re-run this tool."
        )
        layout.addWidget(guidance_msg)

        open_store_button = QPushButton("Open Microsoft Store for Winget")
        open_store_button.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://aka.ms/winget-install"))
            or None
        )

        layout.addWidget(open_store_button)

        open_github_button = QPushButton("Open Winget GitHub Releases")
        open_github_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/microsoft/winget-cli/releases")
            )
            or None
        )
        layout.addWidget(open_github_button)

        guidance_dialog.setLayout(layout)
        guidance_dialog.setWindowTitle("Winget Installation Guide")
        guidance_dialog.exec_()

    def install_adobe_reader(self):
        architecture = platform.architecture()[0]

        if architecture == "32bit":
            package_id = "Adobe.Acrobat.Reader.32-bit"
        elif architecture == "64bit":
            package_id = "Adobe.Acrobat.Reader.64-bit"
        else:
            return f"Unknown system architecture: {architecture}. Cannot install Adobe Acrobat Reader."

        try:
            subprocess.run(
                ["winget", "install", "--id=" + package_id, "-e"], check=True
            )
            return f"Adobe Acrobat Reader for {architecture} installed successfully!"
        except subprocess.CalledProcessError:
            return f"Error installing Adobe Acrobat Reader for {architecture}."
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def install_winget_packages(self):
        installed_packages = []
        failed_packages = []

        adobe_msg = self.install_adobe_reader()
        # TODO: Display adobe_msg in GUI, perhaps append to the 'terminal'?

        for package in self.packages:
            try:
                subprocess.run(
                    ["winget", "install", "--id=" + package, "-e"], check=True
                )
                installed_packages.append(package)
            except subprocess.CalledProcessError:
                failed_packages.append(package)
            except Exception as e:
                failed_packages.append(package)

        return installed_packages, failed_packages

    def inform_about_winget_gui(self):
        response = (
            "Installation process completed. If you wish to install or update other applications, "
            "or manage your existing installations, consider using the Winget GUI which offers a user-friendly interface "
            "with features such as updates, installation tracking, and more. Do you want to install and open Winget GUI now?"
        )

        return response

    def run_winget_gui(self):
        try:
            # Install the WingetUI Store
            subprocess.run(
                ["winget", "install", "-e", "--id", "SomePythonThings.WingetUIStore"],
                check=True,
            )
            # Launch the WingetUI
            subprocess.run(["WingetUI"], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error occurred during installation or launch:\n{e.stderr}"
        except Exception as e:
            return f"Error occurred: {e}"


class OfficeSetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.manager = OfficeSetupManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Office Tool Plus Setup")

        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Terminal-like display
        self.terminal_display = QTextEdit(self)
        self.terminal_display.setReadOnly(True)
        layout.addWidget(self.terminal_display)

        # Install button
        self.install_button = QPushButton("Setup Office Tool Plus", self)
        self.install_button.clicked.connect(self.setup_office)
        layout.addWidget(self.install_button)

        # Set layout
        self.setLayout(layout)

    def print_to_terminal(self, message):
        self.terminal_display.append(message)

    def setup_office(self):
        self.manager.download_and_setup_office(
            self.print_to_terminal, self.progress_bar
        )


class OfficeSetupManager:
    BASE_DIR = "C:\\NexTool"
    TRUSTED_URLS = {
        "64": "https://github.com/YerongAI/Office-Tool/releases/download/v10.1.10.1/Office_Tool_with_runtime_v10.1.10.1_x64.zip",
        "32": "https://github.com/YerongAI/Office-Tool/releases/download/v10.1.10.1/Office_Tool_with_runtime_v10.1.10.1_x86.zip",
    }

    def create_office_config(self, architecture, destination):
        """Generate Office XML configuration for a given architecture."""
        xml_content = f"""
        <Configuration>
          <Add OfficeClientEdition="{architecture}" Channel="PerpetualVL2021" MigrateArch="true" AllowCdnFallback="true">
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
        """

        with open(destination, "w") as xml_file:
            xml_file.write(xml_content)

    def download_and_setup_office(self, print_func, progress_bar):
        print_func("INITIATING OFFICE TOOL PLUS SETUP...")

        arch = platform.architecture()[0]
        if arch == "64bit":
            architecture = "64"
        elif arch == "32bit":
            architecture = "32"
        else:
            print_func(f"Unsupported architecture: {arch}")
            return

        url = self.TRUSTED_URLS.get(architecture)
        if not url:
            print_func("Invalid architecture specified.")
            return

        office_dir = os.path.join(self.BASE_DIR, f"Office_Tool_{architecture}")
        if not os.path.exists(office_dir):
            os.makedirs(office_dir)

        destination_zip = os.path.join(office_dir, "Office_Tool.zip")

        print_func("Attempting to download Office Tool Plus...")
        try:
            urllib.request.urlretrieve(url, destination_zip)
        except Exception as e:
            print_func(f"Error downloading {url}: {e}")
            return
        print_func("Downloaded Office Tool Plus.")

        print_func("Attempting to extract Office Tool Plus...")
        with zipfile.ZipFile(destination_zip, "r") as zip_ref:
            zip_ref.extractall(office_dir)
        print_func("Extracted Office Tool Plus.")

        destination_xml = os.path.join(office_dir, "office_config.xml")
        self.create_office_config(architecture, destination_xml)
        print_func("Generated Office XML configuration.")

        try:
            otp_exe_path = os.path.join(
                office_dir, "Office Tool", "Office Tool Plus.exe"
            )
            subprocess.run([otp_exe_path, "-xml", destination_xml], check=True)
            print_func("Office Tool Plus launched with XML configuration!")
        except Exception as e:
            print_func(f"Error occurred while trying to run Office Tool Plus: {e}")


class DriverUpdaterManager(QObject):
    finished = pyqtSignal()

    def __init__(self, print_func):
        super().__init__()
        self.BASE_DIR = "C:\\NexTool\\Updater"
        self.SNAPPY_URL = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SNAPPY_DRIVER.zip"
        self.print_func = print_func
        self.update_paths()

    def update_paths(self):
        self.SNAPPY_ZIP_PATH = os.path.join(self.BASE_DIR, "SNAPPY_DRIVER.zip")
        self.SNAPPY_EXTRACT_PATH = os.path.join(self.BASE_DIR, "SNAPPY_DRIVER")

    def set_base_dir(self, new_base_dir):
        self.BASE_DIR = new_base_dir
        self.update_paths()

    def download_file(self, url, destination):
        try:
            urllib.request.urlretrieve(url, destination)
            self.print_func(f"Downloaded file from {url} to {destination}.")
        except Exception as e:
            self.print_func(f"Error downloading {url}: {e}")

    def run(self):
        self.print_func("RUNNING DRIVER UPDATER...")
        try:
            if not os.path.exists(self.BASE_DIR):
                os.makedirs(self.BASE_DIR)

            # Download the Snappy Driver zip file
            self.download_file(self.SNAPPY_URL, self.SNAPPY_ZIP_PATH)

            # Extract the downloaded zip
            with zipfile.ZipFile(self.SNAPPY_ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(self.SNAPPY_EXTRACT_PATH)

            # Execute the appropriate Snappy Driver Installer based on the system's architecture
            arch = platform.architecture()[0]
            if arch == "64bit":
                exe_path = os.path.join(self.SNAPPY_EXTRACT_PATH, "SDI_x64_R2111.exe")
            elif arch == "32bit":
                exe_path = os.path.join(self.SNAPPY_EXTRACT_PATH, "SDI_R2111.exe")
            else:
                raise Exception(f"Unsupported architecture: {arch}")

            subprocess.run(
                [exe_path, "-checkupdates", "-autoupdate", "-autoclose"],
                check=True,
            )
            self.print_func("Driver update completed!")
        except Exception as e:
            self.print_func(f"Error occurred: {e}")
        self.finished.emit()


class DriverUpdaterManagerGUI(QDialog):
    def __init__(self, print_func):
        super().__init__()
        self.thread = None
        self.updater = DriverUpdaterManager(self.print_to_terminal)

        # Default save path
        self.save_path = "C:\\NexTool\\Updater"
        self.updater.finished.connect(self.on_updater_finished)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Terminal-like display
        self.terminal_display = QTextEdit(self)
        self.terminal_display.setReadOnly(True)
        layout.addWidget(self.terminal_display)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Save Path button
        self.save_path_button = QPushButton(
            f"Set Save Path (Current: {self.save_path})", self
        )
        self.save_path_button.clicked.connect(self.set_save_path)
        layout.addWidget(self.save_path_button)

        # Start button
        self.start_button = QPushButton("Start Driver Update", self)
        self.start_button.clicked.connect(self.start_update)
        layout.addWidget(self.start_button)

        self.setLayout(layout)
        self.setWindowTitle("Driver Updater GUI")
        self.resize(500, 350)

    def print_to_terminal(self, message):
        self.terminal_display.append(message)

    def set_save_path(self):
        dir_ = QFileDialog.getExistingDirectory(
            self, "Select a directory", self.save_path
        )
        if dir_:
            self.save_path = dir_
            self.updater.set_base_dir(self.save_path)
            self.save_path_button.setText(f"Set Save Path (Current: {self.save_path})")

    def start_update(self):
        # Ideally, the updater should be run in a separate thread to avoid freezing the GUI.
        self.start_button.setEnabled(False)
        self.thread = QThread()
        self.updater.moveToThread(self.thread)
        self.thread.started.connect(self.updater.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.start_button.setEnabled)
        self.thread.start()

    def on_updater_finished(self):
        # This method will be called when the updater is done
        self.start_button.setEnabled(True)


class CustomUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.defender_thread = None
        self.signals = ()

        self.setWindowTitle("NexTool")
        self.setGeometry(100, 100, 800, 600)
        self.setFont(QFont("Segoe UI", 10))

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        top_layout = QHBoxLayout()

        self.main_menu = QListWidget(self)
        top_layout.addWidget(self.main_menu)

        self.submenu_stacks = QStackedLayout()
        self.submenus = QStackedWidget(self)
        self.submenu_lists = QStackedWidget(self)
        self.submenu_stacks.addWidget(self.submenus)
        self.submenu_stacks.addWidget(self.submenu_lists)

        self.apply_fluent_style()

        top_layout.addLayout(self.submenu_stacks)
        main_layout.addLayout(top_layout)

        # Create a menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # Add a refresh action
        refresh_action = QAction("Refresh System Info", self)
        refresh_action.triggered.connect(self.refresh_system_info)
        file_menu.addAction(refresh_action)

        # Construct the menu based on the tabs dictionary
        self.construct_menu(tabs)

        # Terminal Output and Progress bar
        self.terminal_output = QTextEdit(self)
        self.terminal_output.setPlaceholderText("Terminal Output Goes Here...")
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        main_layout.addWidget(self.terminal_output)
        main_layout.addWidget(self.progress_bar)

        # Initialize the fade animation for submenus
        self.opacity_effect = QGraphicsOpacityEffect(self.submenus)
        self.submenus.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.main_menu.currentRowChanged.connect(self.display_submenu)

        self.setCentralWidget(central_widget)

    def refresh_system_info(self):
        updated_info = consolidate_info(get_system_information())
        self.system_info_text_display.setPlainText(updated_info)

    def construct_menu(self, menu_dict):
        for main, subitems in menu_dict.items():
            if main == "System Information":
                submenu = QWidget()
                layout = QVBoxLayout(submenu)

                consolidated_info_text = consolidate_info(get_system_information())
                self.system_info_text_display = QTextEdit(
                    self
                )  # Change to instance variable
                self.system_info_text_display.setPlainText(consolidated_info_text)
                self.system_info_text_display.setReadOnly(
                    True
                )  # Make the widget read-only
                layout.addWidget(self.system_info_text_display)

                self.submenus.addWidget(submenu)
                self.main_menu.addItem(main)
            else:
                self.main_menu.addItem(main)
                if isinstance(subitems, list):
                    submenu = QWidget()
                    layout = QVBoxLayout(submenu)

                    for item in subitems:
                        btn = QPushButton(item, self)
                        if item == "Test Connection":
                            btn.clicked.connect(self.run_speed_test)
                        elif item == "List Adapters":
                            btn.clicked.connect(self.display_adapters)
                        elif item == "Auto Config Network":
                            btn.clicked.connect(self.on_auto_configure_button_clicked)
                        elif item == "Manual Config Network":
                            btn.clicked.connect(self.on_manual_configure_button_clicked)
                        elif item == "Ping Hosts":
                            btn.clicked.connect(self.open_ping_dialog)
                        elif item == "Trace Route":
                            btn.clicked.connect(self.traceroute)
                        elif item == "Network Share Manager":
                            btn.clicked.connect(self.open_network_share_manager)
                        elif item == "Wi-Fi Password Extract":
                            btn.clicked.connect(self.open_wifi_password_extract)
                        elif item == "Enable/Disable Windows Defender":
                            btn.clicked.connect(self.open_defender_dialog)
                        elif (
                            item
                            == "Remove Windows Defender - This is a one-time action"
                        ):
                            btn.clicked.connect(self.on_remove_defender_dialog)
                        elif item == "Block Telemetry":
                            btn.clicked.connect(self.open_telemetry_dialog)
                        elif item == "Services Management":
                            btn.clicked.connect(self.launch_system_manager)
                        elif item == "Microsoft Activation Script":
                            btn.clicked.connect(self.open_MASTool)
                        elif item == "Windows Update":
                            btn.clicked.connect(self.execute_windows_update)
                        elif item == "PatchMyPC":
                            btn.clicked.connect(self.launch_patchmypc_tool)
                        elif item == "Chocolatey":
                            btn.clicked.connect(self.launch_chocolatey_gui)
                        elif item == "Winget":
                            btn.clicked.connect(self.launch_winget_gui)
                        elif item == "Office Instalations":
                            btn.clicked.connect(self.launch_office_installer)
                        elif item == "Snappy Driver":
                            btn.clicked.connect(self.launch_driver_updater)

                        # elif item == "PatchMyPC":
                        #    btn.clicked.connect(self.launch_patchmypc_tool)

                        layout.addWidget(btn)

                    self.submenus.addWidget(submenu)

                elif isinstance(subitems, dict):  # Nested submenu
                    submenu_list = QListWidget(self)
                    self.submenu_lists.addWidget(submenu_list)

                    for subkey, sublist in subitems.items():
                        submenu_list.addItem(subkey)
                        submenu = QWidget()
                        layout = QVBoxLayout(submenu)
                        for item in sublist:
                            btn = QPushButton(item, self)
                            layout.addWidget(btn)

                        self.submenus.addWidget(submenu)

                    submenu_list.currentRowChanged.connect(self.display_subsubmenu)

    def show_detail(self, key, value):
        # This function will be called when an item from "System Information" is clicked
        # For now, it just prints the key and value, but you can update it to show more details or other functionality.
        print(f"{key}: {value}")

    def display_submenu(self, index):
        # Start the fade animation
        self.fade_animation.start()

        if self.submenu_lists.widget(index):  # Check if it's a nested submenu
            self.submenu_stacks.setCurrentIndex(1)
            self.submenu_lists.setCurrentIndex(index)
        else:
            self.submenu_stacks.setCurrentIndex(0)
            self.submenus.setCurrentIndex(index)

    def display_subsubmenu(self, index):
        self.submenu_stacks.setCurrentIndex(0)
        self.submenus.setCurrentIndex(index)

    def download_file(
        self, url, destination_path
    ):  # Only for "small" files that don't need to be downloaded in chunks
        response = requests.get(url, stream=True)
        with open(destination_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    def print_to_terminal(self, text: str):
        self.terminal_output.append(text)
        QApplication.processEvents()

    def handle_button_click(self, action_name):
        if action_name == "Microsoft Activation Script":
            self.open_MASTool()

    def open_MASTool(self):
        self.mas_tool = MASTool()  # instantiate the MAS Tool
        self.mas_tool.show()  # display it

    def get_input_from_user(self, prompt: str) -> str:  # Add the self parameter
        text, okPressed = QInputDialog.getText(
            self, "Input", prompt, QLineEdit.Normal, ""
        )
        if okPressed and text != "":
            return text
        return ""

    def get_adapters(self) -> str:
        try:
            # Fetch the list of adapters using subprocess
            output = subprocess.check_output(
                ["netsh", "interface", "ipv4", "show", "interface"]
            )
            adapters = [
                line.split(maxsplit=4)[-1]
                for line in output.decode().splitlines()
                if "Connected" in line or "Disconnected" in line
            ]

            # If no adapters, print to terminal and return
            if not adapters:
                self.print_to_terminal("No adapters found.")
                return ""

            # Get user choice from the fetched list of adapters
            adapter, okPressed = QInputDialog.getItem(
                self, "Select Adapter", "Choose a network adapter:", adapters, 0, False
            )
            if okPressed and adapter:
                return adapter

            return ""

        except Exception as e:
            self.print_to_terminal(f"Failed to fetch adapters: {e}")
            return ""

    def apply_fluent_style(self):
        if is_dark_mode():
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def run_speed_test(self):
        self.print_to_terminal(
            "THIS SECTION WILL RUN A CLI BASED SPEED TEST TO DETECT INTERNET STABILITY"
        )

        # Define the base directory and ensure it exists
        base_dir = "C:\\NexTool\\Configuration\\Network"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Download the speedtest.exe file
        exe_destination = os.path.join(base_dir, "speedtest.exe")
        self.download_file(
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
                        self.print_to_terminal(line.strip())
            proc.wait()
        except Exception as e:
            self.print_to_terminal(f"Error occurred: {e}")
        finally:
            os.remove(exe_destination)
            self.print_to_terminal("Speed test completed")

    def list_adapters(self) -> List[str]:
        try:
            # Fetch the list of adapters using subprocess
            output = subprocess.check_output(
                ["netsh", "interface", "ip", "show", "config"]
            ).decode()

            # Extract adapter names from the output
            adapters = re.findall(r"Configuration for interface \"(.+?)\"", output)

            return adapters

        except Exception as e:
            self.print_to_terminal(f"Failed to list adapters: {e}")
            return []

    def display_adapters(self):
        adapters = self.list_adapters()
        if adapters:
            message = "\n".join(adapters)
        else:
            message = "No adapters found."
        self.print_to_terminal(message)

    def on_auto_configure_button_clicked(self):
        selected_adapter = self.choose_adapter()
        if selected_adapter:
            self.auto_config_adapter(selected_adapter)
        else:
            # Handle case where user didn't select an adapter
            self.print_to_terminal(
                "Adapter not selected. Automatic configuration aborted."
            )

    def on_manual_configure_button_clicked(self):
        selected_adapter = self.choose_adapter()
        if selected_adapter:
            self.manual_config_adapter(selected_adapter)
        else:
            # Handle case where user didn't select an adapter
            self.print_to_terminal(
                "Adapter not selected. Manual configuration aborted."
            )

    def choose_adapter(self) -> str:
        adapters = self.list_adapters()
        adapter, okPressed = QInputDialog.getItem(
            self, "Select Adapter", "Choose a network adapter:", adapters, 0, False
        )

        if okPressed and adapter:
            return adapter
        return ""

    def extract_ip_address(self, output):
        """
        Extract IP address from netsh command output.
        """
        match = re.search(r"IP Address:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output)
        if match:
            return match.group(1)
        return "Not Found"

    def get_current_config(self, adapter_name: str) -> dict:
        """Fetch current network configurations for the given adapter."""
        try:
            output = subprocess.check_output(
                ["netsh", "interface", "ipv4", "show", "config", f"name={adapter_name}"]
            ).decode()

            # Use regex to extract configurations
            ip_address = re.search(r"IP Address:\s+(\d+\.\d+\.\d+\.\d+)", output)
            subnet_mask = re.search(r"Subnet Prefix:\s+(\d+\.\d+\.\d+\.\d+)", output)
            gateway = re.search(r"Default Gateway:\s+(\d+\.\d+\.\d+\.\d+)", output)
            dns_primary = re.search(
                r"Statically Configured DNS Servers:\s+(\d+\.\d+\.\d+\.\d+)", output
            )
            dns_secondary = re.search(
                r"\n\s+(\d+\.\d+\.\d+\.\d+)",
                dns_primary.group(0) if dns_primary else "",
            )

            return {
                "IP Address": ip_address.group(1) if ip_address else "Not Found",
                "Subnet Mask": subnet_mask.group(1) if subnet_mask else "Not Found",
                "Gateway": gateway.group(1) if gateway else "Not Found",
                "Primary DNS": dns_primary.group(1) if dns_primary else "Not Found",
                "Secondary DNS": dns_secondary.group(1)
                if dns_secondary
                else "Not Found",
            }
        except Exception as e:
            return {
                "IP Address": "Error",
                "Subnet Mask": "Error",
                "Gateway": "Error",
                "Primary DNS": "Error",
                "Secondary DNS": "Error",
            }

    def auto_config_adapter(self, adapter_name):
        # First, get the list of available adapters
        adapters = self.list_adapters()

        if not adapters:
            QMessageBox.warning(
                self,
                "No Adapters Found",
                "No network adapters were found on the device.",
                QMessageBox.Ok,
            )
            return

        if adapter_name not in adapters:
            QMessageBox.warning(
                self,
                "Adapter Not Found",
                f"The selected adapter '{adapter_name}' was not found.",
                QMessageBox.Ok,
            )
            return

        # Fetch current configurations
        current_configs = self.get_current_config(adapter_name)
        current_settings = (
            f"IP Address: {current_configs.get('IP Address', 'N/A')}\n"
            f"Subnet Mask: {current_configs.get('Subnet Mask', 'N/A')}\n"
            f"Gateway: {current_configs.get('Gateway', 'N/A')}\n"
            f"Primary DNS: {current_configs.get('Primary DNS', 'N/A')}\n"
            f"Secondary DNS: {current_configs.get('Secondary DNS', 'N/A')}"
        )

        reply = QMessageBox.question(
            self,
            "Current Settings",
            f"Here are your current settings:\n\n{current_settings}\n\nWould you like to continue with auto-configuration?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        # Adjusted commands for adapter configuration
        address_cmd = [
            "netsh",
            "interface",
            "ipv4",
            "set",
            "address",
            f"name={adapter_name}",
            "source=dhcp",
        ]
        dns_cmd = [
            "netsh",
            "interface",
            "ipv4",
            "set",
            "dns",
            f"name={adapter_name}",
            "source=dhcp",
        ]

        try:
            print(f"Running address command: {' '.join(address_cmd)}")
            subprocess.run(address_cmd)

            print(f"Running DNS command: {' '.join(dns_cmd)}")
            subprocess.run(dns_cmd)

            # Fetching the new IP address to show to the user
            output = subprocess.check_output(
                [
                    "netsh",
                    "interface",
                    "ipv4",
                    "show",
                    "config",
                    f"name={adapter_name}",
                ]
            )
            ip_address = self.extract_ip_address(output.decode())

            QMessageBox.information(
                self,
                "Success",
                f"Successfully set {adapter_name} to automatic. IP Address: {ip_address}",
                QMessageBox.Ok,
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while setting {adapter_name} to automatic. Error: {e}",
                QMessageBox.Ok,
            )

    def manual_config_adapter(self, adapter_name: str):
        adapters = self.list_adapters()

        if not adapters:
            QMessageBox.warning(
                self,
                "No Adapters Found",
                "No network adapters were found on the device.",
                QMessageBox.Ok,
            )
            return

        if adapter_name not in adapters:
            QMessageBox.warning(
                self,
                "Adapter Not Found",
                f"The selected adapter '{adapter_name}' was not found.",
                QMessageBox.Ok,
            )
            return

        dialog = ManualConfigDialog(adapter_name, self)
        if dialog.exec_():
            ip_address = dialog.ip_input.text()
            subnet_mask = dialog.subnet_mask_input.text()
            gateway = dialog.gateway_input.text() or None  # If empty, set to None
            dns_primary = dialog.dns_primary_input.text() or None
            dns_secondary = dialog.dns_secondary_input.text() or None

            try:
                # Set the IP, subnet mask, and gateway
                cmd_address = [
                    "netsh",
                    "interface",
                    "ipv4",
                    "set",
                    "address",
                    f"name={adapter_name}",
                    f"static {ip_address} {subnet_mask}",
                ]
                if gateway:
                    cmd_address.append(gateway)
                subprocess.run(cmd_address)

                # Set the DNS servers
                if dns_primary:
                    subprocess.run(
                        [
                            "netsh",
                            "interface",
                            "ipv4",
                            "set",
                            "dns",
                            f"name={adapter_name}",
                            f"static {dns_primary} primary",
                        ]
                    )
                if dns_secondary:
                    subprocess.run(
                        [
                            "netsh",
                            "interface",
                            "ipv4",
                            "set",
                            "dns",
                            f"name={adapter_name}",
                            f"static {dns_secondary} secondary",
                        ]
                    )

                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully set manual configuration for {adapter_name}",
                    QMessageBox.Ok,
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while setting manual configuration for {adapter_name}. Error: {e}",
                    QMessageBox.Ok,
                )

            QMessageBox.information(
                self,
                "Success",
                f"Successfully set manual configuration for {adapter_name}",
                QMessageBox.Ok,
            )

    def open_ping_dialog(self):
        dialog = PingResultsDialog(self)
        dialog.exec_()

    def traceroute(self):
        # Directly open the TracerouteDialog without initial popup
        dialog = TracerouteDialog(self)
        dialog.exec_()

    def open_network_share_manager(self):
        dialog = NetworkShareDialog(
            self
        )  # `self` here refers to the parent, which might be your main window or any other widget.
        dialog.exec_()

    def open_wifi_password_extract(self):
        dialog = WifiPasswordDialog(self)
        dialog.exec_()

    def open_defender_dialog(self):
        dialog = DefenderDialog(self)
        dialog.exec_()

    def on_remove_defender_dialog(self):
        dialog = RemoveDefenderDialog(self)
        dialog.exec_()

    def open_telemetry_dialog(self):
        dialog = TelemetryManagementDialog(self)
        dialog.exec_()

    def launch_system_manager(self):
        self.system_manager_popup = SystemManagerUI(self)
        self.system_manager_popup.exec_()

    def execute_windows_update(self):
        updater = WindowsUpdaterTool()
        updater.run_update(self.update_callback)

    def launch_patchmypc_tool(self):
        self.patchmypc_tool = PatchMyPCTool()
        self.patchmypc_tool.show()

    def launch_chocolatey_gui(self):
        self.chocolatey_gui = ChocolateyGUI()
        self.chocolatey_gui.show()

    def launch_winget_gui(self):
        self.winget_gui = WingetGUI()
        self.winget_gui.show()

    def OfficeSetupDialog(self):
        dialog = OfficeSetupDialog()
        dialog.exec_()

    def launch_driver_updater(self):
        dialog = DriverUpdaterManagerGUI(self)
        dialog.exec_()


tabs = {
    "System Information": [],
    "Network": [
        "Test Connection",
        "List Adapters",
        "Auto Config Network",
        "Manual Config Network",
        "Ping Hosts",
        "Trace Route",
        "Network Share Manager",
        "Wi-Fi Password Extract",
    ],
    "Security": [
        "Enable/Disable Windows Defender",
        "Remove Windows Defender - This is a one-time action",
        "Block Telemetry",
        "Services Management",
        "Microsoft Activation Script",
    ],
    "Additional Tool": [],
    "Software Management": [
        "Windows Update",
        "Windows Update Pauser",
        "PatchMyPC",
        "Chocolatey",
        "Winget",
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
        "Advanced Hardware Info",
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomUI()
    window.show()
    sys.exit(app.exec_())
