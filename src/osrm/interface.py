from typing import List, Tuple, Dict

import requests

from src.config.config import OSRM_ADDRESS
from src.routing_problem.segment import Segment


class OSRMInterface:
    """
    OSRMInterface is an interface for communication with an OSRM fork supporting segment ID referencing.

    The fork of the OSRM is the intellectual property of Atlatec GmbH and can't be shared. However, this repository
    provides example distance matrices and routing problems created with the OSRM fork that suffice for testing
    and demo purposes.

    Please contact me if you're interested in the OSRM fork implementation details.

    Information about OSRM: https://github.com/Project-OSRM/osrm-backend
    """

    @staticmethod
    def request_table(sources: List[int], destinations: List[int],
                      osrm_file_path: str) -> Tuple[List[float], List[float]]:
        return requests.get(f"{OSRM_ADDRESS}/table", json={
            "origins": sources,
            "destinations": destinations,
            "osrm_file_path": osrm_file_path
        }, timeout=1).json()

    @staticmethod
    def request_route(routing_segments: List[Segment], osrm_file_path: str) -> Dict:
        segments = [(int(float(segment.id)), 1 if segment.is_forward else 0) for segment in routing_segments[:-1]]
        segments.append(
            (int(float(routing_segments[-1].id)), 1 if routing_segments[0].is_forward else 0))

        return requests.get(f"{OSRM_ADDRESS}/route", json={
            "segments": segments,
            "osrm_file_path": osrm_file_path
        }, timeout=1).json()
