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

    def update_connectors(self):
        for connector in self.connectors:
            connector.update()


class Frame(Connectable):

    prefix = "frame"

    def __init__(self, canvas, x, y):
        Connectable.__init__(self, canvas)
        self.variables = []
        self.rect = canvas.create_rectangle(x, y, x+150, y+200, tag=self.tag,
                                            fill="white")
        canvas.create_oval(x+130, y-20, x+170, y+20, tag=self.tag, fill="white")
        canvas.create_oval(x+145, y-5, x+155, y+5, tag=self.tag, fill="black")

    @property
    def pos(self):
        return self.canvas.coords(self.rect)[0:2]

    def add_variable(self, variable):
        """
        Adds a Variable to this Frame. Returns the position that the Variable
        should be drawn at.

        TODO: Automatically grow frame when too many variables are defined.
        """
        self.variables.append(variable)
        x, y = self.pos
        return x + 10, y + len(self.variables) * 20

class Function(Connectable):

    prefix = "function"

    def __init__(self, canvas, x, y):
        Connectable.__init__(self, canvas)
        self.top = canvas.create_line(x, y, x+150, y, x+150, y+30, x+160, y+30)
        canvas.create_line(x, y+20, x+10, y+20, x+10, y+50, x+160, y+50)


class Variable(Connectable):

    prefix = "variable"

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = frame.add_variable(self)
        self.text = canvas.create_text(x, y, anchor=tk.NW, text=name+":")

    @property
    def pos(self):
        return self.canvas.coords(self.text)[0:2]

    @property
    def width(self):
        x1, _, x2, _ = self.canvas.bbox(self.text)
        return x2 - x1

    @property
    def height(self):
        _, y1, _, y2 = self.canvas.bbox(self.text)
        return y2 - y1

    @property
    def handleout(self):
        x, y = self.pos
        return x + self.width, y + self.height // 2
        

# Connector

class Connector(Drawable):
    """
    Represents an arrow between two Connectables.
    """

    prefix = "connector"

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def update(self):
        """
        Redraws this Connector based on the new position of its head and tail.
        """
        pass

if __name__ == '__main__':
    master = tk.Tk()
    canvas = tk.Canvas(master)
    canvas.pack(fill=tk.BOTH, expand=1)
    f = Frame(canvas, 100, 100)
    Variable(canvas, f, "foo")
    Variable(canvas, f, "bar")
    Function(canvas, 100, 400)
    tk.mainloop()
