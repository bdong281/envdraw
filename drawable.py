class Drawable(object):

    _next_id = 0

    def __init__(self):
        self.id = Drawable._next_id
        Drawable._next_id += 1

    @property
    def tag(self):
        """
        Returns the tag used to group components of this Drawable.
        """
        return self.prefix + str(self.id)


# Connectables

class Connectable(Drawable):

    @property
    def pos(self):
        raise NotImplementedError


class Frame(Connectable):

    prefix = "frame"


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
