from map_shape.models import shape as model, route as routeModel
from map_shape.views import shape as view

def make_map_by_route_id(route):
    points = model.get_by_route(route)
    color = routeModel.get_color(route)
    return view.draw(points, color)

def make_map_by_shape_id(route):
    points = model.get_by_shape(route)
    return view.draw(points, '000')