import resource
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Dict

from src.config.config import MEMORY_HISTORY_DELTA


class ResourcesMonitor:
    """
    ResourcesMonitor logs resources usage of a running Python process.
    """

    def __init__(self):
        self.keep_measuring = True

    def measure_usage(self):
        memory_usage = []
        while self.keep_measuring:
            memory_usage.append(round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20, 2))
            sleep(MEMORY_HISTORY_DELTA)

        system_mode_time = resource.getrusage(resource.RUSAGE_SELF).ru_stime
        user_mode_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime

        return memory_usage, user_mode_time, system_mode_time


def measure_resources_usage(function, args, return_dict: Dict = None, proc_num: int = None):
    # Start a thread that measures system resources

    with ThreadPoolExecutor() as executor:
        monitor = ResourcesMonitor()
        mem_thread = executor.submit(monitor.measure_usage)
        try:
            args = args + (return_dict, proc_num)
            fn_thread = executor.submit(function, *args)
            _ = fn_thread.result()
        finally:
            monitor.keep_measuring = False
            memory_usage, user_mode_time, system_mode_time = mem_thread.result()

        if return_dict is not None:
            return_dict[proc_num + 100] = {
                "memory": memory_usage,
                "cpu_user": user_mode_time,
                "cpu_system": system_mode_time,
            }
        else:
            print(f"Memory usage: {memory_usage}")
            print(f"CPU user time: {user_mode_time}")
            print(f"CPU system time: {system_mode_time}")
