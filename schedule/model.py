import psycopg2
from math import sqrt, fabs
import re

connection = psycopg2.connect("dbname=subway_schedule")
cursor = connection.cursor()

limit = 0

def collect_on(collection, aggregator_key):
    collected = {}
    for item in collection:
        aggregator_value = item[aggregator_key]
        if aggregator_value not in collected:
            collected[aggregator_value] = []

        collected[aggregator_value].append(item)

    return collected


def get_route(route_id):
    cursor.execute("SELECT * FROM routes where route_id = '%s';" % route_id)

    return cursor.fetchone()

class Station:
    def __init__(self, data):
        self.id = data[2]
        self.name = data[4]
        self.position = None
        self.uptown = None
        self.downtown = None

    def __repr__(self):
        return '{"id": "%s", "name": "%s", "uptown": %s, "downtown": %s, ' \
            '"position": %s, "distance": %c}' % \
            (
                self.id, self.name,
                '"%s"' % self.uptown.id if self.uptown else 'null',
                '"%s"' % self.downtown.id if self.downtown else 'null',
                self.position
            )

    def set_next(self, next, direction):
        if direction == 0:
            if self.uptown is None:
                self.uptown = next
                next.downtown = self
            elif self.uptown is not next:
                print('not equal...')
        elif direction == 1:
            if self.downtown is None:
                self.downtown = next
                next.uptown = self
            elif self.downtown is not next:
                print('not equal...')

    def set_position(self, pos):
        self.position = pos

    def toDict(self):
        return {
            'downtown': self.downtown.id if self.downtown else None,
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'uptown': self.uptown.id if self.uptown else None
        }



def get_stations(route_id, day_of_week):
    cursor.execute("""
        SELECT stop_times.trip_id, stop_sequence, stops.parent_station,
            direction_id, stop_name, arrival_time, departure_time, stop_lat,
            stop_lon
        FROM stop_times
          JOIN trips on stop_times.trip_id = trips.trip_id
          JOIN stops on stop_times.stop_id = stops.stop_id
        WHERE stop_times.trip_id IN (
          SELECT stop_times.trip_id
          FROM trips
            JOIN stop_times ON trips.trip_id = stop_times.trip_id
            JOIN stops ON stop_times.stop_id = stops.stop_id
            JOIN calendar ON trips.service_id = calendar.service_id
            JOIN routes ON trips.route_id = routes.route_id
          WHERE
            trips.route_id = '%s' AND
            %s IS TRUE
        )
        ORDER BY stop_times.trip_id, stop_sequence
        %s
    """ % (route_id, day_of_week, 'LIMIT %s' % limit if limit > 0 else ''))

    # (trip_id, stop_sequence, parent_station, direction_id, stop_name,
    # arrival_time, departure_time)
    trips = collect_on(cursor.fetchall(), 0)  # 0 is trip_id

    stations = {}

    # Note all of the stations
    for trip, trip_stops in trips.items():
        for stop in trip_stops:
            if stop[2] not in stations.keys():
                stations[stop[2]] = Station(stop)

    # Set which station comes after which
    for trip, trip_stops in trips.items():
        for i, stop in enumerate(trip_stops):
            if i < len(trip_stops) - 1:
                currentStation = stations[stop[2]]
                nextStation = stations[trip_stops[i + 1][2]]
                currentStation.set_next(nextStation, stop[3])

    # Assign the list to to the route
    uptown_start = None
    downtown_start = None
    stations_ordered = []

    # Arbitrary element
    # https://stackoverflow.com/questions/3097866/access-an-arbitrary-element-in-a-dictionary-in-python
    tmp_station = next(iter(stations.values()))

    # get to the beginning
    while tmp_station.uptown:
        tmp_station = tmp_station.uptown

    uptown_start = tmp_station

    tmp_station.set_position(len(stations_ordered))
    tmp_station.distance = 0
    stations_ordered.append(tmp_station)

    while tmp_station.downtown:
        tmp_station = tmp_station.downtown
        tmp_station.set_position(len(stations_ordered))
        stations_ordered.append(tmp_station)

    downtown_start = tmp_station

    return (stations, stations_ordered, uptown_start, downtown_start, trips)

# Thank you Pythagoras
def calculate_distance(x1, y1, x2, y2):
    return sqrt(fabs(x2 - x1) ** 2 + fabs(y2 - y1) ** 2)

def make_relative_time(time_string):
    time_parse = re.compile(r"(?P<hr>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})")

    match = time_parse.match(time_string)
    sec = int(match.group('sec'))
    min = int(match.group('min'))
    hr = int(match.group('hr')) % 24

    return {
        'relative': time_string,
        'value': (sec + min * 60 + hr * 60 * 60) % 86400,
        'time_of_day': '%s:%s' % (hr, str(min).zfill(2))
    }


def get_timetable(trips, stations):
    spans = []
    max_distance = 0

    for trip_id, trip in trips.items():
        for i, details in enumerate(trip):
            if i < len(trip) - 1:
                start = details
                stop = trip[i + 1]
                # (trip_id, stop_sequence, parent_station, direction_id,
                # stop_name, arrival_time, departure_time, stop_lat, stop_lon)
                if start and stop:
                    # save max distance for distance index below
                    distance = calculate_distance(
                        start[7], start[8], stop[7], stop[8]
                    )
                    max_distance = max(max_distance, distance)

                    spans.append({
                        'from': stations[start[2]].toDict(),
                        'to': stations[stop[2]].toDict(),
                        'departure_time': make_relative_time(start[6]),
                        'arrival_time': make_relative_time(stop[5]),
                        'distance': distance
                    })

    # Convert distance into a distance index
    for span in spans:
        span['distance'] = span['distance'] / max_distance
    return spans

