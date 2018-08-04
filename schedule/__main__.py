import sys
from schedule import controller


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
    if len(args) == 0:
        print("Please supply a route and day. `python -m schedule W weekday`")
    else:
        controller.main(args[0], args[1])


if __name__ == "__main__":
    main()
