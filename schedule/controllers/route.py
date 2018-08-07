from schedule.models import route as model

from lib.classes import Route

def get (id, trips):
    print('getting %s route' % id)
        
    return Route(model.get(id), trips)