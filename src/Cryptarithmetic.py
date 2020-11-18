# Write a function, solve(formula) that solves cryptarithmetic puzzles.
# The input should be a formula like 'ODD + ODD == EVEN', and the
# output should be a string with the digits filled in, or None if the
# problem is not solvable.

import cProfile
import itertools
import re
import string
import time
import typing


def solve(formula):
    """Given a formula like 'ODD + ODD == EVEN', fill in digits to solve it.

    Input formula is a string; output is a digit-filled-in string or None.
    """
    # all unique uppercase letters are considered as arguments to a
    # boolean lambda function that represents the compiled formula
    arguments = list(set(letter for letter in formula if letter.isupper()))
    lambda_function = create_lambda(arguments, formula)
    for args in itertools.permutations(range(10), len(arguments)):
        try:
            if lambda_function(*args) is True:
                table = str.maketrans("".join(arguments), "".join(map(str, args)))
                return formula.translate(table)
        except ArithmeticError:
            pass
    return None


def create_lambda(arguments: list, formula: string) -> typing.Callable[..., bool]:
    """Compile formula into a lambda function.

    The first digit of a multi-digit number can't be 0. So if YOU is a word in the formula, and the function
    is called with Y equal to 0, the lambda function should return False.
    """
    words = re.split("([A-Z]+)", formula)
    parsed_formula = "(" + "".join(map(parse_word, words)) + ")"
    first_letters = set(word[0] for word in words if word.isupper() and len(word) > 1)
    if len(first_letters) > 0:
        first_letters_check = " and " + "*".join(first_letters) + " != 0"
    else:
        first_letters_check = ""
    expression = "lambda " + ", ".join(arguments) + ": " + parsed_formula + first_letters_check
    print(expression)
    return eval(expression)


def parse_word(word: str) -> str:
    """Compile a word of uppercase letters as numeric digits. Non-uppercase letter words are returned unchanged."""
    if not word.isupper():
        return word
    compiled_word = " + ".join([letter + "*" + str(10**index) for index, letter in enumerate(word[:: -1])])
    return "(" + compiled_word + ")"


def test():
    examples = ["TWO + TWO == FOUR",
                "RAMN == R**3 + RM**3 == N**3 + RX**3",
                "A**2 + B**2 == C**2",
                "GLITTERS != GOLD",
                "ONE < TWO < THREE",
                "ONE < TWO and FOUR < FIVE",
                "sum(range(POP)) == BOBO",
                "SPYROS + EROS + OLGA == 425731"]

    for formula in examples:
        print("\n" + 13 * " " + formula)
        start = time.time_ns()
        result = solve(formula)
        end = time.time_ns()
        print("%6.4f sec:  %s" % ((end - start) / 1e9, result))


def func(O, R, T, F, U, W):
    return (O * 1 + W * 10 + T * 100) + (O * 1 + W * 10 + T * 100) == (R * 1 + U * 10 + O * 100 + F * 1000)


if __name__ == "__main__":
    cProfile.run("test()", sort="cumulative")
