import ctypes
import sys
import os
import subprocess
import tempfile
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit,
                             QLabel, QFileDialog, QMessageBox, QComboBox, QProgressBar)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class DeploymentGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Label for introduction and instructions
        self.label = QLabel('Welcome to the Windows Deployment Tool.\nPlease follow the instructions and click on the buttons accordingly.', self)

        # Console-like TextEdit to display messages/output
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)

        # Disk type ComboBox
        self.diskTypeCombo = QComboBox(self)
        self.diskTypeCombo.addItems(["GPT", "MBR"])
        self.label_disk_type = QLabel('Choose disk type:', self)

        # Disk selection ComboBox
        self.diskSelectionCombo = QComboBox(self)
        self.diskSelectionCombo.addItems(self.get_disks())  # populate with available disks
        self.label_disk_selection = QLabel('Choose a disk:', self)

        # Button to select .wim file
        self.wimButton = QPushButton('Select install.wim file', self)
        self.wimButton.clicked.connect(self.selectWIMFile)

        # Placeholder button for starting the deployment (will run the batch script or other operations)
        self.deployButton = QPushButton('Start Deployment', self)
        self.deployButton.clicked.connect(self.startDeployment)
        self.deployButton.setEnabled(False)  # Disable the button initially

        # Add a "Refresh Disks" button
        self.refreshButton = QPushButton('Refresh Disks', self)
        self.refreshButton.clicked.connect(self.refresh_disks)

        # Adding all the widgets to the layout
        layout.addWidget(self.label)
        layout.addWidget(self.console)
        layout.addWidget(self.label_disk_type)
        layout.addWidget(self.diskTypeCombo)
        layout.addWidget(self.label_disk_selection)
        layout.addWidget(self.diskSelectionCombo)
        layout.addWidget(self.wimButton)
        layout.addWidget(self.deployButton)
        layout.addWidget(self.refreshButton)  # Add the refresh button to the layout

        self.setLayout(layout)
        self.setWindowTitle('Windows Deployment Tool')
        self.show()

    def selectWIMFile(self):
        options = QFileDialog.Options()
        self.filePath, _ = QFileDialog.getOpenFileName(self, "Select install.wim", "", "WIM Files (*.wim);;All Files (*)", options=options)
        if self.filePath:
            self.console.append(f"Selected {self.filePath} for deployment.")
            self.deployButton.setEnabled(True)  # Enable the button here after file is selected

    def startDeployment(self):
        # Checking for privileges
        if not self.check_privileges():
            return

        # Before any other deployment steps, validate disk selection:
        selected_disk = self.diskSelectionCombo.currentText()
        if selected_disk in ["Disk 0"]:  # Adjust based on how primary/system disks are listed in your application
            QMessageBox.critical(self, "Error", "You've selected the primary/system disk! Please choose another disk.")
            return

        # Warning the user about disk initialization
        reply = QMessageBox.question(self, 'Warning',
            "Proceeding will initialize the selected disk, which can result in data loss. Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Proceed with Deployment
            self.initialize_disk()  # Initialize the selected disk
            success = self.deploy_windows_image()  # Apply the Windows image

            if success:
                # Displaying a success message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Deployment Completed!")
                msg.setWindowTitle("Info")
                msg.exec_()
            else:
                # Displaying an error message
                QMessageBox.critical(self, "Error", "Deployment failed!")

    def refresh_disks(self):
        """Refreshes the list of available disks in the ComboBox."""
        available_disks = self.get_disks()
        self.diskSelectionCombo.clear()  # Clear the existing items
        self.diskSelectionCombo.addItems(available_disks)

    def check_privileges(self):
        # This function checks for admin privileges
        if os.name == 'nt':
            try:
                # Check admin privileges by trying to run a command that requires them
                subprocess.check_call(["net", "session"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "You need to run this as an administrator.")
                sys.exit(1)
            except:
                QMessageBox.critical(self, "Error", "Error checking for admin privileges.")
                sys.exit(1)
            else:
                self.console.append('Running with admin privileges.')
                return True
        else:
            QMessageBox.critical(self, "Error", "This OS is not supported.")
            sys.exit(1)
            return False

    def get_disks(self):
        # This will create a temporary script for diskpart to run
        with tempfile.NamedTemporaryFile(delete=False, mode="w+t") as f:
            f.write('list disk')
            f.seek(0)  # This resets the file's position to the beginning

            # Run the diskpart command
            process = subprocess.Popen(['diskpart', '/s', f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, err = process.communicate()

        # Cleanup (remove the temporary script file)
        os.unlink(f.name)

        # Display raw output for debugging
        self.console.append("Output from diskpart:")
        self.console.append(output)

        # Extract the available disks
        disks = []
        for line in output.splitlines():
            line = line.strip()  # Remove leading and trailing whitespace
            if line.startswith("Disk"):
                disk_number = line.split()[1]  # Extracting disk number
                disks.append(f"Disk {disk_number}")

        if err:
            self.console.append(f"Error while getting disk list: {err}")

        return disks

    def initialize_disk(self):
        disk_type = self.diskTypeCombo.currentText()
        disk_number = self.diskSelectionCombo.currentIndex()

        if disk_type == "GPT":
            commands = [
                f'select disk {disk_number}',
                'clean',
                'convert gpt',
                'cre par efi size=100',
                'format quick fs=fat32 label="System"',
                'assign letter=W',
                'cre par msr size=16',
                'cre par pri',
                'format quick fs=ntfs label="Windows"',
                'assign letter=C'
        ]
        elif disk_type == "MBR":
            commands = [
                f'select disk {disk_number}',
                'clean',
                'convert mbr',
                'cre par pri size=100',
                'format quick fs=ntfs label="System"',
                'assign letter=W',
                'cre par pri',  # Directly create a primary partition without the need for an extended partition
                'format quick fs=ntfs label="Windows"',
                'assign letter=C'
            ]
        else:
            self.console.append(f"Unexpected disk type: {disk_type}")
            return

        self.run_diskpart(commands)

        # After initializing the disk, deploy the Windows image.
        success = self.deploy_windows_image()

        if success:
            # Displaying a success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Deployment Completed!")
            msg.setWindowTitle("Info")
            msg.exec_()
        else:
            # Displaying an error message
            QMessageBox.critical(self, "Error", "Deployment failed!")

    def deploy_windows_image(self):
        if hasattr(self, 'filePath') and self.filePath:
            deploy_command = f'dism /Apply-Image /ImageFile:"{self.filePath}" /Index:1 /ApplyDir:C:\\'
            result = self.run_command(deploy_command)
            if result:
                self.console.append("Deployment completed successfully!")
                return True
            else:
                self.console.append("Deployment failed!")
                return False
        else:
            self.console.append("Please select an install.wim file first.")
            return False

    def run_diskpart(self, commands):
        # Utility function to run diskpart with a list of commands
        with tempfile.NamedTemporaryFile(delete=False) as script:
            script.write('\n'.join(commands).encode())
            script.close()

            process = subprocess.Popen(f'diskpart /s {script.name}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            out, err = process.communicate()
            os.unlink(script.name)

            self.console.append(out)
            if err:
                self.console.append(f"Error: {err}")

    def run_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        out, err = process.communicate()
        self.console.append(out)
        if err:
            self.console.append(f"Error: {err}")
            return False
        return True


if __name__ == '__main__':
    try:
        if is_admin():
            app = QApplication(sys.argv)
            ex = DeploymentGUI()
            sys.exit(app.exec_())
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close.")
