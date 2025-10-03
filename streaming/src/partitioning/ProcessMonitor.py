import psutil
import threading
import time


class ProcessMonitor:
    def __init__(self):
        """
        Initialize the process monitor with default values.
        """

        self.max_cpu = 0
        self.max_memory = 0
        self.running = False
        self.previous_times = {}

    def start(self):
        """
        Start the process monitoring in a separate daemon thread.
        """

        self.running = True
        self._get_current_metrics()
        time.sleep(1)
        threading.Thread(target=self._monitor, daemon=True).start()

    def stop(self):
        """
        Stop the process monitoring and print the peak CPU and memory usage.
        """

        self.running = False
        print(f"Peak CPU: {self.max_cpu:.1f}% | Peak Memory: {self.max_memory:.2f} GB")

    def _get_current_metrics(self):
        """
        Get current CPU and memory metrics for Python/Java processes.
        Returns total CPU percentage and memory in GB.
        """

        total_cpu = 0
        total_memory = 0
        current_times = {}

        for proc in psutil.process_iter(["pid", "name", "cpu_times", "memory_info"]):
            try:
                name = proc.info["name"].lower()
                if "python" in name or "java" in name:
                    pid = proc.info["pid"]

                    cpu_times = proc.info["cpu_times"]
                    total_time = cpu_times.user + cpu_times.system
                    current_times[pid] = total_time

                    if pid in self.previous_times:
                        time_diff = total_time - self.previous_times[pid]
                        cpu_percent = min(time_diff * 100, 100.0)
                        total_cpu += cpu_percent

                    memory_gb = proc.info["memory_info"].rss / (1024**3)
                    total_memory += memory_gb

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self.previous_times = current_times

        return total_cpu, total_memory

    def _monitor(self):
        """
        Monitor the CPU and memory usage of Python and Java processes.
        Update the peak usage values every second.
        """

        while self.running:
            cpu, memory = self._get_current_metrics()

            self.max_cpu = max(self.max_cpu, cpu)
            self.max_memory = max(self.max_memory, memory)

            time.sleep(1)

    def get_current_snapshot(self):
        """
        Get a one-time snapshot of current resource usage.
        """

        cpu, memory = self._get_current_metrics()
        return {"cpu_percent": cpu, "memory_gb": memory}
