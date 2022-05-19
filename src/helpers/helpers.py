from typing import List


def list_difference(list1: List, list2: List) -> List:
    result = []
    for item in list1:
        if item not in list2:
            result.append(item)

    return result
