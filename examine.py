import sys, inspect, gc

GLOBAL_FRAME = inspect.currentframe()

class Tracker(object):
    
    def __init__(self, ignore_modules = set()):
        self.frames = {}
        self.frames[GLOBAL_FRAME] = "global"
        self.env_number = 1
        self.ignore_modules = ignore_modules
        self.ignore_modules.add("inspect")
        
    def untrace(self, fn):
        self.do_not_trace.add(fn)

    def trace(self, frame, event, args):

        """
        print(current_function, frame.f_locals)
        frame.f_locals[current_function]
        """
        current_function = self._get_called_function()
        if not self._should_trace(current_function):
            return self.trace

        if frame in self.frames:
            name = self.frames[frame]
        else:
            self.frames[frame] = "E{0}".format(self.env_number)
            name = self.frames[frame]
            self.env_number += 1
        cleaned_frame = self.clean_frame(frame.f_locals)
        print("{4} {3} | event '{1}' in {0}: \n{2}\n" \
                .format(name, event, cleaned_frame, frame.f_lineno, current_function.__name__))
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
                key == "GLOBAL_FRAME" or \
                inspect.ismodule(value)

    def _get_called_function(self):
        """
        Should only be called from trace
        It is only here so I do not clutter up that function


        NOT SURE IF THIS IS RIGHT
        """
        frame = inspect.currentframe().f_back.f_back
        code = frame.f_code
        global_obs = frame.f_globals
        functype = type(lambda: 0)
        for possible in gc.get_referrers(code):
            if type(possible) == functype:
                return possible

    def _should_trace(self, current_function):
        return not inspect.isbuiltin(current_function) and \
            not getattr(Tracker, current_function.__name__, None) == current_function and \
            not getattr(current_function, "__module__", None) in self.ignore_modules

if __name__ == "__main__":

    tracker = Tracker()
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
    
    # for testing
    print(tracker.clean_frame(GLOBAL_FRAME.f_locals))
