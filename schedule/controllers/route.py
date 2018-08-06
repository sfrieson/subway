from schedule.models import route as model
from math import inf as infinity

class Route:
    def __init__ (self, route_data, trips):
        self.id, self.agency_id, self.letter, self.name, self.description, \
        self.type, self.url, self. color, self.text_color = route_data
        self.trips = trips

    def get_transfers(self):
        pass
    def get_longest_trip_distance(self):
        longest = 0
        for trip in self.trips:
            longest = max(longest, trip.distance)

        return longest

    def get_master_schedule(self):
        pass

    def get_time_range(self):
        earliest = infinity
        latest = 0

        for trip in self.trips:
            earliest = min(
                earliest,
                trip.stops[0].departure_time.get_time_of_day_value()
            )
            latest = max(
                latest,
                trip.stops[-1].arrival_time.get_time_of_day_value()
            )
        
        return (earliest, latest)

    def get_stations(self):
        stations = set()
        for trip in self.trips:
            for stop in trip.stops:
                stations.add(stop.station)

        return stations

def get (id, trips):
    print('getting %s route' % id)
        
    return Route(model.get(id), trips)