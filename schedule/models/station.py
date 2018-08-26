from lib import db

def get_stops(route_id, day, fields):
    return db.get_many("""
        SELECT
          %s
        FROM stop_times
          JOIN trips on stop_times.trip_id = trips.trip_id
          JOIN stops on stop_times.stop_id = stops.stop_id
        WHERE
          stop_times.drop_off_type = 0 AND
          stop_times.pickup_type = 0 AND
          stop_times.trip_id IN (
            SELECT stop_times.trip_id
            FROM trips
              JOIN stop_times ON trips.trip_id = stop_times.trip_id
              JOIN stops ON stop_times.stop_id = stops.stop_id
              JOIN calendar ON trips.service_id = calendar.service_id
              JOIN routes ON trips.route_id = routes.route_id
            WHERE
              trips.route_id = '%s' AND
              %s IS TRUE
          )
        ORDER BY stop_times.trip_id, stop_sequence
    """ % (', '.join(fields), route_id, day))

def get(station_id, fields):
  return db.get_one("""
    SELECT
      %s
    FROM
      stations
    WHERE
      stations.stop_id = '%s'
  """ % (', '.join(fields), station_id))
