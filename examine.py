#! /usr/bin/env python3

import inspect, gc
from envdraw import *
from components import *
from util import *
import tkinter as tk
import random
import sys

FUNCTION_TYPE = type(lambda x: 0)
IGNORE_MODULES = {"envdraw", "drawable", "inspect", "code", "locale",
                  "encodings.utf_8", "codecs", "ast", "_ast", "rewrite",
                  "envdraw", "tkinter", "_functools", "_heapq", "util"}
IGNORE_VARS = {"IGNORE_MODULES", "IGNORE_VARS", "test", "ENVDRAW", "Tracker",
                "self.glob", "EnvDraw", "envdraw", "AddImport", "AddDecorator",
                "GLOBAL_FRAME", "FUNCTION_TYPE", "TRACKER", "funcreturn", "funcdef",
                "_get_called_function", "TRACKER", "EnvFrame", "pprint", "funccall"}

def _get_called_function():
    frame = inspect.currentframe().f_back.f_back
    code = frame.f_code
    global_obs = frame.f_globals
    for possible in gc.get_referrers(code):
        if type(possible) == FUNCTION_TYPE:
            return possible


def funcdef(func):
    funcdef.tracker.defined_function(func)
    debug_print('def:', func)
    return func


def funccall():
    tracker = funccall.tracker
    fn = _get_called_function()
    debug_print("making a new frame for function call to ", fn)
    tracker.call_stack.append(tracker.current_frame)
    debug_print("CALL STACK APPEND", fn)
    tracker.current_frame = EnvFrame(f_back=tracker.static_link[fn])
    tracker.frames.append(tracker.current_frame)


def funcreturn(val):
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
    if fn.__closure__:
        closures = set([x.cell_contents for x in fn.__closure__])
        for k,v in py_fr.f_locals.items():
            if v in closures and k not in args:
                del f_locals[k]
    debug_print('returning from', fn)
    funcreturn.tracker.exiting_function(fn, py_fr, f_locals, f_globals)
    debug_print('return:', val)
    return val


class EnvFrame(object):
    """Represents a frame in the environment diagram."""

    def __init__(self, f_back=None, tk=None):
        self.variables = {}
        self.f_back = f_back
        self.f_forward = []

    def extends(self, frame):
        """Set the frame which this EnvFrame is extending."""
        self.f_back = frame

    def extended_by(self, frame):
        """Add a frame that extends this EnvFrame."""
        self.f_forward.append(frame)

    def add_vars(self, dic):
        """Add a series of bindings represented in a dictionary mapping names
        to values."""
        # TODO: Should this wipe out pre-existing bindings or just add
        # additional ones?
        dic = dict(dic) #TODO (Tom): Figure out why this line is here?
        self.variables = dic


class Tracker(object):

    def __init__(self):
        self.current_frame = EnvFrame() #this is global
        self.frames = [self.current_frame]
        self.call_stack = []
        self.static_link = {}
        self.function_tk = {}
        self.frame_tk = {}

    def defined_function(self, fn):
        self.current_frame.variables[fn.__name__] = fn
        self.static_link[fn] = self.current_frame

    def exiting_function(self, fn, py_fr, frame_vars, glob):
        frame = self.current_frame
        frame.add_vars(frame_vars)
        debug_print(frame.variables)
        debug_print("CALL STACK POP", fn)
        self.current_frame = self.call_stack.pop()

    def clean_frame(self, frame_locals):
        to_remove = []
        for key, value in frame_locals.items():
            if self._should_clean(key, value):
                to_remove.append(key)
        cleaned_frame = dict(frame_locals)
        for key in to_remove:
            del cleaned_frame[key]
        return cleaned_frame

    def _should_clean(self, key, value):
        return key.startswith("__") or \
                key in IGNORE_VARS or \
                inspect.ismodule(value) or \
                getattr(value, "__module__", None) in IGNORE_MODULES

    def draw(self, cur_globals=None):
        if cur_globals is None:
            cur_globals = inspect.currentframe().f_globals
        self.current_frame.add_vars(self.clean_frame(cur_globals))
        master = tk.Tk()
        canvas = tk.Canvas(master, width=800, height=600)
        canvas.pack(fill=tk.BOTH, expand=1)
        for i, fr in enumerate(self.frames):
            x, y = self.place(canvas)
            fr_tk = Frame(canvas, x, y, i == 0)
            self.frame_tk[fr] = fr_tk
            for var, val in fr.variables.items():
                variable_draw = Variable(canvas, fr_tk, var)
                if val in self.function_tk:
                    value_draw = self.function_tk[val]
                elif type(val) == FUNCTION_TYPE:
                    x, y = self.place(canvas)
                    value_draw = Function(canvas, x, y, val.__name__,
                        inspect.getargspec(val).args)
                    self.function_tk[val] = value_draw
                else:
                    value_draw = Value(canvas, fr_tk, val)
                fr_tk.add_binding(variable_draw, value_draw)
                #Connector(canvas, value_draw, variable_draw)

        for f, ftk in self.frame_tk.items():
            f_back = f.f_back
            if f_back:
                Connector(canvas, self.frame_tk[f.f_back], ftk)

        debug_pprint(self.static_link)
        for fn, fr in self.static_link.items():
            debug_print(fn, fr.variables)
            fn_tk = self.function_tk[fn]
            fr_tk = self.frame_tk[fr]
            Connector(canvas, fr_tk, fn_tk)

    def place(self, canvas):
        if len(canvas.find_all()) == 0:
            return 50, 50
        x, y = random.randint(50, 600), random.randint(50, 500)
        x, y = x//10*10, y//10*10
        attempts = 0
        while len(canvas.find_overlapping(x-10, y-10, x+160, y+80)) > 0:
            if attempts > 30:
                break
            x, y = random.randint(50, 650), random.randint(50, 500)
            x, y = x//10*10, y//10*10
            attempts += 1
        return x, y


TRACKER = Tracker()
funcdef.tracker = TRACKER
funcreturn.tracker = TRACKER
funccall.tracker = TRACKER

IGNORE_MODULES = {"envdraw", "drawable", "inspect", "code", "locale",
                  "encodings.utf_8", "codecs", "ast", "_ast", "rewrite",
                  "envdraw", "tkinter", "_functools", "_heapq", "util"}
"""
IGNORE_VARS = {"IGNORE_MODULES", "IGNORE_VARS", "test", "ENVDRAW", "Tracker",
                "self.glob", "EnvDraw", "envdraw", "AddImport", "AddDecorator",
                "GLOBAL_FRAME", "FUNCTION_TYPE", "TRACKER", "funcreturn", "funcdef",
                "_get_called_function", "TRACKER", "EnvFrame", "pprint", "funccall"}
                """
IGNORE_VARS = set(locals().keys())

if __name__ == '__main__':
    tree = ast.parse(open(sys.argv[1]).read())
    new_tree = ast.fix_missing_locations(AddFuncCall().visit(AddFuncReturn().visit(AddFuncDef().visit(tree))))
    exec(compile(new_tree, '<unknown>', 'exec'))

    debug_pprint([v.variables for v in TRACKER.frames])
    debug_print()
    debug_pprint(TRACKER.frames)

    TRACKER.draw()
    input()
