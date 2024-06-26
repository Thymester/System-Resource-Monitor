import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading
import os
import csv
from tkinter import filedialog
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plyer import notification
import platform

# Resource Monitor class to encapsulate variables and functions
class ResourceMonitor:
    def __init__(self):
        self.CPU_THRESHOLD = 99.15  # Default CPU threshold
        self.MEMORY_THRESHOLD = 85  # Default Memory threshold
        self.HISTORY_LENGTH = 7  # Number of data points to store in history
        self.CPU_MON_INTERVAL = 1  # Length of time the app monitors the CPU usage

        self.cpu_history = deque(maxlen=self.HISTORY_LENGTH)
        self.memory_history = deque(maxlen=self.HISTORY_LENGTH)
        self.time_history = deque(maxlen=self.HISTORY_LENGTH)

        self.all_cpu_history = []
        self.all_memory_history = []
        self.all_time_history = []

        self.monitoring = False

        self.root = tk.Tk()
        self.root.title("System Resource Monitor")
        self.root.minsize(800, 740)
        self.root.maxsize(800, 740)
        self.root.resizable(False, False)

        # Calculate the position to center the window
        window_width = 800
        window_height = 740
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3

        # Set the position of the window
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both")

        self.create_gui()

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
            self.graph_thread = threading.Thread(target=self.update_graph, daemon=True)
            self.monitor_thread.start()
            self.graph_thread.start()
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.monitoring_label.config(text="Monitoring the CPU usage based on monitoring time before graphing CPU percentage.")
            self.monitoring_label_info.config(text="Simply put, the CPU monitor interval value is the duration for which the application calculates the average CPU usage before displaying it on a graph.")

    # Function to update the resource graphs
    def update_graph(self):
        while self.monitoring:
            self.ax.clear()
            self.ax.plot(self.all_time_history[-self.HISTORY_LENGTH:], self.all_cpu_history[-self.HISTORY_LENGTH:], label='CPU %')
            self.ax.plot(self.all_time_history[-self.HISTORY_LENGTH:], self.all_memory_history[-self.HISTORY_LENGTH:], label='Memory %')
            self.ax.legend()
            self.ax.set_xlabel('Time')
            self.ax.set_ylabel('Percentage')
            self.ax.set_title('Resource Usage Graph')
            self.canvas.draw()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.monitoring_label.config(text="")
        self.monitoring_label_info.config(text="")

    def create_gui(self):
        # Tab control
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both")

        # CPU and Memory Monitoring Tab
        monitor_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(monitor_tab, text="Resource Monitoring")

        # Resource Threshold Setting Frame
        threshold_frame = ttk.LabelFrame(monitor_tab, text="Resource Thresholds")
        threshold_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # CPU Threshold Entry
        cpu_label = ttk.Label(threshold_frame, text="CPU Threshold (%):")
        cpu_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        cpu_entry = ttk.Entry(threshold_frame)
        cpu_entry.grid(row=0, column=1, padx=5, pady=5)
        cpu_entry.insert(0, str(self.CPU_THRESHOLD))

        # CPU Monitoring Interval Entry
        cpu_interval_label = ttk.Label(threshold_frame, text="CPU Monitoring Interval (seconds):")
        cpu_interval_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        cpu_interval_entry = ttk.Entry(threshold_frame)
        cpu_interval_entry.grid(row=2, column=1, padx=5, pady=5)
        cpu_interval_entry.insert(0, str(self.CPU_MON_INTERVAL))

        # Memory Threshold Entry
        memory_label = ttk.Label(threshold_frame, text="Memory Threshold (%):")
        memory_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        memory_entry = ttk.Entry(threshold_frame)
        memory_entry.grid(row=1, column=1, padx=5, pady=5)
        memory_entry.insert(0, str(self.MEMORY_THRESHOLD))

        def save_cpu_threshold(event):
            try:
                self.CPU_THRESHOLD = float(cpu_entry.get())
            except ValueError:
                cpu_entry.delete(0, "end")
                cpu_entry.insert(0, str(self.CPU_THRESHOLD))

        def save_memory_threshold(event):
            try:
                self.MEMORY_THRESHOLD = float(memory_entry.get())
            except ValueError:
                memory_entry.delete(0, "end")
                memory_entry.insert(0, str(self.MEMORY_THRESHOLD))

        def save_cpu_interval(event):
            try:
                self.CPU_MON_INTERVAL = float(cpu_interval_entry.get())
            except ValueError:
                cpu_interval_entry.delete(0, "end")
                cpu_interval_entry.insert(0, str(self.CPU_MON_INTERVAL))

        # Bind events to entry boxes
        cpu_entry.bind('<FocusOut>', save_cpu_threshold)
        memory_entry.bind('<FocusOut>', save_memory_threshold)
        cpu_interval_entry.bind('<FocusOut>', save_cpu_interval)

        # Start and Stop Monitoring Buttons
        self.start_button = ttk.Button(threshold_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.grid(row=5, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(threshold_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.grid(row=5, column=1, padx=5, pady=5)

        # Monitoring Label
        self.monitoring_label = ttk.Label(monitor_tab, text="")
        self.monitoring_label_info = ttk.Label(monitor_tab, text="")
        self.monitoring_label.pack(pady=5)
        self.monitoring_label_info.pack(pady=0.5, padx=0.5)

        # Graph Frame
        graph_frame = ttk.LabelFrame(monitor_tab, text="Resource Usage Graph")
        graph_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.fig = plt.figure(figsize=(8, 4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Percentage')
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Export Data Button
        export_button = ttk.Button(monitor_tab, text="Export Data", command=self.export_data)
        export_button.pack(pady=10)

        # System Information Tab
        info_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(info_tab, text="System Information")

        # System Information Display
        system_info_text = tk.Text(info_tab, wrap="word", height=50, width=80)
        system_info_text.pack(padx=10, pady=10)

        # Gather system information
        cpu_info1 = "General System Info: \n"
        cpu_info = f"CPU Cores: {os.cpu_count()}\n"
        cpu_model = f"CPU Model: {platform.processor()}\n"  # Fetch CPU model information using platform module
        ram_info = f"System RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB\n"
        os_info = f"OS Platform & Name: {platform.system()} {platform.release()}\n\n"  # Fetch OS platform and name using platform module

        disk_info = "Disk Usage:\n"
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info += f"  {partition.device} - {usage.percent}% used ({usage.free / (1024 ** 3):.2f} GB free / {usage.total / (1024 ** 3):.2f} GB total)\n\n"

        network_info = "Network Interfaces:\n"
        for interface, addresses in psutil.net_if_addrs().items():
            network_info += f"  Interface: {interface}\n"
            for address in addresses:
                network_info += f"    - {address.family.name}: {address.address}\n"

        # Insert gathered system information into the Text widget
        system_info_text.insert(tk.END, cpu_info1)
        system_info_text.insert(tk.END, cpu_info)
        system_info_text.insert(tk.END, cpu_model)
        system_info_text.insert(tk.END, ram_info)
        system_info_text.insert(tk.END, os_info)
        system_info_text.insert(tk.END, disk_info)
        system_info_text.insert(tk.END, network_info)

        # Disable editing for all system information
        system_info_text.configure(state="disabled")

    # Function to export resource data to a file
    def export_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "CPU (%)", "Memory (%)"])
                for i in range(len(self.all_time_history)):
                    writer.writerow([self.all_time_history[i], self.all_cpu_history[i], self.all_memory_history[i]])

    # Function to monitor system resources
    def monitor_resources(self):
        last_notification_time = 0
        while self.monitoring:
            cpu_percent_per_core = psutil.cpu_percent(interval=self.CPU_MON_INTERVAL, percpu=True)
            avg_cpu_percent = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
            memory_percent = psutil.virtual_memory().percent

            self.cpu_history.append(avg_cpu_percent)
            self.memory_history.append(memory_percent)
            self.time_history.append(time.strftime('%H:%M:%S'))

            self.all_cpu_history.append(avg_cpu_percent)
            self.all_memory_history.append(memory_percent)
            self.all_time_history.append(time.strftime('%H:%M:%S'))

            if avg_cpu_percent > self.CPU_THRESHOLD:
                current_time = time.time()
                if current_time - last_notification_time >= 3:
                    notification.notify(
                        title="Resource Alert",
                        message=f"CPU usage is over {self.CPU_THRESHOLD}%!",
                        timeout=3
                    )
                    last_notification_time = current_time

            if memory_percent > self.MEMORY_THRESHOLD:
                current_time = time.time()
                if current_time - last_notification_time >= 3:
                    notification.notify(
                        title="Resource Alert",
                        message=f"Memory usage is over {self.MEMORY_THRESHOLD}%!",
                        timeout=3
                    )
                    last_notification_time = current_time

    def cleanup(self):
        self.monitoring = False  # Stop monitoring
        self.root.quit()  # Quit Tkinter main loop

if __name__ == "__main__":
    monitor = ResourceMonitor()
    monitor.root.protocol("WM_DELETE_WINDOW", monitor.cleanup)
    monitor.root.mainloop()
