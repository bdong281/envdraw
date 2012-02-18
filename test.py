"""
def foo():
    x = 5
    def bar(y):
        nonlocal x
        x = 6
        return y+1
    bar(x)
    return x

foo()
"""
def square(x):
    return x*x

def double(f):
    y = 1
    def doubler(x):
        nonlocal y
        y += 1
        return f(f(x))
    return doubler
fourth_power = double(square)
fourth_power(2)

"""
def square(x):
    return x*x

square(2)
"""
