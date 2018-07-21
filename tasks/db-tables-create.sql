CREATE TABLE agency (
  -- ALL LENGTHS ARE EXACT
  agency_id CHAR(8) PRIMARY KEY,
  agency_name CHAR(25),
  agency_url CHAR(19),
  agency_timezone CHAR(16),
  agency_lang CHAR(2),
  agency_phone CHAR(12)
);

CREATE TABLE calendar (
  service_id VARCHAR(32) PRIMARY KEY, -- ESTIMATE
  monday BOOLEAN,
  tuesday BOOLEAN,
  wednesday BOOLEAN,
  thursday BOOLEAN,
  friday BOOLEAN,
  saturday BOOLEAN,
  sunday BOOLEAN,
  start_date DATE,
  end_date DATE
);

CREATE TABLE calendar_dates (
  service_id VARCHAR(32) REFERENCES calendar (service_id),
  date DATE,
  exception_type SMALLINT
);

CREATE TABLE routes (
  route_id VARCHAR(5)  PRIMARY KEY, -- ESTIMATE
  agency_id VARCHAR(12), -- EXACT
  route_short_name VARCHAR(5), -- ESTIMATE
  route_long_name VARCHAR(32), -- ESTIMATE
  route_desc TEXT,
  route_type INT, -- ?? Is this a boolean?
  route_url VARCHAR(255),
  route_color CHAR(6), -- EXACT (HEX)
  route_text_color VARCHAR(32) -- UNSURE
);

-- shape_id + shape_pt_sequence creates unique key
CREATE TABLE shapes (
  shape_id CHAR(10),
  shape_pt_lat FLOAT,
  shape_pt_lon FLOAT,
  shape_pt_sequence SMALLINT,
  shape_dist_traveled FLOAT -- UNSURE
);

CREATE TABLE stops (
  stop_id VARCHAR(8) PRIMARY KEY, -- ESTIMATE
  stop_code VARCHAR(16), -- UNSURE
  stop_name VARCHAR(64), -- ESTIMATE
  stop_desc TEXT, -- UNSURE
  stop_lat FLOAT,
  stop_lon FLOAT,
  zone_id VARCHAR(8), -- UNSURE
  stop_url VARCHAR(64), -- UNSURE
  location_type SMALLINT,
  parent_station VARCHAR(8) REFERENCES stops (stop_id)
);

CREATE TABLE transfers (
  from_stop_id VARCHAR(8) REFERENCES stops (stop_id),
  to_stop_id VARCHAR(8) REFERENCES stops (stop_id),
  transfer_type SMALLINT,
  min_transfer_time SMALLINT -- seconds?
);

CREATE TABLE trips (
  route_id VARCHAR(5) REFERENCES routes (route_id),
  service_id VARCHAR(32) REFERENCES calendar (service_id),
  trip_id VARCHAR(64) PRIMARY KEY,
  trip_headsign VARCHAR(64), -- ESTIMATE
  direction_id SMALLINT,
  block_id VARCHAR(8), -- UNSURE
  shape_id CHAR(10)
);

CREATE TABLE stop_times (
  trip_id VARCHAR(64) REFERENCES trips (trip_id),
  arrival_time CHAR(8), -- Elapsed time, may go above 24:00:00
  departure_time CHAR(8), -- Elapsed time, may go above 24:00:00
  stop_id VARCHAR(8) REFERENCES stops (stop_id), -- ESTIMATE
  stop_sequence SMALLINT,
  stop_headsign VARCHAR(32), -- UNSURE
  pickup_type SMALLINT,
  drop_off_type SMALLINT,
  shape_dist_traveled FLOAT -- UNSURE
);
