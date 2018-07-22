import json
import re
from functools import reduce
from pprint import pprint

# Load JSON
with open('./results/time-table.json') as file:
    data = json.load(file)

def collect (full_list, agg_on_field):
    agg = {}
    for item in full_list:
        id = item[agg_on_field]
        if id not in agg:
            agg[id] = []

        del item[agg_on_field]
        agg[id].append(item)

    return agg

# Organize data by trip
trips = collect(data, 'trip_id')

# travel times
spans = []

time_parse = re.compile(r"(?P<hr>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})")
def parse_time(time_str):
    time = 0
    match = time_parse.match(time_str)

    time += int(match.group('sec'))
    time += int(match.group('min')) * 60
    time += int(match.group('hr')) * 60 * 60

    return time


for trip_id, trip in trips.items():
    for i, details in enumerate(trip):
        if i < len(trip) - 1:
            start = details
            stop = trip[i + 1]
            if start and stop:
                spans.append({
                    'from': start['stop_id'],
                    'to': stop['stop_id'],
                    'departure_time': parse_time(start['departure_time']),
                    'arrival_time': parse_time(stop['arrival_time'])
                })

json.dump(spans, open('./results/W-times.json', 'w'), separators=(',',':'))
