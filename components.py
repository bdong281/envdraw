import tkinter as tk
from drawable import Drawable, Connectable, Draggable, Connector, Arrowhead

class Frame(Draggable):
    """Represents a Frame in the environment diagram.  A Frame is a Draggable
    GUI element.
    
    At a high level, a Frame consists of:
        - A list of bindings mapping from Variables to Values
        - A StaticLink to the enclosing environment Frame (None if it's
        global)
    """

    prefix = "frame"

    def __init__(self, canvas, x, y, globe=False, extended_frame=None):
        Draggable.__init__(self, canvas)
        self.bindings = [] # List of bindings from variables to values
        self.rect = canvas.create_rectangle(x, y, x + self.width, y +
                                            self.height, tag=self.tag,
                                            fill="white")
        canvas.create_oval(x+135, y-15, x+165, y+15, tag=self.tag,
                           fill="white")
        if globe:
            pass #Shouldn't we still draw a globe?
        else:
            canvas.create_oval(x+145, y-5, x+155, y+5, tag=self.tag,
                                    fill="black")
        if extended_frame is not None:
            self.extend(extended_frame)
        else:
            self.static_link = None

    def extend(self, frame):
        """Extend the given Frame."""
        self.static_link = StaticLink(self.canvas, self, frame)
        self.update()

    @property
    def enclosing_frame(self):
        """The frame that encloses this frame (what is pointed to by the static
        link).
        """
        return self.static_link.frame

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.rect)[0:2])

    def add_binding(self, variable, value):
        """Adds a Binding to this Frame.

        TODO: Figure out what to do if there's a pre-existing binding for that
        variable...
        """
        binding = Binding(self.canvas, variable, value)
        self.bindings.append(binding)
        x, y = self.pos
        variable.set_pos(x + 10, y + len(self.bindings) * 20)
        if value.moves_with_binding:
            value.set_pos(x + 140, y + len(self.bindings) * 20)
        self.update()

    def move(self, dx, dy):
        Draggable.move(self, dx, dy)
        for binding in self.bindings:
            binding.move(dx, dy)

    def update(self):
        x, y = self.pos
        self.canvas.coords(self.rect, x, y, x + self.width, y + self.height)

    @property
    def inhandle(self):
        x, y = self.pos
        leftside = tuple(((x, y + 20 * (i+1)) for i in
                range(len(self.bindings)+1)))
        rightside = tuple(((x + self.width, y + 20 * (i+1)) for i in
                range(len(self.bindings)+1)))
        topside = (x+40, y), (x+110, y)
        downside = tuple(((x, y+self.height) for x, y in topside))
        return leftside + rightside + topside + downside

    @property
    def outhandle(self):
        x, y = self.pos
        return x + self.width, y

    @property
    def width(self):
        return 150

    @property
    def height(self):
        return 40 + 20 * len(self.bindings)


class StaticLink(Connector):
    """Represents a StaticLink pointing to some Frame."""

    def __init__(self, canvas, base, frame):
        """Renamed arguments and changed order to be easier to use."""
        Connector.__init__(self, canvas, frame, base)

    @property
    def frame(self):
        """The frame pointed to by a StaticLink is the head."""
        return self.head

    @property
    def base(self):
        """The base of a StaticLink is the tail."""
        return self.tail


class Variable(Connectable):

    prefix = "variable"

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = 0, 0 # This should be set when it's bound in a Frame
        self.text = canvas.create_text(x, y, anchor=tk.NW, text=name+":",
                tag=self.tag)

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
        #self.update_connectors() # This should be done by the Binding

    def set_pos(self, x, y):
        self.canvas.move(self.tag, x - self.pos[0], y - self.pos[1])
        self.update_connectors()

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.text)[0:2])

    @property
    def width(self):
        x1, _, x2, _ = self.canvas.bbox(self.text)
        return ((x2 - x1)//10)*10

    @property
    def height(self):
        _, y1, _, y2 = self.canvas.bbox(self.text)
        return ((y2 - y1)//10)*10

    @property
    def outhandle(self):
        x, y = self.pos
        return round(x + self.width, -1), round(y + self.height // 2, -1)


class Value(Connectable):

    prefix = "value"
    moves_with_binding = True

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = 0, 0 # Should be updated using set_pos
        self.text = canvas.create_text(x, y, anchor=tk.NE, text=name,
                                       tag=self.tag)

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
        #self.update_connectors() # This should be done by the binding.

    def set_pos(self, x, y):
        self.canvas.move(self.tag, x - self.pos[0], y - self.pos[1])
        self.update_connectors()

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.text)[0:2])

    @property
    def width(self):
        x1, _, x2, _ = self.canvas.bbox(self.text)
        return x2 - x1

    @property
    def height(self):
        _, y1, _, y2 = self.canvas.bbox(self.text)
        return y2 - y1

    @property
    def inhandle(self):
        x, y = self.pos
        return (round(x - self.width, -1), round(y + self.height // 2, -1)),


class Binding(Connector):
    """Represents a Binding between a Variable and a Value.  It is a connector
    which can be moved, resulting in the Variable being moved and the Value
    only being moved if Variable.moves_with_binding is True.
    """

    prefix = "binding"

    def __init__(self, canvas, variable, value):
        """Literally the same constructor, just preferred to give better names
        to the arguments and reorder them.
        """
        Connector.__init__(self, canvas, value, variable)

    @property
    def variable(self):
        """The variable is at the tail of the Binding Connector."""
        return self.tail

    @property
    def value(self):
        """The value is at the tail of the Binding Connector."""
        return self.head

    def move(self, dx, dy):
        """Move the Binding.  Moves the variable by the given amounts.  If
        value.moves_with_binding is True, it is also moved by the given
        amounts.  Updates the Connector after the movement has been done.
        """
        self.variable.move(dx, dy)
        if self.value.moves_with_binding:
            self.value.move(dx, dy)
        self.update()


class Function(Value):
    """Represents a Function Value.  A Function is a Value which does not
    translate with the Binding.

    At a high level, a Function consists of:
        - A StaticLink
        - A name
        - Argument names
        - A body (or a summary of the body)
    """
    prefix = "function"
    moves_with_binding = False

    def __init__(self, canvas, x, y, name, arguments, defining_frame,
                 body="..."):
        Draggable.__init__(self, canvas)
        self.shape = canvas.create_polygon(x, y, x+140, y, x+140, y+30,
                x+150, y+30, x+150, y+60, x+10, y+60, x+10, y+30, x, y+30,
                tag=self.tag, fill="white", outline="white")
        canvas.create_line(x, y, x+140, y, x+140, y+30, x+150, y+30,
                tag=self.tag)
        canvas.create_line(x, y+30, x+10, y+30, x+10, y+60, x+150, y+60,
                tag=self.tag)
        canvas.create_oval(x+125, y-15, x+155, y+15, tag=self.tag, fill="white")
        canvas.create_oval(x+135, y-5, x+145, y+5, tag=self.tag, fill="black")
        self.name = canvas.create_text(x, y+5, tag=self.tag, anchor=tk.NW,
                                       text=name+"("+", ".join(arguments)+"):")
        self.body = canvas.create_text(x+15, y+35, tag=self.tag, anchor=tk.NW,
                                       text=body)
        self.static_link = StaticLink(canvas, self, defining_frame)
        self.update()

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.shape)[0:2])

    @property
    def inhandle(self):
        x, y = self.pos
        return (x, y+10), (x+150, y+50)

    @property
    def outhandle(self):
        x, y = self.pos
        return x+140, y
