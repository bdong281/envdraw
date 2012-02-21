#! /usr/bin/env python3

import inspect, gc
from envdraw import *
from components import *
from util import *
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
    f_locals = dict(py_fr.f_locals)
    f_globals = dict(py_fr.f_globals)
    fn = _get_called_function()
    try:
        fn = fn.orig
    except:
        pass
    args = inspect.getargspec(fn).args
    debug_print(fn.__closure__)
    # If there are "free" variables, variables that are used but not defined in
    # the current scope.
    if fn.__closure__:
        closures = set([x.cell_contents for x in fn.__closure__])
        for k,v in f_locals.items():
            if v in closures and k not in args:
                del f_locals[k]
    debug_print('returning from', fn)
    funcreturn.tracker.exit_function(fn, py_fr, f_locals)
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
        self.current_frame.add_binding(Variable(self.canvas,
                                                self.current_frame,
                                                fn.__name__), fn_tk)

    def enter_function(self, fn):
        x, y = self.place()
        self.call_stack.append(Frame(self.canvas, x, y,
                                     extended_frame=self.current_frame))

    def exit_function(self, fn, py_fr, frame_vars):
        frame = self.current_frame
        for var in frame_vars:
            if type(frame_vars[var]) != FUNCTION_TYPE and \
               not self._should_clean(var, frame_vars[var]):
                diag_var = Variable(self.canvas, self.current_frame, var)
                diag_val = Value(self.canvas, self.current_frame,
                                 frame_vars[var])
                frame.add_binding(diag_var, diag_val)
        debug_print("CALL STACK POP", fn)
        self.call_stack.pop()

    def clean_frame(self, frame_locals):
        """Pretty sure this is deprecated."""
        to_remove = []
        for key, value in frame_locals.items():
            if self._should_clean(key, value):
                to_remove.append(key)
        cleaned_frame = dict(frame_locals)
        for key in to_remove:
            del cleaned_frame[key]
        return cleaned_frame

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
                diag_var = Variable(self.canvas, self.global_frame, var)
                diag_val = Value(self.canvas, self.global_frame, val)
                self.global_frame.add_binding(diag_var, diag_val)

    def draw(self, cur_globals=None):
        """Deprecated."""
        if cur_globals is None:
            cur_globals = inspect.currentframe().f_globals
        self.current_frame.add_vars(self.clean_frame(cur_globals))
        for i, fr in enumerate(self.frames):
            x, y = self.place()
            fr_tk = Frame(self.canvas, x, y, i == 0)
            self.frame_tk[fr] = fr_tk
            for var, val in fr.variables.items():
                variable_draw = Variable(self.canvas, fr_tk, var)
                if val in self.function_tk:
                    value_draw = self.function_tk[val]
                elif type(val) == FUNCTION_TYPE:
                    x, y = self.place()
                    # fr_tk is wrong, but this is a structural problem where we
                    # define functions by bindings we find rather than when we
                    # see it created.
                    value_draw = Function(self.canvas, x, y, val.__name__,
                        inspect.getargspec(val).args, fr_tk)
                    self.function_tk[val] = value_draw
                else:
                    value_draw = Value(self.canvas, fr_tk, val)
                fr_tk.add_binding(variable_draw, value_draw)
                #Connector(self.canvas, value_draw, variable_draw)

        for f, ftk in self.frame_tk.items():
            f_back = f.f_back
            if f_back:
                Connector(self.canvas, self.frame_tk[f.f_back], ftk)

        debug_pprint(self.static_link)
        for fn, fr in self.static_link.items():
            debug_print(fn, fr.variables)
            fn_tk = self.function_tk[fn]
            fr_tk = self.frame_tk[fr]
            #Connector(self.canvas, fr_tk, fn_tk)

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


# TODO: UGLY UGLY UGLY, should be handled differently.  Cold probably make the
# three functions associated with an instance of the Tracker class and could be
# given to the ast NodeTransformers to be used?  Problem there is that we still
# need an identifier for the way we currently pull that off.
TRACKER = Tracker()
funcdef.tracker = TRACKER
funcreturn.tracker = TRACKER
funccall.tracker = TRACKER

# TODO: This and IGNORE_VARS are both redundant and could be better done as a
# dynamically generated set of values.
IGNORE_MODULES = {"envdraw", "drawable", "inspect", "code", "locale",
                  "encodings.utf_8", "codecs", "ast", "_ast", "rewrite",
                  "envdraw", "tkinter", "_functools", "_heapq", "util"}
IGNORE_VARS = set(locals().keys()).union(set(["IGNORE_VARS"]))

if __name__ == '__main__':
    tree = ast.parse(open(sys.argv[1]).read())
    new_tree = ast.fix_missing_locations(AddFuncCall().visit(AddFuncReturn().visit(AddFuncDef().visit(tree))))
    exec(compile(new_tree, '<unknown>', 'exec'))
    TRACKER.insert_global_bindings(globals())
    # TODO: Is there a better way to wait for the user to quit, using Tk?
    input()
