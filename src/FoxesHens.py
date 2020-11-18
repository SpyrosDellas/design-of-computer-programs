import random
from functools import update_wrapper
from collections import namedtuple
from collections.abc import Iterable


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
    """Decorator that caches the return value for each call to function(*args)."""
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

    cache = {}
    return _function


def foxes_and_hens(strategy: callable, foxes=7, hens=45) -> int:
    """Play the game of foxes and hens.

    Foxes and Hens is a one-player game played with a deck of cards in which each card is labelled
    as a hen 'H', or a fox 'F'.

    A player will flip over a random card. If that card is a hen, it is added to the yard.
    If it is a fox, all of the hens currently in the yard are removed.

    Before drawing a card, the player has the choice of two actions, 'gather' or 'wait'.
    - If the player gathers, she collects all the hens in the yard and adds them to her score; the
      drawn card is discarded
    - If the player waits, she sees the next card
    """
    # A state is a tuple of (score-so-far, number-of-hens-in-yard, deck-of-cards)
    State = namedtuple('State', ['score', 'yard', 'cards'])
    state = State(0, 0, 'F' * foxes + 'H' * hens)
    while state.cards:
        action = strategy(state)
        state = do(action, state)
    return state.score + state.yard


def do(action: str, state: namedtuple, card=None) -> namedtuple:
    """Apply action to state, returning a new state.

    action is either 'gather' or 'wait'
    state is a tuple of (score, yard, cards)
    if card is None then a random card is picked from the deck, otherwise the specified card is selected
    """
    if card is None:
        index = random.randint(0, len(state.cards) - 1)
        card = state.cards[index]
    if card == 'F':
        cards = state.cards[1:]
    else:
        cards = state.cards[: len(state.cards) - 1]
    if action == 'gather':
        return state._replace(score=state.score + state.yard, yard=0, cards=cards)
    elif card == 'F':
        return state._replace(yard=0, cards=cards)
    else:
        return state._replace(yard=state.yard + 1, cards=cards)


def take5(state: namedtuple) -> str:
    """A strategy that waits until there are 5 hens in yard, then gathers."""
    if state.yard < 5:
        return 'wait'
    else:
        return 'gather'


def take3(state: namedtuple) -> str:
    """An improved strategy that waits until there are 3 hens in yard, then gathers.

    It also counts the number of foxes in the deck of cards. If no foxes, then it always waits.
    """
    if 'F' not in state.cards:
        return 'wait'
    if state.yard < 3:
        return 'wait'
    else:
        return 'gather'


def average_score(strategy: callable, trials=5000) -> float:
    average = sum(foxes_and_hens(strategy) for _ in range(trials)) / float(trials)
    print("Average score of strategy '%s' over %d trials: %f" % (strategy.__name__, trials, average))
    return average


def superior(first_strategy: callable, second_strategy: callable) -> bool:
    """Does the first strategy have a higher average score than the second one."""
    return average_score(first_strategy) - average_score(second_strategy) > 0


def optimal_strategy(state: namedtuple) -> str:
    def _expected_utility_of_action(action):
        return expected_utility_of_action(action, state)

    return max(actions(state), key=_expected_utility_of_action)


def actions(state: namedtuple) -> list:
    if state.yard == 0:
        return ['wait']
    else:
        return ['wait', 'gather']


def expected_utility_of_action(action: str, state: namedtuple) -> float:
    foxes = state.cards.count('F')
    hens = len(state.cards) - foxes
    return (foxes * expected_utility(do(action, state, 'F'))
            + hens * expected_utility(do(action, state, 'H'))) / len(state.cards)


@memo
def expected_utility(state: namedtuple) -> float:
    if not state.cards:
        return state.score + state.yard
    return max(expected_utility_of_action(action, state) for action in actions(state))


def test(first_strategy: callable, second_strategy: callable) -> str:
    assert superior(first_strategy, second_strategy)
    return 'tests pass'


print(test(optimal_strategy, take5))
print(test(optimal_strategy, take3))



