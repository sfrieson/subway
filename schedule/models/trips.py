from lib import db

def get_by_route_id(route_id, fields, day=None):
    return db.get_many("""
    SELECT
        %s
    FROM
        trips
        JOIN calendar on trips.service_id = calendar.service_id
    WHERE
        route_id = '%s' %s
    """ % (
        ', '.join(fields),
        route_id,
        '' if day is None else 'AND %s = TRUE' % day
    ))
