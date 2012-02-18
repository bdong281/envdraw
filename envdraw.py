from examine import *
import tkinter as tk
from drawable import *

GLOBAL_FRAME = inspect.currentframe()

class EnvDraw(object):
    
    def __init__(self):
        self.master = tk.Tk()
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.tracker = Tracker(self, GLOBAL_FRAME)
        self.frame_tk = {}

    def redraw(self):
        self.frame_tk = {}
        self.canvas.delete(tk.ALL)
        frames = self.tracker.frames
        for frame in frames:
#            pprint(gc.get_referrers(frame))
#            input()
            f = Frame(self.canvas, 100, 100)
            self.frame_tk[frame] = f
            for var, val in frames[frame].items():
                variable_draw = Variable(self.canvas, f, var)
                if type(val) == FUNCTION_TYPE:
                    value_draw = Function(self.canvas, 200, 200, 
                        val.__name__, inspect.getargspec(val).args)
                else:
                    value_draw = Value(self.canvas, f, val)
                Connector(self.canvas, value_draw, variable_draw)

        for f, ftk in self.frame_tk.items():
            if f.f_back:
                Connector(self.canvas, self.frame_tk[f.f_back], ftk)
            

envdraw = EnvDraw()
envdraw.tracker.untrace('examine')
envdraw.tracker.untrace('drawable')
envdraw.tracker.untrace('tkinter')
sys.settrace(envdraw.tracker.trace)

exec(compile(open("test.py").read(), "test.py", 'exec'))
input()
