from typing import List, Tuple, Dict

import requests

from src.config import OSRM_ADDRESS


class OSRMInterface:
    @staticmethod
    def request_table(sources: List[int], destinations: List[int],
                      osrm_file_path: str) -> Tuple[List[float], List[float]]:
        return requests.get(f"{OSRM_ADDRESS}/table", json={
            "origins": sources,
            "destinations": destinations,
            "osrm_file_path": osrm_file_path
        }, timeout=1).json()

    @staticmethod
    def request_route(segments: List[Tuple[int, int]], osrm_file_path: str) -> Dict:
        return requests.get(f"{OSRM_ADDRESS}/route", json={
            "segments": segments,
            "osrm_file_path": osrm_file_path
        }, timeout=1).json()
