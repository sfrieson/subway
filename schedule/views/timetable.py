from lib.classes import SVG, Time

def distance_to_int(mi):
    """
    Converts miles to tenths of a mile `round(mi * 100)`
    """
    return round(mi * 100)

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
    verticals = [drawing.normalize_x(x) for x in range(0, data_width + 1, 30 * Time.MINUTE)]
    horizontals = [ drawing.normalize_y(y) for y in [i for i in range(0, len(route.get_stations()))] ]

    lines = [((x, 0), (x, drawing.height)) for x in verticals] 
    lines = lines + [((0, y), (drawing.width, y)) for y in horizontals]
    drawing.add(
        drawing.group(''.join([drawing.line(line, 'st0') for line in lines]), id='grid-marks')
    )

    drawing.add_style('.trip:hover line', 'stroke: #%s; stroke-width: 3;' % route.color)
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

