import sys
import os

# AGGRESSIVE console suppression - this must be FIRST
if getattr(sys, 'frozen', False):  # Running as PyInstaller executable
    import subprocess
    # Hide the console window completely
    if os.name == 'nt':  # Windows
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 0)
        
        # Get console window and hide it
        hwnd = kernel32.GetConsoleWindow()
        if hwnd != 0:
            user32 = ctypes.windll.user32
            user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0
    
    # Redirect ALL output to devnull
    devnull = open(os.devnull, 'w')
    sys.stdout = devnull
    sys.stderr = devnull
    
    # Also redirect subprocess output
    subprocess.DEVNULL = devnull

from monitor.system_monitor import ResourceMonitor

if __name__ == "__main__":
    CURRENT_VERSION = "v2.0"
    monitor = ResourceMonitor(CURRENT_VERSION)
    monitor.root.protocol("WM_DELETE_WINDOW", monitor.cleanup)
    monitor.root.mainloop()