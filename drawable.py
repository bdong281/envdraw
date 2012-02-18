
class Drawable(object):
    pass


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

    def __init__(self, head, tail):
        pass
