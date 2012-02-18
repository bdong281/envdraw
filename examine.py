import sys, inspect, gc

FUNCTION_TYPE = type(lambda x: 0)
IGNORE_MODULES = {"envdraw", "drawable", "inspect", "code", 
                    "locale", "encodings.utf_8", "codecs", "ast",
                    "_ast", "rewrite", "envdraw2", "tkinter"}
IGNORE_VARS = {"IGNORE_MODULES", "IGNORE_VARS", "test", "ENVDRAW", "Tracker",
                "self.glob", "EnvDraw", "envdraw", "AddImport", "AddDecorator",
                "GLOBAL_FRAME", "FUNCTION_TYPE"}

class Tracker(object):
    
    def __init__(self, envdraw, glob):
        self.glob = glob
        self.frames = {}
        self.frame_names = {}
        self.env_number = 1
        self.envdraw = envdraw
        self.ignore_modules = IGNORE_MODULES
        #self.frame_names[self.glob] = "global"
        #self.frames[self.glob] = self.clean_frame(self.glob.f_locals)
        
    def untrace(self, fn):
        self.ignore_modules.add(fn)

    def refresh_vars(self, frame):
        #self.frames[self.glob] = self.clean_frame(self.glob.f_locals)
        while frame != self.glob:
            self.frames[frame] = self.clean_frame(frame.f_locals)
            frame = frame.f_back

    def trace(self, frame, event, args):
        current_function = self._get_called_function()
        if not self._should_trace(current_function):
            return #self.trace

        if current_function == self.test:
            return
        print(current_function.__module__)
        if frame in self.frames:
            name = self.frame_names[frame]
        else:
            self.frame_names[frame] = "E{0}".format(self.env_number)
            name = self.frame_names[frame]
            self.env_number += 1
        self.refresh_vars(frame)
        cleaned_frame = self.frames[frame]
        self.envdraw.redraw()
        print("{4} {3} | event '{1}' in {0}: \n{2}\n" \
                .format(name, event, cleaned_frame, 
                    frame.f_lineno, current_function.__name__))
        #input()

        return self.trace

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
                getattr(value, "__module__", None) in self.ignore_modules

    def _get_called_function(self):
        """
        Should only be called from trace
        It is only here so I do not clutter up that function


        NOT SURE IF THIS IS RIGHT
        """
        frame = inspect.currentframe().f_back.f_back
        code = frame.f_code
        #print(dir(code))
        global_obs = frame.f_globals
        for possible in gc.get_referrers(code):
            if type(possible) == FUNCTION_TYPE:
                return possible

    def _should_trace(self, current_function):
        return current_function and \
            not inspect.isbuiltin(current_function) and \
            not getattr(Tracker, current_function.__name__, None) == current_function and \
            not getattr(current_function, "__module__", None) in self.ignore_modules

if __name__ == "__main__":

    tracker = Tracker(None)
    sys.settrace(tracker.trace)

    def foo():
        x = 5
        baz = lambda z: z*z
        def bar(y):
            return y+1
        baz(x)
        bar(x)
        return x

    foo()
