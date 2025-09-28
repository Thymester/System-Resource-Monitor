import os
import platform
import psutil
import csv
from tkinter import filedialog

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

def export_data(self):
    """Export monitoring data to CSV with GPU information"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", 
        filetypes=[("CSV files", "*.csv")],
        title="Save monitoring data"
    )
    
    if file_path:
        with open(file_path, "w", newline='') as file:
            writer = csv.writer(file)
            
            # Write headers
            headers = ["Time", "CPU (%)", "Memory (%)"]
            if GPU_AVAILABLE:
                headers.extend(["GPU (%)", "GPU Memory (%)"])
            writer.writerow(headers)
            
            # Write data
            for i in range(len(self.all_time_history)):
                row = [
                    self.all_time_history[i], 
                    self.all_cpu_history[i], 
                    self.all_memory_history[i]
                ]
                
                if GPU_AVAILABLE and i < len(self.all_gpu_history):
                    row.extend([
                        self.all_gpu_history[i], 
                        self.all_gpu_memory_history[i]
                    ])
                
                writer.writerow(row)

def gather_system_info():
    """Gather comprehensive system information including GPU"""
    info = []
    
    # Basic system info
    info.append("=== SYSTEM INFORMATION ===")
    info.append(f"OS: {platform.system()} {platform.release()}")
    info.append(f"Architecture: {platform.architecture()[0]}")
    info.append(f"Processor: {platform.processor()}")
    info.append(f"CPU Cores: {os.cpu_count()}")
    
    # Memory info
    memory = psutil.virtual_memory()
    info.append(f"Total RAM: {memory.total / (1024**3):.2f} GB")
    info.append(f"Available RAM: {memory.available / (1024**3):.2f} GB")
    
    # GPU info
    info.append("\n=== GPU INFORMATION ===")
    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                for i, gpu in enumerate(gpus):
                    info.append(f"GPU {i}: {gpu.name}")
                    info.append(f"  Memory: {gpu.memoryTotal} MB")
                    info.append(f"  Driver: {gpu.driver}")
            else:
                info.append("No GPUs detected")
        except Exception as e:
            info.append(f"GPU detection error: {e}")
    else:
        info.append("GPU monitoring not available (install GPUtil)")
    
    # Network interfaces
    info.append("\n=== NETWORK INTERFACES ===")
    for interface, addresses in psutil.net_if_addrs().items():
        info.append(f"Interface: {interface}")
        for address in addresses:
            if hasattr(address.family, 'name'):
                info.append(f"  {address.family.name}: {address.address}")
    
    return "\n".join(info)