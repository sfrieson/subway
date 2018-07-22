-- SELECT departure_time, stop_name, direction_id, route_long_name
-- FROM trips
--   JOIN stop_times ON trips.trip_id = stop_times.trip_id
--   JOIN stops ON stop_times.stop_id = stops.stop_id
--   JOIN calendar ON trips.service_id = calendar.service_id
--   JOIN routes ON trips.route_id = routes.route_id
-- WHERE
--   trips.route_id = 'W' AND
--   monday IS TRUE AND
--   stop_sequence = 1 AND
--   departure_time LIKE '07:__:__'
-- ORDER BY departure_time ASC
-- ;


-- select stop_sequence, arrival_time, departure_time, stop_name
-- from stop_times
--   join stops on stop_times.stop_id = stops.stop_id
-- where trip_id = 'BSP18GEN-N091-Weekday-00_042450_N..N70R' order by stop_sequence;

-- SELECT trip_id, stop_sequence, stop_id, arrival_time, departure_time
-- FROM stop_times
-- WHERE trip_id IN (
--   SELECT stop_times.trip_id
--   FROM trips
--     JOIN stop_times ON trips.trip_id = stop_times.trip_id
--     JOIN stops ON stop_times.stop_id = stops.stop_id
--     JOIN calendar ON trips.service_id = calendar.service_id
--     JOIN routes ON trips.route_id = routes.route_id
--   WHERE
--     monday IS TRUE AND
--     stop_sequence = 1 AND
--     departure_time LIKE '07:__:__'
-- )
-- ORDER BY trip_id, stop_sequence
-- ;

-- Monday trips starting in the 7am hour
-- https://hashrocket.com/blog/posts/faster-json-generation-with-postgresql
COPY (
  SELECT array_to_json(array_agg(row_to_json(rows))) FROM (
    SELECT stop_times.trip_id, route_id, stop_sequence, stop_id, arrival_time, departure_time
    FROM stop_times
      JOIN trips on stop_times.trip_id = trips.trip_id
    WHERE stop_times.trip_id IN (
      SELECT stop_times.trip_id
      FROM trips
        JOIN stop_times ON trips.trip_id = stop_times.trip_id
        JOIN stops ON stop_times.stop_id = stops.stop_id
        JOIN calendar ON trips.service_id = calendar.service_id
        JOIN routes ON trips.route_id = routes.route_id
      WHERE
        monday IS TRUE AND
        stop_sequence = 1 AND
        departure_time LIKE '07:__:__'
    )
    ORDER BY trip_id, stop_sequence
  ) rows
)
TO '/Users/sfrieson/code/subway-time-map/results/rush-hour-trips.json'
;
