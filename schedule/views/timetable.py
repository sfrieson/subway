from lib.classes import SVG, Time

def change_precision(num, places=0):
    return round(num * 10 ** places)


def distance_to_int(mi):
    """
    Converts miles to tenths of a mile `round(mi * 100)`
    """
    return round(change_precision(mi, 2))


class Line:
    def __init__(self, points):
        self.p1, self.p2 = points
    
    def value(self):
        return (self.p1.value(), self.p2.value())


class Point:
    def __init__(self, data):
        self.x, self.y = data

    def value(self):
        return (self.x.value, self.y.value)


class Axis:
    def __init__(self, value):
        self.value = value


class X(Axis):
    def __init__(self, time, time_of_day=False, time_minus_day=False):
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


def draw(route):
    grid_color = '999999'
    trip_paths = []
    data_width = Time.DAY
    data_height = len(route.get_stations()) - 1
    drawing = SVG((1720, 1080), (data_width, data_height))

    # Make grid
    drawing.add_style('.st0', 'fill: none; stroke: #%s;' % grid_color)

    # self.data_width + 1 allows us to have one final grid mark at the end
    # alternatively a stroke around the whole thing would do the same thing.
    stations = route.get_stations()
   
    verticals = [drawing.normalize_x(x) for x in range(0, data_width + 1, 30 * Time.MINUTE)]
    horizontals = [ drawing.normalize_y(y) for y in [i for i in range(0, len(stations))] ]

    grid_lines = [((x, 0), (x, drawing.height)) for x in verticals] 
    grid_lines = grid_lines + [((0, y), (drawing.width, y)) for y in horizontals]
    drawing.add(
        drawing.group(''.join([drawing.line(line, 'st0') for line in grid_lines]), id='grid-marks')
    )

    y = {}
    for station in stations:
        y[station.id] = Y(station)

    drawing.add_style('.trip:hover line', 'stroke: #%s; stroke-width: 3;' % route.color)
    for trip in route.trips:
        segment_paths = []
        for segment in trip.segments:
            start = segment.start
            end = segment.end
            starts_before_midnight = start.departure_time.value < Time.DAY
            ends_after_midnight = end.arrival_time.value > Time.DAY

            p1 = Point((
                X(start.departure_time, time_of_day=(not starts_before_midnight)), #x[start.departure_time.value]
                y[start.station.id]
            ))
            p2 = Point((
                X(end.arrival_time, time_of_day=(not starts_before_midnight)), #x[end.arrival_time.value]
                y[end.station.id]
            ))
            
            segment_paths.append(Line((p1, p2)))

            # Some lines go off right side of the table, so duplicate them on the left side to come back in
            if ends_after_midnight:
                duplicate_p1 = Point((X(start.departure_time, time_minus_day=True ), Y(start.station)))
                duplicate_p2 = Point((X(end.arrival_time, time_minus_day=True ), y[end.station.id]))

                segment_paths.append(Line((duplicate_p1, duplicate_p2)))

        trip_paths.append(
            SVG.group(
                ''.join([drawing.normalized_line(line.value(), 'st1 %s' % trip.id) for line in segment_paths]),
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

