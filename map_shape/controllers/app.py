from map_shape.controllers import shape

def make_map(id):
    # All route IDs are one or two charachters (A, SI, ...) while shape ids are all(?) seven (N..S11R, ...)
    if len(id) <= 2:
        map_svg = shape.make_map_by_route_id(id.upper())
    else:
        map_svg = shape.make_map_by_shape_id(id.upper())


    svg_file = open('./results/%s-map.svg' % id, 'w')
    svg_file.write(map_svg)
    print('File written: ./results/%s-map.svg' % id)