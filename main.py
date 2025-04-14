from monitor.system_monitor import ResourceMonitor

if __name__ == "__main__":
    CURRENT_VERSION = "v1.0.0"  # Replace with your current version
    monitor = ResourceMonitor(CURRENT_VERSION)
    monitor.root.protocol("WM_DELETE_WINDOW", monitor.cleanup)
    monitor.root.mainloop()
