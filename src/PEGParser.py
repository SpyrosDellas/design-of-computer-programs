from functools import update_wrapper
import re


def decorator(decor):
    """Update the wrapper of decor(function), where decor is a decorator function.

    Returns a reference to the function object update_wrapper()
    """
    def _decor(function):
        return update_wrapper(decor(function), function)
    update_wrapper(_decor, decor)
    return _decor


@decorator
def memo(function):
    """Decorator that caches the return value for each call to function()."""
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


def grammar_from(description, whitespace=r'\s*'):
    """Convert a description to a grammar.

    Each line in the description is a rule for a non-terminal symbol; it looks like this:
        Symbol  => A1 A2 ... | B1 B2 ... | ...
    where the right hand side is one or more alternatives separated by the '|' sign.
    Each alternative is a sequence of atoms, separated by spaces.
    An atom is either a symbol on some left-hand side, or a regular expression that will be
    passed to re.match to match a token.
    The order of the alternatives defines their priority during parsing.

    Notes:
    A. Long lines can be continued using '\'
    B. *, + or ? are not allowed in a rule alternative; only allowed within a token
    C. '=>' and '|' must be surrounded by spaces
    D. The grammar allows whitespace between tokens by default. To change this behaviour, grammar()
    should be called as grammar(description, whitespace='') or grammar(description, whitespace=regex), where
    regex is a regular expression
    """
    grammar = {' ': whitespace}
    # replace tabs with whitespace
    description = description.replace('\t', ' ')
    for line in description.strip().split('\n'):
        lhs, rhs = map(str.strip, line.split(' => ', 1))
        alternatives = rhs.split(' | ')
        grammar[lhs] = tuple(map(str.split, alternatives))
    return grammar


def verify(grammar):
    """This is a debugging tool to help identify typos in the grammar."""
    lhstokens = set(grammar) - set([' '])
    rhstokens = set(term for alts in grammar.values() if alts != grammar[' '] for alt in alts for term in alt)

    def show(title, tokens):
        print(title, '=', '  '.join(sorted(tokens)))

    show('Non-terminals', grammar)
    show('Terminals', rhstokens.difference(lhstokens))
    show('Suspects', [t for t in rhstokens.difference(lhstokens) if t.isalnum()])
    show('Orphans', lhstokens.difference(rhstokens))


def parse(start_symbol, text, grammar):
    """A Deterministic Parsing Expression Grammar (PEG) parser.

    Returns a (tree, remainder) pair. If the remainder is the empty string'', the whole text was
    parsed successfully. If the remainder is None then parsing failed.

    Notes:
    1. Rule order (left-to-right) matters. The grammar rules should be in the form 'E => T op E | T',
    i.e. the longest parse should be first. 'E => T | T op E' won't parse the text correctly as the parser will
    always try to match the left alternative first. If if succeeds, then the right alternative won't be tried
    2. No direct left recursion is allowed: 'E => E op T' introduces infinite recursion
    3. No indirect left recursion is allowed: 'E => C op T' and 'C => E op V' introduces infinite recursion
    """
    fail = (None, None)
    tokenizer = grammar[' '] + '(%s)'

    def parse_sequence(sequence, text):
        result = []
        remainder = text
        for atom in sequence:
            tree, remainder = parse_atom(atom, remainder)
            if remainder is None:
                return fail
            result.append(tree)
        return result, remainder

    @memo
    def parse_atom(atom, text):
        # Non-terminal expression; tuple of alternatives
        if atom in grammar:
            for alternative in grammar[atom]:
                tree, remainder = parse_sequence(alternative, text)
                if remainder is not None:
                    return [atom] + tree, remainder
            return fail
        # Terminal expression; match characters against start of text
        else:
            m = re.match(tokenizer % atom, text)
            return fail if (not m) else (m.group(1), text[m.end():])

    return parse_atom(start_symbol, text)


parsing_expression_grammar = r"""
Exps    => Exp [,] Exps | Exp
Exp     => Term [+-] Exp | Term
Term    => Factor [*/] Term | Factor
Factor  => Funcall | Var | Num | [(] Exp [)]
Funcall => Var [(] Exps [)]
Var     => [a-zA-Z_]\w*
Num     => [+-]?[0-9]+([.][0-9]*)?
"""

grammar = grammar_from(parsing_expression_grammar)
# print(grammar)
print("VERIFY GRAMMAR:")
verify(grammar)
# print()
text = "a*b + func(d + 1)"
tree, remainder = parse('Exp', text, grammar)
print("\nText to parse = '%s'" % text)
print("Parsing Tree = ", tree)
print("Remainder = '%s'" % remainder)



