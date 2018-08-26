from functools import reduce
from schedule.models import trips as model

def get_valid_trips(route_id):
    def mapper(counts, result):
        trip, headsign, shape = result
        if shape not in counts:
            counts[shape] = []
        
        counts[shape].append(trip)
        return counts
    res = model.get_by_route_id(route_id, ['trip_id', 'trip_headsign', 'shape_id'])
    counts = reduce(mapper, res, {})

    [print(key, len(val)) for key, val in counts.items()]