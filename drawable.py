import tkinter as tk
import math
from heapq import heappush, heappop
from functools import reduce

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
        self.update_connectors()



class Frame(Draggable):

    prefix = "frame"

    def __init__(self, canvas, x, y, globe=False):
        Draggable.__init__(self, canvas)
        self.variables = []
        self.values = []
        self.rect = canvas.create_rectangle(x, y, x + self.width, y +
                self.height, tag=self.tag, fill="white")
        canvas.create_oval(x+135, y-15, x+165, y+15, tag=self.tag,
                fill="white")
        if globe:
            pass
        else:
            canvas.create_oval(x+145, y-5, x+155, y+5, tag=self.tag,
                    fill="black")

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

    def mouse_release(self, event):
        Draggable.mouse_release(self, event)
        for variable in self.variables:
            variable.update_connectors()
        for value in self.values:
            value.update_connectors()

    def update(self):
        x, y = self.pos
        self.canvas.coords(self.rect, x, y, x + self.width, y + self.height)

    @property
    def inhandle(self):
        x, y = self.pos
        print("INHANDLE frame: {0}".format((x + self.width, y + self.height), (x,
            y + self.height)))
        return (x + self.width, y + self.height - 20), (x, y + self.height -
                20)

    @property
    def outhandle(self):
        x, y = self.pos
        print("OUTHANDLE frame: {0}".format((x + self.width, y )))
        return x + self.width, y


    @property
    def width(self):
        return 150

    @property
    def height(self):
        return 40 + 20 * len(self.variables)


class Function(Draggable):

    prefix = "function"

    def __init__(self, canvas, x, y, name, arguments, body="..."):
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

    @property
    def pos(self):
        return tuple(self.canvas.coords(self.shape)[0:2])

    @property
    def inhandle(self):
        print("INHANDLE function: {0}".format((self.pos,)))
        return (self.pos,)

    @property
    def outhandle(self):
        x, y = self.pos
        return x+140, y


class Variable(Connectable):

    prefix = "variable"

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = frame.add_variable(self)
        self.text = canvas.create_text(x, y, anchor=tk.NW, text=name+":",
                tag=self.tag)

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)

    @property
    def pos(self):
        print(tuple(self.canvas.coords(self.text)[0:2]))
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
        print("OUTHANDLE var: {0}".format((x + self.width, y +
            self.height)))
        return round(x + self.width, -1), round(y + self.height // 2, -1)


class Value(Connectable):

    prefix = "value"

    def __init__(self, canvas, frame, name):
        Connectable.__init__(self, canvas)
        x, y = frame.add_value(self)
        self.text = canvas.create_text(x, y, anchor=tk.NE, text=name,
                                       tag=self.tag)

    def move(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)
#        self.update_connectors()

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
        self.line = self.gen_coords(update=True)
        canvas.create_line(*self.line, tag=self.tag)
        self.arrow = Arrowhead(canvas, self)

    def update(self):
        """
        Redraws this Connector based on the new position of its head and tail.
        """
        self.canvas.coords(self.tag, *self.gen_coords(update=True))
        self.arrow.update()

    def closest_inhandle(self):
        return min(self.head.inhandle, key=lambda pt: \
                self.distance(self.tail.outhandle, pt))

    def distance(self, point1, point2):
        (x1, y1), (x2, y2) = point1, point2
        return abs(x1 - x2) + abs(y1 - y2)

    def gen_coords(self, update=False):
        """
        Generates a sequence of coordinates for drawing an arrow
        """
        if update:
            start, goal = self.tail.outhandle, self.closest_inhandle()
            closed, fringe = set(), []
            initial = (start, [start])
            heappush(fringe, (0, initial))

            while fringe:
                cost, (state, path) = heappop(fringe)
                print(cost)
                if state == goal:
                    if len(path) == 1:
                        path = path + path
                    self.line = reduce(lambda x, y: x + y, path, ())
                    return self.line

                if state not in closed:
                    closed.add(state)
                    for direction in [(10, 0), (-10, 0), (0, 10), (0, -10)]:
                        point = (state[0] + direction[0], state[1] + direction[1])
                        new_cost = cost + self.heuristic(point, goal)
                        if len(path) > 1:
                            (x1, y1), (x2, y2) = path[0], path[1]
                            if point[0] == x1 == x2 or point[1] == y1 == y2:
                                new_path = [point] + path[1:]
                            else:
                                new_path = [point] + path
                                prev_point = new_path[1]
                                if point[1] == prev_point[1]:
                                    dist = point[0] - prev_point[0]
                                else:
                                    dist = point[1] - prev_point[1]
                                if dist < 2:
                                    new_cost += 100
                                new_cost += 50
                        else:
                            new_path = [point] + path
                        heappush(fringe, (new_cost, (point, new_path)))
            return None
        else:
            return self.line


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
