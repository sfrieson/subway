from schedule.models import station as model
from lib import utils
from lib.classes import Trip

def get_route_trips(route_id, day_type):

    day = 'monday'
    if day_type is 'Saturday':
        day = 'saturday'
    elif day_type is 'Sunday':
        day = 'sunday'

    stops = model.get(route_id, day)
    trips = utils.collect_on(stops, 0) # position 0 in tuple is trip_id
    trips = [Trip(id, stops) for id, stops in trips.items()]

    return trips
