import sys
from map_shape.controllers import app


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
    if len(args) == 0:
        print("Please supply a route. `python -m map W`")
    else:
        app.make_map(args[0])


if __name__ == "__main__":
    main()
