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
        self.rect = canvas.create_rectangle(x, y, x+150, y+200, tag=self.tag)


class Function(Connectable):

    prefix = "function"


class Variable(Connectable):

    prefix = "variable"


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
    Frame(canvas, 100, 100)
    tk.mainloop()
