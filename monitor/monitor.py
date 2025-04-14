import time
import psutil
from plyer import notification

def monitor_resources(self):
    cpu_high_start_time = None
    memory_high_start_time = None

    while self.monitoring:
        try:
            cpu_percent_per_core = psutil.cpu_percent(interval=self.CPU_MON_INTERVAL, percpu=True)
            avg_cpu_percent = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
            memory_percent = psutil.virtual_memory().percent

            self.cpu_history.append(avg_cpu_percent)
            self.memory_history.append(memory_percent)
            self.time_history.append(time.strftime('%H:%M:%S'))

            self.all_cpu_history.append(avg_cpu_percent)
            self.all_memory_history.append(memory_percent)
            self.all_time_history.append(time.strftime('%H:%M:%S'))

            current_time = time.time()

            if avg_cpu_percent > self.CPU_THRESHOLD:
                if cpu_high_start_time is None:
                    cpu_high_start_time = current_time
                elif current_time - cpu_high_start_time >= 60:
                    notification.notify(
                        title="Resource Alert",
                        message=f"CPU usage has been over {self.CPU_THRESHOLD}% for more than {int(current_time - cpu_high_start_time)} seconds!",
                        timeout=3
                    )
                    cpu_high_start_time = None
            else:
                cpu_high_start_time = None

            if memory_percent > self.MEMORY_THRESHOLD:
                if memory_high_start_time is None:
                    memory_high_start_time = current_time
                elif current_time - memory_high_start_time >= 120:
                    notification.notify(
                        title="Resource Alert",
                        message=f"Memory usage has been over {self.MEMORY_THRESHOLD}% for more than 120 seconds!",
                        timeout=3
                    )
                    memory_high_start_time = None
            else:
                memory_high_start_time = None

        except Exception as e:
            print(f"Error during monitoring: {e}")

def update_graph(self):
    while self.monitoring:
        self.ax.clear()
        self.ax.plot(self.all_time_history[-self.HISTORY_LENGTH:], self.all_cpu_history[-self.HISTORY_LENGTH:], label='CPU %')
        self.ax.plot(self.all_time_history[-self.HISTORY_LENGTH:], self.all_memory_history[-self.HISTORY_LENGTH:], label='Memory %')
        self.ax.legend()
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Percentage')
        self.ax.set_title('Resource Usage Graph')
        self.canvas.draw()
