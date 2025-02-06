import sys
from tkinter import Tk, Frame, Button, messagebox
from tkinter import ttk

class NexToolUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NexTool Functions Summary UI")
        self.root.geometry("800x600")
        self.root.configure(bg="#121212")

        # Create a style for the buttons
        style = ttk.Style()
        style.configure("TButton", background="red", foreground="white", font=("Arial", 12))

        # Create a frame for the sidebar
        self.sidebar = Frame(self.root, bg="#1E1E1E", width=200)
        self.sidebar.pack(side="left", fill="y")

        # Create a frame for the main content
        self.main_frame = Frame(self.root, bg="#121212")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Create tabs
        self.create_tabs()

        # Create sidebar buttons
        self.create_sidebar_buttons()

    def create_sidebar_buttons(self):
        categories = [
            "System Information",
            "Network",
            "Security",
            "Software Management",
            "Maintenance"
        ]

        for category in categories:
            button = Button(self.sidebar, text=category, command=lambda c=category: self.show_tab(c))
            button.pack(pady=5, padx=10, fill="x")

    def show_tab(self, category):
        # Show the corresponding tab based on the category
        tab_mapping = {
            "System Information": 0,
            "Network": 1,
            "Security": 2,
            "Software Management": 3,
            "Maintenance": 4
        }
        index = tab_mapping.get(category)
        if index is not None:
            self.notebook.select(index)

    def create_tabs(self):
        self.system_info_tab = Frame(self.notebook)
        self.network_tab = Frame(self.notebook)
        self.security_tab = Frame(self.notebook)
        self.software_management_tab = Frame(self.notebook)
        self.maintenance_tab = Frame(self.notebook)

        self.notebook.add(self.system_info_tab, text="System Information")
        self.notebook.add(self.network_tab, text="Network")
        self.notebook.add(self.security_tab, text="Security")
        self.notebook.add(self.software_management_tab, text="Software Management")
        self.notebook.add(self.maintenance_tab, text="Maintenance")

        self.create_buttons(self.system_info_tab, [
            "get_system_information",
            "consolidate_info"
        ])

        self.create_buttons(self.network_tab, [
            "open_ping_dialog",
            "traceroute",
            "open_network_share_manager",
            "open_wifi_password_extract"
        ])

        self.create_buttons(self.security_tab, [
            "open_defender_dialog",
            "on_remove_defender_dialog",
            "open_telemetry_dialog"
        ])

        self.create_buttons(self.software_management_tab, [
            "execute_windows_update",
            "launch_patchmypc_tool",
            "launch_chocolatey_gui",
            "launch_winget_gui"
        ])

        self.create_buttons(self.maintenance_tab, [
            "launch_disk_cleanup",
            "launch_DiskCheckApp",
            "launch_SystemCheckApp",
            "launch_GroupPolicyResetApp",
            "launch_WMIResetApp"
        ])

    def create_buttons(self, parent_widget, function_headers):
        for header in function_headers:
            button = Button(parent_widget, text=header, command=lambda h=header: self.show_placeholder(h))
            button.pack(pady=5, padx=10, fill="x")

    def show_placeholder(self, function_name):
        # Display a placeholder message for the clicked function
        messagebox.showinfo("Placeholder", f"This is a placeholder for {function_name} function.")

if __name__ == "__main__":
    root = Tk()
    app = NexToolUI(root)
    root.mainloop()
