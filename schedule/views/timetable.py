from schedule.views import template
def station_time_list (route, stations):
    return template.html({
        'html': '<h1 class="route">%s</h1><ul class="stations">%s</ul>' % (
            route.letter,
            ''.join(sorted([
                """<li class="station">
                    <h2 class="station_name">{station.name}</h2>
                    <h3 id="{station.id}-up" class="direction_label">Uptown</h3>
                    <ul class="times" aria-labelledby="{station.id}-up">{uptown}</ul>
                    <h3 id="{station.id}-down" class="direction_label">Downtown</h3>
                    <ul class="times" aria-labelledby="{station.id}-down">{downtown}</ul>
                </li>""".format(
                    station = station,
                    uptown = "".join([
                        '<li class="time">%s</li>' % time.get_time_of_day()
                        for time in sorted(directions['uptown'], key=lambda x: x.get_time_of_day_value())
                    ]),
                    downtown = "".join([
                        '<li class="time">%s</li>' % time.get_time_of_day()
                        for time in sorted(directions['downtown'], key=lambda x: x.get_time_of_day_value())
                    ])
                ) for station, directions in stations.items()
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
            font-weight: bold;
        }

        .station {
            list-type: none;
        }

        .station:hover {
            outline: 2px solid lightgray;
        }

        .direction_label {
            font-family: arial;
            margin: 0;
            font-weight: normal;
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
