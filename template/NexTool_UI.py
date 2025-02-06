import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QStackedWidget, QTabWidget, QFrame, QHBoxLayout
from PyQt6.QtGui import QIcon

class NexToolUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NexTool Functions Summary UI")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Set the style for a modern look
        self.setStyleSheet("background-color: #121212; color: white;")

        # Initialize the layout
        self.main_layout = QHBoxLayout(self.central_widget)

        self.sidebar = QFrame(self.central_widget)
        self.sidebar.setStyleSheet("background-color: #1E1E1E;")
        self.sidebar.setFixedWidth(200)
        self.main_layout.addWidget(self.sidebar)

        self.sidebar_layout = QVBoxLayout(self.sidebar)

        self.tab_widget = QTabWidget(self.central_widget)  # Declare tab_widget as an instance variable
        self.main_layout.addWidget(self.tab_widget)

        self.create_sidebar_buttons()
        self.create_tabs()

    def create_sidebar_buttons(self):
        # Create buttons for the sidebar
        categories = [
            ("System Information", "system_info_icon.png"),
            ("Network", "network_icon.png"),
            ("Security", "security_icon.png"),
            ("Software Management", "software_icon.png"),
            ("Maintenance", "maintenance_icon.png"),
        ]

        for category, icon in categories:
            button = QPushButton(category, self)
            button.setIcon(QIcon(icon))  # Set icon for the button
            button.setStyleSheet("background-color: #1E1E1E; color: white;")
            button.clicked.connect(lambda checked, c=category: self.show_tab(c))
            self.sidebar_layout.addWidget(button)

    def show_tab(self, category):
        # Show the corresponding tab based on the category
        index = self.tab_widget.indexOf(self.tab_widget.findChild(QWidget, category))
        if index != -1:
            self.tab_widget.setCurrentIndex(index)

    def create_tabs(self):
        # Create tabs for different categories
        system_info_tab = QWidget()
        network_tab = QWidget()
        security_tab = QWidget()
        software_management_tab = QWidget()
        maintenance_tab = QWidget()

        self.tab_widget.addTab(system_info_tab, "System Information")
        self.tab_widget.addTab(network_tab, "Network")
        self.tab_widget.addTab(security_tab, "Security")
        self.tab_widget.addTab(software_management_tab, "Software Management")
        self.tab_widget.addTab(maintenance_tab, "Maintenance")

        self.create_buttons(system_info_tab, [
            "get_system_information",
            "consolidate_info"
        ])

        self.create_buttons(network_tab, [
            "open_ping_dialog",
            "traceroute",
            "open_network_share_manager",
            "open_wifi_password_extract"
        ])

        self.create_buttons(security_tab, [
            "open_defender_dialog",
            "on_remove_defender_dialog",
            "open_telemetry_dialog"
        ])

        self.create_buttons(software_management_tab, [
            "execute_windows_update",
            "launch_patchmypc_tool",
            "launch_chocolatey_gui",
            "launch_winget_gui"
        ])

        self.create_buttons(maintenance_tab, [
            "launch_disk_cleanup",
            "launch_DiskCheckApp",
            "launch_SystemCheckApp",
            "launch_GroupPolicyResetApp",
            "launch_WMIResetApp"
        ])

    def create_buttons(self, parent_widget, function_headers):
        layout = QVBoxLayout(parent_widget)

        for header in function_headers:
            button = QPushButton(header, self)
            button.setStyleSheet("background-color: red; color: white;")  # Red button style
            button.clicked.connect(lambda checked, h=header: self.show_placeholder(h))
            layout.addWidget(button)

    def show_placeholder(self, function_name):
        # Display a placeholder message for the clicked function
        self.stacked_widget = QStackedWidget(self.central_widget)
        self.stacked_widget.addWidget(QLabel(f"This is a placeholder for {function_name} function.", self))
        self.stacked_widget.setCurrentIndex(self.stacked_widget.count() - 1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NexToolUI()
    window.show()
    sys.exit(app.exec())
