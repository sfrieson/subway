from schedule.models import route as model
from lib.classes import Geo_Point, Route
from lib.utils import collect_on

def get(id):
    # all route ids in the database are uppercase (A, B, C...)
    return Route(model.get(id.upper()))

def get_longest_contiguous_path(path):
    max_length = 1
    max_start = 0
    max_end = 0
    sequence = 1

    start = 0
    end = 0
    length = 1
    for i, point in enumerate(path):
        if i + 1 != len(path) and point[sequence] + 1 == path[i + 1][sequence]:
            length += 1
            end = i + 1
        else:
            if length > max_length:
                max_length = length
                max_start = start
                max_end = end
            start = i + 1
            end = i + 1
            length = 1

    return path[max_start:max_end + 1]

def get_largest_shared_sequence(route):
    """
    Looks at all the trips in a path and find the largest portion of the path that all trips have in common.
    """
    stations = {str(station.point.lon) + str(station.point.lat): station for station in route.get_stations()}
    # {<shape_id>: [(<point_id>, <shape_pt_sequence>)]}
    paths = collect_on(model.get_paths(route.id), 0, remove_key=True)

    # [{<point_id>, ...}, {<point_id>, ...}]
    shape_point_sets = [{(point[2], point[3]) for point in points} for points in paths.values()]

    shared_set = None
    for point_set in shape_point_sets:
        if shared_set is None:
            shared_set = point_set
        else:
            shared_set = shared_set & point_set

    # get random path
    path = list(paths.values())[0]

    shared = [point for point in path if (point[2], point[3]) in shared_set]
    print('# of shared', len(shared))

    longest = get_longest_contiguous_path(shared)

    return [stations[str(point[2]) + str(point[3])] if str(point[2]) + str(point[3]) in stations else Geo_Point(point[2], point[3]) for point in longest]

def get_station_time_list(route):
    station_times = {station: {'uptown': set(), 'downtown': set()} for station in route.stations.values()}

    for trip in route.trips.values():
        direction = 'downtown' if trip.direction is 0 else 'uptown'
        for stop in trip.stops:
            station_times[stop.station][direction].add(stop.departure_time)
    
    return station_times