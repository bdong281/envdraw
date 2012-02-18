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
        canvas.create_oval(x+135, y-15, x+165, y+15, tag=self.tag, fill="white")
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

    def __init__(self, canvas, x, y, name, arguments, body="..."):
        Connectable.__init__(self, canvas)
        self.top = canvas.create_line(x, y, x+140, y, x+140, y+30, x+150, y+30)
        canvas.create_line(x, y+30, x+10, y+30, x+10, y+60, x+150, y+60)
        canvas.create_oval(x+125, y-15, x+155, y+15, tag=self.tag, fill="white")
        canvas.create_oval(x+135, y-5, x+145, y+5, tag=self.tag, fill="black")
        self.name = canvas.create_text(x, y+5, anchor=tk.NW,
                                       text=name+"("+", ".join(arguments)+"):")
        self.body = canvas.create_text(x+15, y+35, anchor=tk.NW, text=body)


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
    Function(canvas, 100, 400, "adder", ("k", "a"), "return k + n")
    tk.mainloop()
