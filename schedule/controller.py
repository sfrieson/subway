from schedule import model
from schedule import view

def main(route, day_type):
    print("Starting up the routine to make a %s train %s schedule" % (
        route, day_type
    ))

    details = {
        'day': 'monday',
        'route_id': route 
    }

    if day_type is 'Saturday':
        details['day'] = 'saturday'
    elif day_type is 'Sunday':
        details['day'] = 'sunday'

    route = {
        'route_id': details['route_id']
    }

    route_id, agency_id, route_short_name, route_long_name, route_desc, \
        route_type, route_url, route_color, route_text_color = \
        model.get_route(details['route_id'])

    route['train'] = route_short_name
    route['name'] = route_long_name
    route['description'] = route_desc
    route['color'] = route_color
    route['text_color'] = route_text_color

    (stations, stations_ordered, uptown_start, downtown_start, trips) = \
        model.get_stations(details['route_id'], details['day'])

    route['stations'] = [x.toDict() for x in stations_ordered]
    route['uptown_start'] = uptown_start.toDict()
    route['downtown_start'] = downtown_start.toDict()
    route['trips'] = trips
    # ------------------------- #   

    timetable = model.get_timetable(trips, stations)
    route['timetable'] = timetable


    table = view.build_svg(route)

    svg_file = open('./results/%s-times.svg' % route["route_id"], 'w')
    svg_file.write(table)
    print('File written: ./results/%s-times.svg' % route["route_id"])