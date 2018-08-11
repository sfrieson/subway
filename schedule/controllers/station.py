from schedule.models import station as model
from lib import utils
from lib.classes import Trip

def get_route_trips(route_id, day_type):
    # treating the default as weekday, so picking `monday` to represent weekdays
    day = 'monday'

    if day_type is 'saturday':
        day = 'saturday'
    elif day_type is 'sunday':
        day = 'sunday'

    stops = model.get(route_id, day)
    trips = utils.collect_on(stops, 0) # position 0 is trip_id
    trips = [Trip(id, stops) for id, stops in trips.items()]

    return trips
