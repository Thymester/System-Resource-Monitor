import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from utils.utils import gather_system_info
import requests
from tkinter import messagebox

def create_gui(self):
    def check_for_updates(self):
        try:
            # GitHub API URL for the latest release
            repo_owner = "Thymester"
            repo_name = "System-Resource-Monitor"
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

            # Fetch the latest release data
            response = requests.get(url)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release["tag_name"]

            # Compare with the current version
            if self.CURRENT_VERSION != latest_version:
                messagebox.showinfo(
                    "Update Available",
                    f"A new version ({latest_version}) is available! Please update your application.\n\nDownload Link: {url}"
                )
            else:
                messagebox.showinfo(
                    "Latest Version",
                    f"You are already using the latest version ({latest_version}) of {repo_name}."
                )
        except requests.exceptions.RequestException as e:
            messagebox.showerror(
                "Update Check Failed",
                f"Failed to check for updates. Please try again later.\nError: {e}"
            )

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
    system_info_text.insert(tk.END, gather_system_info())

    # Disable editing for all system information
    system_info_text.configure(state="disabled")

    check_for_updates(self)