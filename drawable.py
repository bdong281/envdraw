import tkinter as tk

class Drawable(object):

    _next_id = 0

    def __init__(self, canvas):
        self.id = Drawable._next_id
        Drawable._next_id += 1
        self.canvas = canvas

    @property
    def tag(self):
        """
        Returns the tag used to group components of this Drawable.
        """
        return self.prefix + str(self.id)


# Connectables

class Connectable(Drawable):

    def __init__(self, canvas):
        Drawable.__init__(self, canvas)
        self.connectors = []

    @property
    def pos(self):
        raise NotImplementedError

    def add_connector(self, connector):
        self.connectors.append(connector)

    def update_connectors(self):
        for connector in self.connectors:
            connector.update()


class Draggable(Connectable):

    def __init__(self, canvas):
        Connectable.__init__(self, canvas)
        self.canvas.tag_bind(self.tag, '<Button-1>', self.mouse_start)
        self.canvas.tag_bind(self.tag, '<B1-Motion>', self.mouse_drag)
        self._drag_x, self._drag_y= None, None

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
        self.update_connectors()

    def mouse_start(self, event):
        self._drag_x, self._drag_y = event.x, event.y

    def mouse_drag(self, event):
        dx, dy = event.x - self._drag_x, event.y - self._drag_y
        self._drag_x, self._drag_y = event.x, event.y
        self.move(dx, dy)


class Frame(Draggable):

    prefix = "frame"

    def __init__(self, canvas, x, y, globe=False):
        Draggable.__init__(self, canvas)
        self.variables = []
        self.values = []
        self.rect = canvas.create_rectangle(x, y, x+150, y+35, tag=self.tag,
                                            fill="white")
        canvas.create_oval(x+135, y-15, x+165, y+15, tag=self.tag, fill="white")
        if globe:
            pass
        else:
            canvas.create_oval(x+145, y-5, x+155, y+5,
                               tag=self.tag, fill="black")

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.rect)[0:2])

    def add_variable(self, variable):
        """
        Adds a Variable to this Frame. Returns the position that the Variable
        should be drawn at.

        TODO: Automatically grow frame when too many variables are defined.
        """
        self.variables.append(variable)
        self.update()
        x, y = self.pos
        return x + 10, y + len(self.variables) * 20

    def add_value(self, value):
        self.values.append(value)
        x, y = self.pos
        return x + 140, y + len(self.values) * 20

    def move(self, dx, dy):
        Draggable.move(self, dx, dy)
        for variable in self.variables:
            variable.move(dx, dy)
        for value in self.values:
            value.move(dx, dy)

    def update(self):
        x, y = self.pos
        self.canvas.coords(self.rect, x, y, x+150, y+35+20*len(self.variables))

    @property
    def inhandle(self):
        x, y = self.pos
        return x + 150, y + 35 + 20 * len(self.variables)

    @property
    def outhandle(self):
        x, y = self.pos
        return x + 150, y


class Function(Draggable):

    prefix = "function"

    def __init__(self, canvas, x, y, name, arguments, body="..."):
        Draggable.__init__(self, canvas)
        self.shape = canvas.create_polygon(x, y, x+140, y, x+140, y+30, x+150,
                                           y+30, x+150, y+60, x+10, y+60, x+10,
                                           y+30, x, y+30, tag=self.tag,
                                           fill="white", outline="white")
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

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.shape)[0:2])

    @property
    def inhandle(self):
        return self.pos


class Variable(Connectable):

    prefix = "variable"

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = frame.add_variable(self)
        self.text = canvas.create_text(x, y, anchor=tk.NW, text=name+":",
                                       tag=self.tag)

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
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
    def outhandle(self):
        x, y = self.pos
        return x + self.width, y + self.height // 2


class Value(Connectable):

    prefix = "value"

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = frame.add_value(self)
        self.text = canvas.create_text(x, y, anchor=tk.NE, text=name,
                                       tag=self.tag)

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
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
        return x - self.width, y + self.height // 2


# Connector

class Connector(Drawable):
    """
    Represents an arrow between two Connectables.
    """

    prefix = "connector"

    def __init__(self, canvas, head, tail):
        Drawable.__init__(self, canvas)
        self.head = head
        self.head.add_connector(self)
        self.tail = tail
        self.tail.add_connector(self)
        self.line = canvas.create_line(*(head.inhandle + tail.outhandle),
                                        tag=self.tag)

    def update(self):
        """
        Redraws this Connector based on the new position of its head and tail.
        """
        self.canvas.coords(self.tag,
                           *(self.head.inhandle + self.tail.outhandle))

if __name__ == '__main__':
    master = tk.Tk()
    canvas = tk.Canvas(master)
    canvas.pack(fill=tk.BOTH, expand=1)
    f = Frame(canvas, 100, 100, globe=True)
    foo = Variable(canvas, f, "foo")
    bar = Variable(canvas, f, "bar")
    Variable(canvas, f, "baz")
    v = Value(canvas, f, "hello")
    Value(canvas, f, "there")
    f1 = Frame(canvas, 350, 150)
    func = Function(canvas, 100, 400, "adder", ("k", "a"), "return k + n")
    Connector(canvas, func, foo)
    Connector(canvas, f, f1)
    Connector(canvas, v, bar)
    tk.mainloop()
