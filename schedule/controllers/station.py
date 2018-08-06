import re
from schedule.models import station as model
from schedule import utils

stations = {}

class Time:
    time_parse = re.compile(r"(?P<hr>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})")
    SECOND = 1
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 24 * 60 * 60

    def __init__(self, time_string):
        match = self.time_parse.match(time_string)
        self.sec = int(match.group('sec'))
        self.min = int(match.group('min'))
        self.hr = int(match.group('hr'))

        self.relative = time_string
        self.value = self.sec * self.SECOND + self.min * self.MINUTE + self.hr * self.HOUR

    def get_time_of_day(self):
        return '%s:%s' % (self.hr % 24, str(self.min).zfill(2))

    def get_time_of_day_value(self):
        return self.value % self.DAY

    @staticmethod
    def compare_times(t1, t2):
        return t2.value - t1.value

class Station:
    def __init__ (self, data):
        self.id, self.name, latitude, longitude = data
        self.point = (latitude, longitude)
        self.distance_from_start = None
        self.downtown = None
        self.uptown = None
    
    def set_line_order (self, line_order):
        self.line_order = line_order

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
    
    def set_distance_from_start (self, distance):
        self.distance_from_start = distance

class Segment:
    def __init__(self, starting_stop, ending_stop):
        self.start = starting_stop
        self.end = ending_stop
        self.distance = utils.calculate_distance(
            self.start.station.point,
            self.end.station.point
        )

        self.duration = Time.compare_times(
            self.start.departure_time,
            self.end.arrival_time
        )

class Stop:
    def __init__ (self, data):
        self.trip_id, self.sequence, parent_station, self.direction, stop_name, \
        arrival_time, departure_time, lat, lon = data

        if parent_station not in stations:
            stations[parent_station] = Station((parent_station, stop_name, lat, lon))
        self.id = parent_station
        self.arrival_time = Time(arrival_time)
        self.departure_time = Time(departure_time)
        self.station = stations[parent_station]

class Trip:
    def __init__ (self, id, stops):
        self.id = id
        self.stops = [Stop(s) for s in stops]
        self.segments = []
        self.distance = 0
        starting_stop = None
        for ending_stop in self.stops:
            if starting_stop is not None:
                segment = Segment(starting_stop, ending_stop)
                if starting_stop.direction == 0:
                    self.segments.append(segment)
                else:
                    # https://stackoverflow.com/questions/8537916/whats-the-idiomatic-syntax-for-prepending-to-a-short-python-list
                    self.segments.insert(0, segment)
                
                self.distance += segment.distance

            starting_stop = ending_stop

        self.direction = self.stops[0].direction

        for i, stop in enumerate(self.stops):
            if i < len(self.stops) - 1:
                currentStation = stations[stop.id]
                nextStation = stations[self.stops[i + 1].id]
                currentStation.set_next(nextStation, self.direction)

        stations_ordered = []

        # Arbitrary element
        # https://stackoverflow.com/questions/3097866/access-an-arbitrary-element-in-a-dictionary-in-python
        tmp_station = next(iter(stations.values()))

        # get to the beginning
        while tmp_station.uptown:
            tmp_station = tmp_station.uptown

        tmp_station.set_line_order(len(stations_ordered))
        tmp_station.distance = 0
        stations_ordered.append(tmp_station)

        while tmp_station.downtown:
            tmp_station = tmp_station.downtown
            tmp_station.set_line_order(len(stations_ordered))
            stations_ordered.append(tmp_station)

def get_route_trips(route_id, day_type):

    day = 'monday'
    if day_type is 'Saturday':
        day = 'saturday'
    elif day_type is 'Sunday':
        day = 'sunday'

    stops = model.get(route_id, day)
    trips = utils.collect_on(stops, 0) # position 0 in tuple is trip_id
    trips = [Trip(id, stops) for id, stops in trips.items()]

    return trips
