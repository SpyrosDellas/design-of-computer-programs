import random
from functools import update_wrapper


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

    return _function


def fair_die_rolls():
    """Iterator that generates random die rolls."""
    while True:
        yield random.randint(1, 6)


def play_pig_d(A, B, dierolls=fair_die_rolls()):
    """Play a game of pig between two players, represented by their strategies.

    Each time through the main loop we ask the current player for one decision,
    which must be 'hold' or 'roll', and we update the state accordingly.
    When one player's score exceeds the goal, return that player.

    At any point in the game, a player (let's say player A) can offer to 'double' the game.
    Player B then has to decide to 'accept', in which case the game is played through as normal,
    but it is now worth two points, or 'decline,' in which case player B immediately loses and
    player A wins one point.
    """
    strategies = [A, B]
    state = (0, 0, 0, 0, 1)
    other = {1: 0, 0: 1}
    while True:
        (p, me, you, pending, double) = state
        if me >= goal:
            return strategies[p], double
        elif you >= goal:
            return strategies[other[p]], double
        else:
            action = strategies[p](state)
            state = do(action, state, dierolls)


def do(action, state, dierolls):
    """Return the state that results from doing action in state.

    If action is not legal, return a state where the opponent wins.
    Can use dierolls if needed.
    """
    (p, me, you, pending, double) = state
    other = {1: 0, 0: 1}
    if action not in pig_actions_d(state):
        return (other[p], goal, 0, 0, double)
    elif action == 'roll':
        d = next(dierolls)
        if d == 1:
            return (other[p], you, me + 1, 0, double)  # pig out; other player's turn
        else:
            return (p, me, you, pending + d, double)  # accumulate die in pending
    elif action == 'hold':
        return (other[p], you, me + pending, 0, double)
    elif action == 'double':
        return (other[p], you, me, pending, 'double')
    elif action == 'decline':
        return (other[p], goal, 0, 0, 1)
    elif action == 'accept':
        return (other[p], you, me, pending, 2)


def pig_actions_d(state):
    """Take a state (p, me, you, pending, double), as input and return all legal actions.

    double can be either: 1, 2 or 'double'
    - 1 or 2 denote the value of the game
    - 'double' is reserved for the moment at which one player has doubled and is waiting
    for the other to accept or decline

    An action is one of ["roll", "hold", "accept", decline", "double"]
    - If double is "double", can only "accept" or "decline"
    - If double is 1, can "double" (in addition to other moves). If double > 1, cannot "double"
    - Can't "hold" if pending is 0
    """
    (p, me, you, pending, double) = state
    if double == 'double':
        return ['accept', 'decline']
    actions = ['roll']
    if double == 1:
        actions.append('double')
    if pending > 0:
        actions.append('hold')
    return actions


def strategy_compare(first_strategy, second_strategy, trials=1000):
    """Takes two strategies, A and B, as input and returns the percentage of points won by strategy A."""
    first_points, second_points = 0, 0
    for i in range(trials):
        if i % 2 == 0:  # take turns with who goes first
            winner, points = play_pig_d(first_strategy, second_strategy)
        else:
            winner, points = play_pig_d(second_strategy, first_strategy)
        if winner.__name__ == first_strategy.__name__:
            first_points += points
        else:
            second_points += points
    percent = 100 * first_points / float(first_points + second_points)
    print('For goal = %d and number of trials = %d, strategy %s took %s percent of the points against %s.' %
          (goal, trials, first_strategy.__name__, percent, second_strategy.__name__))
    return percent


def clueless_d(state):
    """A strategy that ignores the state and chooses at random from possible moves."""
    return random.choice(pig_actions_d(state))


def hold_20_d(state):
    """A strategy that holds at 20 pending. Always accept; never double."""
    (p, me, you, pending, double) = state
    return ('accept' if double == 'double' else
            'hold' if (pending >= 20 or me + pending >= goal) else
            'roll')


def strategy_d(state):
    """The optimal pig strategy; chooses the action with the highest expectation of points to win."""
    return best_action(state, pig_actions_d, pig_action_utility, pig_utility)


def best_action(state, actions, action_utility, utility):
    """Return the optimal action for a given state.

     - actions is a function that returns the legal actions from the given state
     - action_utility is a function that returns the expected utility (value) of the next state for the
       optimal player. The next state depends on the specified action
     - utility is a function that returns the expected utility (value) of a state for the optimal player
     """
    def expected_utility(action):
        return action_utility(state, action, utility)

    return max(actions(state), key=expected_utility)


def pig_action_utility(state, action, utility):
    """The expected value of choosing action in state.Assumes opponent also plays with optimal strategy.

    An action is one of ["roll", "hold", "accept", decline", "double"]
    """
    if action == 'roll':
        one = iter([1])
        rest = iter([2, 3, 4, 5, 6])
        return (-utility(do(action, state, one)) + sum(utility(do(action, state, rest)) for _ in range(5))) / 6.0
    else:
        return -utility(do(action, state, fair_die_rolls()))


@memo
def pig_utility(state):
    """Return the expected utility (value) of the specified state for an optimal player."""
    (p, me, you, pending, double) = state
    if double == 'double':
        return max(pig_action_utility(state, action, pig_utility) for action in pig_actions_d(state))
    if me + pending >= goal:
        return double
    elif you >= goal:
        return -double
    else:
        return max(pig_action_utility(state, action, pig_utility) for action in pig_actions_d(state))


def test():
    assert set(pig_actions_d((0, 2, 3, 0, 1))) == {'roll', 'double'}
    assert set(pig_actions_d((1, 20, 30, 5, 2))) == {'hold', 'roll'}
    assert set(pig_actions_d((0, 5, 5, 5, 1))) == {'roll', 'hold', 'double'}
    assert set(pig_actions_d((1, 10, 15, 6, 'double'))) == {'accept', 'decline'}
    assert strategy_compare(strategy_d, hold_20_d, trials=10000) > 60  # must win 60% of the points
    return 'test passes'


# goal = 40
# print(test())

for goal in range(35, 46):
    cache = {}
    strategy_compare(strategy_d, hold_20_d, trials=10000)