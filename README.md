# System Resource Monitor v2.0

<div align="center">
  <h3>🖥️ Professional System Monitoring with GPU Support 🎮</h3>
  <p><em>Real-time monitoring of CPU, Memory, and GPU resources with modern UI</em></p>
  
  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
  ![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B-lightgrey.svg)
  ![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
  ![GPU](https://img.shields.io/badge/GPU-NVIDIA%20%7C%20AMD%20%7C%20Intel-orange.svg)
</div>

---

## 📋 Overview

The **System Resource Monitor v2.0** is a comprehensive Python application that provides professional-grade monitoring of system resources. Built with a modern 4-panel dashboard, it offers real-time tracking of CPU, Memory, GPU usage, and GPU memory with intelligent alerting and data export capabilities.

### ✨ What's New in v2.0
- **🎮 Multi-GPU Support**: NVIDIA, AMD Radeon, and Intel Arc GPUs
- **📊 4-Panel Dashboard**: Dedicated graphs for CPU, Memory, GPU, and GPU Memory
- **🎨 Modern UI**: Professional interface with status indicators and emoji icons
- **⚡ Enhanced Performance**: 60-point history with optimized rendering
- **🔧 Smart Detection**: Automatic GPU hardware detection with fallbacks

---

## 🚀 Features

### 📈 **Comprehensive Monitoring**
- **Real-time CPU tracking** with per-core analysis
- **Memory usage monitoring** with threshold alerts
- **GPU utilization tracking** for gaming and content creation
- **GPU memory monitoring** to prevent VRAM overflow
- **Top 20 process tracking** sorted by CPU usage

### 🎯 **Smart Alerting System**
- **Customizable thresholds** for each resource type
- **Desktop notifications** with Windows 10/11 integration
- **Sustained alert logic** (CPU: 60s, Memory: 120s, GPU: 60s)
- **Visual status indicators** with color-coded feedback

### 📊 **Advanced Visualization**
- **4-panel dashboard** with dedicated resource graphs
- **60-point history** for detailed trend analysis
- **Professional styling** with modern matplotlib themes
- **Real-time updates** with smooth graph rendering
- **Threshold visualization** with danger lines

### 💾 **Data Management**
- **CSV export functionality** with GPU metrics included
- **Process list export** for system analysis
- **Historical data retention** for trend analysis
- **Configurable monitoring intervals** (1-10 seconds)

---

## 🎮 GPU Support Matrix

| GPU Vendor | Support Level | Monitoring Method | Requirements |
|------------|---------------|-------------------|--------------|
| **NVIDIA** | ✅ Full | nvidia-ml-py3, GPUtil | Latest NVIDIA drivers |
| **AMD** | ✅ Full | Windows Performance Counters | Latest AMD drivers |
| **Intel Arc** | ⚠️ Basic | Hardware detection | Intel Arc drivers |
| **Integrated** | ℹ️ Detection | System information only | N/A |

### 🔥 Tested Hardware
- **AMD Radeon RX 6800 XT** - Full monitoring support ✅
- **NVIDIA GeForce RTX Series** - Full monitoring support ✅
- **NVIDIA GTX Series** - Full monitoring support ✅

---

## ⚙️ Installation & Setup

### 🎯 **Quick Start (End Users)**
1. **Download** the latest release from the releases page
2. **Extract** the ZIP file to your preferred location
3. **Run** `install.bat` to check system compatibility
4. **Launch** `SystemResourceMonitor.exe`

### 👨‍💻 **Development Setup**
```bash
# Clone the repository
git clone https://github.com/your-username/System-Resource-Monitor.git
cd System-Resource-Monitor

# Install dependencies
pip install -r requirements.txt

# For GPU monitoring (optional)
pip install GPUtil nvidia-ml-py3

# Run the application
python main.py
```

### 📦 **Build from Source**
```bash
# Install build tools
pip install pyinstaller

# Build executable
python build_system_monitor.py

# Find your executable in the 'release' folder
```

---

## 🎮 Usage Guide

### 🖥️ **Main Interface**

#### **Resource Monitor Tab**
- **Control Panel**: Set thresholds and monitoring intervals
- **4-Panel Dashboard**: View CPU, Memory, GPU, and GPU Memory
- **Status Indicator**: 🟢 Active / 🔴 Stopped monitoring
- **Export Functions**: Save data and process lists

#### **Top Processes Tab**
- **Real-time Process List**: Top 20 CPU-intensive processes
- **Detailed Information**: PID, Name, CPU%, Memory%
- **Export Capability**: Save process snapshots

### ⚡ **Quick Actions**
- **Start Monitoring**: Click ▶️ or press `Alt+S`
- **Stop Monitoring**: Click ⏹️ or press `Alt+T`
- **Export Data**: Click 💾 or press `Ctrl+E`

### 🎯 **Recommended Thresholds**
```
CPU: 85%     (Gaming/Workstation)
Memory: 90%  (General Use)
GPU: 99.5%   (High-performance applications)
```

---

## 🔧 Technical Specifications

### 📋 **System Requirements**
- **OS**: Windows 10 or later (Windows 11 recommended)
- **Python**: 3.8+ (for development)
- **RAM**: 100MB minimum, 200MB recommended
- **Permissions**: Administrator rights for optimal GPU monitoring

### 🏗️ **Architecture**
```
├── main.py                 # Application entry point
├── monitor/
│   ├── system_monitor.py   # Core monitoring class
│   ├── gui.py             # Modern UI implementation
│   └── monitor.py         # Resource monitoring logic
├── utils/
│   └── utils.py           # Utility functions & system info
└── build_system_monitor.py # Distribution builder
```

### 🔌 **Dependencies**
```python
# Core Requirements
psutil>=5.8.0          # System monitoring
matplotlib>=3.4.3      # Graph rendering
tkinter                # GUI framework
plyer>=2.0.0          # Notifications

# GPU Monitoring (Optional)
GPUtil                 # Cross-platform GPU support
nvidia-ml-py3         # NVIDIA-specific monitoring
```

---

## 🚨 Troubleshooting

### 🎮 **GPU Issues**

#### **GPU Shows 0% Usage**
1. **Update drivers** to latest version
2. **Run as Administrator** for hardware access
3. **Test with GPU load** (run a game or benchmark)
4. **Run diagnostic**: `python gpu_diagnostic.py`

#### **GPU Not Detected**
- **NVIDIA**: Install drivers from [nvidia.com/drivers](https://nvidia.com/drivers)
- **AMD**: Install drivers from [amd.com/support](https://amd.com/support)
- **Integrated Graphics**: Normal behavior - not a dedicated GPU

### 💻 **Performance Issues**
- **High CPU usage**: Increase monitoring interval to 2-5 seconds
- **Memory leaks**: Restart application after extended use
- **Graph lag**: Close other monitoring applications

### 🔧 **Build Issues**
```bash
# Common solutions
pip install --upgrade pyinstaller
pip install --upgrade matplotlib tkinter
python -m pip install --force-reinstall psutil
```

---

## 🎯 Configuration

### ⚙️ **Monitoring Settings**
| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| CPU Threshold | 85% | 1-100% | CPU usage alert level |
| Memory Threshold | 90% | 1-100% | Memory usage alert level |
| GPU Threshold | 99.5% | 1-100% | GPU usage alert level |
| Update Interval | 1s | 0.5-10s | Monitoring frequency |
| History Length | 60 | 10-300 | Graph data points |

### 🔔 **Alert Timing**
- **CPU Alerts**: Triggered after 60 seconds of sustained high usage
- **Memory Alerts**: Triggered after 120 seconds of sustained high usage  
- **GPU Alerts**: Triggered after 60 seconds of sustained high usage

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 **Bug Reports**
- Use the **Issues** tab to report bugs
- Include system information and GPU model
- Provide steps to reproduce the issue

### ✨ **Feature Requests**
- Suggest new monitoring capabilities
- Request additional GPU vendor support
- Propose UI/UX improvements

### 👨‍💻 **Pull Requests**
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** thoroughly with different GPU configurations
4. **Commit** changes (`git commit -m 'Add amazing feature'`)
5. **Push** to branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.

### 📝 **License Summary**
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed  
- ✅ **Distribution** allowed
- ✅ **Private use** allowed
- ❗ **License and copyright notice** required

---

## 👥 Authors & Acknowledgments

### 👨‍💻 **Created By**
- **Thymester/Tyler** - *Lead Developer & GPU Specialist*

### 🙏 **Special Thanks**
- **AMD RX 6800 XT** users for testing GPU monitoring
- **NVIDIA** community for driver compatibility feedback
- **Open source community** for libraries and inspiration

### 🌟 **Show Your Support**
If this project helped you, please give it a ⭐ on GitHub!

---

## ⚠️ Disclaimer

This application is provided **"as-is"** without any warranty. The authors and contributors are not responsible for any damage, data loss, or system issues caused by the use of this software.

### 🔒 **Privacy & Security**
- **No data collection**: All monitoring data stays on your system
- **No network communication**: Operates entirely offline
- **No user tracking**: Your privacy is completely protected

---

<div align="center">
  <h3>🎮 Ready to monitor your system like a pro? 🚀</h3>
  <p><strong>Download System Resource Monitor v2.0 today!</strong></p>
  
  [📥 Download Latest Release](https://github.com/your-username/System-Resource-Monitor/releases) | 
  [📖 Documentation](https://github.com/your-username/System-Resource-Monitor/wiki) | 
  [🐛 Report Bug](https://github.com/your-username/System-Resource-Monitor/issues) | 
  [💡 Request Feature](https://github.com/your-username/System-Resource-Monitor/issues/new)
</div>
