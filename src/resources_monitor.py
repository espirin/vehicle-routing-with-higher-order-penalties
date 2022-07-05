import resource
from concurrent.futures import ThreadPoolExecutor
from time import sleep


class MemoryMonitor:
    def __init__(self):
        self.keep_measuring = True

    def measure_usage(self):
        memory_usage = []
        while self.keep_measuring:
            memory_usage.append(round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20, 2))
            sleep(1)

        system_mode_time = resource.getrusage(resource.RUSAGE_SELF).ru_stime
        user_mode_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime

        return memory_usage, user_mode_time, system_mode_time


def measure_resources_usage(function):
    with ThreadPoolExecutor() as executor:
        monitor = MemoryMonitor()
        mem_thread = executor.submit(monitor.measure_usage)
        try:
            fn_thread = executor.submit(function)
            _ = fn_thread.result()
        finally:
            monitor.keep_measuring = False
            memory_usage, user_mode_time, system_mode_time = mem_thread.result()

        print(f"Memory usage: {memory_usage}")
        print(f"CPU user time: {user_mode_time}")
        print(f"CPU system time: {system_mode_time}")
