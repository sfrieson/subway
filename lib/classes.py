from math import inf as infinity
import re
from lib import utils

class Route:
    def __init__ (self, route_data, trips):
        self.id, self.agency_id, self.letter, self.name, self.description, \
        self.type, self.url, self.color, self.text_color = route_data
        self.trips = trips

    def get_transfers(self):
        pass
    def get_longest_trip_distance(self):
        longest = 0
        for trip in self.trips:
            longest = max(longest, trip.distance)

        return longest

    def get_master_schedule(self):
        pass

    def get_time_range(self):
        earliest = infinity
        latest = 0

        for trip in self.trips:
            earliest = min(
                earliest,
                trip.stops[0].departure_time.get_time_of_day_value()
            )
            latest = max(
                latest,
                trip.stops[-1].arrival_time.get_time_of_day_value()
            )
        
        return (earliest, latest)

    def get_stations(self):
        stations = set()
        for trip in self.trips:
            for stop in trip.stops:
                stations.add(stop.station)

        return stations

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
    stations = {}
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

        if parent_station not in Station.stations:
            Station.stations[parent_station] = Station((parent_station, stop_name, lat, lon))
        self.id = parent_station
        self.arrival_time = Time(arrival_time)
        self.departure_time = Time(departure_time)
        self.station = Station.stations[parent_station]

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
                currentStation = Station.stations[stop.id]
                nextStation = Station.stations[self.stops[i + 1].id]
                currentStation.set_next(nextStation, self.direction)

        stations_ordered = []

        # Arbitrary element
        # https://stackoverflow.com/questions/3097866/access-an-arbitrary-element-in-a-dictionary-in-python
        tmp_station = next(iter(Station.stations.values()))

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

class SVG:
    def __init__(self, artboard_size, data_size):
        self.width, self.height = artboard_size
        self.data_width, self.data_height = data_size
        self.contents = []
        self.styles = []


    def add(self, contents):
        self.contents.append(contents)

    def add_style(self, name, defs):
        self.styles.append((name, defs))
    
    def body(self, contents):
        return """
        <svg version="1.1" id="Layer_1"
            xmlns="http://www.w3.org/2000/svg"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            viewbox="0 0 {height} {width}" style="enable-background:new 0 0 {height} {width};"
            x="0px" y="0px" xml:space="preserve"
        >
        {contents}
        </svg>
        """.format(height = self.height, width = self.width, contents = ' '.join(contents))

    @staticmethod
    def group(data, id=None, classname=None):
        return '<g {id} {classname}>{content}</g>'.format(
            content = data,
            id = 'id="%s"' % id if id else '',
            classname = 'class="%s"' % classname if classname else ''
        )

    header = """<?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 22.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    """

    @staticmethod
    def line(line, classname=None):
        p1, p2 = line
        x1, y1 = p1
        x2, y2 = p2
        return '<line {classname} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'.format(
            x1 = round(x1, 2),
            x2 = round(x2, 2),
            y1 = round(y1, 2),
            y2 = round(y2, 2),
            classname = 'class="%s"' % classname if classname else ''
        )

    def normalize_x(self, x):
        return x / self.data_width * self.width

    def normalize_y(self, y):
        return y / self.data_height * self.height

    def normalize_point(self, point):
        x, y = point
        return (self.normalize_x(x), self.normalize_y(y))

    def normalized_line(self, line, classname):
        p1, p2 = line
        return self.line(
            (self.normalize_point(p1), self.normalize_point(p2)),
            classname
        )

    def print(self):
        return """{header}
        {body}""".format(
            header = self.header,
            body = self.body([
                    '<style type="text/css">',
                    ''.join(['%s { %s }' % style for style in self.styles]),
                    '</style>'
                ] + self.contents
            )
        )