from schedule.controllers import route as route_controller, station as station_controller
from schedule.views import timetable

def make_route_timetable(route_id, day_type):
    print('making route timetable')
    
    # all route ids in the database are uppercase (A, B, C...)
    route_id = route_id.upper()
    # all days in the database are lower case (monday, tuesday, wednesday, ...)
    day_type = day_type.lower()
    trips = station_controller.get_route_trips(route_id, day_type)
    route = route_controller.get(route_id, trips)
    
    route.depth_first(route.get_stations()[0], edges=print)
    table = timetable.draw(route)

    svg_file = open('./results/%s-times.svg' % route.id, 'w')
    svg_file.write(table)
    print('File written: ./results/%s-times.svg' % route.id)
