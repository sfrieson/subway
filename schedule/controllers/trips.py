from functools import reduce
from schedule.models import trips as model
from lib.classes import Segment, Track, Trip

def get_valid_trips(route, day_type):
    # all days in the database are lower case (monday, tuesday, wednesday, ...)
    day_type = day_type.lower()
    # treating the default as weekday, so picking `monday` to represent weekdays
    day = 'monday'

    if day_type is 'saturday':
        day = 'saturday'
    elif day_type is 'sunday':
        day = 'sunday'

    trips = [
        Trip(id, headsign, direction, shape)
        for id, headsign, direction, shape
        in model.get_by_route_id(route.id, ['trip_id', 'trip_headsign', 'direction_id', 'shape_id'], day=day)
    ]
    for trip in trips:
        route.add_trip(trip)

    return trips

def create_segments(route):
    for trip in route.trips.values():
        # temp variable for creating segments
        segment_start = None
        # Stops are already in order
        for segment_end in trip.stops:
            if segment_start is not None:
                segment = Segment(route, segment_start, segment_end)
                
                if trip.direction == 0:
                    trip.segments.append(segment)
                else:
                    # https://stackoverflow.com/questions/8537916/whats-the-idiomatic-syntax-for-prepending-to-a-short-python-list
                    trip.segments.insert(0, segment)
                
                track_id = segment_start.station.id + segment_end.station.id
                if track_id not in route.tracks:
                    track = Track(segment.start.station, segment.end.station)
                    segment.set_track(track)
                    route.add_track(track)

            segment_start = segment_end
