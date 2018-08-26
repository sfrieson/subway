from lib import db

def get_by_route_id(route_id, fields):
    return db.get_many("""
    SELECT
        %s
    FROM
        trips
    WHERE
        route_id = '%s'
    """ % (', '.join(fields), route_id))
