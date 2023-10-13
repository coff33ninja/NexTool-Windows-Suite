import os
import subprocess
import threading
import time
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QApplication
from PyQt6.QtCore import QEvent, QEventLoop
from typing import cast, Protocol

from media_manager import InstallMediaManager
from disk_manager import DiskManager
from wim_manager import WIMManager

class DeploymentParentProtocol(Protocol):
    install_media_manager: InstallMediaManager

class DeploymentManager(QWidget):
    def __init__(self, main_window, wim_manager, disk_manager, install_media_manager):
        super().__init__()

        # Bindings
        self.main_window = main_window
        self.wim_manager = wim_manager
        self.disk_manager = disk_manager
        self.install_media_manager = install_media_manager

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
        iso_path = self.main_window.install_media_manager.iso_path_label.text().replace("Selected ISO: ", "")
        if not iso_path or iso_path == "No ISO selected.":
            self.append_feedback("Please select a valid ISO file before proceeding.")
            return

        mounted_drive = self.install_media_manager.get_mounted_drive(iso_path)
        if not mounted_drive:
            self.append_feedback("ISO file not found on the system. Please check the ISO file path and try again.")
            return

        wim_or_esd_path = self.wim_manager.get_wim_esd_path(mounted_drive)
        if not wim_or_esd_path:
            self.append_feedback("Neither WIM nor ESD file detected.")
            return

    def get_image_info(self, wim_or_esd_path):
        try:
            cmd = ['dism', '/Get-WimInfo', f'/WimFile:{wim_or_esd_path}']
            result = subprocess.check_output(cmd, universal_newlines=True)

            # Parsing the 'result' to extract the image indexes and names
            image_info_pattern = re.compile(r"Index\s+:\s+(\d+).*?Name\s+:\s+(.*?)\s*$", re.DOTALL | re.MULTILINE)
            matches = image_info_pattern.findall(result)

            parsed_info = [{"index": int(match[0]), "name": match[1]} for match in matches]
            return parsed_info
        except subprocess.CalledProcessError:
            self.append_feedback("Failed to fetch image info. Please check logs for more details.")
            return None

        # Deploy image
        self.deploy_image(wim_or_esd_path, image_index, target_disk)

        # Step 2: Deploying Windows image
        self.append_feedback("Deploying chosen Windows version to the selected disk...")
        time.sleep(5)  # Simulated delay. Replace with DISM or other deployment command.
        self.append_feedback("Deployment of Windows image completed!")

        # Finalize
        self.append_feedback("Windows deployment process completed successfully!")
        app_instance = cast(QApplication, QApplication.instance()).postEvent(self.deploy_button, EnableButtonEvent())

    def append_feedback(self, text):
        app_instance = cast(QApplication, QApplication.instance())
        app_instance.postEvent(self.feedback_text, AppendTextEvent(text))



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
