from schedule.models import route as model
from lib.classes import Route

def get (id):
    # all route ids in the database are uppercase (A, B, C...)
    return Route(model.get(id.upper()))