from map_shape.models import shape as model, route as routeModel
from map_shape.views import shape as view

def make_map(route):
    points = model.get_by_route(route)
    color = routeModel.get_color(route)
    return view.draw(points, color)