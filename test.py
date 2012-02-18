def foo():
    x = 5
    def bar(y):
        nonlocal x
        x = 6
        return y+1
    bar(x)
    return x

foo()
