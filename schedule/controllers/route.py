from schedule.models import route as model
from lib.classes import Route
from lib.utils import collect_on

def get(id):
    # all route ids in the database are uppercase (A, B, C...)
    return Route(model.get(id.upper()))

def get_longest_contiguous_path(path):
    max_length = 1
    max_start = 0
    max_end = 0
    sequence = 1

    start = 0
    end = 0
    length = 1
    for i, point in enumerate(path):
        if i + 1 != len(path) and point[sequence] + 1 == path[i + 1][sequence]:
            length += 1
            end = i + 1
        else:
            if length > max_length:
                max_length = length
                max_start = start
                max_end = end
            start = i + 1
            end = i + 1
            length = 1

    return path[max_start:max_end + 1]

def get_largest_shared_sequence(route):
    paths = collect_on(model.get_paths(route.id), 0, remove_key=True)

    point_id_sets = [{point[0] for point in points} for points in paths.values()]

    shared = None
    for point_set in point_id_sets:
        if shared is None:
            shared = point_set
        else:
            shared = shared & point_set

    # get random path
    path = list(paths.values())[0]

    shared = [point for point in path if point[0] in shared]
    print(len(shared))

    longest = get_longest_contiguous_path(shared)

    return longest
