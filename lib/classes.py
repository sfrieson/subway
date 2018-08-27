from math import inf as infinity
import re
from lib import utils
from lib.graph import Graph, Edge, DirectedVertex

class Route(Graph):
    """
    A Route or a line is best referenced a general classification of several train Trips servicing geographic locations with affordance for some difference depending on time of day or just general splitting (the A train forks 3 directions in Queens).
    """

    def __init__ (self, route_data):
        super().__init__()
        self.id, self.agency_id, self.letter, self.name, self.description, \
        self.type, self.url, self.color, self.text_color = route_data
        self.stations = {}
        self.stops = {}
        self.tracks = {}
        self.trips = {}

    def add_stop(self, stop):
        self.stops[stop.id] = stop
        self.stations[stop.station.id] = stop.station
        self.add_vertex(stop.station.vertex)
    
    def add_track(self, track):
        self.tracks[track.start.id + track.end.id] = track
        self.add_edge(track.edge)
    
    def add_trip(self, trip):
        self.trips[trip.id] = trip

    def get_longest_possible_trip_length(self):
        """
        Determines the longest amount of track from a starting station to an ending station even though no train may take that specific journey. This is helpful to decide the height of the timetable graph showing every stop spaced by relative distance.
        """
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

    def find_end_points(self):
        """Find all the extreme points for the given route (not necessarily trip extremes as some trips may end in the middle of the route???)"""
        trip_endpoints = {trip.get_origin() for trip in self.trips.values()} | {trip.get_terminus() for trip in self.trips.values()}
        # End points of a line are assumed to only have 1 indegree and 1 outdegree which is one for either direction since this is a directed graph.
        [
            print(
                "%s/%s, S:%s %s | up: %s | down: %s" % (deg[1]['indegree'], deg[1]['outdegree'], deg[0].id, deg[0].name, deg[0].uptown, deg[0].downtown)
            ) for deg in sorted(self.get_all_degrees(), key=lambda x: x[0].name)
        ]
        route_endpoints = {v for v, d in filter(lambda vertex_degree: vertex_degree[1]['indegree'] == 1 and vertex_degree[1]['outdegree'] == 1, self.get_all_degrees())}
        print(trip_endpoints)
        [print(station, station.id) for station in trip_endpoints]
        return route_endpoints & trip_endpoints

class Time:
    """
    A time object to help manage the fact that Stop times go higher than 24:00:00 when the same trip passes over midnight.
    """
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


class Segment:
    """
    To be a Segment of a Trip is being on a specific Track at a specific time of day.
    """

    def __init__(self, route, starting_stop, ending_stop):
        self.start = starting_stop
        self.end = ending_stop
        self.track = None

        self.duration = Time.compare_times(
            self.start.departure_time,
            self.end.arrival_time
        )
    
    def set_track(self, track):
        self.track = track

class Trip:
    """
    A Trip is best imagined as the journey one train takes from on it's specific Route from one end to the other. This could include alternate stations, etc.
    """
    def __init__ (self, id, headsign, direction, shape_id, path):
        self.id = id
        self.headsign = headsign
        self.shape_id = shape_id
        self.direction = direction
        self.path = path
        self.stops = []
        self.segments = []

    def add_stop(self, stop):
        self.stops.append(stop)

    def add_segment(self, segment):
        self.segments.append(segment)

    def get_origin(self):
        return self.stops[0].station

    def get_terminus(self):
        return self.stops[-1].station

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

    @staticmethod
    def text(text, point):
        return '<text x="{x}" y="{y}">{text}</text>'.format(x=point[0], y=point[1], text=text)

class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    
    def value(self):
        return (self.p1.value(), self.p2.value())


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def value(self):
        return (self.x.value, self.y.value)

class Geo_Point(Point):
    def __init__(self, lon, lat):
        super().__init__(lon, lat)
        self.lon = lon
        self.lat = lat

class Station:
    """
    A station is a specific place that Routes connect to and Trips have Stops at.
    """
    def __init__ (self, data):
        id, self.name, self.pickup_type, longitude, latitude = data
        # composition
        self.vertex = DirectedVertex(id)
        self.point = Geo_Point(longitude, latitude)
        
        self.id = id
        self.downtown = set()
        self.uptown = set()

    def set_next(self, next, direction):
        if direction == 0:
            self.uptown.add(next)
        elif direction == 1:
            self.downtown.add(next)

    def __get_attr__(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        if hasattr(self.vertex, attr):
            return getattr(self.vertex, attr)
        if hasattr(self, attr.point):
            return getattr(self.point, attr)

        return None

    def __str__(self):
        return 'Station(%s)' % self.name

    __repr__ = __str__

class Axis:
    def __init__(self, value):
        self.value = value


class X(Axis):
    def __init__(self, value):
        super().__init__(value)


class Y(Axis):
    def __init__(self, value):
        super().__init__(value)


class Geo_Line(Line):
    def calculate_distance(self, p1, p2):
        return utils.calculate_distance(p1, p2)


class Path:
    def __init__(self, points):
        # points should already be ordered correctly
        self.points = points
        self.lines = [Geo_Line(point, points[i + 1]) for i, point in enumerate(points) if i + 1 in points]

    def get_distance(self):
        return sum([line.calculate_distance() for line in self.lines])

    def segment(self, p1, p2):
        idx1 = None
        idx2 = None
        segment = None
        for i, point in enumerate(self.points):
            if not idx1 and (point.lon, point.lat) == (p1.lon, p1.lat):
                idx1 = i
            if not idx2 and (point.lon, point.lat) == (p2.lon, p2.lat):
                idx2 = i
            if idx1 is not None and idx2 is not None:
                break
        
        if idx1 is not None and idx2 is not None:
            segment = Path(self.points[idx1:idx2:1 if idx1 > idx2 else -1])
        
        return segment


class Track:
    """
    A physical portion of track, defined as being between two stations. The two stations can be express or location stations.
    """
    def __init__(self, starting_station, ending_station, path):
        self.start = starting_station
        self.end = ending_station
        self.path = path # The Track can be on other paths too but it should not matter
        self.edge = Edge(self.start, self.end)

        self.__length = None
    
    def __get_attr__(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        if hasattr(self.edge, attr):
            return getattr(self.edge, attr)

        return None

    def __str__(self):
        return 'Track(%s, %s)' % (self.start.name, self.end.name)


class Stop:
    stations = {}
    Station = Station
    """
    A Stop on a Trip is to be at a specific Station  at a specific time of day.
    """
    def __init__ (self, data):
        self.sequence, station_id, stop_name, \
        arrival_time, departure_time, pickup_type, lon, lat = data

        self.id = self.sequence
        self.arrival_time = Time(arrival_time)
        self.departure_time = Time(departure_time)

        if station_id not in self.stations:
            self.stations[station_id] = self.Station((station_id, stop_name, pickup_type, lon, lat))
        self.station = self.stations[station_id]
