import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QProgressBar, QLabel
from PyQt6.QtCore import Qt

from disk_manager import DiskManager
from media_manager import InstallMediaManager
from wim_manager import WIMManager
from deployment_manager import DeploymentManager, AppendTextEvent, EnableButtonEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows Deployment Toolkit")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)

        # Modules
        self.disk_manager = DiskManager()
        self.central_layout.addWidget(QLabel("1. Choose a disk and format type:"))
        self.central_layout.addWidget(self.disk_manager)

        self.install_media_manager = InstallMediaManager()
        self.central_layout.addWidget(QLabel("2. Choose a Windows ISO:"))
        self.central_layout.addWidget(self.install_media_manager)

        self.wim_manager = WIMManager()
        self.central_layout.addWidget(QLabel("3. Fetch Windows versions from the selected ISO:"))
        self.central_layout.addWidget(self.wim_manager)

        self.deployment_manager = DeploymentManager(self, self.wim_manager, self.disk_manager, self.install_media_manager)
        self.central_layout.addWidget(QLabel("4. Start the Windows deployment:"))
        self.central_layout.addWidget(self.deployment_manager)

        self.setCentralWidget(self.central_widget)


class ProgressBarManager(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setValue(0)

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
