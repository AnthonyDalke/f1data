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

    def start(self):
        """
        Start the process monitoring in a separate daemon thread.
        """

        self.running = True
        threading.Thread(target=self._monitor, daemon=True).start()

    def stop(self):
        """
        Stop the process monitoring and print the peak CPU and memory usage.
        """

        self.running = False
        print(f"Peak CPU: {self.max_cpu:.1f}% | Peak Memory: {self.max_memory:.2f} GB")

    def _monitor(self):
        """
        Monitor the CPU and memory usage of Python and Java processes.
        Update the peak usage values every second.
        """

        while self.running:
            total_cpu = total_memory = 0
            for proc in psutil.process_iter(["name", "cpu_percent", "memory_info"]):
                try:
                    name = proc.info["name"].lower()
                    if "python" in name or "java" in name:
                        total_cpu += proc.cpu_percent()
                        total_memory += proc.info["memory_info"].rss / (1024**3)
                except:
                    continue

            self.max_cpu = max(self.max_cpu, total_cpu)
            self.max_memory = max(self.max_memory, total_memory)
            time.sleep(1)
