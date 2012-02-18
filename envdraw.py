from examine import *
import tkinter as tk
from drawable import *
import ast
from rewrite import *
import random

GLOBAL_FRAME = inspect.currentframe()

def test(f):
    try:
        envdraw = test.envdraw
        current = inspect.currentframe().f_back
        frame = envdraw.tracker.clean_frame(inspect.currentframe().f_back.f_locals)
        envdraw.static_link[f] = current
        print(f.__name__, frame)
    except:
        print("exception")

    return f

class EnvDraw(object):

    def __init__(self):
        self.master = tk.Tk()
        self.canvas = tk.Canvas(self.master, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.tracker = Tracker(self, GLOBAL_FRAME)
        self.frame_tk = {}
        self.function_tk = {}
        self.static_link = {}

    def redraw(self):
        self.frame_tk = {}
        self.canvas.delete(tk.ALL)
        frames = self.tracker.frames
        for frame in frames:
            x, y = self.place()
            f = Frame(self.canvas, x, y)
            self.frame_tk[frame] = f
            for var, val in frames[frame].items():
                variable_draw = Variable(self.canvas, f, var)
                if type(val) == FUNCTION_TYPE:
                    value_draw = Function(self.canvas, 200, 200,
                        val.__name__, inspect.getargspec(val).args)
                    self.function_tk[val] = value_draw
                else:
                    value_draw = Value(self.canvas, f, val)
                Connector(self.canvas, value_draw, variable_draw)

        for f, ftk in self.frame_tk.items():
            f_back = f.f_back
            if f_back and f_back != GLOBAL_FRAME:
                Connector(self.canvas, self.frame_tk[f.f_back], ftk)

        for fn, fr in self.static_link.items():
            fn_tk = self.function_tk[fn]
            fr_tk = self.frame_tk[fr]
            Connector(self.canvas, fr_tk, fn_tk)

    def place(self):
        x, y = random.randint(50, 650), random.randint(50, 500)
        x, y = x//10*10, y//10*10
        attempts = 0
        while len(self.canvas.find_overlapping(x-10, y-10, x+160, y+80)) > 0:
            if attempts > 30:
                break
            x, y = random.randint(50, 650), random.randint(50, 500)
            x, y = x//10*10, y//10*10
            attempts += 1
        return x, y

test.envdraw = EnvDraw()
#exec(compile(open("test.py").read(), "test.py", 'exec'))
if __name__ == "__main__":
    ENVDRAW = test.envdraw
    ENVDRAW.tracker.test = test
    sys.settrace(ENVDRAW.tracker.trace)
    tree = ast.parse(open('test.py').read())
    #new_tree = ast.fix_missing_locations(AddDecorator().visit(AddImport().visit(tree)))
    new_tree = ast.fix_missing_locations(AddDecorator().visit(tree))
    eval(compile(new_tree, 'test.py', 'exec'))
    input()
