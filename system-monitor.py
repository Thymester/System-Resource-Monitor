import tkinter as tk
from tkinter import ttk, filedialog
import psutil
import time
import threading
import os
import sys
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from plyer import notification

# Global variables
CPU_THRESHOLD = 80  # Default CPU threshold
MEMORY_THRESHOLD = 80  # Default Memory threshold
MONITOR_INTERVAL = 1  # Refresh interval for monitoring (in seconds)
HISTORY_LENGTH = 7  # Number of data points to store in history

cpu_history = deque(maxlen=HISTORY_LENGTH)
memory_history = deque(maxlen=HISTORY_LENGTH)
time_history = deque(maxlen=HISTORY_LENGTH)

all_cpu_history = []
all_memory_history = []
all_time_history = []

monitoring = False

# Function to monitor system resources
def monitor_resources():
    global monitoring
    last_notification_time = 0
    while monitoring:
        cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)
        avg_cpu_percent = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
        memory_percent = psutil.virtual_memory().percent

        cpu_history.append(avg_cpu_percent)
        memory_history.append(memory_percent)
        time_history.append(time.strftime('%H:%M:%S'))

        all_cpu_history.append(avg_cpu_percent)
        all_memory_history.append(memory_percent)
        all_time_history.append(time.strftime('%H:%M:%S'))

        if avg_cpu_percent > CPU_THRESHOLD:
            current_time = time.time()
            if current_time - last_notification_time >= 3:
                notification.notify(
                    title="Resource Alert",
                    message=f"CPU usage is over {CPU_THRESHOLD}%!",
                    timeout=3
                )
                last_notification_time = current_time

        if memory_percent > MEMORY_THRESHOLD:
            current_time = time.time()
            if current_time - last_notification_time >= 3:
                notification.notify(
                    title="Resource Alert",
                    message=f"Memory usage is over {MEMORY_THRESHOLD}%!",
                    timeout=3
                )
                last_notification_time = current_time

        time.sleep(MONITOR_INTERVAL)

# Function to update the resource graphs
def update_graph():
    while monitoring:
        fig.clf()
        ax = fig.add_subplot(111)
        ax.plot(all_time_history[-HISTORY_LENGTH:], all_cpu_history[-HISTORY_LENGTH:], label='CPU %')
        ax.plot(all_time_history[-HISTORY_LENGTH:], all_memory_history[-HISTORY_LENGTH:], label='Memory %')
        ax.legend()
        ax.set_xlabel('Time')
        ax.set_ylabel('Percentage')
        ax.set_title('Resource Usage')
        ax.grid(True)
        canvas.draw()
        time.sleep(2)

# Function to start monitoring
def start_monitoring():
    global monitoring
    if not monitoring:
        monitoring = True
        threading.Thread(target=monitor_resources, daemon=True).start()
        threading.Thread(target=update_graph, daemon=True).start()
        start_button.config(state="disabled")
        stop_button.config(state="normal")
        monitoring_label.config(text="Monitoring CPU usage. Values may vary due to Task Manager's faster updates.")

# Function to stop monitoring
def stop_monitoring():
    global monitoring
    monitoring = False
    start_button.config(state="normal")
    stop_button.config(state="disabled")
    monitoring_label.config(text="")

# Function to export resource data to a file
def export_data():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, "w") as file:
            file.write("Time,CPU (%),Memory (%)\n")
            for i in range(len(all_time_history)):
                file.write(f"{all_time_history[i]},{all_cpu_history[i]},{all_memory_history[i]}\n")

# Create GUI
root = tk.Tk()
root.title("System Resource Monitor")
root.geometry("800x700")
root.minsize(800, 700)

# Tab control
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both")

# CPU and Memory Monitoring Tab
monitor_tab = ttk.Frame(tab_control)
tab_control.add(monitor_tab, text="Resource Monitoring")

# Resource Threshold Setting Frame
threshold_frame = ttk.LabelFrame(monitor_tab, text="Resource Thresholds")
threshold_frame.pack(padx=10, pady=10, fill="both", expand=True)

# CPU Threshold Entry
cpu_label = ttk.Label(threshold_frame, text="CPU Threshold (%):")
cpu_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
cpu_entry = ttk.Entry(threshold_frame)
cpu_entry.grid(row=0, column=1, padx=5, pady=5)
cpu_entry.insert(0, CPU_THRESHOLD)

# Memory Threshold Entry
memory_label = ttk.Label(threshold_frame, text="Memory Threshold (%):")
memory_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
memory_entry = ttk.Entry(threshold_frame)
memory_entry.grid(row=1, column=1, padx=5, pady=5)
memory_entry.insert(0, MEMORY_THRESHOLD)

# Start and Stop Monitoring Buttons
start_button = ttk.Button(threshold_frame, text="Start Monitoring", command=start_monitoring)
start_button.grid(row=2, column=0, padx=5, pady=5)

stop_button = ttk.Button(threshold_frame, text="Stop Monitoring", command=stop_monitoring, state="disabled")
stop_button.grid(row=2, column=1, padx=5, pady=5)

# Monitoring Label
monitoring_label = ttk.Label(monitor_tab, text="")
monitoring_label.pack(pady=5)

# Graph Frame
graph_frame = ttk.LabelFrame(monitor_tab, text="Resource Usage Graph")
graph_frame.pack(padx=10, pady=10, fill="both", expand=True)

fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(111)
ax.grid(True)
ax.set_xlabel('Time')
ax.set_ylabel('Percentage')
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill='both', expand=True)

# Export Data Button
export_button = ttk.Button(monitor_tab, text="Export Data", command=export_data)
export_button.pack(pady=10)

# System Information Tab
info_tab = ttk.Frame(tab_control)
tab_control.add(info_tab, text="System Information")

# System Information Display
system_info_text = tk.Text(info_tab, wrap="word", height=20, width=60)
system_info_text.pack(padx=10, pady=10)
system_info_text.insert(tk.END, f"CPU Cores: {os.cpu_count()}\n")
system_info_text.insert(tk.END, f"System RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB\n")
system_info_text.insert(tk.END, f"OS Platform & Name: {sys.platform} {os.name}\n")
system_info_text.configure(state="disabled")

# Run the GUI
root.mainloop()
