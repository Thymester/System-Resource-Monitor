import os
import platform
import psutil
import csv
from tkinter import filedialog

def export_data(self):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "CPU (%)", "Memory (%)"])
            for i in range(len(self.all_time_history)):
                writer.writerow([self.all_time_history[i], self.all_cpu_history[i], self.all_memory_history[i]])

def gather_system_info():
    cpu_info1 = "General System Info: \n"
    cpu_info = f"CPU Cores: {os.cpu_count()}\n"
    cpu_model = f"CPU Model: {platform.processor()}\n"
    ram_info = f"System RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB\n"
    os_info = f"OS Platform & Name: {platform.system()} {platform.release()}\n\n"

    disk_info = "Disk Usage:\n"
    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info += f"  {partition.device} - {usage.percent}% used ({usage.free / (1024 ** 3):.2f} GB free / {usage.total / (1024 ** 3):.2f} GB total)\n\n"

    network_info = "Network Interfaces:\n"
    for interface, addresses in psutil.net_if_addrs().items():
        network_info += f"  Interface: {interface}\n"
        for address in addresses:
            network_info += f"    - {address.family.name}: {address.address}\n"

    return cpu_info1 + cpu_info + cpu_model + ram_info + os_info + disk_info + network_info
