import sys
import os
import platform
import urllib.request
import zipfile
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QPushButton, QWidget, QTextEdit
from PySide6.QtCore import QThread, Signal as pyqtSignal, Slot as pyqtSlot

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
            progress_bar(50)  # Assuming download is half the process for demonstration purposes
        except Exception as e:
            print_func(f"Error downloading {url}: {e}")
            return
        print_func("Downloaded Office Tool Plus.")

        print_func("Attempting to extract Office Tool Plus...")
        with zipfile.ZipFile(destination_zip, "r") as zip_ref:
            zip_ref.extractall(office_dir)
        progress_bar(100)  # Set progress to 100 after extraction
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
            return True
        except Exception as e:
            print_func(f"Error occurred while trying to run Office Tool Plus: {e}")
            return False

class SetupWorker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    completed = pyqtSignal()
    exe_loaded = pyqtSignal()
    error = pyqtSignal(str)

    def run(self):
        try:
            manager = OfficeSetupManager()
            success = manager.download_and_setup_office(self.message.emit, self.progress.emit)
            if success:
                self.exe_loaded.emit()
            else:
                self.completed.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.logTextEdit = QTextEdit(self)
        self.logTextEdit.setReadOnly(True)
        layout.addWidget(self.logTextEdit)

        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)

        self.downloadButton = QPushButton("Start Office Setup", self)
        self.downloadButton.clicked.connect(self.startSetup)
        layout.addWidget(self.downloadButton)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.show()

    @pyqtSlot()
    def startSetup(self):
        self.worker = SetupWorker()
        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.message.connect(self.logMessage)
        self.worker.completed.connect(self.onSetupCompleted)
        self.worker.exe_loaded.connect(self.closeUI)
        self.worker.error.connect(self.onError)
        self.worker.start()
        self.logMessage("Started Office Tool Plus setup...")

    @pyqtSlot(str)
    def logMessage(self, message):
        self.logTextEdit.append(message)

    @pyqtSlot()
    def onSetupCompleted(self):
        self.logMessage("Setup completed successfully!")


    @pyqtSlot(str)
    def onError(self, error_message):
        self.logMessage(f"Error: {error_message}")

    @pyqtSlot()
    def closeUI(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
