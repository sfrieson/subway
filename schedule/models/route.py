from lib import db
def get(route_id):
    return db.get_one("SELECT * FROM routes where route_id = '%s';" % route_id)

def get_shapes(route_id):
    return db.get_many("""
        SELECT
            shape_id, point_id, shape_pt_sequence
        FROM
            shapes
        WHERE
            shape_id IN (
                SELECT DISTINCT
                    shapes.shape_id
                FROM
                    shapes
                    JOIN trips ON trips.shape_id = shapes.shape_id
                WHERE route_id = '%s'
            )
        GROUP BY
            shape_id
        ORDER BY
            shape_id, shape_pt_sequence
    """ % route_id)