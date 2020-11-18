"""Collection of functions representing a regular expression generator API.

Each function takes a set of integers Ns as its sole argument, where the integers in Ns represent
the lengths of generated strings we are interested in. The generated strings are in the language defined
by the corresponding regular expression and their lengths are in Ns.
"""

# The empty set
null = frozenset([])


def lit(s):
    return lambda Ns: set([s]) if len(s) in Ns else null


def oneof(chars):
    return lambda Ns: set(chars) if 1 in Ns else null

# The empty string
epsilon = lit('')

# '$' represents any character. This is to avoid returning the full set of characters in the alphabet.
dot = oneof('$')


def opt(x):
    """Represents 'x?'."""
    return alt(epsilon, x)


def alt(x, y):
    """Represents 'x|y'."""
    return lambda Ns: x(Ns) | y(Ns)


def star(x):
    """Represents 'x*'. Defined recursively in terms of plus(x)."""
    return lambda Ns: opt(plus(x))(Ns)


def plus(x):
    """Represents 'x+'. Defined recursively in terms of genseq() and star(x)."""
    return lambda Ns: genseq(x, star(x), Ns, startx=1)


def seq(x, y):
    """Represents 'xy'."""
    return lambda Ns: genseq(x, y, Ns)


def genseq(x, y, Ns, startx=0):
    """Return the set of matches to 'xy' whose total length is in Ns.

    Note:
    plus(x) is defined recursively as genseq(x, star(x), Ns, startx=1) and star(x) in its turn
    is defined recursively in terms of the empty string and plus(x).
    Setting startx=1 when calling genseq() from plus(x) is necessary to avoid infinite recursion:
    it forces x to generate at least one character and then the recursive star(x)
    has one less character to match when called from within genseq().
    For example, suppose that genseq() is called initially with Ns={0, 1, 2}. Then star(x)
    will be called with Ns={0, 1} and will return the empty string plus a call to plus(x) with
    Ns={0, 1}.
    """
    if not Ns:
        return null
    xmatches = x(set(range(startx, max(Ns) + 1)))
    Ns_x = set(len(m) for m in xmatches)
    Ns_y = set(n - m for n in Ns for m in Ns_x if n - m >= 0) 
    ymatches = y(Ns_y)
    return set(m1 + m2 for m1 in xmatches for m2 in ymatches if len(m1) + len(m2) in Ns)


def test():
    f = lit('hello')
    assert f(set([1, 2, 3, 4, 5])) == set(['hello'])
    assert f(set([1, 2, 3, 4])) == null

    g = alt(lit('hi'), lit('bye'))
    assert g(set([1, 2, 3, 4, 5, 6])) == set(['bye', 'hi'])
    assert g(set([1, 3, 5])) == set(['bye'])

    h = oneof('theseletters')
    assert h(set([1, 2, 3])) == set(['t', 'h', 'e', 's', 'l', 'r'])
    assert h(set([2, 3, 4])) == null

    j = star(oneof('ab'))
    assert j(set([0, 1, 2])) == set(['', 'a', 'b', 'aa', 'bb', 'ab', 'ba'])

    k = plus(oneof('ab'))
    assert k(set([0, 1, 2])) == set(['a', 'b', 'aa', 'bb', 'ab', 'ba'])

    m = seq(plus(lit('a')), seq(plus(lit('b')), plus(lit('c'))))
    assert m(set([4])) == set(['aabc', 'abbc', 'abcc'])

    return 'tests pass'


print(test())