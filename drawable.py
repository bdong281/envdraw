class Drawable(object):

    @property
    def tag(self):
        """
        Returns the tag used to group components of this Drawable.
        """
        raise NotImplementedError


# Connectables

class Connectable(Drawable):

    @property
    def pos(self):
        raise NotImplementedError


class Frame(Connectable):
    pass


class Function(Connectable):
    pass


class Variable(Connectable):
    pass



# Connector

class Connector(Drawable):
    """
    Represents an arrow between two Connectables.
    """

    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def update(self):
        """
        Redraws this Connector based on the new position of its head and tail.
        """
        pass
