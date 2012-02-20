"""util.py

Various useful functions for development and general use in the program.

Written by Tom Magrino (tmagrino@berkeley.edu)

TODO:
    - Perhaps find a cleaner way of remembering if debugging is on/off (without
    using a global variable).
"""

from pprint import pprint

# Debugging off by default
_DEBUG_MODE = False

def debug_print(*args):
    """Print a message to stderr if debugging is on, uses the same arguments as
    a print call (except for the file argument).
    """
    if _DEBUG_MODE:
        print(*args, file=stderr)

def debug_pprint(*args):
    """Pretty print a message to stderr if debugging is on, uses the same
    arguments as a pprint call (except for the stream argument).
    """
    if _DEBUG_MODE:
        pprint(*args, stream=stderr)

def is_debug_mode():
    """Check if debugging is enabled."""
    return _DEBUG_MODE

def debug_on():
    """Turn on debugging code."""
    global _DEBUG_MODE
    _DEBUG_MODE = True

def debug_off():
    """Turn off debugging code."""
    global _DEBUG_MODE
    _DEBUG_MODE = False
