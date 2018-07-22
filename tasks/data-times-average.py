import json
import re
from functools import reduce
from pprint import pprint

# Load JSON
with open('./results/rush-hour-trips.json') as file:
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
spans = {}

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
                span_id = start['stop_id'] + '-' + stop['stop_id']
                if span_id not in spans:
                    spans[span_id] = {
                        'route': details['route_id'],
                        'from': start['stop_id'],
                        'to': stop['stop_id'],
                        'times': []
                    }

                spans[span_id]['times'].append(parse_time(stop['arrival_time']) - parse_time(start['arrival_time']))

for span in spans.values():
    span['time'] = int(sum(span['times']) / len(span['times']))
    del span['times']

routes = collect(spans.values(), 'route')

json.dump(routes, open('./results/rush-hour-routes.json', 'w'), separators=(',',':'))

for route, spans in routes.items():
    seconds = 0
    for span in spans:
        seconds += span['time']

    minutes = int(seconds / 60)
    seconds %= 60

    hours = int(minutes / 60)
    minutes %= 60

    print('%s\t%s:%s:%s' % (route, str(hours).zfill(2), str(minutes).zfill(2), str(seconds).zfill(2)))
