def search(pattern, text):
    """Match pattern anywhere in text; return longest earliest match or None."""
    for i in range(len(text)):
        m = match(pattern, text[i:])
        if m is not None:
            return m


def match(pattern, text):
    """Match pattern against start of text; return longest match found or None."""
    remainders = matchset(pattern, text)
    if remainders:
        shortest = min(remainders, key=len)
        return text[: len(text) - len(shortest)]


def matchset(pattern, text):
    """Match pattern at start of text; return a set of remainders of text.

    For example, matchset(star(lit(a)), 'aaab'), returns a set with elements
    {'aaab', 'aab', 'ab', 'b'}, since a* can consume one, two or all three of the a's in the text.
    dot:   matches any character.
    oneof: matches any of the characters in the string it is
       called with. oneof('abc') will match a or b or c.
    """
    null = frozenset()  # assign null to empty set
    op, x, y = components(pattern)
    if 'lit' == op:
        return set([text[len(x):]]) if text.startswith(x) else null
    elif 'seq' == op:
        return set(t2 for t1 in matchset(x, text) for t2 in matchset(y, t1))
    elif 'alt' == op:
        return matchset(x, text) | matchset(y, text)
    elif 'dot' == op:
        return set([text[1:]]) if text else null
    elif 'oneof' == op:
        return set([text[1:]]) if text.startswith(x) else null
    elif 'eol' == op:
        return set(['']) if text == '' else null
    elif 'star' == op:
        return (set([text]) |
                set(t2 for t1 in matchset(x, text)
                    for t2 in matchset(pattern, t1) if t1 != text))
    else:
        raise ValueError('unknown pattern: %s' % pattern)


def components(pattern):
    """Return the op, x, and y arguments; x and y are None if missing."""
    x = pattern[1] if len(pattern) > 1 else None
    y = pattern[2] if len(pattern) > 2 else None
    return pattern[0], x, y


def lit(string):
    return 'lit', string


def seq(x, y):
    """seq(x, y) represents 'xy'."""
    return 'seq', x, y


def alt(x, y):
    """alt(x, y) represents 'x|y'."""
    return 'alt', x, y


def star(x):
    """star(x) represents 'x*'."""
    return 'star', x


def plus(x):
    """plus(x) represents 'x+'."""
    return 'seq', x, star(x)


def opt(x):
    """opt(x) represents 'x?', i.e. zero or one matches with x"""
    return alt(lit(''), x)


def oneof(chars):
    """oneof(chars) represents 'a1|a2|a3|...|an', i.e match with any character in chars."""
    return 'oneof', tuple(chars)


# Represents '.'
dot = ('dot',)

# Represents end of line
eol = ('eol',)


def test_matchset():
    assert matchset(('lit', 'abc'), 'abcdef') == set(['def'])
    assert matchset(('seq', ('lit', 'hi '),
                     ('lit', 'there ')),
                    'hi there nice to meet you') == set(['nice to meet you'])
    assert matchset(('alt', ('lit', 'dog'),
                     ('lit', 'cat')), 'dog and cat') == set([' and cat'])
    assert matchset(('dot',), 'am i missing something?') == set(['m i missing something?'])
    assert matchset(('oneof', 'a'), 'aabc123') == set(['abc123'])
    assert matchset(('eol',), '') == set([''])
    assert matchset(('eol',), 'not end of line') == frozenset([])
    assert matchset(('star', ('lit', 'hey')), 'heyhey!') == set(['!', 'heyhey!', 'hey!'])
    return 'matchset() tests pass'


def test_API():
    assert lit('abc') == ('lit', 'abc')
    assert seq(('lit', 'a'), ('lit', 'b')) == ('seq', ('lit', 'a'), ('lit', 'b'))
    assert alt(('lit', 'a'), ('lit', 'b')) == ('alt', ('lit', 'a'), ('lit', 'b'))
    assert star(('lit', 'a')) == ('star', ('lit', 'a'))
    assert plus(('lit', 'c')) == ('seq', ('lit', 'c'), ('star', ('lit', 'c')))
    assert opt(('lit', 'x')) == ('alt', ('lit', ''), ('lit', 'x'))
    assert oneof('abc') == ('oneof', ('a', 'b', 'c'))
    return 'API tests pass'


def test_search():
    assert match(('star', ('lit', 'a')),'aaabcd') == 'aaa'
    assert match(('alt', ('lit', 'b'), ('lit', 'c')), 'ab') == None
    assert match(('alt', ('lit', 'b'), ('lit', 'a')), 'ab') == 'a'
    assert search(('alt', ('lit', 'b'), ('lit', 'c')), 'ab') == 'b'
    return 'match() and search() tests pass'


print(test_matchset())
print(test_API())
print(test_search())
