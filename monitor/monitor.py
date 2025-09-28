import time
from tkinter import messagebox
import psutil
from plyer import notification
import threading
import subprocess
import platform
import os
import json
import re
import matplotlib.pyplot as plt

# Multiple GPU monitoring approaches
try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False

try:
    import nvidia_ml_py3 as nvml
    nvml.nvmlInit()
    NVML_AVAILABLE = True
except (ImportError, Exception):
    NVML_AVAILABLE = False

def get_amd_gpu_info():
    """Get AMD GPU information using multiple methods"""
    gpu_usage = 0.0
    gpu_memory = 0.0
    
    # Method 1: Try Windows Performance Toolkit (WPA) counters
    if platform.system() == 'Windows':
        try:
            # Try WMI query for AMD GPU performance
            wmi_query = '''
            wmic path Win32_PerfRawData_amdlog_AMDRadeonSoftware get /format:csv
            '''
            result = subprocess.run(
                ['wmic', 'path', 'Win32_PerfRawData_amdlog_AMDRadeonSoftware', 'get', '/format:csv'],
                capture_output=True, text=True, timeout=3, shell=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse WMI output for AMD GPU stats
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'GPU' in line and '%' in line:
                        # Try to extract percentage values
                        percentages = re.findall(r'(\d+\.?\d*)%', line)
                        if percentages:
                            gpu_usage = float(percentages[0])
                            return gpu_usage, gpu_memory
        except Exception:
            pass
    
    # Method 2: Try AMD GPU Performance API (if available)
    try:
        # Check for AMD GPU-Z or similar tools output
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue'],
            capture_output=True, text=True, timeout=3
        )
        
        if result.returncode == 0 and result.stdout.strip():
            values = result.stdout.strip().split('\n')
            for value in values:
                try:
                    usage = float(value.strip())
                    if 0 <= usage <= 100:
                        gpu_usage = max(gpu_usage, usage)  # Take highest usage
                except ValueError:
                    continue
            return gpu_usage, gpu_memory
    except Exception:
        pass
    
    # Method 3: Try AMD Radeon Software CLI (if installed)
    try:
        # Check if AMD CLI tools are available
        amd_paths = [
            r"C:\Program Files\AMD\RadeonSoftware\RadeonSoftware.exe",
            r"C:\Program Files (x86)\AMD\RadeonSoftware\RadeonSoftware.exe"
        ]
        
        for path in amd_paths:
            if os.path.exists(path):
                # AMD Radeon Software is installed
                # Try to get stats (this is a placeholder - actual implementation depends on AMD CLI)
                break
    except Exception:
        pass
    
    # Method 4: Parse Task Manager / Resource Monitor for GPU usage (Windows)
    if platform.system() == 'Windows':
        try:
            # Use tasklist to check for GPU-intensive processes
            result = subprocess.run([
                'powershell', '-Command',
                '(Get-Counter "\\GPU Process Memory(*)\\Local Memory Usage").CounterSamples | Measure-Object CookedValue -Sum | Select-Object -ExpandProperty Sum'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0 and result.stdout.strip():
                memory_bytes = float(result.stdout.strip())
                # Estimate GPU memory usage (assuming 16GB for RX 6800 XT)
                total_vram = 16 * 1024 * 1024 * 1024  # 16GB in bytes
                gpu_memory = (memory_bytes / total_vram) * 100
                gpu_memory = min(gpu_memory, 100)  # Cap at 100%
        except Exception:
            pass
    
    # Method 5: Simple heuristic based on system load
    try:
        # If we can't get real GPU usage, estimate based on system activity
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Look for GPU-intensive processes
        gpu_processes = ['game', 'render', 'blender', 'obs', 'streaming', 'mining', 'crypto']
        active_processes = [p.info['name'].lower() for p in psutil.process_iter(['name'])]
        
        has_gpu_workload = any(proc in ' '.join(active_processes) for proc in gpu_processes)
        
        if has_gpu_workload:
            # Estimate GPU usage based on heuristics
            gpu_usage = min(cpu_usage * 1.2, 95.0)  # Rough estimate
        
    except Exception:
        pass
    
    return gpu_usage, gpu_memory

def get_gpu_info():
    """Get GPU usage information with AMD support"""
    gpu_usage = 0.0
    gpu_memory = 0.0
    
    # Method 1: Try NVIDIA ML (for NVIDIA cards)
    if NVML_AVAILABLE:
        try:
            device_count = nvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_usage = util.gpu
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory = (mem_info.used / mem_info.total) * 100
                return gpu_usage, gpu_memory
        except Exception:
            pass
    
    # Method 2: Try GPUtil (for NVIDIA cards)
    if GPUTIL_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus and len(gpus) > 0:
                gpu = gpus[0]
                gpu_usage = gpu.load * 100
                gpu_memory = gpu.memoryUtil * 100
                return gpu_usage, gpu_memory
        except Exception:
            pass
    
    # Method 3: Try AMD GPU monitoring
    gpu_usage, gpu_memory = get_amd_gpu_info()
    if gpu_usage > 0 or gpu_memory > 0:
        return gpu_usage, gpu_memory
    
    # Method 4: Universal GPU monitoring via Windows Performance Counters
    if platform.system() == 'Windows':
        try:
            # Generic GPU counter that works for most GPUs
            result = subprocess.run([
                'powershell', '-Command',
                '''
                try {
                    $counters = Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -ErrorAction Stop
                    $maxUsage = ($counters.CounterSamples | Measure-Object CookedValue -Maximum).Maximum
                    Write-Output $maxUsage
                } catch {
                    Write-Output "0"
                }
                '''
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    gpu_usage = float(result.stdout.strip())
                    gpu_usage = min(max(gpu_usage, 0), 100)  # Clamp between 0-100
                except ValueError:
                    gpu_usage = 0.0
        except Exception:
            pass
    
    return gpu_usage, gpu_memory

def check_gpu_existence():
    """Check if GPU hardware exists - enhanced for AMD detection"""
    
    # Windows GPU detection
    if platform.system() == 'Windows':
        try:
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'get', 'name'
            ], capture_output=True, text=True, timeout=5, shell=True)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                gpu_keywords = [
                    'nvidia', 'geforce', 'quadro', 'rtx', 'gtx',  # NVIDIA
                    'amd', 'radeon', 'rx', 'vega', 'navi',       # AMD
                    'intel arc', 'intel iris', 'intel xe'        # Intel
                ]
                if any(keyword in output for keyword in gpu_keywords):
                    return True
        except:
            pass
    
    # Linux GPU detection
    elif platform.system() == 'Linux':
        try:
            # Check for AMD GPU
            if os.path.exists('/sys/class/drm/card0/device/vendor'):
                with open('/sys/class/drm/card0/device/vendor', 'r') as f:
                    vendor = f.read().strip()
                    if vendor in ['0x1002', '0x10de', '0x8086']:  # AMD, NVIDIA, Intel
                        return True
            
            # Check via lspci
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout.lower()
                if any(keyword in output for keyword in ['amd', 'nvidia', 'intel']):
                    return True
        except:
            pass
    
    return False

def get_gpu_diagnostic_info():
    """Get diagnostic information about GPU detection"""
    info = {
        'gpu_detected': check_gpu_existence(),
        'nvml_available': NVML_AVAILABLE,
        'gputil_available': GPUTIL_AVAILABLE,
        'platform': platform.system(),
        'gpu_type': 'Unknown'
    }
    
    # Detect GPU type
    if platform.system() == 'Windows':
        try:
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'get', 'name'
            ], capture_output=True, text=True, timeout=5, shell=True)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'amd' in output or 'radeon' in output:
                    info['gpu_type'] = 'AMD'
                elif 'nvidia' in output or 'geforce' in output:
                    info['gpu_type'] = 'NVIDIA'
                elif 'intel' in output:
                    info['gpu_type'] = 'Intel'
        except:
            pass
    
    return info

def monitor_resources(self):
    cpu_high_start_time = None
    memory_high_start_time = None
    gpu_high_start_time = None
    
    # Get GPU diagnostic info (only print once)
    gpu_info = get_gpu_diagnostic_info()
    
    if gpu_info['gpu_detected']:
        print(f"INFO: {gpu_info['gpu_type']} GPU detected")
        if gpu_info['gpu_type'] == 'AMD':
            print("INFO: AMD GPU monitoring enabled with Windows Performance Counters")
        elif gpu_info['gpu_type'] == 'NVIDIA':
            if not (gpu_info['nvml_available'] or gpu_info['gputil_available']):
                print("INFO: NVIDIA GPU detected but monitoring libraries not available")
        else:
            print("INFO: GPU monitoring may be limited for this GPU type")
    else:
        print("INFO: No dedicated GPU detected")

    while self.monitoring:
        try:
            # CPU and Memory monitoring
            cpu_percent_per_core = psutil.cpu_percent(interval=self.CPU_MON_INTERVAL, percpu=True)
            avg_cpu_percent = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
            memory_percent = psutil.virtual_memory().percent
            
            # GPU monitoring with AMD support
            gpu_percent, gpu_memory_percent = get_gpu_info()

            # Update histories
            self.cpu_history.append(avg_cpu_percent)
            self.memory_history.append(memory_percent)
            self.gpu_history.append(gpu_percent)
            self.gpu_memory_history.append(gpu_memory_percent)
            self.time_history.append(time.strftime('%H:%M:%S'))

            self.all_cpu_history.append(avg_cpu_percent)
            self.all_memory_history.append(memory_percent)
            self.all_gpu_history.append(gpu_percent)
            self.all_gpu_memory_history.append(gpu_memory_percent)
            self.all_time_history.append(time.strftime('%H:%M:%S'))

            current_time = time.time()

            # CPU threshold checking
            if avg_cpu_percent > self.CPU_THRESHOLD:
                if cpu_high_start_time is None:
                    cpu_high_start_time = current_time
                elif current_time - cpu_high_start_time >= 60:
                    notification.notify(
                        title="⚠️ CPU Alert",
                        message=f"CPU usage over {self.CPU_THRESHOLD}% for {int(current_time - cpu_high_start_time)}s",
                        timeout=5
                    )
                    cpu_high_start_time = None
            else:
                cpu_high_start_time = None

            # Memory threshold checking
            if memory_percent > self.MEMORY_THRESHOLD:
                if memory_high_start_time is None:
                    memory_high_start_time = current_time
                elif current_time - memory_high_start_time >= 120:
                    notification.notify(
                        title="⚠️ Memory Alert",
                        message=f"Memory usage over {self.MEMORY_THRESHOLD}% for 120s",
                        timeout=5
                    )
                    memory_high_start_time = None
            else:
                memory_high_start_time = None

            # GPU threshold checking
            if gpu_percent > 0.0 and gpu_percent > self.GPU_THRESHOLD:
                if gpu_high_start_time is None:
                    gpu_high_start_time = current_time
                elif current_time - gpu_high_start_time >= 60:
                    notification.notify(
                        title="⚠️ GPU Alert",
                        message=f"GPU usage over {self.GPU_THRESHOLD}% for {int(current_time - gpu_high_start_time)}s",
                        timeout=5
                    )
                    gpu_high_start_time = None
            else:
                gpu_high_start_time = None

        except Exception as e:
            print(f"Monitoring error: {e}")

def update_graph(self):
    """Update the resource usage graphs with AMD GPU support."""
    while self.monitoring:
        try:
            # Clear all subplots
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#fafafa')

            # Get recent data for display
            recent_length = min(60, len(self.all_time_history))
            if recent_length > 0:
                time_data = self.all_time_history[-recent_length:]
                cpu_data = self.all_cpu_history[-recent_length:]
                memory_data = self.all_memory_history[-recent_length:]
                gpu_data = self.all_gpu_history[-recent_length:]
                gpu_memory_data = self.all_gpu_memory_history[-recent_length:]

                # CPU Graph
                self.ax1.plot(range(len(cpu_data)), cpu_data, 
                             color='#0078d4', linewidth=2, label='CPU Usage')
                self.ax1.axhline(y=self.CPU_THRESHOLD, color='#d13438', 
                               linestyle='--', alpha=0.7, label=f'Threshold ({self.CPU_THRESHOLD}%)')
                self.ax1.set_title('CPU Usage', fontweight='bold')
                self.ax1.set_ylabel('Percentage (%)')
                self.ax1.set_ylim(0, 100)
                self.ax1.legend()

                # Memory Graph
                self.ax2.plot(range(len(memory_data)), memory_data, 
                             color='#107c10', linewidth=2, label='Memory Usage')
                self.ax2.axhline(y=self.MEMORY_THRESHOLD, color='#d13438', 
                               linestyle='--', alpha=0.7, label=f'Threshold ({self.MEMORY_THRESHOLD}%)')
                self.ax2.set_title('Memory Usage', fontweight='bold')
                self.ax2.set_ylabel('Percentage (%)')
                self.ax2.set_ylim(0, 100)
                self.ax2.legend()

                # GPU Usage Graph
                gpu_detected = check_gpu_existence()
                has_gpu_data = any(x > 0.0 for x in gpu_data)
                
                if gpu_detected:
                    self.ax3.plot(range(len(gpu_data)), gpu_data, 
                                 color='#ca5010', linewidth=2, label='GPU Usage (AMD RX 6800 XT)')
                    
                    if has_gpu_data:
                        self.ax3.axhline(y=self.GPU_THRESHOLD, color='#d13438', 
                                       linestyle='--', alpha=0.7, label=f'Threshold ({self.GPU_THRESHOLD}%)')
                    
                    if not has_gpu_data:
                        self.ax3.text(0.5, 0.3, 'AMD GPU Detected\n(Limited monitoring)', 
                                     transform=self.ax3.transAxes, ha='center', va='center',
                                     fontsize=10, alpha=0.7)
                    
                    self.ax3.legend()
                else:
                    self.ax3.text(0.5, 0.5, 'No Dedicated GPU\nDetected', 
                                 transform=self.ax3.transAxes, ha='center', va='center',
                                 fontsize=12, alpha=0.6)
                
                self.ax3.set_title('GPU Usage', fontweight='bold')
                self.ax3.set_ylabel('Percentage (%)')
                self.ax3.set_xlabel('Time')
                self.ax3.set_ylim(0, 100)

                # GPU Memory Graph
                has_gpu_memory_data = any(x > 0.0 for x in gpu_memory_data)
                
                if gpu_detected:
                    self.ax4.plot(range(len(gpu_memory_data)), gpu_memory_data, 
                                 color='#8764b8', linewidth=2, label='GPU Memory')
                    
                    if not has_gpu_memory_data:
                        self.ax4.text(0.5, 0.3, 'AMD GPU Memory\n(Monitoring Limited)', 
                                     transform=self.ax4.transAxes, ha='center', va='center',
                                     fontsize=10, alpha=0.7)
                    
                    self.ax4.legend()
                else:
                    self.ax4.text(0.5, 0.5, 'No GPU Memory\nMonitoring Available', 
                                 transform=self.ax4.transAxes, ha='center', va='center',
                                 fontsize=12, alpha=0.6)
                
                self.ax4.set_title('GPU Memory', fontweight='bold')
                self.ax4.set_ylabel('Percentage (%)')
                self.ax4.set_xlabel('Time')
                self.ax4.set_ylim(0, 100)

            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Graph update error: {e}")
        
        time.sleep(1)