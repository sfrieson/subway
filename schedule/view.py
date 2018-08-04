config = {
    'height': 1080,
    'width': 1720,
    'grid_color': '#999999',
    'path_color': '#000000'
}

def build_svg(route):
    lines = [
        (
            (x['from']['position'], x['departure_time']['value']),
            (x['to']['position'], x['arrival_time']['value'])
        ) for x in route['timetable']
    ]

    for x in route['timetable']:
        if x['to']['position'] is None:
            print(x)
    
    stations = route['stations']

    config['height'] = 1080
    config['width'] = 1720
    max_rows = len(stations)
    max_columns = 24 * 60 * 60

    def normalize_x (x):
        return x / max_columns * config['width']
    
    def normalize_y (y):
        return y / max_rows * config['height']

    svg_lines = ''
    grid_lines = ''

    for column in range(0, max_columns, 30 * 60):
        grid_lines += '<line class="st0" x1="{x}" y1="0" x2="{x}" y2="{height}" />'.format(
            height = config['height'],
            x = normalize_x(column)
        )

    grid_set = set()
    for a, b in lines:
        grid_set.add(
            '<line class="st0" x1="0" y1="{y}" x2="{width}" y2="{y}" />'.format(
                y = normalize_y(a[0]),
                width = config['width']
            )
        )
        # print(a, b)
        svg_lines += '<line class="st1" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />'.format(
            x1 = normalize_x(a[1]),
            y1 = normalize_y(a[0]),
            x2 = normalize_x(b[1]),
            y2 = normalize_y(b[0])
        )

    for line in grid_set:
        grid_lines += line

    svg_file = """<?xml version="1.0" encoding="utf-8"?>
    <!-- Generator: Adobe Illustrator 22.1.0, SVG Export Plug-In . SVG Version: 6.00 Build 0)  -->
    <svg version="1.1" id="Layer_1"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        viewbox="0 0 {height} {width}" style="enable-background:new 0 0 {height} {width};"
        x="0px" y="0px" xml:space="preserve"
    >
        <style type="text/css">
            .st0 {{
                fill: none;
                stroke: {grid_color};
            }}
            .st1 {{
                fill: none;
                stroke: {path_color};
                stroke-width: 2;
            }}
        </style>
        <g id="grid-marks">{grid_lines}</g>
        <g id="routes">{path_lines}</g>
    </svg>""".format(
        height = config['height'],
        width = config['width'],
        grid_lines = grid_lines,
        path_lines = svg_lines,
        path_color = config['path_color'],
        grid_color = config['grid_color']
    )

    return svg_file
