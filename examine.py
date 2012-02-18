import sys, inspect

GLOBAL_FRAME = inspect.currentframe()

class Tracker(object):
    
    def __init__(self):
        self.frames = {}
        self.frames[GLOBAL_FRAME] = "global"
        self.env_number = 1

    def untrace(self, fn):
        self.do_not_trace.add(fn)

    def trace(self, frame, event, args):
        if frame in self.frames:
            name = self.frames[frame]
        else:
            self.frames[frame] = "E{0}".format(self.env_number)
            name = self.frames[frame]
            self.env_number += 1
        cleaned_frame = self.clean_frame(frame.f_locals)
        print("({3}) event '{1}' in {0}: {2}".format(name, event, cleaned_frame, frame.f_lineno))
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

if __name__ == "__main__":

    tracker = Tracker()
    sys.settrace(tracker.trace)

    def foo():
        x = 5
        def bar(y):
            return y+1
        bar(x)
        return x

    foo()
    
    # for testing
    print(tracker.clean_frame(GLOBAL_FRAME.f_locals))
