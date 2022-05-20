import os
from typing import List, Tuple, Dict

import requests

osrm_address = f'http://"127.0.0.1":8000'


class OSRMInterface:
    @staticmethod
    def request_table(sources: List[int], destinations: List[int],
                      osrm_file_path: str) -> Tuple[List[float], List[float]]:
        return requests.get(f"{osrm_address}/table", json={
            "origins": sources,
            "destinations": destinations,
            "osrm_file_path": osrm_file_path
        }).json()

    @staticmethod
    def request_route(segments: List[Tuple[int, int]], osrm_file_path: str) -> Dict:
        return requests.get(f"{osrm_address}/route", json={
            "segments": segments,
            "osrm_file_path": osrm_file_path
        }).json()
