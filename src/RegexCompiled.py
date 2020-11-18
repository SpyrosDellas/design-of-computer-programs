# --------------
# User Instructions
#
# Fill out the function match(pattern, text), so that
# remainders is properly assigned.

null = frozenset([])

def search(pattern, text):
    """Match pattern anywhere in text; return longest earliest match or None."""
    for i in range(len(text)):
        m = match(pattern, text[i:])
        if m is not None:
            return m


def match(pattern, text):
    """Match pattern against start of text; return longest match found or None."""
    remainders = pattern(text)
    if remainders:
        shortest = min(remainders, key=len)
        return text[: len(text) - len(shortest)]


def lit(s):
    return lambda text: set([text[len(s):]]) if text.startswith(s) else null


def seq(x, y):
    return lambda text: set().union(*map(y, x(text)))


def alt(x, y):
    return lambda text: x(text).union(y(text))


def oneof(chars):
    return lambda text: set([text[1:]]) if (text and text[0] in chars) else null


dot = lambda text: set([text[1:]]) if text else null

eol = lambda text: set(['']) if text == '' else null


def star(x):
    return lambda text: (set([text]) | set(t2 for t1 in x(text) if t1 != text for t2 in star(x)(t1)))


def test():
    assert match(star(lit('a')), 'aaaaabbbaa') == 'aaaaa'
    assert match(lit('hello'), 'hello how are you?') == 'hello'
    assert match(lit('x'), 'hello how are you?') == None
    assert match(oneof('xyz'), 'x**2 + y**2 = r**2') == 'x'
    assert match(oneof('xyz'), '   x is here!') == None
    assert search(seq(seq(seq(lit('S'), dot), dot), lit('ros')), "Dellas Spyros...") == 'Spyros'
    return 'tests pass'


print(test())