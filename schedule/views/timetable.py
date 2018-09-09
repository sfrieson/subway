def station_time_list (route, stations):
    return '<h1 class="route">%s</h1><ul class="stations">%s</ul>' % (
        route.letter,
        ''.join(sorted([
            '<li class="station"><span class="station_name">%s</span><ul class="times">%s</ul></li>' % (
                station.name,
                "".join([
                    '<li class="time">%s</li>' % time.get_time_of_day()
                    for time in sorted(times, key=lambda x: x.get_time_of_day_value())
                ])
            ) for station, times in stations.items()
        ]))
    )
