from lib import db
def get(route_id):
    return db.get_one("SELECT * FROM routes where route_id = '%s';" % route_id)