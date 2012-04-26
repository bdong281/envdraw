#! /usr/bin/env python3

import inspect, gc
from envdraw import *
from components import *
from util import *
from pprint import pprint
import tkinter as tk
import random
import sys


FUNCTION_TYPE = type(lambda x: 0)


def _get_called_function():
    frame = inspect.currentframe().f_back.f_back
    code = frame.f_code
    global_obs = frame.f_globals
    for possible in gc.get_referrers(code):
        if type(possible) == FUNCTION_TYPE:
            return possible


def funcdef(func):
    """This is called on a function when it is first created (lambda or def
    statement).  This leads to transformations of for def statements where
        def foo(x):
            return x * x
    becomes
        @funcdef
        def foo(x):
            return x * x
    and, for lambdas,
        x = lambda y: y * y
    becomes
        x = funcdef(lambda y: y * y)

    Arguments:
        func -- The function we're decorating in the inputted code.
    """
    funcdef.tracker.defined_function(func)
    debug_print('def:', func)
    return func


def funccall():
    """This is inserted as a call before the body of a function."""
    fn = _get_called_function()
    debug_print("making a new frame for function call to ", fn)
    funccall.tracker.enter_function(fn)


def funcreturn(val):
    """Used as a replacement for any locations in a function where the program
    exits the function (either at a return or at the end of the suite).
    Essentially we do transformations like:

        return expr --> return funcreturn(expr)
    
    Arguments:
        val -- the value you'd normally return.
    """
    py_fr = inspect.currentframe().f_back
    fn = _get_called_function()
    try:
        fn = fn.orig
    except:
        pass
    debug_print(fn.__closure__)
    debug_print('returning from', fn)
    funcreturn.tracker.exit_function(fn, py_fr)
    debug_print('return:', val)
    return val


class Tracker(object):

    def __init__(self):
        # Set up canvas
        self.canvas = tk.Canvas(tk.Tk(), width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Set up call_stack with global frame
        x, y = self.place()
        self.call_stack = [Frame(self.canvas, x, y, globe=True)]

        # Keep a directory of Function objects in case we need to re-use.
        # There's an assumption here that the function will be defined by the
        # time we need to bind something to it, which when you think about it,
        # HAS to be true :P
        self.functions = {}
        self.static_links = {}

    @property
    def current_frame(self):
        return self.call_stack[-1]

    @property
    def global_frame(self):
        return self.call_stack[0]

    def defined_function(self, fn):
        """We've defined the given function, now draw it in the current
        frame.

        Arguments:
            fn -- The function value that was just created in the current
            frame.

        TODO: Needs to handle lambdas correctly (currently it adds an incorrect
        variable binding since it doesn't differentiate between creation of the
        function object and binding it to a variable).
        """
        x, y = self.place()
        fn_tk = Function(self.canvas, x, y, fn.__name__,
                         inspect.getargspec(fn).args, self.current_frame)
        if fn.__name__ != "<lambda>": # TODO: Kind of a hack
            self.current_frame.add_binding(fn.__name__, fn_tk)
        self.functions[fn] = fn_tk
        self.static_links[fn] = self.current_frame

    def enter_function(self, fn):
        x, y = self.place()
        self.call_stack.append(Frame(self.canvas, x, y,
                                     extended_frame=self.static_links[fn]))

    def exit_function(self, fn, py_fr):
        frame = self.current_frame
        local_vars = { var : py_fr.f_locals[var] for var in \
                      py_fr.f_code.co_varnames }
        nonlocal_varnames = [ var for var in py_fr.f_locals.keys() if var not \
                             in local_vars.keys() ]
        nonlocal_vars = { var : py_fr.f_locals[var] for var in \
                         nonlocal_varnames }
        for var, val in py_fr.f_globals.items():
            if var not in nonlocal_vars:
                nonlocal_vars[var] = val
        # For current local variables
        for var, val in local_vars.items():
            if not self._should_clean(var, val):
                if type(val) != FUNCTION_TYPE:
                    diag_val = Value(self.canvas, self.current_frame, val)
                else:
                    diag_val = self.functions[val]
                frame.add_binding(var, diag_val)
        # For nonlocal variables
        for var, val in nonlocal_vars.items():
            if not self._should_clean(var, val):
                if type(val) != FUNCTION_TYPE:
                    diag_val = Value(self.canvas, self.current_frame, val)
                else:
                    diag_val = self.functions[val]
                frame.update_binding(var, diag_val)
        debug_print("CALL STACK POP", fn)
        self.call_stack.pop()

    def _should_clean(self, key, value):
        """Should this key and value in some environment be cleaned out of the
        final product?
        """
        return key.startswith("__") or \
                key in IGNORE_VARS or \
                inspect.ismodule(value) or \
                getattr(value, "__module__", None) in IGNORE_MODULES

    def insert_global_bindings(self, global_vals):
        """THIS IS A HACK... WE NEED A BETTER WAY TO TRACK UPDATES AND FILL IN
        GLOBAL/NONLOCAL FRAMES (tmagrino).
        """
        for var, val in global_vals.items():
            if not self._should_clean(var, val):
                if type(val) != FUNCTION_TYPE:
                    diag_val = Value(self.canvas, self.global_frame, val)
                else:
                    diag_val = self.functions[val]
                self.global_frame.add_binding(var, diag_val)

    def place(self):
        """Find an available space to place a new item on the GUI canvas."""
        if len(self.canvas.find_all()) == 0:
            return 50, 50
        x, y = random.randint(50, 600), random.randint(50, 500)
        x, y = x//10*10, y//10*10
        attempts = 0
        while len(self.canvas.find_overlapping(x-10, y-10, x+160, y+80)) > 0:
            if attempts > 30:
                break
            x, y = random.randint(50, 650), random.randint(50, 500)
            x, y = x//10*10, y//10*10
            attempts += 1
        return x, y


# TODO: UGLY UGLY UGLY, should be handled differently.  Could probably make the
# three functions associated with an instance of the Tracker class and could be
# given to the ast NodeTransformers to be used?  Problem there is that we still
# need an identifier for the way we currently pull that off.
def run(input_file, additional_ignore_vars=None, wait=True):
    # TODO: Oh god there's so much wrong and sins here.
    global TRACKER, IGNORE_VARS
    old_ignore_vars = IGNORE_VARS
    if additional_ignore_vars:
        IGNORE_VARS = IGNORE_VARS.union(set(additional_ignore_vars))
    TRACKER = Tracker()
    funcdef.tracker = TRACKER
    funcreturn.tracker = TRACKER
    funccall.tracker = TRACKER

    tree = ast.parse(open(input_file).read(), filename=input_file)
    new_tree = envdraw_decorate(tree)
    exec_globals = locals()
    for k, v in globals().items():
        exec_globals[k] = v
    IGNORE_VARS = IGNORE_VARS.union(set(locals()))
    exec(compile(new_tree, input_file, 'exec'), exec_globals, locals())
    # TODO: Is there a better way to wait for the user to quit, using Tk?
    if wait:
        try:
            input()
        except EOFError:
            pass

    IGNORE_VARS = old_ignore_vars

# TODO: So bad, this is so bad, whyyyyyyyyy.
TRACKER = None
# TODO: This and IGNORE_VARS are both redundant and could be better done as a
# dynamically generated set of values.
IGNORE_MODULES = {"envdraw", "drawable", "inspect", "code", "locale",
                  "encodings.utf_8", "codecs", "ast", "_ast", "rewrite",
                  "envdraw", "tkinter", "_functools", "_heapq", "util"}
IGNORE_VARS = set(locals().keys()).union(set(["IGNORE_VARS"]))

if __name__ == '__main__':
    run(sys.argv[1])
