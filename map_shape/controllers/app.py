from map_shape.controllers import shape

def make_map(route):
    map_svg = shape.make_map(route)

    svg_file = open('./results/%s-map.svg' % route, 'w')
    svg_file.write(map_svg)
    print('File written: ./results/%s-map.svg' % route)