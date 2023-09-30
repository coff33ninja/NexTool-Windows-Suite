# NexTool Windows Suite 🛠️

## Introduction

NexTool Windows Suite offers an all-in-one solution for Windows users, ranging from enthusiasts to IT professionals. It's designed to simplify and optimize the Windows environment, making complex tasks straightforward.

## Features

### 🖥️ System Information

Gain detailed insights about your machine's specs and performance:
- CPU Specifications
- Memory Statistics
- BIOS Version
- Windows Build and Version
- Connected Disks

### 🔧 Windows Configuration

Personalize and control various facets of Windows:
- Basic Computer Report: Overview of system details.
- Advanced Hardware Info: Deep dive into hardware and system resources.
- Defender Management: Fine-tune Windows Defender settings.
- Telemetry: Control the extent of Windows data collection.
- Software & Windows Updates Manager: Seamless updates management.
- Driver Updater: Ensure your drivers are always up to date.
- Office Installations: Effortless installation and management of Microsoft Office.
- Network Setup: Personalize network settings and connections.

### 🚀 Services Manager

Achieve optimal performance by managing Windows services:
- DISM and SFC Windows Repair: Mend corrupted Windows files.
- Windows Debloater: Eliminate bloatware.
- Group Policy Reset: Restore group policies to defaults.
- WMI Reset: Reinitialize the Windows Management Instrumentation service.

### Additional Features
- 🌐 Network Optimizer: Fine-tune your network settings.
- 💽 Disk Cleaner: Maintain and optimize storage drives.
- 🚫 Firewall Manager: Enhance your firewall settings.
- 🔒 Security Audit Tool: Detect vulnerabilities and get security recommendations.

## Setup Instructions

### Prerequisites

1. PowerShell with elevated privileges (Run as Administrator).
2. Active internet connection to download required packages and tools.
3. Ensure execution policies allow the script to run. You can set this with: `Set-ExecutionPolicy RemoteSigned`.

### Installation Steps

1. There are multiple ways to execute the setup script:

   a. **Directly from the Web**:
   
      Execute the following command in an elevated PowerShell window:

      Method 1 - Using net.webclient for downloading and executing
            ```powershell
      iex (new-object net.webclient).DownloadString('https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/master/AdminLaunchOption.ps1')
      ```
      
      Method 2 - Using Invoke-WebRequest with its alias iwr 
      ```powershell
      iwr -useb https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/master/AdminLaunchOption.ps1 | iex
      ```
      
      Method 3 - Using Invoke-RestMethod with its alias irm 
      ```powershell
      irm https://raw.githubusercontent.com/coff33ninja/NexTool-Windows-Suite/master/AdminLaunchOption.ps1 | iex
      ```

   b. **Local Execution**:
   
      - Download the provided PowerShell script (`NexTool-Setup.ps1`).
      - Right-click on the downloaded file and choose "Run with PowerShell".

3. The script will automatically handle the setup:
   - It checks and installs Chocolatey if not present.
   - Installs or updates essential tools like `aria2`, `wget`, `curl`, and `powershell-core`.
   - Ensures Python is installed and sets up required Python packages.
   - Downloads and sets up Winget if not present.
   - Downloads the NexTool Python script and prepares it for execution.

4. After the script execution completes, it will launch the `NexTool.py` Python script.

**Note**: The script creates temporary directories (`C:\NexTool` & `C:\PS`) during its operation, which will be cleared out once the setup is complete.

For users who prefer an executable, a `PS2EXE` version of the script is available in the [Releases](https://github.com/coff33ninja/NexTool-Windows-Suite/releases) section of our GitHub repository.

For issues during installation, refer to the "Feedback & Issues" section and report any problems you encounter.


## TODO & Progress

Here's our roadmap for NexTool's development and the milestones achieved:

### Completed:
- [x] Windows Configuration Section: Integrated tools for managing and modifying Windows settings.
- [x] GUI Development: Building an intuitive and user-friendly interface using Python.
- [x] Office Installations Manager: Implemented streamlined processes for managing Microsoft Office applications.
- [x] Driver & Windows Updates Manager: Integrated tools for driver updates and Windows update management.
- [x] Winget and Choco Integration: Implementing these package managers for easier software management.
- [x] Network Optimizer: Analyze current network settings, also offer tweaks to optimize online connectivity and reduce latency.
- [x] Network Optimizer: Tools for analyzing and enhancing network settings.
- [x] Winget and Choco Integration: Provide a guided mode for beginners and a selective mode for advanced users to choose their preferred applications for installation or updates.

### In Progress / Planned:
- [ ] Services Manager Section: Introduced tools for managing services for improved performance.

- [ ] Device Configuration: Adding functionalities for device settings customization.
- [ ] Windows Debloating Tool: Tools to remove unnecessary pre-installed applications.

- [ ] Telemetry and Data Collection Settings: Allow users to control the extent of data Windows collects.
- [ ] Add a "Services Manager" section: Introduce tools to:
         Disable unnecessary services to improve system performance.
         Customize startup services to ensure a faster boot time.
         Manage service dependencies for a stable system operation.
- [ ] Windows Installation for Advanced Users: Offer features to facilitate custom Windows installations.
- [ ] Disk Cleaner:  Scan for junk files, temporary files, and cache. Provide options to clean and reclaim storage space.
- [ ] Firewall Manager: Customize firewall rules. Monitor incoming and outgoing connections for improved security.
- [ ] Security Audit Tool: Scan the system for potential vulnerabilities. Provide recommendations and fixes for identified security loopholes.


And possibly more...: Continue to seek user feedback, identify common pain points, and integrate more tools and functionalities to make the NexTool Windows Suite the go-to toolbox for every Windows user.

## Feedback & Issues

Your feedback fuels NexTool! If you stumble upon a bug or have suggestions, kindly open an issue on our GitHub page.

## Upcoming Enhancements

Stay informed about what's next for NexTool! Check out our GitHub Milestones and Projects for a peek into our roadmap.

## Contribute

Passionate about NexTool? We welcome contributions. For guidelines, please review our `CONTRIBUTING.md`.

# Closing Remarks

The NexTool Windows Suite aims to be the comprehensive toolbox for Windows users, building on the foundational work done in [AIO](https://github.com/coff33ninja/AIO). The previous version of the application was archived, as there were aspects that felt too routine and monotonous, including the layout and the version numbering approach.

With the insights gained from [AIO](https://github.com/coff33ninja/AIO), this project intends to craft an "All-Purpose" toolbox that's both intuitive and user-friendly. Using Python for the GUI allows for a more dynamic and responsive interface, catering to the diverse needs of Windows users.
