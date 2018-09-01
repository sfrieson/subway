from schedule.controllers import route as route_controller, stops as stops_controller, trips as trip_controller
from schedule.views import timetable

def make_route_timetable(route_id, day_type):
    print('start')
    route = route_controller.get(route_id)
    # print('made route')
    # trip_controller.get_valid_trips(route, day_type)
    # print('made trips')
    # stops_controller.get_by_route(route)
    # print('made stops')
    # trip_controller.create_segments(route)
    # print('made segments')
    # stops_controller.set_next_stations(route)
    # print('set stations\' next stations')

    sequence = route_controller.get_largest_shared_sequence(route)
    print(sequence)

    # print(route.find_end_points())
    # table = timetable.draw(route)
    # print('drew timetable')
    # svg_file = open('./results/%s-times.svg' % route.id, 'w')
    # svg_file.write(table)
    # print('File written: ./results/%s-times.svg' % route.id)
