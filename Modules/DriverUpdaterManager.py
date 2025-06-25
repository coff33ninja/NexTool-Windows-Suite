import os
import sys
import platform
import zipfile
import subprocess
import requests
from typing import Callable
from PySide6.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QPushButton, QTextEdit, QWidget
from PySide6.QtCore import QThread, Signal as pyqtSignal, Slot as pyqtSlot, QObject


class DriverUpdaterManager(QObject):
    finished = pyqtSignal()
    message_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self, print_func: Callable[[str], None]):
        super().__init__()
        self.BASE_DIR = "C:\\NexTool\\Updater"
        self.SNAPPY_URL = "https://raw.githubusercontent.com/coff33ninja/AIO/main/TOOLS/3.UPDATER/SNAPPY_DRIVER.zip"
        self.print_func = print_func
        self.update_paths()

    def update_paths(self):
        self.SNAPPY_ZIP_PATH = os.path.join(self.BASE_DIR, "SNAPPY_DRIVER.zip")
        self.SNAPPY_EXTRACT_PATH = os.path.join(self.BASE_DIR, "SNAPPY_DRIVER")

    def set_base_dir(self, new_base_dir):
        self.BASE_DIR = new_base_dir
        self.update_paths()

    def ensure_directory_exists(self):
        if not os.path.exists(self.BASE_DIR):
            os.makedirs(self.BASE_DIR)
            self.print_func(f"Directory {self.BASE_DIR} created.")
        else:
            self.print_func(f"Directory {self.BASE_DIR} already exists.")

    def download_driver(self):
        # Download the Snappy Driver zip file
        self.download_file(self.SNAPPY_URL, self.SNAPPY_ZIP_PATH)

    def download_file(self, url: str, destination: str) -> None:
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))

            with open(destination, 'wb') as f:
                for data in response.iter_content(8192):
                    f.write(data)
                    downloaded_size = f.tell()
                    progress = int((downloaded_size / total_size) * 50)  # Assuming download is 50% of the total process
                    self.progress_signal.emit(progress)

            self.message_signal.emit(f"Downloaded file from {url} to {destination}.")

        except Exception as e:
            self.message_signal.emit(f"Error downloading {url}: {e}")

    def extract_driver(self):
        # Extract the downloaded zip
        with zipfile.ZipFile(self.SNAPPY_ZIP_PATH, "r") as zip_ref:
            total_files = len(zip_ref.infolist())
            for index, file in enumerate(zip_ref.infolist()):
                zip_ref.extract(file, self.SNAPPY_EXTRACT_PATH)
                progress = 50 + int((index / total_files) * 50)
                self.progress_signal.emit(progress)

    def install_driver(self):
        # Execute the appropriate Snappy Driver Installer based on system's architecture
        arch = platform.architecture()[0]
        if arch == "64bit":
            exe_path = os.path.join(self.SNAPPY_EXTRACT_PATH, "SDI_x64_R2111.exe")
        elif arch == "32bit":
            exe_path = os.path.join(self.SNAPPY_EXTRACT_PATH, "SDI_R2111.exe")
        else:
            raise Exception(f"Unsupported architecture: {arch}")

        subprocess.run([exe_path, "-checkupdates", "-autoupdate", "-autoclose"], check=True)

    def run(self):
        self.message_signal.emit("RUNNING DRIVER UPDATER...")
        try:
            self.ensure_directory_exists()
            self.download_driver()
            self.extract_driver()
            self.install_driver()
            # Optionally, delete the downloaded ZIP after the update
            os.remove(self.SNAPPY_ZIP_PATH)
            self.message_signal.emit("Driver update completed!")
        except Exception as e:
            self.message_signal.emit(f"Error occurred: {e}")
        self.finished.emit()


class DriverUpdaterWorker(QThread):
    progress_signal = pyqtSignal(int)
    message_signal = pyqtSignal(str)
    completed_signal = pyqtSignal()

    def run(self):
        manager = DriverUpdaterManager(self.message_signal.emit)
        try:
            manager.ensure_directory_exists()
            manager.download_driver()
            manager.extract_driver()
            manager.install_driver()
            # Optionally, delete the downloaded ZIP after the update
            os.remove(manager.SNAPPY_ZIP_PATH)
            self.message_signal.emit("Driver update completed!")
            self.completed_signal.emit()
        except Exception as e:
            self.message_signal.emit(str(e))

class DriverUpdaterManagerGUI(QMainWindow):
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

        self.downloadButton = QPushButton("Start Driver Update", self)
        self.downloadButton.clicked.connect(self.startUpdate)
        layout.addWidget(self.downloadButton)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.show()

    @pyqtSlot()
    def startUpdate(self):
        self.worker = DriverUpdaterWorker()
        self.worker.progress_signal.connect(self.progressBar.setValue)
        self.worker.message_signal.connect(self.logMessage)
        self.worker.completed_signal.connect(self.onUpdateCompleted)
        self.worker.start()
        self.logMessage("Started Driver Update...")

    @pyqtSlot(str)
    def logMessage(self, message):
        self.logTextEdit.append(message)

    @pyqtSlot()
    def onUpdateCompleted(self):
        self.logMessage("Update completed successfully!")
        self.close()  # Close the UI once the update is completed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = DriverUpdaterManagerGUI()
    sys.exit(app.exec_())
