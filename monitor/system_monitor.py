import tkinter as tk
from tkinter import ttk
from collections import deque
import threading
from utils.utils import export_data
from .monitor import monitor_resources, update_graph
from .gui import create_gui

class ResourceMonitor:
    def __init__(self, current_version):
        self.CURRENT_VERSION = current_version
        self.CPU_THRESHOLD = 99.15
        self.MEMORY_THRESHOLD = 85
        self.HISTORY_LENGTH = 7
        self.CPU_MON_INTERVAL = 1

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

        # Center the window
        window_width = 800
        window_height = 740
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Create GUI
        create_gui(self)

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=monitor_resources, args=(self,), daemon=True)
            self.graph_thread = threading.Thread(target=update_graph, args=(self,), daemon=True)
            self.monitor_thread.start()
            self.graph_thread.start()
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.monitoring_label.config(text="Monitoring the CPU usage based on monitoring time before graphing CPU percentage.")
            self.monitoring_label_info.config(text="Simply put, the CPU monitor interval value is the duration for which the application calculates the average CPU usage before displaying it on a graph.")

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.monitoring_label.config(text="")
        self.monitoring_label_info.config(text="")

    def export_data(self):
        export_data(self)

    def cleanup(self):
        self.monitoring = False
        self.root.quit()
