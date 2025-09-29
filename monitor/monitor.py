import time
from tkinter import messagebox
import psutil
from plyer import notification
import threading
import subprocess
import platform
import os
import sys

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
    
    if platform.system() == 'Windows':
        try:
            # FIXED: Add creationflags to prevent console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
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
            ], capture_output=True, text=True, timeout=5,
               startupinfo=startupinfo,
               creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and result.stdout and result.stdout.strip():
                try:
                    gpu_usage = float(result.stdout.strip())
                    gpu_usage = min(max(gpu_usage, 0), 100)
                except (ValueError, AttributeError):
                    gpu_usage = 0.0
        except Exception:
            pass
    
    return gpu_usage, gpu_memory

def get_gpu_info():
    """Get GPU usage information with AMD support"""
    gpu_usage = 0.0
    gpu_memory = 0.0
    
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
    
    gpu_usage, gpu_memory = get_amd_gpu_info()
    return gpu_usage, gpu_memory

def check_gpu_existence():
    """Check if GPU hardware exists"""
    
    if platform.system() == 'Windows':
        try:
            # FIXED: Add creationflags to prevent console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'get', 'name'
            ], capture_output=True, text=True, timeout=5, shell=True,
               startupinfo=startupinfo,
               creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                output = result.stdout.lower()
                gpu_keywords = [
                    'nvidia', 'geforce', 'quadro', 'rtx', 'gtx',
                    'amd', 'radeon', 'rx', 'vega', 'navi',
                    'intel arc', 'intel iris', 'intel xe'
                ]
                if any(keyword in output for keyword in gpu_keywords):
                    return True
        except:
            pass
    
    elif platform.system() == 'Linux':
        try:
            if os.path.exists('/sys/class/drm/card0/device/vendor'):
                with open('/sys/class/drm/card0/device/vendor', 'r') as f:
                    vendor = f.read().strip()
                    if vendor in ['0x1002', '0x10de', '0x8086']:
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
    
    if platform.system() == 'Windows':
        try:
            # FIXED: Add creationflags to prevent console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'get', 'name'
            ], capture_output=True, text=True, timeout=5, shell=True,
               startupinfo=startupinfo,
               creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and result.stdout:
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
    
    try:
        gpu_info = get_gpu_diagnostic_info()
        self.gpu_info = gpu_info
    except:
        self.gpu_info = {'gpu_detected': False, 'gpu_type': 'Unknown'}

    while self.monitoring:
        try:
            cpu_percent_per_core = psutil.cpu_percent(interval=self.CPU_MON_INTERVAL, percpu=True)
            avg_cpu_percent = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
            memory_percent = psutil.virtual_memory().percent
            
            gpu_percent, gpu_memory_percent = get_gpu_info()

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

            if avg_cpu_percent > self.CPU_THRESHOLD:
                if cpu_high_start_time is None:
                    cpu_high_start_time = current_time
                elif current_time - cpu_high_start_time >= 60:
                    try:
                        notification.notify(
                            title="CPU Alert",
                            message=f"CPU usage over {self.CPU_THRESHOLD}% for {int(current_time - cpu_high_start_time)}s",
                            timeout=5
                        )
                    except:
                        pass
                    cpu_high_start_time = None
            else:
                cpu_high_start_time = None

            if memory_percent > self.MEMORY_THRESHOLD:
                if memory_high_start_time is None:
                    memory_high_start_time = current_time
                elif current_time - memory_high_start_time >= 120:
                    try:
                        notification.notify(
                            title="Memory Alert",
                            message=f"Memory usage over {self.MEMORY_THRESHOLD}% for 120s",
                            timeout=5
                        )
                    except:
                        pass
                    memory_high_start_time = None
            else:
                memory_high_start_time = None

            if gpu_percent > 0.0 and gpu_percent > self.GPU_THRESHOLD:
                if gpu_high_start_time is None:
                    gpu_high_start_time = current_time
                elif current_time - gpu_high_start_time >= 60:
                    try:
                        notification.notify(
                            title="GPU Alert",
                            message=f"GPU usage over {self.GPU_THRESHOLD}% for {int(current_time - gpu_high_start_time)}s",
                            timeout=5
                        )
                    except:
                        pass
                    gpu_high_start_time = None
            else:
                gpu_high_start_time = None

        except Exception:
            pass

def update_graph(self):
    """Update the resource usage graphs"""
    while self.monitoring:
        try:
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#fafafa')

            recent_length = min(60, len(self.all_time_history))
            if recent_length > 0:
                time_data = self.all_time_history[-recent_length:]
                cpu_data = self.all_cpu_history[-recent_length:]
                memory_data = self.all_memory_history[-recent_length:]
                gpu_data = self.all_gpu_history[-recent_length:]
                gpu_memory_data = self.all_gpu_memory_history[-recent_length:]

                self.ax1.plot(range(len(cpu_data)), cpu_data, 
                             color='#0078d4', linewidth=2, label='CPU Usage')
                self.ax1.axhline(y=self.CPU_THRESHOLD, color='#d13438', 
                               linestyle='--', alpha=0.7, label=f'Threshold ({self.CPU_THRESHOLD}%)')
                self.ax1.set_title('CPU Usage', fontweight='bold')
                self.ax1.set_ylabel('Percentage (%)')
                self.ax1.set_ylim(0, 100)
                self.ax1.legend()

                self.ax2.plot(range(len(memory_data)), memory_data, 
                             color='#107c10', linewidth=2, label='Memory Usage')
                self.ax2.axhline(y=self.MEMORY_THRESHOLD, color='#d13438', 
                               linestyle='--', alpha=0.7, label=f'Threshold ({self.MEMORY_THRESHOLD}%)')
                self.ax2.set_title('Memory Usage', fontweight='bold')
                self.ax2.set_ylabel('Percentage (%)')
                self.ax2.set_ylim(0, 100)
                self.ax2.legend()

                gpu_detected = check_gpu_existence()
                has_gpu_data = any(x > 0.0 for x in gpu_data)
                
                if gpu_detected:
                    self.ax3.plot(range(len(gpu_data)), gpu_data, 
                                 color='#ca5010', linewidth=2, label='GPU Usage')
                    
                    if has_gpu_data:
                        self.ax3.axhline(y=self.GPU_THRESHOLD, color='#d13438', 
                                       linestyle='--', alpha=0.7, label=f'Threshold ({self.GPU_THRESHOLD}%)')
                    
                    if not has_gpu_data:
                        self.ax3.text(0.5, 0.3, 'GPU Detected\n(Idle or Limited Monitoring)', 
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

                has_gpu_memory_data = any(x > 0.0 for x in gpu_memory_data)
                
                if gpu_detected:
                    self.ax4.plot(range(len(gpu_memory_data)), gpu_memory_data, 
                                 color='#8764b8', linewidth=2, label='GPU Memory')
                    
                    if not has_gpu_memory_data:
                        self.ax4.text(0.5, 0.3, 'GPU Memory\n(Limited Monitoring)', 
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

            import matplotlib.pyplot as plt
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception:
            pass
        
        time.sleep(1)