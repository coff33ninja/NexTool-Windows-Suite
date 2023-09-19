import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox

class NexToolApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("NexTool Windows Suite")
        self.geometry("900x700")

        # Styling and Theme
        self.dark_mode_colors = {
            "bg": "#333",
            "fg": "white",
            "terminal_bg": "#222",
            "terminal_fg": "lime",
            "tooltip_bg": "#444",
            "tooltip_fg": "white"
        }
        
        self.light_mode_colors = {
            "bg": "#fff",
            "fg": "black",
            "terminal_bg": "#fff",
            "terminal_fg": "black",
            "tooltip_bg": "#ffffe0",
            "tooltip_fg": "black"
        }

        # Apply a theme to make it look more modern
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#333", foreground="white", padding=10)
        style.configure("TFrame", background="#444")
        style.configure("TLabelFrame", background="#444", foreground="white")
        style.configure("TLabelFrame.Label", background="#444", foreground="white")

        # Menu Bar Initialization
        menu_bar = tk.Menu(self)

        # Create main frames for organization
        self.left_frame = ttk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=True, fill=tk.BOTH)

        # PanedWindow for resizable layout
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.paned_window.add(self.left_frame)
        self.paned_window.add(self.right_frame)
        self.paned_window.sash_place(0, 225, 0)  # Initial position of the sash

        # Group related functionalities under LabelFrames
        config_frame = ttk.LabelFrame(self.left_frame, text="Configuration")
        config_frame.pack(pady=20, fill=tk.BOTH)

        management_frame = ttk.LabelFrame(self.left_frame, text="Management")
        management_frame.pack(pady=20, fill=tk.BOTH)
        
        # Create menu buttons
        menu_buttons = []
        options = [
            ("System Information", self.run_system_info, config_frame),
            ("Windows Configuration", self.run_windows_config, config_frame),
            ("Office Installations", self.run_office_install, config_frame),
            ("Device Configuration", self.run_device_config, config_frame),
            ("Windows Installation", self.run_windows_install, config_frame),
            ("Services Manager", self.run_services_manager, management_frame),
            ("Group Policy Management", self.run_group_policy, management_frame),
            ("Driver & Updates Manager", self.run_updates_manager, management_frame),
            ("Debloating", self.run_debloating, management_frame)
        ]
        for text, command, parent_frame in options:
            btn = ttk.Button(parent_frame, text=text, command=command, width=30)
            btn.pack(pady=10)
            menu_buttons.append(btn)

        # PanedWindow for resizable layout
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

# Adjust these frames to be inside the paned window
self.paned_window.add(left_frame)
self.paned_window.add(right_frame)
self.paned_window.sash_place(0, 225, 0)  # You can adjust the 225 to set the initial position of the sash


        # Add Settings dropdown in the menu bar
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        self.dark_mode_var = tk.IntVar()  # 0 for off, 1 for on
        settings_menu.add_checkbutton(label="Dark Mode", variable=self.dark_mode_var, command=self.toggle_dark_mode)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # 'File' menu on the menu bar
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

        # Status Bar
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Adding tooltips to buttons
        self.tooltips = {}
        for btn, tip in zip(menu_buttons, ["Info about the system", "Configure various settings", "Install MS Office", "Configure devices", "Advanced Windows installation", "Manage services", "Manage policies", "Manage updates", "Debloat Windows"]):
            self.add_tooltip(btn, tip)

        # Terminal output section
        self.terminal_output = scrolledtext.ScrolledText(self.right_frame, width=50, height=30, wrap=tk.WORD)
        self.terminal_output.pack(pady=20, padx=20)
        self.terminal_output.insert(tk.END, "Welcome to NexTool Windows Suite!\n")
        self.terminal_output.config(state=tk.DISABLED)

    def toggle_dark_mode(self):
        colors = self.dark_mode_colors if self.dark_mode_var.get() else self.light_mode_colors
        self.config(bg=colors["bg"])
        self.status_bar.config(bg=colors["bg"], fg=colors["fg"])
        self.terminal_output.config(bg=colors["terminal_bg"], fg=colors["terminal_fg"])
        for tooltip in self.tooltips.values():
            tooltip.update_colors(colors["tooltip_bg"], colors["tooltip_fg"])

    # Tooltip Helper Function
    def add_tooltip(self, widget, text):
        tooltip = ToolTip(widget, text=text)
        self.tooltips[widget] = tooltip

    # Update status bar helper
    def update_status(self, text):
        self.status_bar.config(text=text)

    # Create a terminal output section
        self.terminal_output = scrolledtext.ScrolledText(right_frame, width=50, height=30, wrap=tk.WORD, bg="#222", fg="lime")
        self.terminal_output.pack(pady=20, padx=20)
        self.terminal_output.insert(tk.END, "Welcome to NexTool Windows Suite!\n")
        self.terminal_output.config(state=tk.DISABLED)

    def append_to_terminal(self, message):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, message + "\n")
        self.terminal_output.config(state=tk.DISABLED)

    # Placeholder methods for menu buttons
    def run_system_info(self):
        # Run the actual script/command here
        self.append_to_terminal("Fetching system information...")

    def run_windows_config(self):
        self.append_to_terminal("Configuring Windows...")

    def run_services_manager(self):
        self.append_to_terminal("Managing services...")

    def run_group_policy(self):
        self.append_to_terminal("Managing group policies...")

    def run_office_install(self):
        self.append_to_terminal("Installing Office...")

    def run_updates_manager(self):
        self.append_to_terminal("Managing updates...")

    def run_device_config(self):
        self.append_to_terminal("Configuring devices...")

    def run_debloating(self):
        self.append_to_terminal("Debloating Windows...")

    def run_windows_install(self):
        self.append_to_terminal("Installing Windows for Advanced Users...")

    # A new method to exit the app
    def quit(self):
        if messagebox.askyesno("Quit", "Are you sure you want to exit?"):
            self.destroy()

    def update_status(self, text):
        self.status_bar.config(text=text)


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", borderwidth=1, relief="solid")
        label.pack()
    
    def update_colors(self, bg, fg):
        self.tooltip_bg = bg
        self.tooltip_fg = fg
        if self.tooltip:  # If tooltip is visible, update its colors immediately
            label = tk.Label(self.tooltip, text=self.text, background=self.tooltip_bg, fg=self.tooltip_fg, borderwidth=1, relief="solid")
            label.pack()

    def on_leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()

if __name__ == "__main__":
    app = NexToolApp()
    app.mainloop()
