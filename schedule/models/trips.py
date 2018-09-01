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

def get_path_by_shape_id(shape_id):
    return db.get_many("""
    SELECT
        point_lon, point_lat
    FROM
        shapes
        JOIN points on shapes.point_id = points.point_id
    WHERE
        shape_id = '%s'
    ORDER BY
        shape_pt_sequence
    """ % shape_id)