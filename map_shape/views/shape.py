from math import inf
from lib.classes import SVG

def draw(points, color):
    # starting values are the opposite bounds of the II quandrant, alternatively they could be the bounds of the North Western hemisphere
    max_x = -inf
    max_y = 0
    min_x = 0
    min_y = inf

    for lon, lat in points:
        max_x = max(max_x, lon)
        max_y = max(max_y, lat)
        min_x = min(min_x, lon)
        min_y = min(min_y, lat)


    width = max_x - min_x
    height = max_y - min_y

    artboard_width = 500
    artboard_height = height *  artboard_width / width

    x_multiplier = artboard_width / width
    y_multiplier = artboard_height / height

    points = map(lambda p: ((p[0] - min_x) * x_multiplier, ((p[1] - min_y) * -y_multiplier) + artboard_height), points)
    drawing = SVG(
        (0 , 0, artboard_width, artboard_height),
        (min_x, min_y, max_x, max_y)
    )

    drawing.add(
        drawing.path(points, classname='st0')
    )

    drawing.add_style('.st0', 'fill: none; stroke: #%s; stroke-width: 2' % color)

    return drawing.print()