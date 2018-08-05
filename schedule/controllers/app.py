from schedule.controllers import route as route_controller, station as station_controller
from schedule.views import timetable

def make_route_timetable(route_id, day_type):
    print('making route timetable')
    trips = station_controller.get_route_trips(route_id, day_type)
    route = route_controller.get(route_id, trips)

    table = timetable.draw(route)

    svg_file = open('./results/%s-times.svg' % route.id, 'w')
    svg_file.write(table)
    print('File written: ./results/%s-times.svg' % route.id)
