import os
import subprocess
import sys
import shutil
import ctypes
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QFileDialog, QMessageBox, QSplitter, QProgressBar,
                             QTextEdit, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt
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
            None, "Error", "Administrator permissions are required to run this operation.")
        sys.exit(1)  # Exit the application with an error code


BACKUP_DIR = "C:\\BACKUP"


class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setting up main window
        self.setWindowTitle("Backup & Restore Utility")

        # Main Vertical Layout
        main_layout = QVBoxLayout()

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal, self)

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
        self.backup_location_label = QLabel(f"Backup Location: {BACKUP_DIR}")
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
        # ... Add other backup related buttons to the layout ...

    def init_restore_buttons(self, layout):
        # Buttons for WiFi
        self.restore_wifi_button = QPushButton(
            "Restore WiFi Configurations", self)
        self.restore_wifi_button.clicked.connect(
            lambda: self.threaded_backup_function(self.restore_wifi))
        layout.addWidget(self.restore_wifi_button)

        self.restore_ip_button = QPushButton("Restore IP Configurations", self)
        self.restore_ip_button.clicked.connect(self.restore_ip)
        layout.addWidget(self.restore_ip_button)

        # Buttons to restore drivers
        self.restore_drivers_button = QPushButton("Restore Drivers", self)
        self.restore_drivers_button.clicked.connect(self.restore_drivers)
        layout.addWidget(self.restore_drivers_button)

        # ... You can add other buttons similarly ...

    def threaded_backup_function(self, func, *args, **kwargs):
        def thread_func():
            try:
                result = func(*args, **kwargs)
                self.safe_update(self.on_operation_success, result)
            except Exception as e:
                self.safe_update(self.on_operation_error, e)
            finally:
                self.safe_update(self.on_operation_complete)

        thread = threading.Thread(target=thread_func)
        thread.daemon = True
        thread.start()

    def safe_update(self, func, *args, **kwargs):
        """Safely update GUI elements from another thread."""
        QApplication.instance().QMetaObject.invokeMethod(
            self, "update_func", Qt.QueuedConnection,
            (func, args, kwargs))

    def update_func(self, data):
        func, args, kwargs = data
        func(*args, **kwargs)

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

    def get_backup_dir_with_timestamp(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(BACKUP_DIR, timestamp)

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
                    global BACKUP_DIR
                    backup_dir = self.get_backup_dir_with_timestamp()
                    QMessageBox.information(
                        self, "Info", f"Backup directory changed to: {BACKUP_DIR}")
            else:
                backup_dir = self.get_backup_dir_with_timestamp()
                QMessageBox.information(
                    self, "Info", f"Backup directory changed to: {BACKUP_DIR}")
        self.backup_location_label.setText(f"Backup Location: {BACKUP_DIR}")

    def backup_wifi(self):
        try:
            self.global_progress.setValue(0)
            backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(self), "NETWORK", "WIFI")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            self.global_progress.setValue(50)
            subprocess.run(["netsh", "wlan", "export", "profile",
                           "key=clear", f"folder={backup_dir}"])
            self.global_progress.setValue(100)
            QMessageBox.information(self, "Info", "WiFi profiles backed up!")
        except Exception as e:
            self.global_progress.setValue(0)
            QMessageBox.critical(
                self, "Error", f"Failed to backup WiFi profiles: {e}")

    def restore_wifi(self):
        backup_dir = os.path.join(
            self.get_backup_dir_with_timestamp(self), "NETWORK", "WIFI")
        wifi_name, _ = QFileDialog.getOpenFileName(
            self, "Select WiFi profile", backup_dir, "XML files (*.xml);;All Files (*)")
        if wifi_name:
            subprocess.run(["netsh", "wlan", "add", "profile",
                           "filename", wifi_name, "user=all"])
            QMessageBox.information(self, "Info", "WiFi profile restored!")

    def backup_ip(self):
        try:
            self.global_progress.setValue(0)
            backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(self), "NETWORK", "Interfaces")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            self.global_progress.setValue(50)
            with open(os.path.join(backup_dir, "netcfg.txt"), "w") as f:
                subprocess.run(["netsh", "interface", "dump"], stdout=f)
            self.global_progress.setValue(100)
            QMessageBox.information(
                self, "Info", "IP configurations backed up!")
        except Exception as e:
            self.global_progress.setValue(0)
            QMessageBox.critical(
                self, "Error", f"Failed to backup IP configurations: {e}")

    def restore_ip(self):
        backup_dir = os.path.join(
            self.get_backup_dir_with_timestamp(self), "NETWORK", "Interfaces")
        subprocess.run(
            ["netsh", "exec", os.path.join(backup_dir, "netcfg.txt")])
        QMessageBox.information(self, "Info", "IP configurations restored!")

    def backup_drivers(self):
        try:
            self.global_progress.setValue(0)
            backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(self), "DRIVERS_EXPORT")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            self.global_progress.setValue(50)
            subprocess.run(["powershell", "Dism", "/Online",
                           "/Export-Driver", f"/Destination:{backup_dir}"])
            self.global_progress.setValue(100)
            QMessageBox.information(self, "Info", "Drivers backed up!")
        except Exception as e:
            self.global_progress.setValue(0)
            QMessageBox.critical(
                self, "Error", f"Failed to backup drivers: {e}")

    def restore_drivers(self):
        backup_dir = os.path.join(
            self.get_backup_dir_with_timestamp(self), "DRIVERS_EXPORT")
        if os.path.exists(backup_dir):
            subprocess.run(["powershell", "Dism", "/Online",
                           "/Add-Driver", f"/Driver:{backup_dir}", "/Recurse"])
            QMessageBox.information(self, "Info", "Drivers restored!")
        else:
            QMessageBox.warning(
                self, "Warning", "Backup directory for drivers not found!")

    def backup_user_data(self):
        try:
            self.global_progress.setValue(0)
            user_dirs = ["Desktop", "Documents", "Pictures"]
            for u_dir in user_dirs:
                user_path = os.path.join(os.environ["USERPROFILE"], u_dir)
                backup_path = os.path.join(BACKUP_DIR, "USER_DATA", u_dir)
                if not os.path.exists(backup_path):
                    os.makedirs(backup_path)
                for item in os.listdir(user_path):
                    s = os.path.join(user_path, item)
                    d = os.path.join(backup_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, False, None)
                    else:
                        shutil.copy2(s, d)
            self.global_progress.setValue(100)
            QMessageBox.information(
                self, "Info", "User data (Desktop, Documents, Pictures) backed up!")
        except Exception as e:
            self.global_progress.setValue(0)
            QMessageBox.critical(
                self, "Error", f"Failed to backup user data: {e}")

    def backup_thunderbird(self):
        try:
            self.global_progress.setValue(0)
            user_profile = os.environ["USERPROFILE"]
            thunderbird_profile = os.path.join(
                user_profile, "AppData", "Roaming", "Thunderbird", "Profiles")

            backup_dir = os.path.join(
                self.get_backup_dir_with_timestamp(self), "EMAIL", "Thunderbird")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            self.global_progress.setValue(50)

            for item in os.listdir(thunderbird_profile):
                s = os.path.join(thunderbird_profile, item)
                d = os.path.join(backup_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, False, None)

            self.global_progress.setValue(100)
            QMessageBox.information(
                self, "Info", "Thunderbird data backed up!")
        except Exception as e:
            self.global_progress.setValue(0)
            QMessageBox.critical(
                self, "Error", f"Failed to backup Thunderbird data: {e}")

    def backup_outlook(self):
        user_profile = os.environ["USERPROFILE"]

        # Backup PST files
        outlook_data = os.path.join(user_profile, "Documents", "Outlook Files")
        backup_dir = os.path.join(
            self.get_backup_dir_with_timestamp(self), "EMAIL", "Outlook")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        for item in os.listdir(outlook_data):
            if item.endswith(('.pst', '.ost')):
                s = os.path.join(outlook_data, item)
                d = os.path.join(backup_dir, item)
                shutil.copy2(s, d)

        # Backup Signatures
        sig_source = os.path.join(
            user_profile, "AppData", "Roaming", "Microsoft", "Signatures")
        sig_dest = os.path.join(backup_dir, "Signatures")
        if os.path.exists(sig_source):
            shutil.copytree(sig_source, sig_dest)

        # Backup Templates
        template_source = os.path.join(
            user_profile, "AppData", "Roaming", "Microsoft", "Templates")
        template_dest = os.path.join(backup_dir, "Templates")
        if os.path.exists(template_source):
            shutil.copytree(template_source, template_dest)

        # Backup Outlook registry settings
        # This is a bit more complex and may require third-party libraries like 'winreg' to interact with the Windows Registry.

        # NOTE: The above doesn't fully cover every setting, configuration, or customization that a user might have.
        # But it does get the main data and some personal customizations.

        QMessageBox.information(
            self, "Info", "Outlook data and some configurations backed up!")

    # Browser Backup for Chrome and Firefox
    def backup_browser(self):
        try:
            self.global_progress.setValue(0)

            # Backup Chrome
            chrome_path = os.path.join(
                os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")
            if os.path.exists(chrome_path):
                backup_dir = os.path.join(
                    self.get_backup_dir_with_timestamp(self), "BROWSER", "Chrome")
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                shutil.copytree(chrome_path, backup_dir)
                self.global_progress.setValue(50)
                QMessageBox.information(
                    self, "Info", "Chrome browser data backed up!")

            # Backup Firefox
            firefox_path = os.path.join(
                os.environ["APPDATA"], "Mozilla", "Firefox", "Profiles")
            if os.path.exists(firefox_path):
                backup_dir = os.path.join(
                    self.get_backup_dir_with_timestamp(self), "BROWSER", "Firefox")
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                for item in os.listdir(firefox_path):
                    s = os.path.join(firefox_path, item)
                    d = os.path.join(backup_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                self.global_progress.setValue(100)
                QMessageBox.information(
                    self, "Info", "Firefox browser data backed up!")
        except Exception as e:
            self.global_progress.setValue(0)
            QMessageBox.critical(
                self, "Error", f"Failed to backup browser data: {e}")

    # ... Add other functions similarly ...


if __name__ == '__main__':
    ensure_admin_rights()  # Ensure we have admin rights before running our app

    app = QApplication(sys.argv)
    try:
        window = BackupApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")
