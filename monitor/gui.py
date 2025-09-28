import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from utils.utils import gather_system_info
import requests
from tkinter import messagebox

def create_gui(self):
    # Configure matplotlib for modern look
    plt.style.use('default')
    
    # Main container with padding
    main_frame = ttk.Frame(self.root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tab control with modern styling
    self.tab_control = ttk.Notebook(main_frame)
    self.tab_control.pack(expand=1, fill="both")

    # ==================== MONITORING TAB ====================
    monitor_tab = ttk.Frame(self.tab_control)
    self.tab_control.add(monitor_tab, text="📊 Resource Monitor")

    # Control Panel
    control_frame = ttk.LabelFrame(monitor_tab, text="Control Panel", padding=15)
    control_frame.pack(fill="x", pady=(0, 10))

    # Status indicator
    status_frame = ttk.Frame(control_frame)
    status_frame.pack(fill="x", pady=(0, 10))
    
    self.status_label = ttk.Label(status_frame, text="🔴 Monitoring Stopped", 
                                 font=('Segoe UI', 10, 'bold'))
    self.status_label.pack(side="left")

    # Threshold settings in a grid
    threshold_grid = ttk.Frame(control_frame)
    threshold_grid.pack(fill="x", pady=10)

    # CPU Threshold
    ttk.Label(threshold_grid, text="CPU Threshold (%):").grid(
        row=0, column=0, padx=5, pady=5, sticky="w")
    cpu_entry = ttk.Entry(threshold_grid, width=10)
    cpu_entry.grid(row=0, column=1, padx=5, pady=5)
    cpu_entry.insert(0, str(self.CPU_THRESHOLD))

    # Memory Threshold
    ttk.Label(threshold_grid, text="Memory Threshold (%):").grid(
        row=0, column=2, padx=5, pady=5, sticky="w")
    memory_entry = ttk.Entry(threshold_grid, width=10)
    memory_entry.grid(row=0, column=3, padx=5, pady=5)
    memory_entry.insert(0, str(self.MEMORY_THRESHOLD))

    # GPU Threshold
    ttk.Label(threshold_grid, text="GPU Threshold (%):").grid(
        row=1, column=0, padx=5, pady=5, sticky="w")
    gpu_entry = ttk.Entry(threshold_grid, width=10)
    gpu_entry.grid(row=1, column=1, padx=5, pady=5)
    gpu_entry.insert(0, str(self.GPU_THRESHOLD))

    # Monitoring Interval
    ttk.Label(threshold_grid, text="Update Interval (s):").grid(
        row=1, column=2, padx=5, pady=5, sticky="w")
    interval_entry = ttk.Entry(threshold_grid, width=10)
    interval_entry.grid(row=1, column=3, padx=5, pady=5)
    interval_entry.insert(0, str(self.CPU_MON_INTERVAL))

    # Threshold save functions
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

    def save_gpu_threshold(event):
        try:
            self.GPU_THRESHOLD = float(gpu_entry.get())
        except ValueError:
            gpu_entry.delete(0, "end")
            gpu_entry.insert(0, str(self.GPU_THRESHOLD))

    def save_interval(event):
        try:
            self.CPU_MON_INTERVAL = float(interval_entry.get())
        except ValueError:
            interval_entry.delete(0, "end")
            interval_entry.insert(0, str(self.CPU_MON_INTERVAL))

    # Bind events
    cpu_entry.bind('<FocusOut>', save_cpu_threshold)
    memory_entry.bind('<FocusOut>', save_memory_threshold)
    gpu_entry.bind('<FocusOut>', save_gpu_threshold)
    interval_entry.bind('<FocusOut>', save_interval)

    # Control buttons
    button_frame = ttk.Frame(control_frame)
    button_frame.pack(pady=10)

    self.start_button = ttk.Button(button_frame, text="▶ Start Monitoring", 
                                  command=self.start_monitoring, style='Modern.TButton')
    self.start_button.pack(side="left", padx=5)

    self.stop_button = ttk.Button(button_frame, text="⏹ Stop Monitoring", 
                                 command=self.stop_monitoring, state="disabled", 
                                 style='Modern.TButton')
    self.stop_button.pack(side="left", padx=5)

    export_button = ttk.Button(button_frame, text="💾 Export Data", 
                              command=self.export_data, style='Modern.TButton')
    export_button.pack(side="left", padx=5)

    # Graph Frame with modern styling
    graph_frame = ttk.LabelFrame(monitor_tab, text="Real-time Resource Usage", 
                                padding=10)
    graph_frame.pack(fill="both", expand=True)

    # Create figure with subplots for better organization
    self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, 
                                                                          figsize=(12, 8))
    self.fig.suptitle('System Resource Monitor', fontsize=14, fontweight='bold')
    
    # Style the subplots
    for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#fafafa')
    
    self.ax1.set_title('CPU Usage', fontweight='bold')
    self.ax1.set_ylabel('Percentage (%)')
    
    self.ax2.set_title('Memory Usage', fontweight='bold')
    self.ax2.set_ylabel('Percentage (%)')
    
    self.ax3.set_title('GPU Usage', fontweight='bold')
    self.ax3.set_ylabel('Percentage (%)')
    self.ax3.set_xlabel('Time')
    
    self.ax4.set_title('GPU Memory', fontweight='bold')
    self.ax4.set_ylabel('Percentage (%)')
    self.ax4.set_xlabel('Time')

    plt.tight_layout()
    
    self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
    self.canvas.get_tk_widget().pack(fill='both', expand=True)

    # ==================== PROCESSES TAB ====================
    processes_tab = ttk.Frame(self.tab_control)
    self.tab_control.add(processes_tab, text="🔧 Top Processes")

    # Process info frame
    process_info_frame = ttk.LabelFrame(processes_tab, text="Top 20 Processes by CPU Usage", 
                                       padding=10)
    process_info_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Process list with modern styling
    process_container = ttk.Frame(process_info_frame)
    process_container.pack(fill="both", expand=True)

    process_scrollbar = ttk.Scrollbar(process_container, orient="vertical")
    process_scrollbar.pack(side="right", fill="y")

    self.process_list = tk.Text(process_container, height=25, state="disabled", 
                               yscrollcommand=process_scrollbar.set,
                               font=('Consolas', 9), bg='#fafafa')
    self.process_list.pack(side="left", fill="both", expand=True)
    process_scrollbar.config(command=self.process_list.yview)

    # Export button for processes
    export_proc_button = ttk.Button(processes_tab, text="💾 Export Processes", 
                                   command=self.export_top_processes,
                                   style='Modern.TButton')
    export_proc_button.pack(pady=10)

    # Schedule updates
    self.update_process_info()