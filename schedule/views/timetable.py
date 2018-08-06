from schedule.controllers.station import Time
def distance_to_int(mi):
    """
    Converts miles to tenths of a mile `round(mi * 100)`
    """
    return round(mi * 100)

class SVG:
    def __init__(self, artboard_size, data_size, horizontal_grid_marks):
        self.width, self.height = artboard_size
        self.data_width, self.data_height = data_size

        self.contents = []
        self.grid_color = '#999999'
        self.horizontal_grid_marks = horizontal_grid_marks
        self.styles = [
            ('.st0', 'fill: none; stroke: %s;' % self.grid_color),
            ('.trip:hover line', 'stroke: #0000ff; stroke-width: 3;')
        ]


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

    def grid(self, x_inc):
        verticals = [self.normalize_x(x) for x in range(0, self.data_width, x_inc)]
        horizontals = [self.normalize_y(y) for y in self.horizontal_grid_marks]

        lines = [((x, 0), (x, self.height)) for x in verticals] 
        lines = lines + [((0, y), (self.width, y)) for y in horizontals]
        return self.group(''.join([self.line(line, 'st0') for line in lines]), id='grid-marks')

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
            x1 = x1,
            x2 = x2,
            y1 = y1,
            y2 = y2,
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
                    '</style>',
                    self.grid(30 * Time.MINUTE)
                ] + self.contents
            )
        )


def draw(route):
    trip_paths = []
    drawing = SVG(
        (1720, 1080),
        (Time.DAY, len(route.get_stations())),
        [i for i in range(0, len(route.get_stations()))]
    )
    for trip in route.trips:
        segment_paths = []
        for segment in trip.segments:
            start = segment.start
            end = segment.end
            starts_before_midnight = start.departure_time.value < Time.DAY
            ends_after_midnight = end.arrival_time.value > Time.DAY

            p1 = (
                start.departure_time.value if starts_before_midnight else start.departure_time.get_time_of_day_value(),
                start.station.line_order
            )
            p2 = (
                end.arrival_time.value if starts_before_midnight else end.arrival_time.get_time_of_day_value(),
                end.station.line_order
            )
            
            segment_paths.append((p1, p2))

            # Some lines go off right side of the table, so duplicate them on the left side to come back in
            if ends_after_midnight:
                duplicate_p1 = (start.departure_time.value - Time.DAY, start.station.line_order)
                duplicate_p2 = (end.arrival_time.value - Time.DAY, end.station.line_order)

                segment_paths.append((duplicate_p1, duplicate_p2))

        trip_paths.append(
            SVG.group(
                ''.join([drawing.normalized_line(line, 'st1 %s' % trip.id) for line in segment_paths]),
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

