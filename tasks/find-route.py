# Takes a given line_id and day of the week to find the trips' route
import json
from math import sqrt, fabs
import psycopg2
import re

limit = 0

connection = psycopg2.connect("dbname=subway_schedule")
cursor = connection.cursor()


def collect_on(collection, aggregator_key):
    collected = {}
    for item in collection:
        aggregator_value = item[aggregator_key]
        if aggregator_value not in collected:
            collected[aggregator_value] = []

        collected[aggregator_value].append(item)

    return collected


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


def make_relative_time(time_string):
    time_parse = re.compile(r"(?P<hr>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})")

    match = time_parse.match(time_string)
    sec = int(match.group('sec'))
    min = int(match.group('min'))
    hr = int(match.group('hr')) % 24

    return {
        'relative': time_string,
        'value': sec + min * 60 + hr * 60 * 60,
        'time_of_day': '%s:%s' % (hr, str(min).zfill(2))
    }


def get_route(route_id):
    cursor.execute("SELECT * FROM routes where route_id = '%s';" % route_id)

    return cursor.fetchone()


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


def make_route(route_id, day_type):
    day = 'monday'
    if day_type is 'Saturday':
        day = 'saturday'
    elif day_type is 'Sunday':
        day = 'sunday'

    route = {
        'route_id': route_id
    }

    route_id, agency_id, route_short_name, route_long_name, route_desc, \
        route_type, route_url, route_color, route_text_color = \
        get_route(route_id)

    route['train'] = route_short_name
    route['name'] = route_long_name
    route['description'] = route_desc
    route['color'] = route_color
    route['text_color'] = route_text_color

    (stations, stations_ordered, uptown_start, downtown_start, trips) = \
        get_stations(route_id, day)

    route['stations'] = [x.toDict() for x in stations_ordered]
    # route['uptown_start'] = uptown_start.toDict()
    # route['downtown_start'] = downtown_start.toDict()
    # route['trips'] = trips

    timetable = get_timetable(trips, stations)
    # route['timetable'] = timetable
    route['timetablelines'] = [
        (
            (x['from']['position'], x['departure_time']['value']),
            (x['to']['position'], x['arrival_time']['value'])
        ) for x in timetable]
    return route


route = make_route('W', 'weekday')

json.dump(
    route,
    open('./results/%s-times.json' % route["route_id"], 'w'),
    separators=(',', ':')
)
print('File written: ./results/%s-times.json' % route["route_id"])


def build_svg(lines, stations):
    artboard_height = 1080
    artboard_width = 1720
    max_rows = len(stations)
    max_columns = 24 * 60 * 60

    svg_lines = ''
    grid_lines = ''

    for a, b in lines:
        grid_lines += '<line class="st0" x1="0" y1="%s" x2="%s" y2="%s" />' % (
            a[0] / max_rows * artboard_height,
            artboard_width,
            a[0] / max_rows * artboard_height
        )
        svg_lines += '<line class="st1" x1="%s" y1="%s" x2="%s" y2="%s" />' % (
            a[1] / max_columns * artboard_width,
            a[0] / max_rows * artboard_height,
            b[1] / max_columns * artboard_width,
            b[0] / max_rows * artboard_height
        )

    return """<?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 22.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    <svg version="1.1" id="Layer_1"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewbox="0 0 %s %s" style="enable-background:new 0 0 %s %s;"
        x="0px" y="0px" xml:space="preserve"
    >
        <style type="text/css">
            .st0{fill:none;stroke:#999999;}
            .st1{fill:none;stroke:#000000;stroke-width:2;}
        </style>
        <g id="grid-marks">%s</g>
        <g id="routes">%s</g>
    </svg>""" % (
        artboard_height, artboard_width, artboard_height, artboard_width,
        grid_lines, svg_lines
    )


svg = open('./results/%s-times.svg' % route["route_id"], 'w')
svg.write(build_svg(route['timetablelines'], route['stations']))
print('File written: ./results/%s-times.svg' % route["route_id"])
