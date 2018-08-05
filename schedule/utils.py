from math import sqrt, fabs

def collect_on(data, aggregator_key):
    """
    Collects data into lists in a dictionary based off of a key in the input
    """
    collected = {}
    for item in data:
        aggregator_value = item[aggregator_key]
        if aggregator_value not in collected:
            collected[aggregator_value] = []

        collected[aggregator_value].append(item)

    return collected

def calculate_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return sqrt(fabs(x2 - x1) ** 2 + fabs(y2 - y1) ** 2)