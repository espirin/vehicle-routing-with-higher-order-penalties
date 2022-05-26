from typing import List, Dict


def list_difference(list1: List, list2: List) -> List:
    result = []
    for item in list1:
        if item not in list2:
            result.append(item)

    return result


def format_matrix(sources: List[int], destinations: List[int], matrix: List[float]) -> Dict[str, Dict[str, int]]:
    sources = [str(source) for source in sources]
    destinations = [str(destination) for destination in destinations]
    formatted_matrix = dict()
    len_sources = len(sources)
    len_destinations = len(destinations)
    for i in range(len_sources):
        formatted_matrix[sources[i]] = dict()
        for j in range(len_destinations):
            formatted_matrix[sources[i]][destinations[j]] = int(matrix[i * len_sources + j])

    return formatted_matrix
