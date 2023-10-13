import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QMessageBox, QPushButton
from utils import get_disks


class DiskManager(QWidget):
    disk_dropdown: QComboBox
    disk_type_dropdown: QComboBox
    disk_details: QLabel

    def __init__(self):
        super().__init__()

        # Create layout
        layout = QVBoxLayout(self)

        # Create and configure GUI components
        # 1. Disk dropdown
        self.disk_dropdown = QComboBox(self)
        available_disks = get_disks()  # Assuming this function returns a list of available disks.
        self.disk_dropdown.addItems(available_disks)

        # 2. Disk type dropdown (MBR and GPT)
        self.disk_type_dropdown = QComboBox(self)
        self.disk_type_dropdown.addItems(["MBR", "GPT"])

        # 3. Info label for disk details
        self.disk_details = QLabel(self)

        # 4. Button to initiate the format
        self.format_button = QPushButton("Format Disk", self)
        self.format_button.clicked.connect(self.on_format_disk)  # Connect button's click event

        # Add the components to the layout
        layout.addWidget(self.disk_details)
        layout.addWidget(self.disk_dropdown)
        layout.addWidget(self.disk_type_dropdown)
        layout.addWidget(self.format_button)

        # Set the layout to the widget
        self.setLayout(layout)


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

    def run_diskpart(self, commands: list[str]) -> str:
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
