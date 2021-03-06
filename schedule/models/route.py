from lib import db
def get(route_id):
    return db.get_one("SELECT * FROM routes where route_id = '%s';" % route_id)

def get_paths(route_id):
    return db.get_many("""
        SELECT
            shape_id, points.point_id, shape_pt_sequence, point_lon, point_lat
        FROM
            shapes
            JOIN points on shapes.point_id = points.point_id
        WHERE
            shape_id IN (
                SELECT DISTINCT
                    shapes.shape_id
                FROM
                    shapes
                    JOIN trips ON trips.shape_id = shapes.shape_id
                WHERE route_id = '%s'
            )
        ORDER BY
            shape_id, shape_pt_sequence
    """ % route_id)