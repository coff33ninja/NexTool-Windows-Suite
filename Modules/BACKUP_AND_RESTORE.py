import os
import subprocess
import sys
import shutil
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox
# pip install PyQt5 pyqt5-tools

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

BACKUP_DIR = "C:\\AIO_BACKUP"

class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setting up main window
        self.setWindowTitle("Backup & Restore Utility")

        # Create main layout
        layout = QVBoxLayout()

        # Buttons to change backup directory
        self.change_backup_dir_button = QPushButton("Change Backup Directory", self)
        self.change_backup_dir_button.clicked.connect(self.change_backup_directory)
        layout.addWidget(self.change_backup_dir_button)

        # Buttons for WiFi
        self.backup_wifi_button = QPushButton("Backup WiFi Configurations", self)
        self.backup_wifi_button.clicked.connect(self.backup_wifi)
        layout.addWidget(self.backup_wifi_button)

        self.restore_wifi_button = QPushButton("Restore WiFi Configurations", self)
        self.restore_wifi_button.clicked.connect(self.restore_wifi)
        layout.addWidget(self.restore_wifi_button)

        # Buttons for IP Configurations
        self.backup_ip_button = QPushButton("Backup IP Configurations", self)
        self.backup_ip_button.clicked.connect(self.backup_ip)
        layout.addWidget(self.backup_ip_button)

        self.restore_ip_button = QPushButton("Restore IP Configurations", self)
        self.restore_ip_button.clicked.connect(self.restore_ip)
        layout.addWidget(self.restore_ip_button)

        # Buttons for Drivers
        self.backup_drivers_button = QPushButton("Backup Drivers", self)
        self.backup_drivers_button.clicked.connect(self.backup_drivers)
        layout.addWidget(self.backup_drivers_button)

        # Buttons to restore drivers
        self.restore_drivers_button = QPushButton("Restore Drivers", self)
        self.restore_drivers_button.clicked.connect(self.restore_drivers)
        layout.addWidget(self.restore_drivers_button)

        # Buttons to Backup User Data
        self.backup_user_data_button = QPushButton("Backup User Data", self)
        self.backup_user_data_button.clicked.connect(self.backup_user_data)
        layout.addWidget(self.backup_user_data_button)

        # ... You can add other buttons similarly ...

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def change_backup_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if new_dir:
            main_drive = os.path.splitdrive(os.environ["USERPROFILE"])[0]
            chosen_drive = os.path.splitdrive(new_dir)[0]
            if main_drive == chosen_drive:
                reply = QMessageBox.warning(self, "Warning",
                                            "It's recommended not to backup onto the same drive you're backing data off. Continue anyway?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    global BACKUP_DIR
                    BACKUP_DIR = new_dir
                    QMessageBox.information(self, "Info", f"Backup directory changed to: {BACKUP_DIR}")
            else:
                BACKUP_DIR = new_dir
                QMessageBox.information(self, "Info", f"Backup directory changed to: {BACKUP_DIR}")

    def backup_wifi(self):
        backup_dir = os.path.join(BACKUP_DIR, "NETWORK", "WIFI")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        subprocess.run(["netsh", "wlan", "export", "profile", "key=clear", f"folder={backup_dir}"])
        QMessageBox.information(self, "Info", "WiFi profiles backed up!")

    def restore_wifi(self):
        backup_dir = os.path.join(BACKUP_DIR, "NETWORK", "WIFI")
        wifi_name, _ = QFileDialog.getOpenFileName(self, "Select WiFi profile", backup_dir, "XML files (*.xml);;All Files (*)")
        if wifi_name:
            subprocess.run(["netsh", "wlan", "add", "profile", "filename", wifi_name, "user=all"])
            QMessageBox.information(self, "Info", "WiFi profile restored!")

    def backup_ip(self):
        backup_dir = os.path.join(BACKUP_DIR, "NETWORK", "Interfaces")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        with open(os.path.join(backup_dir, "netcfg.txt"), "w") as f:
            subprocess.run(["netsh", "interface", "dump"], stdout=f)
        QMessageBox.information(self, "Info", "IP configurations backed up!")

    def restore_ip(self):
        backup_dir = os.path.join(BACKUP_DIR, "NETWORK", "Interfaces")
        subprocess.run(["netsh", "exec", os.path.join(backup_dir, "netcfg.txt")])
        QMessageBox.information(self, "Info", "IP configurations restored!")

    def backup_drivers(self):
        backup_dir = os.path.join(BACKUP_DIR, "DRIVERS_EXPORT")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        subprocess.run(["powershell", "Dism", "/Online", "/Export-Driver", f"/Destination:{backup_dir}"])
        QMessageBox.information(self, "Info", "Drivers backed up!")

    def restore_drivers(self):
        backup_dir = os.path.join(BACKUP_DIR, "DRIVERS_EXPORT")
        if os.path.exists(backup_dir):
            subprocess.run(["powershell", "Dism", "/Online", "/Add-Driver", f"/Driver:{backup_dir}", "/Recurse"])
            QMessageBox.information(self, "Info", "Drivers restored!")
        else:
            QMessageBox.warning(self, "Warning", "Backup directory for drivers not found!")

    def backup_user_data(self):
        # Now, it'll back up Desktop, Documents, and Pictures. You can add more if you like.
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

        QMessageBox.information(self, "Info", "User data (Desktop, Documents, Pictures) backed up!")

    # ... Add other functions similarly ...

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec_())
