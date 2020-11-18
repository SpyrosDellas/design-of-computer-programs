from functools import update_wrapper


def decorator(decor):
    """Update the wrapper of decor(function), where decor is a decorator function.

    Returns a reference to the function object update_wrapper()
    """
    def _decor(function):
        return update_wrapper(decor(function), function)
    update_wrapper(_decor, decor)
    return _decor


def decorator_x(decor):
    """Update the wrapper of decor(function), where decor is a decorator function."""
    return update_wrapper(lambda function: update_wrapper(decor(function), function), decor)


@decorator_x
def n_ary(function):
    """Decorator that converts a binary function into n-ary function.

    Given function(x, y), return an n-ary function such that f(x, y, z) = f(x, f(y,z)), etc.
    Also allow f(x) = x.
    """
    def n_ary_function(x, *args):
        if not args:
            return x
        else:
            return function(x, n_ary_function(*args))
    return n_ary_function


@decorator
def memo(function):
    """Decorator that caches the return value for each call to function(*args)."""
    cache = {}
    def _function(*args):
        try:
            return cache[args]
        # not in cache
        except KeyError:
            cache[args] = function(*args)
            return cache[args]
        # args is not hashable
        except TypeError:
            return function(*args)
    return _function


@decorator
def countcalls(function):
    """Decorator that counts the calls to function."""
    def _function(*args):
        callcounts[_function] += 1
        return function(*args)
    callcounts[_function] = 0
    return _function


@decorator
def trace(function):
    """Decorators that prints a trace of the calls to function."""
    trace.level = 0
    indent = '    '
    def _function(*args):
        signature = "%s(%s)" % (function.__name__, ', '.join(map(repr, args)))
        print("%s--> %s" % (trace.level * indent, signature))
        trace.level += 1
        try:
            result = function(*args)
            print("%s<-- %s === %s" % ((trace.level - 1) * indent, signature, result))
        finally:
             trace.level -= 1
        return result
    return _function


def disabled(function):
    """Can be used to disable a decorator.

    Usage:
    decor = disabled, disables the decorator function 'decor'.
    """
    return function


callcounts = {}
@countcalls
@trace
@memo
def fibonacci(n):
    return 1 if n <= 1 else fibonacci(n - 1) + fibonacci(n - 2)


@n_ary
def add(a, b):
    """Add two numbers."""
    return a + b


def test():
    print(add(1), add(1, 1, 1))
    print("add() name = " + add.__name__ + ", docstring = " + add.__doc__)
    print("n_ary name = " + n_ary.__name__)
    print("n_ary(add) name = " + n_ary(add).__name__)
    print("decorator(n_ary) name = " + decorator(n_ary).__name__)
    print("decorator(n_ary)(add) name = " + decorator(n_ary)(add).__name__)
    n = 6
    print()
    print("\nfibonacci(%d) = %d, number of calls to fibonacci() = %d" %(n, fibonacci(n), callcounts[fibonacci]))


test()