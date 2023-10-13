import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
from media_manager import InstallMediaManager
from typing import Protocol, cast

class InstallMediaManagerMixin(Protocol):
    install_media_manager: InstallMediaManager

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

    def get_wim_esd_path(self, mounted_drive):
        wim_path = Path(mounted_drive, "sources", "install.wim")
        esd_path = Path(mounted_drive, "sources", "install.esd")
        if wim_path.exists():
            return wim_path
        elif esd_path.exists():
            return esd_path
        else:
            return None

    def fetch_windows_versions(self):
        try:
            parent = cast(InstallMediaManagerMixin, self.parent())  # Cast the parent
            assert hasattr(parent, "install_media_manager"), "Parent must have install_media_manager attribute"

            iso_path = parent.install_media_manager.iso_path_label.text().replace("Selected ISO: ", "")
            mounted_drive = parent.install_media_manager.get_mounted_drive(iso_path)

            # Fetch the path of the WIM/ESD file
            file_path = self.get_wim_esd_path(mounted_drive)

            # Display the detected WIM/ESD file
            if "wim" in str(file_path):
                self.wim_label.setText(f"Selected WIM: {file_path}")
            else:
                self.wim_label.setText(f"Selected ESD: {file_path}")

            # Extract Windows versions from the file
            cmd = ['dism', '/Get-ImageInfo', f'/ImageFile:{file_path}']
            try:
                result = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                self.feedback_label.setText("Failed to fetch Windows versions.")
                return

            # Parse the result to extract available versions
            lines = result.split('\n')
            versions = [line.split(":")[1].strip() for line in lines if "Index" in line or "Name" in line]

            # Update the dropdown
            self.version_dropdown.clear()
            self.version_dropdown.addItems(versions)

            # Provide feedback
            self.feedback_label.setText(f"Found {len(versions)//2} Windows versions in the file.")

        except Exception as e:
            self.feedback_label.setText(f"Error: {e}")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    window = WIMManager()
    window.show()
    app.exec()
