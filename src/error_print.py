import sys


def error_print(*args, **kwargs):
    """print function to stderr"""
    print(*args, file=sys.stderr, **kwargs)
