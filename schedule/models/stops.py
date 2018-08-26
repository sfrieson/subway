from lib import db, utils

def get_by_trip_ids(trip_ids, fields):
    results = db.get_many("""
        SELECT
          trip_id, %s
        FROM stops
          JOIN stop_times on stop_times.stop_id = stops.stop_id
          JOIN stations on stations.stop_id = stops.parent_station
        WHERE
          stop_times.trip_id in (%s) AND
          stop_times.drop_off_type = 0 AND
          stop_times.pickup_type = 0
        ORDER BY stop_sequence
    """ % (', '.join(fields), ', '.join(["'%s'" % id for id in trip_ids])))

    return utils.collect_on(results, 0, remove_key=True)

def get(station_id, fields):
  return db.get_one("""
    SELECT
      %s
    FROM
      stations
    WHERE
      stations.stop_id = '%s'
  """ % (', '.join(fields), station_id))
