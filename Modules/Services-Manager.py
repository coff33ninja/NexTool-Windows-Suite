import tkinter as tk
from tkinter import ttk
import subprocess
import json
import winreg as reg
from tkinter import messagebox
import webbrowser

def redirect_to_github():
    webbrowser.open("https://github.com/YourRepoName")

RECOMMENDED_DISABLE = [
    "bits", "BDESVC", "BcastDVRUserService_7c360", "GoogleChromeElevationService",
    "gupdate", "gupdatem", "vmickvpexchange", "vmicguestinterface", "vmicshutdown"
]
class ServiceHandler:
    @staticmethod
    def list_all_services():
        command = ["sc", "query", "type=", "service"]
        output = subprocess.check_output(command, text=True).splitlines()
        services = [line.split(":")[1].strip() for line in output if "SERVICE_NAME" in line]
        return services

    @staticmethod
    def backup_services():
        services = ServiceHandler.list_all_services()
        service_status = {}
        for service in services:
            status_cmd = ["sc", "qc", service]
            status_output = subprocess.check_output(status_cmd, text=True).splitlines()
            status = [line.split(":", 1)[1].strip() for line in status_output if "START_TYPE" in line][0]
            service_status[service] = status

        with open("backup_services.json", "w") as file:
            json.dump(service_status, file)

    @staticmethod
    def restore_services():
        try:
            with open("backup_services.json", "r") as file:
                backup_statuses = json.load(file)
            for service, status in backup_statuses.items():
                ServiceHandler.set_service_start_type(service, status)
        except FileNotFoundError:
            return "No backup file found. Please backup services first."

    @staticmethod
    def get_service_start_type(service):
        status_cmd = ["sc", "qc", service]
        status_output = subprocess.check_output(status_cmd, text=True).splitlines()
        status = [line.split(":", 1)[1].strip() for line in status_output if "START_TYPE" in line]
        return status[0] if status else None

    @staticmethod
    def set_service_start_type(service, start_type):
        subprocess.run(["sc", "config", service, f"start= {start_type}"], text=True)

    @staticmethod
    def modify_service(service, action):
        try:
            if action in ["start", "stop", "pause", "continue"]:
                result = subprocess.run(["sc", action, service], capture_output=True, text=True)
            elif action in ["auto", "demand", "disabled"]:
                result = subprocess.run(["sc", "config", service, f"start= {action}"], capture_output=True, text=True)
            else:
                return f"Invalid action: {action}"

            output = result.stdout + result.stderr
            if "Access is denied" in output:
                return f"Cannot control '{service}' due to system restrictions."
            elif "Pending" in output:
                return f"Changes to '{service}' will take effect after system restart."
            elif "FAILED" in output:
                return f"Failed to perform action '{action}' on '{service}'."
            else:
                return f"Successfully performed action '{action}' on '{service}' with new status '{start_type}'."
        except Exception as e:
            return f"An error occurred: {str(e)}"

class StartupHandler:
    @staticmethod
    def add_startup_application(name, path):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as key:
            reg.SetValueEx(key, name, 0, reg.REG_SZ, path)

    @staticmethod
    def remove_startup_application(app_name):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as key:
            reg.DeleteValue(key, app_name)

    @staticmethod
    def list_startup_applications():
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        startup_apps = {}
        with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ) as key:
            index = 0
            while True:
                try:
                    name, value, _ = reg.EnumValue(key, index)
                    startup_apps[name] = value
                    index += 1
                except OSError:
                    break
        return startup_apps

class ScheduledTaskHandler:
    @staticmethod
    def list_scheduled_tasks():
        tasks = subprocess.check_output(["schtasks", "/query", "/fo", "LIST"]).decode()
        return tasks

    @staticmethod
    def create_scheduled_task(name, command, time="12:00", frequency="daily"):
        subprocess.run(["schtasks", "/create", "/sc", frequency, "/tn", name, "/tr", command, "/st", time])

    @staticmethod
    def delete_scheduled_task(name):
        subprocess.run(["schtasks", "/delete", "/tn", name, "/f"])

class ServiceManagementModule(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Service Management")

        # Status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Whenever you want to update the status bar:
    def update_status(self, message):
        self.status_bar.config(text=message)

        # Create Notebook (Tabbed Pane)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Service Tab
        self.services_frame = ttk.Frame(self.notebook)
        self.create_services_widgets()
        self.notebook.add(self.services_frame, text="Services")

        # Startup Applications Tab
        self.startup_frame = ttk.Frame(self.notebook)
        self.create_startup_widgets()
        self.notebook.add(self.startup_frame, text="Startup Applications")

        # Scheduled Tasks Tab
        self.tasks_frame = ttk.Frame(self.notebook)
        self.create_tasks_widgets()
        self.notebook.add(self.tasks_frame, text="Scheduled Tasks")

    def create_services_widgets(self):
        # List services
        self.services_listbox = tk.Listbox(self.services_frame)
        self.services_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.refresh_services_button = ttk.Button(self.services_frame, text="Refresh List", command=self.refresh_services)
        self.refresh_services_button.pack(pady=5)

        self.disable_services_button = ttk.Button(self.services_frame, text="Disable Selected", command=self.disable_selected_services)
        self.disable_services_button.pack(pady=5)
        self.service_states = ttk.Combobox(self.services_frame, values=["auto", "demand", "disabled"])
        self.service_states.pack(pady=5)

    def change_selected_service_state(self):
        selected_service = self.services_listbox.get(tk.ACTIVE)
        new_state = self.service_states.get()
        ServiceHandler.set_service_start_type(selected_service, new_state)
        self.refresh_services()

    def refresh_services(self):
        services = ServiceHandler.list_all_services()
        self.services_listbox.delete(0, tk.END)
        for service in services:
            status = ServiceHandler.get_service_start_type(service)
            self.services_listbox.insert(tk.END, f"{service} - {status}")

    def disable_selected_services(self):
        selected_indices = self.services_listbox.curselection()
        selected_services = [self.services_listbox.get(i) for i in selected_indices]
        results = [ServiceHandler.modify_service(service, "disabled") for service in selected_services]
        show_popup("\n".join(results), "Service Status")
        self.refresh_services()

    def create_startup_widgets(self):
        # List startup applications
        self.startup_listbox = tk.Listbox(self.startup_frame)
        self.startup_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.refresh_startup_button = ttk.Button(self.startup_frame, text="Refresh List", command=self.refresh_startup)
        self.refresh_startup_button.pack(pady=5)

        self.remove_startup_button = ttk.Button(self.startup_frame, text="Remove Selected", command=self.remove_startup_app)
        self.remove_startup_button.pack(pady=5)

    def remove_task(self):
        selection = self.tasks_listbox.curselection()
        if selection:
            task_name = self.tasks_listbox.get(selection).split(":")[0].strip()
            ScheduledTaskHandler.delete_scheduled_task(task_name)  # Use class name prefix
            show_popup(f"Removed scheduled task '{task_name}'", "Task Removal")

    def add_task(self):
        task_name = self.task_name_entry.get()
        task_command = self.task_command_entry.get()
        ScheduledTaskHandler.create_scheduled_task(task_name, task_command)  # Use class name prefix
        show_popup(f"Added new task '{task_name}' with command '{task_command}'", "Task Addition")

    def refresh_startup(self):
        apps = StartupHandler.list_startup_applications()
        self.startup_listbox.delete(0, tk.END)  # Clear the listbox
        for app_name, app_path in apps.items():
            self.startup_listbox.insert(tk.END, f"{app_name}: {app_path}")

    def create_tasks_widgets(self):
        # List scheduled tasks
        self.tasks_listbox = tk.Listbox(self.tasks_frame)
        self.tasks_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.refresh_tasks_button = ttk.Button(self.tasks_frame, text="Refresh Tasks", command=self.refresh_tasks)
        self.refresh_tasks_button.pack(pady=5)

        self.remove_task_button = ttk.Button(self.tasks_frame, text="Remove Selected Task", command=self.remove_task)
        self.remove_task_button.pack(pady=5)

        # Inputs for creating new tasks
        self.new_task_label = ttk.Label(self.tasks_frame, text="Create New Task:")
        self.new_task_label.pack(pady=5)

        self.task_name_entry = ttk.Entry(self.tasks_frame)
        self.task_name_entry.pack(pady=5)
        self.task_name_entry.insert(0, "Enter Task Name")

        self.task_command_entry = ttk.Entry(self.tasks_frame)
        self.task_command_entry.pack(pady=5)
        self.task_command_entry.insert(0, "Enter Command")

        self.add_task_button = ttk.Button(self.tasks_frame, text="Add Task", command=self.add_task)
        self.add_task_button.pack(pady=5)

def show_popup(message, title="Info"):
    """
    Displays a detailed popup message box informing the user of the action performed.
    """
    full_message = f"Action performed:\n\n{message}"
    messagebox.showinfo(title, full_message)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Service Management")
    app = ServiceManagementModule(master=root)
    root.mainloop()
