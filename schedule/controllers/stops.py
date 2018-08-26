from schedule.models import stops as model
from lib.classes import Stop

def get_by_route(route):
    
    stops_by_trip = model.get_by_trip_ids(
        route.trips.keys(),
        [
            'stop_sequence', 'complex_id', 'stops.stop_name', 'arrival_time', 
            'departure_time', 'pickup_type', 'stop_lon', 'stop_lat'
        ]
    )
    
    stops_by_trip = {key: [Stop(s) for s in stops] for key, stops in stops_by_trip.items()}

    for trip_id, stops in stops_by_trip.items():
        trip = route.trips[trip_id]
        for stop in stops:
            trip.add_stop(stop)
            route.add_stop(stop)

def set_next_stations(route):
    for trip in route.trips.values():
        for i, stop in enumerate(trip.stops):
            if i < len(trip.stops) - 1:
                currentStation = stop.station
                nextStation = trip.stops[i + 1].station
                currentStation.set_next(nextStation, trip.direction)
