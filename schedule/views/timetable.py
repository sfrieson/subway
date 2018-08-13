from lib.classes import SVG, Time

def change_precision(num, places=0):
    return round(num * 10 ** places)


def distance_to_int(mi):
    """
    Converts miles to tenths of a mile `round(mi * 100)`
    """
    return round(change_precision(mi, 2))


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


class Axis:
    def __init__(self, value):
        self.value = value


class X(Axis):
    def __init__(self, time, time_of_day=False, time_minus_day=False):
        if isinstance(time, int):
            value = time
        else:
            if (time_of_day):
                value = time.get_time_of_day_value()
            elif (time_of_day):
                value = time.value - Time.DAY
            else:
                value = time.value
        
        super().__init__(value)

class Y(Axis):
    def __init__(self, station):
        super().__init__(station.line_order)
        self.data = station


def draw(route):
    grid_color = '999999'
    trip_paths = []
    endpoints = route.find_end_points()
    
    stations = sorted(route.get_stations(), key=lambda s: s.line_order)

    y_points = {}
    for index, station in enumerate(stations):
        y_points[station.id] = Y(station)
        y_points[station.id].value = index

    # Make grid
    data_width = Time.DAY
    data_height = len(stations) - 1
    drawing = SVG((1720, 1080), (data_width, data_height))
    drawing.add_style('.st0', 'fill: none; stroke: #%s;' % grid_color)
   
    # self.data_width + 1 allows us to have one final grid mark at the end
    # alternatively a stroke around the whole thing would do the same thing.
    verticals = [x for x in range(0, data_width + 1, 30 * Time.MINUTE)]
    horizontals = [y_points[s.id] for s in stations]
    
    grid_lines = [Line(
        Point(X(x), y_points[stations[0].id]),
        Point(X(x), y_points[stations[len(stations) - 1].id])
    ) for x in verticals] 

    grid_lines = grid_lines + [Line(Point(X(0), y), Point(X(data_width), y)) for y in horizontals]
    drawing.add(
        drawing.group(''.join([drawing.normalize_line(line.value(), 'st0') for line in grid_lines]), id='grid-marks')
    )

    drawing.add_style('.trip:hover line', 'stroke: #%s; stroke-width: 3;' % route.color)
    for trip in route.trips:
        segment_paths = []
        for segment in trip.segments:
            start = segment.start
            end = segment.end
            starts_before_midnight = start.departure_time.value < Time.DAY
            ends_after_midnight = end.arrival_time.value > Time.DAY

            p1 = Point(
                X(start.departure_time, time_of_day=(not starts_before_midnight)),
                y_points[start.station.id]
            )
            p2 = Point(
                X(end.arrival_time, time_of_day=(not starts_before_midnight)),
                y_points[end.station.id]
            )
            
            segment_paths.append(Line(p1, p2))

            # Some lines go off right side of the table, so duplicate them on the left side to come back in
            if ends_after_midnight:
                duplicate_p1 = Point(X(start.departure_time, time_minus_day=True ), Y(start.station))
                duplicate_p2 = Point(X(end.arrival_time, time_minus_day=True ), y_points[end.station.id])

                segment_paths.append(Line(duplicate_p1, duplicate_p2))

        trip_paths.append(
            SVG.group(
                ''.join([drawing.normalize_line(line.value(), 'st1 %s' % trip.id) for line in segment_paths]),
                id=trip.id,
                classname='trip'
            )
        )

    drawing.add_style('.st1', """
        fill: none;
        stroke: %s;
        stroke-width: 2;
    """ % '#000000')

    drawing.add(SVG.group(''.join(trip_paths), id='routes', classname='routes'))
    return drawing.print()

