class SVG:
    def __init__(self, artboard_size, data_size):
        self.width, self.height = artboard_size
        self.data_width, self.data_height = data_size

        self.grid_color = '#999999'
        self.styles = [('st0', 'fill: none; stroke: %s;' % self.grid_color)]
        self.contents = []


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

    def grid(self, x_inc, y_inc):
        verticals = [self.normalize_x(x) for x in range(0, self.data_width, x_inc)]
        horizontals = [self.normalize_y(y) for y in range(0, self.data_height, y_inc)]

        lines = [((v, 0), (v, self.height)) for v in verticals] 
        lines = lines + [((0, h), (self.width, h)) for h in horizontals]
        return self.group((
            'grid-marks',
            ''.join([self.line(line, 'st0') for line in lines])
        ))

    def group(self, data):
        return '<g id="%s">%s</g>' % data

    def line(self, line, classname=None):
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

    header = """<?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 22.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    """

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
                    ''.join(['.%s { %s }' % style for style in self.styles]),
                    '</style>',
                    self.grid(30 * 60, 1)
                ] + self.contents
            )
        )


def draw(route):
    drawing = SVG((1720, 1080), (24 * 60 * 60, len(route.get_stations())))

    trip_lines = []
    for trip in route.trips:
        for segment in trip.segments:
            trip_lines.append(
                ((segment.start.departure_time.value, segment.start.station.line_order),
                (segment.end.arrival_time.value, segment.end.station.line_order))
            )

    drawing.add_style('st1', """
        fill: none;
        stroke: %s;
        stroke-width: 2;
    """ % '#000000')

    drawing.add(drawing.group((
        'routes',
        ''.join([drawing.normalized_line(line, 'st1') for line in trip_lines])
    )))
    return drawing.print()

