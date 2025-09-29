# gpu_diagnostic.py - Run this to diagnose GPU monitoring issues
import subprocess
import platform
import sys

def check_gpu_hardware():
    """Check what GPU hardware you have"""
    print("=== GPU HARDWARE DETECTION ===")
    
    if platform.system() == 'Windows':
        try:
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'get', 'name,driverversion'
            ], capture_output=True, text=True, timeout=10, shell=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print("Detected GPUs:")
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        print(f"  - {line.strip()}")
            else:
                print("Could not detect GPU hardware")
        except Exception as e:
            print(f"Error detecting GPU: {e}")
    
    elif platform.system() == 'Linux':
        try:
            result = subprocess.run(['lspci', '-nn', '|', 'grep', 'VGA'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("Detected GPUs:")
                print(result.stdout)
            else:
                print("Could not detect GPU hardware")
        except:
            print("lspci not available")

def check_nvidia_tools():
    """Check NVIDIA tools availability"""
    print("\n=== NVIDIA TOOLS CHECK ===")
    
    # Check nvidia-smi
    try:
        result = subprocess.run(['nvidia-smi', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ nvidia-smi is available")
            print(f"Version: {result.stdout.split('NVIDIA')[1].split('v')[1].split()[0] if 'NVIDIA' in result.stdout else 'Unknown'}")
        else:
            print("❌ nvidia-smi failed")
    except FileNotFoundError:
        print("❌ nvidia-smi not found in PATH")
        print("   Solution: Install NVIDIA drivers from nvidia.com/drivers")
    except Exception as e:
        print(f"❌ nvidia-smi error: {e}")
    
    # Test nvidia-smi query
    try:
        result = subprocess.run([
            'nvidia-smi', '--query-gpu=name,utilization.gpu,memory.used,memory.total',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ nvidia-smi GPU query works")
            print(f"GPU Info: {result.stdout.strip()}")
        else:
            print("❌ nvidia-smi GPU query failed")
    except Exception as e:
        print(f"❌ nvidia-smi query error: {e}")

def check_python_libraries():
    """Check Python GPU monitoring libraries"""
    print("\n=== PYTHON LIBRARIES CHECK ===")
    
    # Check GPUtil
    try:
        import GPUtil
        print("✅ GPUtil is installed")
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                print(f"✅ GPUtil detects {len(gpus)} GPU(s)")
                for i, gpu in enumerate(gpus):
                    print(f"   GPU {i}: {gpu.name}")
                    print(f"   Load: {gpu.load*100:.1f}%, Memory: {gpu.memoryUtil*100:.1f}%")
            else:
                print("❌ GPUtil finds no GPUs")
        except Exception as e:
            print(f"❌ GPUtil error: {e}")
    except ImportError:
        print("❌ GPUtil not installed")
        print("   Solution: pip install GPUtil")
    
    # Check nvidia-ml-py3
    try:
        import nvidia_ml_py3 as nvml
        print("✅ nvidia-ml-py3 is installed")
        try:
            nvml.nvmlInit()
            device_count = nvml.nvmlDeviceGetCount()
            print(f"✅ NVML detects {device_count} GPU(s)")
            
            if device_count > 0:
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                name = nvml.nvmlDeviceGetName(handle).decode('utf-8')
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                
                print(f"   GPU 0: {name}")
                print(f"   Usage: {util.gpu}%, Memory: {(mem_info.used/mem_info.total)*100:.1f}%")
        except Exception as e:
            print(f"❌ NVML error: {e}")
    except ImportError:
        print("❌ nvidia-ml-py3 not installed")
        print("   Solution: pip install nvidia-ml-py3")

def check_amd_tools():
    """Check for AMD GPU tools"""
    print("\n=== AMD GPU CHECK ===")
    
    # Check for AMD tools
    try:
        # Try rocm-smi for AMD
        result = subprocess.run(['rocm-smi', '--showuse'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ AMD rocm-smi available")
            print(result.stdout)
        else:
            print("❌ AMD rocm-smi not working")
    except FileNotFoundError:
        print("❌ AMD rocm-smi not found")
    except Exception as e:
        print(f"❌ AMD rocm-smi error: {e}")

def check_intel_tools():
    """Check for Intel GPU tools"""
    print("\n=== INTEL GPU CHECK ===")
    
    if platform.system() == 'Windows':
        try:
            # Check for Intel GPU in device manager
            result = subprocess.run([
                'wmic', 'path', 'win32_VideoController', 'where', 
                '"name like \'%intel%\'"', 'get', 'name'
            ], capture_output=True, text=True, timeout=5, shell=True)
            
            if result.returncode == 0 and 'intel' in result.stdout.lower():
                print("✅ Intel GPU detected")
                print("❌ Intel GPU monitoring not implemented yet")
            else:
                print("❌ No Intel GPU detected")
        except Exception as e:
            print(f"❌ Intel GPU check error: {e}")

def provide_solutions():
    """Provide step-by-step solutions"""
    print("\n=== SOLUTIONS ===")
    print("\n1. For NVIDIA GPUs:")
    print("   a) Download latest drivers: https://nvidia.com/drivers")
    print("   b) Install Python libraries: pip install GPUtil nvidia-ml-py3")
    print("   c) Restart your computer after driver installation")
    print("   d) Run as Administrator if permission issues persist")
    
    print("\n2. For AMD GPUs:")
    print("   a) Download latest drivers: https://amd.com/support")
    print("   b) Install ROCm tools (Linux) or AMD Software (Windows)")
    print("   c) Currently limited Python library support for monitoring")
    
    print("\n3. For Intel Arc GPUs:")
    print("   a) Download latest drivers: https://intel.com/content/www/us/en/support/products/80939/graphics.html")
    print("   b) Currently limited monitoring support")
    
    print("\n4. General troubleshooting:")
    print("   a) Restart the application")
    print("   b) Run Python as Administrator (Windows)")
    print("   c) Check if GPU is being used by other applications")
    print("   d) Update your GPU drivers")

if __name__ == "__main__":
    print("GPU Monitoring Diagnostic Tool")
    print("=" * 50)
    
    check_gpu_hardware()
    check_nvidia_tools()
    check_python_libraries()
    check_amd_tools()
    check_intel_tools()
    provide_solutions()
    
    print("\n" + "=" * 50)
    print("Diagnostic complete! Check the results above for next steps.")