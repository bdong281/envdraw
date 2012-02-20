import tkinter as tk
import math

class Drawable(object):

    _next_id = 0

    def __init__(self, canvas):
        self.id = Drawable._next_id
        Drawable._next_id += 1
        self.canvas = canvas

    @property
    def tag(self):
        """Returns the tag used to group components of this Drawable."""
        return self.prefix + str(self.id)

    def heuristic(self, point, goal):
        distance = abs(point[0] - goal[0]) + abs(point[1] - goal[1])
        x, y = point
        covering = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        proximity = self.canvas.find_overlapping(x - 15, y - 15, x + 15, y +
                15)
        cost = len(covering) * 200 + len(proximity) * 150
        return distance + cost


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
        self.canvas.tag_bind(self.tag, '<ButtonRelease-1>',
                self.mouse_release)
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

    def mouse_release(self, event):
        coords = self.canvas.coords(self.tag)
        x, y = coords[0], coords[1]
        self.move(-(x % 10), -(y % 10))


# Connector
class Connector(Drawable):
    """Represents an arrow between two Connectables."""

    prefix = "connector"

    def __init__(self, canvas, head, tail):
        self.inhandle = None
        Drawable.__init__(self, canvas)
        self.head = head
        self.head.add_connector(self)
        self.tail = tail
        self.tail.add_connector(self)
        self.line = self.gen_coords(update=True)
        canvas.create_line(*self.line, tag=self.tag)
        self.arrow = Arrowhead(canvas, self)

    def update(self):
        """Redraws this Connector based on the new position of its head and
        tail.
        """
        self.canvas.coords(self.tag, *self.gen_coords(update=True))
        self.arrow.update()

    def closest_inhandle(self, update=False):
        if update:
            inhandle_to_number = {}
            for handle in self.head.inhandle:
                inhandle_to_number[handle] = 0
            for connector in self.head.connectors:
                if connector.inhandle in inhandle_to_number and connector.inhandle != self.inhandle:
                    inhandle_to_number[connector.inhandle] += 1
            self.inhandle = min(self.head.inhandle, key=lambda pt:
                    self.distance(self.tail.outhandle, pt) + 50 *
                    inhandle_to_number[pt])
        return self.inhandle

    def distance(self, point1, point2):
        (x1, y1), (x2, y2) = point1, point2
        return abs(x1 - x2) + abs(y1 - y2)

    def gen_coords(self, update=False):
        """Generates a sequence of coordinates for drawing an arrow"""
        (x1, y1), (x2, y2) = self.closest_inhandle(update=update), self.tail.outhandle
        return x1, y1, x2, y1, x2, y2


class Arrowhead(Drawable):

    points = ((0, 0), (-15, -5), (-10, 0), (-15, 5))

    def __init__(self, canvas, conn):
        Drawable.__init__(self, canvas)
        self.conn = conn
        x, y = self.pos
        angle = self.angle
        self.head = self.canvas.create_polygon(*self.gen_coords(x, y, angle))

    def update(self):
        x, y = self.pos
        angle = self.angle
        self.canvas.coords(self.head, *self.gen_coords(x, y, angle))

    @property
    def pos(self):
        x, y = self.conn.gen_coords()[0:2]
        return x, y

    @property
    def angle(self):
        x1, y1, x2, y2 = self.conn.gen_coords()[0:4]
        result = math.atan2(y1 - y2, x1 - x2)
        return result

    def gen_coords(self, x, y, angle):
        pts = []
        for pt_x, pt_y in Arrowhead.points:
            rot_x, rot_y = self._rotate(pt_x, pt_y, angle)
            pts.append(x + rot_x)
            pts.append(y + rot_y)
        return pts

    def _rotate(self, x, y, angle):
        c, s = math.cos(angle), math.sin(angle)
        new_x = x * c - y * s
        new_y = x * s + y * c
        return new_x, new_y


if __name__ == '__main__':
    master = tk.Tk()
    canvas = tk.Canvas(master, width=600, height=600)
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
