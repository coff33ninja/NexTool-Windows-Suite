import os
import subprocess
import sys
import shutil
import ctypes
import threading
import comtypes.client
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QMessageBox, QSplitter, QProgressBar,
                             QTextEdit, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
# pip install PyQt5 pyqt5-tools


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def ensure_admin_rights():
    if not is_admin():
        # Try to re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)  # Exit the current non-elevated process

    # If after elevation attempt we're still not admin
    if not is_admin():
        QMessageBox.critical(
            None, "Error", "Administrator permissions are required to run this operation.") # type: ignore
        sys.exit(1)  # Exit the application with an error code


backup_dir = "C:\\BACKUP"


class BackupApp(QMainWindow):
    operationCompletedSignal = pyqtSignal(str)
    operationErrorSignal = pyqtSignal(str)
    showInfoBoxSignal = pyqtSignal(str, str)
    showErrorBoxSignal = pyqtSignal(str, str)
    showWarningBoxSignal = pyqtSignal(str, str)
    updateSignal = pyqtSignal()
    progressUpdateSignal = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.operationCompletedSignal.connect(self.on_operation_success)
        self.operationErrorSignal.connect(self.on_operation_error)
        self.showInfoBoxSignal.connect(self.show_info_box)
        self.showErrorBoxSignal.connect(self.show_error_box)
        self.showWarningBoxSignal.connect(self.show_warning_box)
        self.session_backup_dir = self.get_backup_dir_with_timestamp()
        self.updateSignal.connect(self.on_operation_complete)
        self.backup_dir = "C:\\BACKUP"

        # Setting up main window
        self.setWindowTitle("Backup & Restore Utility")

        # Main Vertical Layout
        main_layout = QVBoxLayout()

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal, self)  # type: ignore

        # Backup Layout
        backup_layout = QVBoxLayout()
        self.backup_widget = QWidget()
        self.backup_widget.setLayout(backup_layout)
        self.init_backup_buttons(backup_layout)
        self.splitter.addWidget(self.backup_widget)

        # Restore Layout
        restore_layout = QVBoxLayout()
        self.restore_widget = QWidget()
        self.restore_widget.setLayout(restore_layout)
        self.init_restore_buttons(restore_layout)
        self.splitter.addWidget(self.restore_widget)

        # Display Backup Location
        self.backup_location_label = QLabel(f"Backup Location: {self.backup_dir}")
        main_layout.addWidget(self.backup_location_label)

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

        # Progress bar and Task Output
        self.global_progress = QProgressBar(self)
        main_layout.addWidget(self.global_progress)

        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        main_layout.addWidget(self.output_display)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def init_backup_buttons(self, layout):
        # Buttons to change backup directory
        self.change_backup_dir_button = QPushButton(
            "Change Backup Directory", self)
        self.change_backup_dir_button.clicked.connect(
            self.change_backup_directory)
        layout.addWidget(self.change_backup_dir_button)

        # Buttons for WiFi
        self.backup_wifi_button = QPushButton(
            "Backup WiFi Configurations", self)
        self.backup_wifi_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_wifi))
        layout.addWidget(self.backup_wifi_button)

        # Buttons for IP Configurations
        self.backup_ip_button = QPushButton("Backup IP Configurations", self)
        self.backup_ip_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_ip))
        layout.addWidget(self.backup_ip_button)

        # Buttons for Drivers
        self.backup_drivers_button = QPushButton("Backup Drivers", self)
        self.backup_drivers_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_drivers))
        layout.addWidget(self.backup_drivers_button)

        # Buttons to Backup User Data
        self.backup_user_data_button = QPushButton("Backup User Data", self)
        self.backup_user_data_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_user_data))
        layout.addWidget(self.backup_user_data_button)

        # Buttons to Backup Thunderbird
        self.backup_thunderbird_button = QPushButton("Backup Thunderbird Data", self)
        self.backup_thunderbird_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_thunderbird))
        layout.addWidget(self.backup_thunderbird_button)

        # Buttons to Backup Outlook Data
        self.backup_outlook_button = QPushButton("Backup Outlook Data", self)
        self.backup_outlook_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_outlook))
        layout.addWidget(self.backup_outlook_button)

        # Buttons to Backup Browser Data
        self.backup_browser_button = QPushButton("Backup Browser Data", self)
        self.backup_browser_button.clicked.connect(
            lambda: self.threaded_backup_function(self.backup_browser))
        layout.addWidget(self.backup_browser_button)

    def init_restore_buttons(self, layout):
        # Buttons for WiFi
        self.restore_wifi_button = QPushButton(
            "Restore WiFi Configurations", self)
        self.restore_wifi_button.clicked.connect(
            lambda: self.threaded_restore_function(self.restore_wifi))
        layout.addWidget(self.restore_wifi_button)

        self.restore_ip_button = QPushButton("Restore IP Configurations", self)
        self.restore_ip_button.clicked.connect(self.restore_ip)
        layout.addWidget(self.restore_ip_button)

        # Buttons to restore drivers
        self.restore_drivers_button = QPushButton("Restore Drivers", self)
        self.restore_drivers_button.clicked.connect(
        lambda: self.threaded_restore_function(self.restore_drivers))
        layout.addWidget(self.restore_drivers_button)

        # Buttons to Restore Thunderbird Data
        self.restore_thunderbird_button = QPushButton("Restore Thunderbird Data", self)
        self.restore_thunderbird_button.clicked.connect(
            lambda: self.threaded_restore_function(self.restore_thunderbird))
        layout.addWidget(self.restore_thunderbird_button)

        # Buttons to Restore Outlook Data
        self.restore_outlook_button = QPushButton("Restore Outlook Data", self)
        self.restore_outlook_button.clicked.connect(self.restore_outlook)
        layout.addWidget(self.restore_outlook_button)

        # Buttons to Restore Browser Data
        self.restore_browser_button = QPushButton("Restore Browser Data", self)
        self.restore_browser_button.clicked.connect(self.restore_browser)
        layout.addWidget(self.restore_browser_button)

    def show_info_box(self, title, message):
        QMessageBox.information(self, title, message)

    def show_error_box(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_warning_box(self, title, message):
        QMessageBox.warning(self, title, message)

    def threaded_backup_function(self, func, *args, **kwargs):
        def thread_func():
            try:
                result = func(*args, **kwargs)
                self.operationCompletedSignal.emit(result)
            except Exception as e:
                self.operationErrorSignal.emit(str(e))
            finally:
                self.safe_update(self.on_operation_complete)

        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()

    def threaded_restore_function(self, func, *args, **kwargs):
        self.threaded_backup_function(func, *args, **kwargs)

    def on_operation_success(self, result=None):
        """Called when the operation is successful."""
        self.output_display.append("Operation completed successfully!")
        # You can further use 'result' if your operations return any results

    def on_operation_error(self, error):
        """Called when the operation encounters an error."""
        self.output_display.append(f"Error: {error}")
        QMessageBox.critical(self, "Error", str(error))

    def on_operation_complete(self):
        """Called when the operation is complete."""
        self.global_progress.setValue(100)

    def safe_update(self, func=None):
        """Emit a signal to safely update the GUI from another thread."""
        self.updateSignal.emit()
        if func:
            func()

    def get_backup_dir_with_timestamp(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(backup_dir, timestamp)

    def change_backup_directory(self):
        new_dir = QFileDialog.getExistingDirectory(
            self, "Select Backup Directory")
        if new_dir:
            main_drive = os.path.splitdrive(os.environ["USERPROFILE"])[0]
            chosen_drive = os.path.splitdrive(new_dir)[0]
            if main_drive == chosen_drive:
                reply = QMessageBox.warning(self, "Warning",
                                            "It's recommended not to backup onto the same drive you're backing data off. Continue anyway?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.backup_dir = self.get_backup_dir_with_timestamp()
                    QMessageBox.information(
                        self, "Info", f"Backup directory changed to: {self.backup_dir}")
            else:
                self.backup_dir = self.get_backup_dir_with_timestamp()
                QMessageBox.information(
                    self, "Info", f"Backup directory changed to: {self.backup_dir}")
        self.backup_location_label.setText(f"Backup Location: {self.backup_dir}")

    def update_progress(self, progress):
        self.global_progress.setValue(progress)

    def backup_wifi(self):
        try:
            self.global_progress.setValue(0)
            action_backup_dir = os.path.join(
                self.session_backup_dir, "NETWORK", "WIFI")
            if not os.path.exists(action_backup_dir):
                os.makedirs(action_backup_dir)
            self.global_progress.setValue(50)
            subprocess.run(["netsh", "wlan", "export", "profile",
                           "key=clear", f"folder={self.backup_dir}"])
            self.global_progress.setValue(100)
            self.showInfoBoxSignal.emit("Info", "WiFi profiles backed up!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", f"Failed to backup WiFi profiles: {e}")

    def restore_wifi(self):
        try:
            wifi_backup_dir = os.path.join(
                self.backup_dir, "NETWORK", "WIFI")
            wifi_name, _ = QFileDialog.getOpenFileName(
                self, "Select WiFi profile", wifi_backup_dir, "XML files (*.xml);;All Files (*)")
            if wifi_name:
                subprocess.run(["netsh", "wlan", "add", "profile",
                                "filename", wifi_name, "user=all"])
            self.showInfoBoxSignal.emit("Info", "WiFi profile restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))

    def backup_ip(self):
        try:
            self.global_progress.setValue(0)
            action_backup_dir = os.path.join(
                self.session_backup_dir, "NETWORK", "Interfaces")
            if not os.path.exists(action_backup_dir):
                os.makedirs(action_backup_dir)
            self.global_progress.setValue(50)
            with open(os.path.join(action_backup_dir, "netcfg.txt"), "w") as f:
                subprocess.run(["netsh", "interface", "dump"], stdout=f)
            self.global_progress.setValue(100)
            self.showInfoBoxSignal.emit("Info", "IP configurations backed up!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", f"Failed to backup IP configurations: {e}")

    def restore_ip(self):
        try:
            self.backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(), "NETWORK", "Interfaces")
            subprocess.run(
                ["netsh", "exec", os.path.join(self.backup_dir, "netcfg.txt")])
            self.showInfoBoxSignal.emit("Info", "IP configurations restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))

    def backup_drivers(self):
        try:
            self.global_progress.setValue(0)
            action_backup_dir = os.path.join(
                self.session_backup_dir, "DRIVERS_EXPORT")
            if not os.path.exists(action_backup_dir):
                os.makedirs(action_backup_dir)
            self.global_progress.setValue(50)
            subprocess.run(["powershell", "Dism", "/Online",
                            "/Export-Driver", f"/Destination:{action_backup_dir}"])
            self.global_progress.setValue(100)
            self.showInfoBoxSignal.emit("Info", "Drivers backed up!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", f"Failed to backup drivers: {e}")

    def restore_drivers(self):
        try:
            self.global_progress.setValue(0)
            self.backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(), "DRIVERS_EXPORT")
            if os.path.exists(self.backup_dir):
                self.global_progress.setValue(50)
                subprocess.run(["powershell", "Dism", "/Online",
                               "/Add-Driver", f"/Driver:{self.backup_dir}", "/Recurse"])
            self.global_progress.setValue(100)
            self.showInfoBoxSignal.emit("Info", "Drivers restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))

    def backup_user_data(self):
        try:
            self.global_progress.setValue(0)
            action_backup_dir = os.path.join(
                self.session_backup_dir, "USER_DATA")
            if not os.path.exists(action_backup_dir):
                os.makedirs(action_backup_dir)
                total_files = sum([len(files) for _, _, files in os.walk(os.environ["USERPROFILE"])])
                files_copied = 0

                user_dirs = ["Desktop", "Documents", "Pictures"]
                for u_dir in user_dirs:
                    user_dir_path = os.path.join(os.environ["USERPROFILE"], u_dir)
                    backup_dir_path = os.path.join(self.backup_dir, "USER_DATA", u_dir)

                    for item in os.listdir(user_dir_path):
                        source = os.path.join(user_dir_path, item)
                        destination = os.path.join(backup_dir_path, item)

                        if os.path.isdir(source):
                            shutil.copytree(source, destination, False, None)
                        else:
                            shutil.copy2(source, destination)

                        files_copied += 1
                        progress = (files_copied / total_files) * 100
                        self.progressUpdateSignal.emit(int(progress))

            self.showInfoBoxSignal.emit("Info", "User data backed up!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", f"Failed to backup user data: {e}")

    def restore_user_data(self):
        try:
            # Prompt user to select a backup directory.
            backup_dir_selected = QFileDialog.getExistingDirectory(self, "Select the directory where your backup resides")
#   "Select the directory where your backup resides", self)
            # If the user cancels the directory selection, return.
            if not backup_dir_selected:
                return

            # Check if the selected directory has the required structure (for example, USER_DATA folder).
            if not os.path.exists(os.path.join(backup_dir_selected, "USER_DATA")):
                self.showErrorBoxSignal.emit("Error", "Selected directory doesn't seem to have a valid backup.")
                return

            self.backup_dir = backup_dir_selected

            reply = QMessageBox.question(self, "Restore User Data",
                "Would you like to restore the profile to its original locations? "
                "If No, a backup folder will be created at C:\\BACKUP and a shortcut placed on your desktop.",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes)

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                total_files = sum([len(files) for _, _, files in os.walk(os.path.join(self.backup_dir, "USER_DATA"))])
                files_restored = 0

                user_dirs = ["Desktop", "Documents", "Pictures"]
                for u_dir in user_dirs:
                    backup_dir_path = os.path.join(self.backup_dir, "USER_DATA", u_dir)
                    user_dir_path = os.path.join(os.environ["USERPROFILE"], u_dir)

                    for item in os.listdir(backup_dir_path):
                        source = os.path.join(backup_dir_path, item)
                        destination = os.path.join(user_dir_path, item)

                        if os.path.isdir(source):
                            if os.path.exists(destination):
                                shutil.rmtree(destination)
                            shutil.copytree(source, destination)
                        else:
                            shutil.copy2(source, destination)

                        files_restored += 1
                        progress = (files_restored / total_files) * 100
                        self.progressUpdateSignal.emit(int(progress))

            self.showInfoBoxSignal.emit("Info", "User data restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))

    def create_shortcut(self, target, title, shortcut_path):
        shell = comtypes.client.CreateObject("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WindowStyle = 3  # 7 - Minimized, 3 - Maximized, 1 - Normal
        shortcut.save()

    def backup_thunderbird(self):
        try:
            self.global_progress.setValue(0)
            action_backup_dir = os.path.join(
        self.session_backup_dir, "EMAIL", "Thunderbird")
            if not os.path.exists(action_backup_dir):
                os.makedirs(action_backup_dir)
            user_profile = os.environ["USERPROFILE"]
            thunderbird_profile = os.path.join(
                user_profile, "AppData", "Roaming", "Thunderbird", "Profiles")

            self.backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(), "EMAIL", "Thunderbird")
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)

            self.global_progress.setValue(50)

            total_files = sum([len(files) for _, _, files in os.walk(thunderbird_profile)])
            files_copied = 0

            for item in os.listdir(thunderbird_profile):
                s = os.path.join(thunderbird_profile, item)
                d = os.path.join(self.backup_dir, item)
                shutil.copy2(s, d)
                files_copied += 1
                progress = (files_copied / total_files) * 100
                self.progressUpdateSignal.emit(int(progress))

            self.showInfoBoxSignal.emit("Info", "Thunderbird data backed up!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", f"Failed to backup Thunderbird data: {e}")

    def restore_thunderbird(self):
        try:
            self.global_progress.setValue(0)

            # Prompt user to select a backup directory.
            backup_dir_selected = QFileDialog.getExistingDirectory(self, "Select the directory where your backup resides")
            if not backup_dir_selected:
                return

            # Check if the selected directory has Thunderbird backup
            if not os.path.exists(os.path.join(backup_dir_selected, "EMAIL", "Thunderbird")):
                self.showErrorBoxSignal.emit("Error", "Selected directory doesn't seem to have a valid Thunderbird backup.")
                return

            # Define the source and target directories
            source_dir = os.path.join(backup_dir_selected, "EMAIL", "Thunderbird")
            target_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Thunderbird", "Profiles")

            # Perform the restore operation
            total_files = sum([len(files) for _, _, files in os.walk(source_dir)])
            files_restored = 0

            for item in os.listdir(source_dir):
                s = os.path.join(source_dir, item)
                d = os.path.join(target_dir, item)
                shutil.copy2(s, d)
                files_restored += 1
                progress = (files_restored / total_files) * 100
                self.progressUpdateSignal.emit(int(progress))

            self.showInfoBoxSignal.emit("Info", "Thunderbird data restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))


    def backup_outlook(self):
        user_profile = os.environ["USERPROFILE"]

        # Backup PST files
        outlook_data = os.path.join(user_profile, "Documents", "Outlook Files")
        self.backup_dir = os.path.join(
            self.get_backup_dir_with_timestamp(), "EMAIL", "Outlook")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        for item in os.listdir(outlook_data):
            if item.endswith(('.pst', '.ost')):
                s = os.path.join(outlook_data, item)
                d = os.path.join(self.backup_dir, item)
                shutil.copy2(s, d)

        # Backup Signatures
        sig_source = os.path.join(
            user_profile, "AppData", "Roaming", "Microsoft", "Signatures")
        sig_dest = os.path.join(self.backup_dir, "Signatures")
        if os.path.exists(sig_source):
            shutil.copytree(sig_source, sig_dest)

        # Backup Templates
        template_source = os.path.join(
            user_profile, "AppData", "Roaming", "Microsoft", "Templates")
        template_dest = os.path.join(self.backup_dir, "Templates")
        if os.path.exists(template_source):
            shutil.copytree(template_source, template_dest)

        # Backup Outlook registry settings
        # This is a bit more complex and may require third-party libraries like 'winreg' to interact with the Windows Registry.

        # NOTE: The above doesn't fully cover every setting, configuration, or customization that a user might have.
        # But it does get the main data and some personal customizations.

        QMessageBox.information(
            self, "Info", "Outlook data and some configurations backed up!")

    def restore_outlook(self):
        try:
            # Prompt user to select a backup directory.
            backup_dir_selected = QFileDialog.getExistingDirectory(self, "Select the directory where your backup resides")
            if not backup_dir_selected:
                return

            # Check if the selected directory has Outlook backup
            if not os.path.exists(os.path.join(backup_dir_selected, "EMAIL", "Outlook")):
                self.showErrorBoxSignal.emit("Error", "Selected directory doesn't seem to have a valid Outlook backup.")
                return

            source_dir = os.path.join(backup_dir_selected, "EMAIL", "Outlook")

            # Restoring PST files
            outlook_data = os.path.join(os.environ["USERPROFILE"], "Documents", "Outlook Files")
            for item in os.listdir(source_dir):
                if item.endswith(('.pst', '.ost')):
                    s = os.path.join(source_dir, item)
                    d = os.path.join(outlook_data, item)
                    shutil.copy2(s, d)

            # Restoring Signatures
            sig_source = os.path.join(source_dir, "Signatures")
            sig_dest = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Microsoft", "Signatures")
            if os.path.exists(sig_source):
                if os.path.exists(sig_dest):
                    shutil.rmtree(sig_dest)
                shutil.copytree(sig_source, sig_dest)

            # Restoring Templates
            template_source = os.path.join(source_dir, "Templates")
            template_dest = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Microsoft", "Templates")
            if os.path.exists(template_source):
                if os.path.exists(template_dest):
                    shutil.rmtree(template_dest)
                shutil.copytree(template_source, template_dest)

            # Note: The Outlook registry settings restoration is still complex and is not covered here.

            self.showInfoBoxSignal.emit("Info", "Outlook data restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))


    # Browser Backup for Chrome and Firefox
    def backup_browser(self):
        try:
            self.global_progress.setValue(0)

            # Backup Chrome
            chrome_path = os.path.join(
                os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")
            if os.path.exists(chrome_path):
                self.backup_dir = os.path.join(
                    self.get_backup_dir_with_timestamp(), "BROWSER", "Chrome")
                if not os.path.exists(self.backup_dir):
                    os.makedirs(self.backup_dir)

                total_files_chrome = sum([len(files) for _, _, files in os.walk(chrome_path)])
                files_copied_chrome = 0

                for item in os.listdir(chrome_path):
                    s = os.path.join(chrome_path, item)
                    d = os.path.join(self.backup_dir, item)
                    shutil.copy2(s, d)
                    files_copied_chrome += 1
                    progress_chrome = (files_copied_chrome / total_files_chrome) * 50  # Assuming Chrome backup is 50% of the whole process
                    self.progressUpdateSignal.emit(int(progress_chrome))
                    self.showInfoBoxSignal.emit("Info", "Chrome browser data backed up!")

            # Backup Firefox
            firefox_path = os.path.join(
                os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles")
            if os.path.exists(firefox_path):
                self.backup_dir = os.path.join(
                    self.get_backup_dir_with_timestamp(), "BROWSER", "Firefox")
                if not os.path.exists(self.backup_dir):
                    os.makedirs(self.backup_dir)

                total_files_firefox = sum([len(files) for _, _, files in os.walk(firefox_path)])
                files_copied_firefox = 0

                for item in os.listdir(firefox_path):
                    s = os.path.join(firefox_path, item)
                    d = os.path.join(self.backup_dir, item)
                    shutil.copy2(s, d)
                    files_copied_firefox += 1
                    progress_firefox = 50 + (files_copied_firefox / total_files_firefox) * 50  # Firefox starts from 50% to 100%
                    self.progressUpdateSignal.emit(int(progress_firefox))

            self.showInfoBoxSignal.emit("Info", "Browser data backed up!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", f"Failed to backup browser data: {e}")

    # ... Add other functions similarly ...

    def restore_browser(self):
        try:
            # Prompt user to select a backup directory.
            backup_dir_selected = QFileDialog.getExistingDirectory(self, "Select the directory where your backup resides")
            if not backup_dir_selected:
                return

            # Restore Chrome Data
            if os.path.exists(os.path.join(backup_dir_selected, "BROWSER", "Chrome")):
                source_dir = os.path.join(backup_dir_selected, "BROWSER", "Chrome")
                chrome_dest = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")

                # Advise user to close Chrome before proceeding
                reply = QMessageBox.warning(self, "Warning",
                        "Please close all instances of Chrome before proceeding. Continue?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    if os.path.exists(chrome_dest):
                        shutil.rmtree(chrome_dest)
                        # Restoring Chrome Data
                        chrome_backup_path = os.path.join(backup_dir_selected, "BROWSER", "Chrome")
                        total_files_chrome = sum([len(files) for _, _, files in os.walk(chrome_backup_path)])
                        files_restored_chrome = 0

                        for item in os.listdir(chrome_backup_path):
                            s = os.path.join(chrome_backup_path, item)
                            d = os.path.join(chrome_dest, item)
                            shutil.copy2(s, d)
                            files_restored_chrome += 1
                            progress_chrome = (files_restored_chrome / total_files_chrome) * 50  # Assuming Chrome restore is 50% of the whole process
                            self.progressUpdateSignal.emit(int(progress_chrome))

            # Restore Firefox Data
            if os.path.exists(os.path.join(backup_dir_selected, "BROWSER", "Firefox")):
                source_dir = os.path.join(backup_dir_selected, "BROWSER", "Firefox")
                firefox_dest = os.path.join(os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles")

                # Advise user to close Firefox before proceeding
                reply = QMessageBox.warning(self, "Warning",
                        "Please close all instances of Firefox before proceeding. Continue?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    for item in os.listdir(source_dir):
                        s = os.path.join(source_dir, item)
                        d = os.path.join(firefox_dest, item)
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        # Restoring Firefox Data
                        firefox_backup_path = os.path.join(backup_dir_selected, "BROWSER", "Firefox")
                        total_files_firefox = sum([len(files) for _, _, files in os.walk(firefox_backup_path)])
                        files_restored_firefox = 0

                        for item in os.listdir(firefox_backup_path):
                            s = os.path.join(firefox_backup_path, item)
                            d = os.path.join(firefox_dest, item)
                            shutil.copy2(s, d)
                            files_restored_firefox += 1
                            progress_firefox = 50 + (files_restored_firefox / total_files_firefox) * 50  # Firefox starts from 50% to 100%
                            self.progressUpdateSignal.emit(int(progress_firefox))

            self.showInfoBoxSignal.emit("Info", "Browser data restored!")
        except Exception as e:
            self.showErrorBoxSignal.emit("Error", str(e))

if __name__ == '__main__':
    ensure_admin_rights()  # Ensure we have admin rights before running our app

    app = QApplication(sys.argv)
    try:
        window = BackupApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
