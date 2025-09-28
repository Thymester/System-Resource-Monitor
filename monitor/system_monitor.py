import tkinter as tk
from tkinter import ttk
from collections import deque
import threading
from tkinter import messagebox
from utils.utils import export_data
from .monitor import monitor_resources, update_graph
from .gui import create_gui
import psutil
import queue
import time
from concurrent.futures import ThreadPoolExecutor

class ResourceMonitor:
    def __init__(self, current_version):
        self.CURRENT_VERSION = current_version
        self.CPU_THRESHOLD = 85
        self.MEMORY_THRESHOLD = 90
        self.GPU_THRESHOLD = 99.5
        self.HISTORY_LENGTH = 60
        self.CPU_MON_INTERVAL = 1

        self.cpu_history = deque(maxlen=self.HISTORY_LENGTH)
        self.memory_history = deque(maxlen=self.HISTORY_LENGTH)
        self.gpu_history = deque(maxlen=self.HISTORY_LENGTH)
        self.gpu_memory_history = deque(maxlen=self.HISTORY_LENGTH)
        self.time_history = deque(maxlen=self.HISTORY_LENGTH)

        self.all_cpu_history = []
        self.all_memory_history = []
        self.all_gpu_history = []
        self.all_gpu_memory_history = []
        self.all_time_history = []

        self.monitoring = False
        self.process_queue = queue.Queue()
        self.process_monitoring_thread = None

        self.root = tk.Tk()
        self.root.title("System Resource Monitor v2.0")
        self.root.minsize(900, 800)
        self.root.maxsize(1200, 900)
        
        # Modern styling
        self.setup_styles()
        
        # Center the window
        window_width = 1000
        window_height = 850
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 3
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Create GUI
        create_gui(self)

    def setup_styles(self):
        """Setup modern styling for the application"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Define modern colors
        bg_color = '#f0f0f0'
        accent_color = '#0078d4'
        text_color = '#323130'
        
        # Configure styles
        style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'), foreground=text_color)
        style.configure('Modern.TButton', padding=(10, 5))
        style.configure('Card.TFrame', relief='flat', borderwidth=1)
        
        self.root.configure(bg=bg_color)

    def update_process_info(self):
        """Update top processes in the GUI."""
        try:
            process_text = self.process_queue.get_nowait()
            self.process_list.config(state="normal")
            self.process_list.delete(1.0, tk.END)
            self.process_list.insert(tk.END, process_text)
            self.process_list.config(state="disabled")
        except queue.Empty:
            pass

        self.root.after(1000, self.update_process_info)

    def export_top_processes(self):
        """Export the current list of processes to a file."""
        try:
            process_text = self.process_list.get(1.0, tk.END).strip()

            if not process_text:
                messagebox.showwarning("Export Failed", "No processes to export.")
                return

            with open("top_processes.txt", "w") as file:
                file.write(process_text)
                messagebox.showinfo("Export Successful", 
                                  "Processes exported to 'top_processes.txt'")

        except Exception as e:
            messagebox.showerror("Export Failed", 
                               f"An error occurred while exporting: {e}")

    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True

            # Start monitoring threads
            self.monitor_thread = threading.Thread(target=monitor_resources, 
                                                 args=(self,), daemon=True)
            self.graph_thread = threading.Thread(target=update_graph, 
                                               args=(self,), daemon=True)
            self.monitor_thread.start()
            self.graph_thread.start()

            if hasattr(self, 'monitor_top_processes'):
                self.process_monitoring_thread = threading.Thread(
                    target=self.monitor_top_processes, daemon=True)
                self.process_monitoring_thread.start()

            # Update GUI state
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="🟢 Monitoring Active", 
                                   foreground="#107c10")

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="🔴 Monitoring Stopped", 
                               foreground="#d13438")

    def monitor_top_processes(self):
        """Monitor all processes and order them by CPU usage."""
        def monitor_chunk(process_chunk):
            processes = []
            for proc in process_chunk:
                try:
                    cpu_percent = proc.info['cpu_percent'] / psutil.cpu_count()
                    proc.info['cpu_percent_normalized'] = cpu_percent
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            return processes

        while self.monitoring:
            try:
                all_processes = list(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']))

                chunk_size = max(1, len(all_processes) // 5)
                process_chunks = [all_processes[i:i + chunk_size] 
                                for i in range(0, len(all_processes), chunk_size)]

                with ThreadPoolExecutor(max_workers=5) as executor:
                    results = executor.map(monitor_chunk, process_chunks)

                all_sorted_processes = sorted(
                    [proc for chunk in results for proc in chunk],
                    key=lambda p: p['cpu_percent_normalized'],
                    reverse=True
                )[:20]  # Top 20 processes

                process_text = "\n".join(
                    f"PID: {proc['pid']:>6} | {proc['name']:<20} | "
                    f"CPU: {proc['cpu_percent_normalized']:>6.2f}% | "
                    f"Memory: {proc['memory_percent']:>6.2f}%"
                    for proc in all_sorted_processes
                )

                self.process_queue.put(process_text)

            except Exception as e:
                messagebox.showerror("Error", 
                                   f"Error monitoring processes: {e}")

            time.sleep(2)

    def export_data(self):
        export_data(self)

    def cleanup(self):
        self.monitoring = False
        self.root.quit()