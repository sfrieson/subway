from schedule.views import template
def station_time_list (route, stations):
    return template.html({
        'html': '<h1 class="route">%s</h1><ul class="stations">%s</ul>' % (
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
        ),
        'css': """
        .route {
            font-family: helvetica;
        }

        .stations {
            padding: 0;
            list-type: none;
        }

        .station_name {
            font-family: helvetica;
            font-size: 1.2em;
            font-weight: bold;
        }

        .station {
            list-type: none;
        }

        .station:hover {
            outline: 2px solid lightgray;
        }

        .times {
            padding: 0;
            margin-left: 1em;
        }

        .time {
            display: inline;
        }

        .time + .time:before {
            content: ', ';
        }
        """,
        'js': ''
    })
