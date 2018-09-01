-- GTFS structured data
COPY agency FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/agency.txt' DELIMITER ',' CSV HEADER;
COPY calendar FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/calendar.txt' DELIMITER ',' CSV HEADER;
COPY calendar_dates FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/calendar_dates.txt' DELIMITER ',' CSV HEADER;
COPY routes FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/routes.txt' DELIMITER ',' CSV HEADER;
UPDATE routes SET route_text_color = DEFAULT WHERE route_text_color IS NULL;
UPDATE routes SET route_text_color = DEFAULT WHERE route_text_color = ' ';
COPY shapes FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/shapes.txt' DELIMITER ',' CSV HEADER;
COPY stops FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/stops.txt' DELIMITER ',' CSV HEADER;
COPY transfers FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/transfers.txt' DELIMITER ',' CSV HEADER;
COPY trips FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/trips.txt' DELIMITER ',' CSV HEADER;
COPY stop_times FROM '/Users/sfrieson/code/subway/data/GTFS-Schedule-Data_NYCT-Subway/stop_times.txt' DELIMITER ',' CSV HEADER;

-- MTA-specific additional data
COPY stations FROM '/Users/sfrieson/code/subway/data/mta_stations.csv' DELIMITER ',' CSV HEADER;
COPY station_entrances FROM '/Users/sfrieson/code/subway/data/StationEntrances.csv' DELIMITER ',' CSV HEADER;

-- Normalize shapes points
INSERT INTO points(point_lon, point_lat)
SELECT DISTINCT shape_pt_lon, shape_pt_lat
FROM shapes;

ALTER TABLE shapes
ADD COLUMN point_id INT REFERENCES points (point_id);

UPDATE shapes
SET point_id = points.point_id
FROM points
WHERE shape_pt_lat = point_lat AND shape_pt_lon = point_lon;

ALTER TABLE shapes
DROP COLUMN shape_pt_lon,
DROP COLUMN shape_pt_lat;