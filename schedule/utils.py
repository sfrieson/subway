from math import radians, cos, sin, asin, sqrt

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

# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def calculate_distance(p1, p2):
    """
    Haversine - calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """

    lat1, lon1 = p1
    lat2, lon2 = p2
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3959 # Radius of earth in miles
    return round(c * r, 2)