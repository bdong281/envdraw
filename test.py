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
    def doubler(x):
        return f(f(x))
    return doubler
fourth_power = double(square)
fourth_power(2)

"""
def square(x):
    return x*x

square(2)
"""
