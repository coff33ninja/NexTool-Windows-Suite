from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.popup import Popup

class NexToolUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'

        # Sidebar
        self.sidebar = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        self.add_widget(self.sidebar)

        # Main content area
        self.main_content = TabbedPanel()
        self.add_widget(self.main_content)

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
            button = Button(text=category, size_hint_y=None, height=40)
            button.bind(on_press=lambda instance, c=category: self.show_tab(c))
            self.sidebar.add_widget(button)

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
            self.main_content.switch_to(self.main_content.tabs[index])

    def create_tabs(self):
        self.system_info_tab = TabbedPanelHeader(text="System Information")
        self.network_tab = TabbedPanelHeader(text="Network")
        self.security_tab = TabbedPanelHeader(text="Security")
        self.software_management_tab = TabbedPanelHeader(text="Software Management")
        self.maintenance_tab = TabbedPanelHeader(text="Maintenance")

        self.main_content.add_widget(self.system_info_tab)
        self.main_content.add_widget(self.network_tab)
        self.main_content.add_widget(self.security_tab)
        self.main_content.add_widget(self.software_management_tab)
        self.main_content.add_widget(self.maintenance_tab)

        # Add buttons to each tab
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
            button = Button(text=header, size_hint_y=None, height=40)
            button.bind(on_press=lambda instance, h=header: self.show_placeholder(h))
            parent_widget.add_widget(button)

    def show_placeholder(self, function_name):
        # Display a placeholder message for the clicked function
        popup = Popup(title='Placeholder', content=Label(text=f'This is a placeholder for {function_name} function.'), size_hint=(0.6, 0.4))
        popup.open()

class NexToolApp(App):
    def build(self):
        return NexToolUI()

if __name__ == "__main__":
    NexToolApp().run()
