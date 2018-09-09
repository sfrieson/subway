from schedule.controllers import route as route_controller, stops as stops_controller, trips as trip_controller
from schedule.views import timeline, timetable

def make_route_time_views(route_id, day_type):
    print('start')
    route = route_controller.get(route_id)
    print('made route')
    trip_controller.get_valid_trips(route, day_type)
    print('made trips')
    stops_controller.get_by_route(route)
    print('made stops')
    trip_controller.create_segments(route)
    print('made segments')
    stops_controller.set_next_stations(route)
    print('set stations\' next stations')

    # sequence = route_controller.get_largest_shared_sequence(route)
    # print(sequence)
    
    
    html = timetable.station_time_list(route, route_controller.get_station_time_list(route))

    html_file = open('./results/station-time-list-%s.html' % route.id, 'w')
    html_file.write(html)
    print('File written: ./results/station-time-list-%s.html' % route.id)


    # print(route.find_end_points())
    # table = timeline.draw(route)
    # print('drew timeline')
    # svg_file = open('./results/%s-times.svg' % route.id, 'w')
    # svg_file.write(table)
    # print('File written: ./results/%s-times.svg' % route.id)
