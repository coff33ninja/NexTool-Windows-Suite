import sys
import subprocess
from qtpy.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QMessageBox, QComboBox, QProgressBar)

class MBR2GPTConverter(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.info_label = QLabel("Convert MBR to GPT:")
        layout.addWidget(self.info_label)

        self.disk_label = QLabel("Select Disk:")
        layout.addWidget(self.disk_label)

        self.disk_combo = QComboBox()
        layout.addWidget(self.disk_combo)

        self.refresh_button = QPushButton("Refresh Disk List")
        self.refresh_button.clicked.connect(self.populate_disk_list)
        layout.addWidget(self.refresh_button)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.convert_button = QPushButton("Convert Selected Disk to GPT")
        self.convert_button.clicked.connect(self.convert_to_gpt)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)
        self.setWindowTitle("MBR to GPT Converter")

        self.populate_disk_list()

    def run_command(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
            return output.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return e.output.decode('utf-8')

    def populate_disk_list(self):
        self.disk_combo.clear()
        command = 'wmic diskdrive get index, caption'
        output = self.run_command(command)
        lines = output.split("\n")[1:]
        for line in lines:
            if line.strip():
                parts = line.split()
                disk_num = parts[0]
                disk_name = ' '.join(parts[1:])
                self.disk_combo.addItem(f"Disk {disk_num} - {disk_name}", disk_num)

    def convert_to_gpt(self):
        reply = QMessageBox.question(self, 'Safety Reminder',
                                     'Ensure you have backed up your data before proceeding. Continue with conversion?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No) # type: ignore
        if reply == QMessageBox.No: # type: ignore
            return

        selected_disk = self.disk_combo.currentData()

        if not selected_disk:
            self.output_area.append("\nPlease select a disk from the list.")
            return

        self.progress_bar.setValue(25)
        validate_cmd = f'mbr2gpt /validate /disk:{selected_disk}'
        self.output_area.append("\nValidating Disk:")
        self.output_area.append(self.run_command(validate_cmd))

        self.progress_bar.setValue(50)
        convert_cmd = f'mbr2gpt /convert /disk:{selected_disk}'
        self.output_area.append("\nConverting to GPT:")
        output = self.run_command(convert_cmd)
        if "Conversion completed successfully" in output:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(0)
        self.output_area.append(output)
        self.output_area.append("\nConversion completed. Please check for any errors.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MBR2GPTConverter()
    mainWin.show()
    sys.exit(app.exec_()) # type: ignore
