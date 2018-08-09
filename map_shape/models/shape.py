from lib import db

def get_by_route(route):
    # There actually may be more than one, but let's start here
    points = db.get_many("""
        SELECT
            shape_pt_lon, shape_pt_lat
        FROM shapes
        WHERE
            shape_id = (
                SELECT shape_id FROM trips WHERE route_id = '%s' LIMIT 1
            )
        ORDER BY shape_pt_sequence
    """ % route)
    return points
