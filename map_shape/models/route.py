from lib import db

def get_color(route):
    # There actually may be more than one, but let's start here
    color = db.get_one("""
        SELECT
            route_color
        FROM routes
        WHERE
            route_id = '%s'
    """ % route)
    return color
