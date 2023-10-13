import sys
import os
import subprocess
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel, QStackedWidget, QProgressBar, QTextEdit, QGridLayout, QFormLayout, QLineEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QEvent
import psutil
from pathlib import Path

def get_disk_details(disk):
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if partition.device.startswith(disk):
            usage = psutil.disk_usage(partition.mountpoint)
            return f"Device: {partition.device}\nMountpoint: {partition.mountpoint}\nFile system type: {partition.fstype}\nTotal Size: {usage.total}\nUsed: {usage.used}\nFree: {usage.free}\nPercentage Used: {usage.percent}%"
    return f"No details found for {disk}"

def get_drive_letters():
    partitions = psutil.disk_partitions()
    return [partition.device[0] for partition in partitions]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Deployment Toolkit")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.home_widget = QWidget()
        self.central_layout = QVBoxLayout(self.home_widget)

        # Modules
        self.disk_manager = DiskManager()
        self.install_media_manager = InstallMediaManager()
        self.wim_manager = WIMManager()

        self.deployment_manager = DeploymentManager(self.wim_manager, self.disk_manager)
        self.progress_bar_manager = ProgressBarManager()

        # Adding to central layout
        self.central_layout.addWidget(self.disk_manager)
        self.central_layout.addWidget(self.install_media_manager)
        self.central_layout.addWidget(self.wim_manager)
        self.deployment_manager = DeploymentManager(self.wim_manager, self.disk_manager)
        self.central_layout.addWidget(self.progress_bar_manager)

        self.central_widget.addWidget(self.home_widget)

def get_disks():
    cmd = ['diskpart', '/s', 'list.txt']
    with open('list.txt', 'w') as f:
        f.write('list disk')
    result = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
    lines = result.split('\n')
    disks = [line.split()[1] for line in lines if line.strip().startswith('Disk')]
    return disks

class DiskManager(QWidget):
    ...
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        ...
        # Add components for Disk type choice
        self.disk_type_label = QLabel("Choose Disk Type:")
        self.disk_type_dropdown = QComboBox()
        self.disk_type_dropdown.addItems(["GPT", "MBR"])

        # Add components to layout
        layout.addWidget(self.disk_type_label)
        layout.addWidget(self.disk_type_dropdown)
        ...

    def on_format_disk(self):
        selected_disk = self.disk_dropdown.currentText()
        disk_type = self.disk_type_dropdown.currentText()

        # Display a warning to the user about formatting
        reply = QMessageBox.question(self, 'Warning', f'Are you sure you want to format {selected_disk} as {disk_type}? This action cannot be undone!', QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.prepare_disk(selected_disk, disk_type):
                self.disk_details.setText(f"Disk {selected_disk} formatted and partitioned successfully!")
            else:
                self.disk_details.setText(f"Failed to format and partition disk {selected_disk}.")

    def prepare_disk(self, disk, disk_type):
        try:
            if disk_type == "MBR":
                # Run the logic to prepare and format the disk as MBR
                return self.initialize_mbr(disk)
            elif disk_type == "GPT":
                # Run the logic to prepare and format the disk as GPT
                return self.initialize_gpt(disk)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def initialize_mbr(self, disk):
        try:
            # Create the diskpart script for MBR
            commands = [
                'select disk ' + disk,
                'clean',
                'convert mbr',
                'create partition primary',
                'format quick fs=ntfs label="Windows"',
                'assign'
            ]

            # Execute the diskpart commands
            result = self.run_diskpart(commands)

            if "successfully" in result.lower():
                return True
            else:
                return False

        except Exception as e:
            print(f"Error initializing MBR: {e}")
            return False

    def initialize_gpt(self, disk):
        try:
            # Create the diskpart script for GPT
            commands = [
                'select disk ' + disk,
                'clean',
                'convert gpt',
                'create partition efi size=100',
                'format quick fs=fat32 label="System"',
                'assign',
                'create partition msr size=16',
                'create partition primary',
                'format quick fs=ntfs label="Windows"',
                'assign',
                'create partition primary',
                'format quick fs=ntfs label="WinRE"',
                'set id="de94bba4-06d1-4d40-a16a-bfd50179d6ac"'
            ]

            # Execute the diskpart commands
            result = self.run_diskpart(commands)

            if "successfully" in result.lower():
                return True
            else:
                return False

        except Exception as e:
            print(f"Error initializing GPT: {e}")
            return False

def run_diskpart(self, commands):
    """Executes diskpart with the given list of commands."""
    try:
        # Create a temporary file to write the diskpart script
        with open("temp_diskpart_script.txt", "w") as script:
            for cmd in commands:
                script.write(cmd + "\n")

        # Use subprocess to run the diskpart with the script
        result = subprocess.check_output(['diskpart', '/s', 'temp_diskpart_script.txt'], stderr=subprocess.STDOUT, universal_newlines=True)

        # Cleanup the temporary file
        os.remove("temp_diskpart_script.txt")

        return result

    except subprocess.CalledProcessError as e:
        print(f"Error executing diskpart: {e.output}")
        return e.output

class InstallMediaManager(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # GUI Components
        self.select_iso_button = QPushButton("Select ISO File")
        self.iso_path_label = QLabel("No ISO selected.")
        self.mount_button = QPushButton("Mount ISO")
        self.feedback_label = QLabel("")
        self.unmount_button = QPushButton("Unmount ISO")
        # Initially hide the unmount button
        self.unmount_button.hide()
        self.unmount_button.clicked.connect(self.unmount_iso)

        # Add components to layout
        layout.addWidget(self.select_iso_button)
        layout.addWidget(self.iso_path_label)
        layout.addWidget(self.mount_button)
        layout.addWidget(self.unmount_button)
        layout.addWidget(self.feedback_label)

        # Connect buttons to their slots
        self.select_iso_button.clicked.connect(self.select_iso)
        self.mount_button.clicked.connect(self.mount_iso)

    def select_iso(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select ISO File", "", "ISO Files (*.iso);;All Files (*)")
            if file_name:
                self.iso_path_label.setText(f"Selected ISO: {file_name}")
        except Exception as e:
            # If something goes wrong, print the error message to the console
            print(f"An error occurred: {e}")
        self.mount_button.show()

    def mount_iso(self):
        iso_path = self.iso_path_label.text().replace("Selected ISO: ", "")

        # Get current drive letters
        before_mount = get_drive_letters()

        # Mount the ISO
        if self.mount_iso_cmd(iso_path):
            self.feedback_label.setText(f"Successfully mounted: {iso_path}")
            time.sleep(5)  # delay to ensure mounting completes
        else:
            self.feedback_label.setText(f"Failed to mount: {iso_path}")
            return  # Return early since mounting failed.

        # Find out which drive letter was used for mounting
        after_mount = get_drive_letters()
        mounted_drive = list(set(after_mount) - set(before_mount))[0]

        sources_path = os.path.join(f"{mounted_drive}:", "sources")
        if os.path.exists(os.path.join(sources_path, "install.wim")):
            self.feedback_label.setText("Found install.wim in the ISO!")
        elif os.path.exists(os.path.join(sources_path, "install.esd")):
            self.feedback_label.setText("Found install.esd in the ISO!")
        else:
            self.feedback_label.setText("Could not find install.wim or install.esd in the ISO.")
        self.mount_button.hide()
        self.unmount_button.show()

    def get_mounted_drive(iso_path):
        cmd = ["powershell", "Get-DiskImage", f'-ImagePath "{iso_path}"', "|", "Get-Volume"]
        result = subprocess.check_output(cmd, universal_newlines=True)
        # parse the result to get the drive letter, for simplicity consider it starts with a letter and ends with ":"
        drive_letter = None
        for line in result.splitlines():
            if ":" in line:
                drive_letter = line.strip().split()[0]
                break
        return drive_letter

    def unmount_iso_cmd(self, iso_path):
        try:
            cmd = ["powershell", "Dismount-DiskImage", f'-ImagePath "{iso_path}"']
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def unmount_iso(self):
        iso_path = self.iso_path_label.text().replace("Selected ISO: ", "")
        if self.unmount_iso_cmd(iso_path):
            self.feedback_label.setText(f"Successfully unmounted: {iso_path}")
        else:
            self.feedback_label.setText(f"Failed to unmount: {iso_path}")
        self.mount_button.show()
        self.unmount_button.hide()

class WIMManager(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # GUI Components
        self.wim_label = QLabel("Selected WIM/ESD: None")
        self.fetch_button = QPushButton("Fetch Windows Versions")
        self.version_dropdown = QComboBox()
        self.feedback_label = QLabel("")

        # Add components to layout
        layout.addWidget(self.wim_label)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.version_dropdown)
        layout.addWidget(self.feedback_label)

        # Connect button to slot
        self.fetch_button.clicked.connect(self.fetch_windows_versions)

    def get_wim_esd_path(mounted_drive):
        wim_path = os.path.join(mounted_drive, "sources", "install.wim")
        esd_path = os.path.join(mounted_drive, "sources", "install.esd")
        if os.path.exists(wim_path):
            return wim_path
        elif os.path.exists(esd_path):
            return esd_path
        else:
            return None

    def fetch_windows_versions(self):
        # For this example, let's get the mounted drive from InstallMediaManager
        mounted_drive = self.parent().install_media_manager.mounted_drive

        wim_file = Path(mounted_drive, "sources", "install.wim")
        esd_file = Path(mounted_drive, "sources", "install.esd")

        if os.path.exists(wim_file):
            self.wim_label.setText(f"Selected WIM: {wim_file}")
            file_path = wim_file
        elif os.path.exists(esd_file):
            self.wim_label.setText(f"Selected ESD: {esd_file}")
            file_path = esd_file
        else:
            self.feedback_label.setText("Neither WIM nor ESD file detected.")
            return

        # Extract Windows versions from the file
        cmd = ['dism', '/Get-ImageInfo', f'/ImageFile:{file_path}']
        result = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)

        # Parse the result to extract available versions
        lines = result.split('\n')
        versions = [line.split(":")[1].strip() for line in lines if "Index" in line or "Name" in line]

        # Update the dropdown
        self.version_dropdown.clear()
        self.version_dropdown.addItems(versions)

        # Provide feedback
        self.feedback_label.setText(f"Found {len(versions)//2} Windows versions in the file.")

class DeploymentManager(QWidget):
    def __init__(self, wim_manager, disk_manager):
        super().__init__()

        self.wim_manager = wim_manager
        self.disk_manager = disk_manager

        layout = QVBoxLayout(self)

        # GUI Components
        self.info_label = QLabel("Once you're ready, click the button below to start the Windows deployment.")
        self.deploy_button = QPushButton("Start Deployment")
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)

        # Add components to layout
        layout.addWidget(self.info_label)
        layout.addWidget(self.deploy_button)
        layout.addWidget(self.feedback_text)

        # Connect button to slot
        self.deploy_button.clicked.connect(self.initiate_deployment)

    def initiate_deployment(self):
        # Disable the deploy button to prevent multiple threads initiation
        self.deploy_button.setEnabled(False)
        # Start the deployment in a separate thread
        deployment_thread = threading.Thread(target=self.start_deployment)
        deployment_thread.start()

    def deploy_image(self, wim_or_esd_path, image_index, target_disk):
        try:
            cmd = ['dism', '/Apply-Image', f'/ImageFile:{wim_or_esd_path}', f'/index:{image_index}', f'/ApplyDir:{target_disk}']
            subprocess.run(cmd, check=True)
            self.append_feedback(f"Successfully deployed image to {target_disk}!")
        except subprocess.CalledProcessError:
            self.append_feedback("Failed to deploy image. Please check logs for more details.")

    def start_deployment(self):
        # Step 1: Check system requirements
        self.append_feedback("Checking system requirements...")
        time.sleep(2)  # Simulated delay. Replace with actual system check.
        self.append_feedback("System requirements met!")

        # Fetch WIM/ESD path
        mounted_drive = self.parent().install_media_manager.mounted_drive
        wim_or_esd_path = self.wim_manager.get_wim_esd_path(mounted_drive)
        if not wim_or_esd_path:
            self.append_feedback("Neither WIM nor ESD file detected.")
            return

        # Simulated fetching of version index. Replace with actual index from GUI.
        image_index = 1  # In reality, fetch the selected version from self.wim_manager.version_dropdown
        target_disk = self.disk_manager.disk_dropdown.currentText()

        # Deploy image
        self.deploy_image(wim_or_esd_path, image_index, target_disk)

        # Step 2: Deploying Windows image
        self.append_feedback("Deploying chosen Windows version to the selected disk...")
        time.sleep(5)  # Simulated delay. Replace with DISM or other deployment command.
        self.append_feedback("Deployment of Windows image completed!")

        # Finalize
        self.append_feedback("Windows deployment process completed successfully!")
        QApplication.instance().postEvent(self.deploy_button, EnableButtonEvent())

    def append_feedback(self, text):
        QApplication.instance().postEvent(self.feedback_text, AppendTextEvent(text))

    def event(self, e):
        if e.type() == AppendTextEvent.EVENT_TYPE:
            self.feedback_text.append(e.text())
            return True
        elif e.type() == EnableButtonEvent.EVENT_TYPE:
            self.deploy_button.setEnabled(True)
            return True
        return super().event(e)

class AppendTextEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text):
        super().__init__(AppendTextEvent.EVENT_TYPE)
        self._text = text

    def text(self):
        return self._text


class EnableButtonEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self):
        super().__init__(EnableButtonEvent.EVENT_TYPE)

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())

class ProgressBarManager(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setValue(0)

if __name__ == '__main__':
    main()
