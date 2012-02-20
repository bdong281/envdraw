def foo(x):
    def bar(y):
        return x + y
    return bar

gar = foo(3)

x1 = gar(1)
x2 = foo(4)(2)
