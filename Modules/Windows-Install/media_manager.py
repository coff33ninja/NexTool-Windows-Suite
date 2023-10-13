import os
import subprocess
import time  # Import the time module
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from utils import get_drive_letters


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

        def select_iso(self):
            try:
                file_name, _ = QFileDialog.getOpenFileName(self, "Select ISO File", "", "ISO Files (*.iso);;All Files (*)")
                if file_name:
                    self.iso_path_label.setText(f"Selected ISO: {file_name}")
                    self.mount_button.show()  # Only show the mount button if a file is selected
                else:
                    self.feedback_label.setText("No ISO file was selected.")
            except Exception as e:

                # If something goes wrong, print the error message to the console
                print(f"An error occurred: {e}")

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

        sources_path = Path(mounted_drive + ":").joinpath("sources")
        if os.path.exists(os.path.join(sources_path, "install.wim")):
            self.feedback_label.setText("Found install.wim in the ISO!")
        elif os.path.exists(os.path.join(sources_path, "install.esd")):
            self.feedback_label.setText("Found install.esd in the ISO!")
        else:
            self.feedback_label.setText("Could not find install.wim or install.esd in the ISO.")
        self.mount_button.hide()
        self.unmount_button.show()

    def mount_iso_cmd(self, iso_path):  # Define this method appropriately
        try:
            cmd = ["powershell", "Mount-DiskImage", f'-ImagePath "{iso_path}"']
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_mounted_drive(self, iso_path):  # Add self parameter
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
