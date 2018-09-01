-- BOOLEANS ARE SET TO EMPTY BECAUSE THEY'RE SMALL
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
  route_type SMALLINT, -- ?? Is this a boolean?
  route_url VARCHAR(255),
  route_color CHAR(6), -- EXACT (HEX)
  route_text_color VARCHAR(6) DEFAULT '000000' -- optional hex
);

-- shape_id + shape_pt_sequence creates unique key
CREATE TABLE shapes (
  shape_id CHAR(10),
  shape_pt_lat FLOAT,
  shape_pt_lon FLOAT,
  shape_pt_sequence SMALLINT,
  shape_dist_traveled BOOLEAN -- EMPTY
);

CREATE TABLE stops (
  stop_id VARCHAR(8) PRIMARY KEY, -- ESTIMATE
  stop_code BOOLEAN, -- EMPTY
  stop_name VARCHAR(64), -- ESTIMATE
  stop_desc BOOLEAN, -- EMPTY
  stop_lat FLOAT,
  stop_lon FLOAT,
  zone_id BOOLEAN, -- EMPTY
  stop_url BOOLEAN, -- EMPTY
  location_type SMALLINT,
  parent_station VARCHAR(8) REFERENCES stops (stop_id)
);

CREATE TABLE transfers (
  from_stop_id VARCHAR(8) REFERENCES stops (stop_id),
  to_stop_id VARCHAR(8) REFERENCES stops (stop_id),
  transfer_type SMALLINT,
  min_transfer_time SMALLINT -- seconds all divisible by 30?
);

CREATE TABLE trips (
  route_id VARCHAR(5) REFERENCES routes (route_id),
  service_id VARCHAR(32) REFERENCES calendar (service_id),
  trip_id VARCHAR(64) PRIMARY KEY,
  trip_headsign VARCHAR(64), -- ESTIMATE
  direction_id SMALLINT,
  block_id BOOLEAN, -- EMPTY
  shape_id CHAR(10)
);

CREATE TABLE stop_times (
  trip_id VARCHAR(64) REFERENCES trips (trip_id),
  arrival_time CHAR(8), -- Elapsed time, may go above 24:00:00
  departure_time CHAR(8), -- Elapsed time, may go above 24:00:00
  stop_id VARCHAR(8) REFERENCES stops (stop_id), -- ESTIMATE
  stop_sequence SMALLINT,
  stop_headsign BOOLEAN, -- EMPTY
  pickup_type SMALLINT,
  drop_off_type SMALLINT,
  shape_dist_traveled BOOLEAN -- EMPTY
);

CREATE TABLE stations (
  station_id SMALLINT,
  complex_id SMALLINT,
  stop_id VARCHAR(8) PRIMARY KEY REFERENCES stops (stop_id),
  division VARCHAR(32), -- ESTIMATE (ENUM) 
  line VARCHAR(255), -- ENUM
  stop_name VARCHAR(255),
  borough VARCHAR(2), -- ENUM
  daytime_routes VARCHAR(10), -- SPACE SEPARATED LIST
  structure VARCHAR(16), -- ENUM
  lat FLOAT,
  lon FLOAT
);

CREATE TABLE station_entrances (
  division VARCHAR(32),
  line VARCHAR(32),
  station_name VARCHAR(255),
  station_lat FLOAT,
  station_lon FLOAT,
  route_1 VARCHAR(2),
  route_2 VARCHAR(2),
  route_3 VARCHAR(2),
  route_4 VARCHAR(2),
  route_5 VARCHAR(2),
  route_6 VARCHAR(2),
  route_7 VARCHAR(2),
  route_8 VARCHAR(2),
  route_9 VARCHAR(2),
  route_10 VARCHAR(2),
  route_11 VARCHAR(2),
  entrance_type VARCHAR(10),
  entry VARCHAR(10),
  exit_only VARCHAR(10),
  vending VARCHAR(10),
  staffing VARCHAR(10),
  staff_Hours VARCHAR(255),
  ada VARCHAR(10),
  ada_notes VARCHAR(255),
  free_crossover VARCHAR(10),
  north_south_street VARCHAR(32),
  east_west_street VARCHAR(32),
  corner VARCHAR(5),
  lat FLOAT,
  lon FLOAT
);

CREATE TABLE points(
  point_id SERIAL PRIMARY KEY,
  point_lon FLOAT,
  point_lat FLOAT
);
