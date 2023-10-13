import subprocess
import psutil

def get_disk_details(disk):
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if partition.device.startswith(disk):
            usage = psutil.disk_usage(partition.mountpoint)
            return f"Device: {partition.device}\nMountpoint: {partition.mountpoint}\nFile system type: {partition.fstype}\nTotal Size: {usage.total}\nUsed: {usage.used}\nFree: {usage.free}\nPercentage Used: {usage.percent}%"
    return f"No details found for {disk}"

def get_drive_letters():
    partitions = psutil.disk_partitions()
    return [partition.device[0] for partition in partitions]

def get_disks():
    cmd = ['diskpart']
    script = 'list disk\n'

    # Execute diskpart with stdin input
    result = subprocess.check_output(cmd, input=script, universal_newlines=True, stderr=subprocess.STDOUT, text=True)

    lines = result.split('\n')
    disks = [line.split()[1] for line in lines if line.strip().startswith('Disk')]
    return disks
