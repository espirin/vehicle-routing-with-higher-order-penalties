from multiprocessing import Process, Manager
from typing import Dict

from src.helpers.resources_monitor import measure_resources_usage


def batch_run(functions_packs, measure_resources: bool = False) -> Dict:
    # Run multiple function in batch using the multiprocessing package
    manager = Manager()
    return_dict = manager.dict()

    processes = []
    for i, (function, args) in enumerate(functions_packs):
        if measure_resources:
            process = Process(target=measure_resources_usage, args=(function, args, return_dict, i))
        else:
            process = Process(target=function, args=args + (return_dict, i))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    return return_dict
