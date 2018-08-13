from math import inf as infinity
import re
from lib import utils
from lib.graph import *

class Route(Graph):
    stations = {}
    tracks = {}

    def __init__ (self, route_data, trips):
        super().__init__()
        self.id, self.agency_id, self.letter, self.name, self.description, \
        self.type, self.url, self.color, self.text_color = route_data
        self.trips = trips

        for station in self.stations.values():
            self.add_vertex(station)

        for track in self.tracks.values():
            self.add_edge(track)

    def get_longest_trip_distance(self):
        longest = 0
        for trip in self.trips:
            longest = max(longest, trip.distance)

        return longest

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
        return [x for x in Route.stations.values()]

    def find_end_points(self):
        """Find all the end points for the given route"""

        # End points of a line are assumed to only have 1 indegree and 1 outdegree which is one for either direction since this is a directed graph.
        return [v for v, d in filter(lambda vertex_degree: vertex_degree[1]['indegree'] == 1 or vertex_degree[1]['outdegree'] == 1, self.get_all_degrees())]

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

class Station(DirectedVertex):
    def __init__ (self, data):
        id, self.name, self.pickup_type, longitude, latitude = data
        super().__init__(id)
        self.point = (longitude, latitude)
        self.distance_from_start = None
        self.downtown = None
        self.uptown = None
        Route.stations[id] = self
        
    def set_line_order (self, line_order):
        self.line_order = line_order

    def set_next(self, next, direction):
        if direction == 0:
            if self.uptown is None:
                self.uptown = next
                next.downtown = self
            elif self.uptown is not next:
                current = self.uptown
                found = False
                while current:
                    if current.uptown is next:
                        found = True
                        self.uptown = current
                    if found:
                        break
                    current = current.uptown
        elif direction == 1:
            if self.downtown is None:
                self.downtown = next
                next.uptown = self
            elif self.downtown is not next:
                current = self.downtown
                found = False
                while current:
                    if current.downtown is next:
                        found = True
                        self.downtown = current
                    if found:
                        break
                    current = current.downtown
    
    def set_distance_from_start (self, distance):
        self.distance_from_start = distance

    def __str__(self):
        return 'Station(%s)' % self.name

class Track(Edge):
    def __init__(self, starting_station, ending_station):
        super().__init__(starting_station, ending_station)
        self.start = starting_station
        self.end = ending_station
        self.distance = utils.calculate_distance(
            starting_station.point,
            ending_station.point
        )
        Route.tracks[starting_station.id + ending_station.id] = self
    
    def __str__(self):
        return 'Track(%s, %s)' % (self.start.name, self.end.name)

class Segment:
    def __init__(self, starting_stop, ending_stop):
        self.start = starting_stop
        self.end = ending_stop

        track_id = self.start.station.id + self.end.station.id
        if track_id not in Route.tracks:
            Track(starting_stop.station, ending_stop.station)
        self.track = Route.tracks[track_id]

        self.duration = Time.compare_times(
            self.start.departure_time,
            self.end.arrival_time
        )

class Stop:
    def __init__ (self, data):
        self.trip_id, self.sequence, parent_station, self.direction, stop_name, \
        arrival_time, departure_time, pickup_type, lon, lat = data

        self.id = parent_station
        self.arrival_time = Time(arrival_time)
        self.departure_time = Time(departure_time)

        if parent_station not in Route.stations:
            Station((parent_station, stop_name, pickup_type, lon, lat))
        self.station = Route.stations[parent_station]

class Trip:
    def __init__ (self, id, stops):
        self.id = id
        self.stops = [Stop(s) for s in stops]
        self.segments = []

        starting_stop = None
        for ending_stop in self.stops:
            if starting_stop is not None:
                segment = Segment(starting_stop, ending_stop)

                if starting_stop.direction == 0:
                    self.segments.append(segment)
                else:
                    # https://stackoverflow.com/questions/8537916/whats-the-idiomatic-syntax-for-prepending-to-a-short-python-list
                    self.segments.insert(0, segment)
                
            starting_stop = ending_stop

        self.direction = self.stops[0].direction

        for i, stop in enumerate(self.stops):
            if i < len(self.stops) - 1:
                currentStation = Route.stations[stop.id]
                nextStation = Route.stations[self.stops[i + 1].id]
                currentStation.set_next(nextStation, self.direction)

        stations_ordered = []

        # Arbitrary element
        # https://stackoverflow.com/questions/3097866/access-an-arbitrary-element-in-a-dictionary-in-python
        tmp_station = next(iter(Route.stations.values()))

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
    annotation = {
        'plain': '',
        'illustrator': """<?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 22.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    """
    }
    type_attributes = {
        'plain': 'xmlns="http://www.w3.org/2000/svg" viewBox="{origin_x} {origin_y} {width} {height}"',
        'illustrator': """
            xmlns="http://www.w3.org/2000/svg"
            viewbox="{origin_x} {origin_y} {width} {height}"
            version="1.1" id="Layer_1"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            style="enable-background:new {origin_x} {origin_y} {width} {height};"
            x="0px" y="0px" xml:space="preserve"
        """
    }
    def __init__(self, artboard_size, data_size, svg_type='plain'):
        if len(artboard_size) == 4:
            self.origin_x, self.origin_y, self.width, self.height = artboard_size
        else:
            self.origin_x, self.origin_y = 0, 0
            self.width, self.height = artboard_size
        if len(data_size) == 4:
            self.data_origin_x, self.data_origin_y, self.data_width, self.data_height = data_size
        else:
            self.data_origin_x, self.data_origin_y = 0, 0
            self.data_width, self.data_height = data_size
        self.contents = []
        self.styles = []
        self.header = self.annotation[svg_type]
        self.attributes = self.type_attributes[svg_type]

    def add(self, contents):
        self.contents.append(contents)

    def add_style(self, name, defs):
        self.styles.append((name, defs))
    
    def body(self, contents):
        return """
        <svg {attributes}>
        {contents}
        </svg>
        """.format(
            attributes = self.attributes.format(
                origin_x = self.origin_x,
                origin_y = self.origin_y,
                height = self.height,
                width = self.width,
            ),
            contents = ' '.join(contents)
        )

    @staticmethod
    def group(data, id=None, classname=None):
        return '<g {id} {classname}>{content}</g>'.format(
            content = data,
            id = 'id="%s"' % id if id else '',
            classname = 'class="%s"' % classname if classname else ''
        )

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
    
    @staticmethod
    def path(points, classname=None):
        points = ' L'.join(map(lambda x: "%s,%s" % x, points))
        return '<path {classname} d="M{points}" />'.format(
            points = points,
            classname = 'class="%s"' % classname if classname else ''
        )

    def normalize_x(self, x):
        return x / self.data_width * self.width

    def normalize_y(self, y):
        return y / self.data_height * self.height

    def normalize_point(self, point):
        return (
            self.normalize_x(point[0]),
            self.normalize_y(point[1])
        )

    def normalize_line(self, line, classname):
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