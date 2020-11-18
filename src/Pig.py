import random
from functools import update_wrapper
import itertools


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


def play_tournament(strategies, games=50):
    length = len(strategies)
    wins = [[0] * length for _ in range(length)]
    indices = dict()
    for index, strategy in enumerate(strategies):
        indices[strategy] = index
    for player_1, player_2 in itertools.permutations(strategies, 2):
        for _ in range(games):
            winner = play_pig(player_1, player_2)
            if winner == player_1:
                loser = player_2
            else:
                loser = player_1
            wins[indices[winner]][indices[loser]] += 1
    print_stats(strategies, wins)


def print_stats(strategies, wins):
    for index, strategy in enumerate(strategies):
        total_wins = sum(wins[index])
        columns = ["{:4d}".format(wins[index][i]) for i in range(len(wins[index]))]
        row = " ".join(columns)
        print("{:<14s}: {:s}  -> total wins = {}".format(strategy.__name__, row, total_wins))


def fair_die_rolls():
    """Iterator that generates random die rolls."""
    while True:
        yield random.randint(1, 6)


def play_pig(strategy_1, strategy_2, die_rolls=fair_die_rolls()):
    """Play a game of pig between two players, represented by their strategies.

    Each time through the main loop we ask the current player for one decision,
    which must be 'hold' or 'roll', and we update the state accordingly.
    When one player's score exceeds the goal, return that player.

    States are represented as a tuple of (p, me, you, pending), where
    p:       an int, 0 or 1, indicating which player's turn it is.
    me:      an int, the player-to-move's current score
    you:     an int, the other player's current score.
    pending: an int, the number of points accumulated on current turn, not yet scored
    """
    state = (0, 0, 0, 0)
    strategies = (strategy_1, strategy_2)
    while not game_over(state):
        current_strategy = strategies[state[0]]
        move = current_strategy(state)
        if move == 'hold':
            state = hold(state)
        else:
            dice = next(die_rolls)
            state = roll(state, dice)
    return strategies[not state[0]]


def game_over(state):
    return state[1] >= goal or state[2] >= goal


def hold(state):
    """Apply the hold action to a state to yield a new state.

    Reap the 'pending' points and it becomes the other player's turn.
    """
    player, me, you, pending = state
    return (not player, you, me + pending, 0)


def roll(state, dice):
    """Apply the roll action to a state (and a die roll d) to yield a new state.

    If d is 1, get 1 point (losing any accumulated 'pending' points),
    and it is the other player's turn. If d > 1, add d to 'pending' points.
    """
    player, me, you, pending = state
    if dice == 1:
        return (not player, you, me + 1, 0)
    else:
        return (player, me, you, pending + dice)


def clueless(state):
    """A strategy that ignores the state and chooses at random from possible moves."""
    possible_moves = ['roll', 'hold']
    return random.choice(possible_moves)


def always_roll(state):
    """Always roll strategy."""
    return 'roll'


def always_hold(state):
    """Always hold strategy."""
    return 'hold'


def hold_at(x):
    """Return a strategy function that holds if and only if pending >= x or player reaches goal."""

    def strategy(state):
        strategy.__name__ = 'hold_at(%d)' % x
        _, me, _, pending = state
        return 'hold' if (pending >= x or me + pending >= goal) else 'roll'

    return strategy


def max_wins(state):
    """The optimal pig strategy; chooses an action with the highest win probability."""
    return best_action(state, pig_actions, Q_pig, Pwin)


def best_action(state, actions, Q, U):
    """Return the optimal action for a state, given U."""

    def EU(action):
        return Q(state, action, U)

    return max(actions(state), key=EU)


def pig_actions(state):
    """The legal actions from a state."""
    pending = state[3]
    return ['roll', 'hold'] if pending else ['roll']


def Q_pig(state, action, utility):
    """The expected value of choosing action in state.

    Assumes opponent also plays with optimal strategy.
    """
    if action == 'hold':
        return 1 - utility(hold(state))
    if action == 'roll':
        return (1 - utility(roll(state, 1)) + sum(utility(roll(state, d)) for d in (2, 3, 4, 5, 6))) / 6.0
    raise ValueError


@memo
def Pwin(state):
    """The probability that an optimal player whose turn is to move can win from the current state.
    """
    (p, me, you, pending) = state
    if me + pending >= goal:
        return 1
    elif you >= goal:
        return 0
    else:
        return max(Q_pig(state, action, Pwin) for action in pig_actions(state))


def Q_pig_2(state, action, utility):
    """The expected value of choosing action in state.

    Assumes opponent also plays with optimal strategy.
    """
    if action == 'hold':
        return -utility(hold(state))
    if action == 'roll':
        return (-utility(roll(state, 1)) + sum(utility(roll(state, d)) for d in (2, 3, 4, 5, 6))) / 6.0
    raise ValueError


def max_difference(state):
    """A strategy that maximizes the expected difference between my final score and my opponent's."""
    return best_action(state, pig_actions, Q_pig, win_diff)


def max_difference_2(state):
    """A strategy that maximizes the expected difference between my final score and my opponent's."""
    return best_action(state, pig_actions, Q_pig_2, win_diff_2)


@memo
def win_diff(state):
    """The utility of a state: here the winning differential (pos or neg)."""
    (p, me, you, pending) = state
    if me + pending >= goal or you >= goal:
        return me + pending - you
    else:
        return max(Q_pig(state, action, win_diff) for action in pig_actions(state))


@memo
def win_diff_2(state):
    """The utility of a state: here the winning differential (pos or neg)."""
    (p, me, you, pending) = state
    if me + pending >= goal or you >= goal:
        return me + pending - you
    else:
        return max(Q_pig_2(state, action, win_diff_2) for action in pig_actions(state))


def test1():
    for _ in range(10):
        winner = play_pig(always_hold, always_roll)
        assert winner.__name__ == 'always_roll'
    return 'tests pass'


def test2():
    A, B = hold_at(50), clueless
    rolls = iter([6] * 9)
    assert play_pig(A, B, rolls) == A
    return 'test passes'


def test3():
    assert (max_wins((1, 5, 34, 4))) == "roll"
    assert (max_wins((1, 18, 27, 8))) == "roll"
    assert (max_wins((0, 23, 8, 8))) == "roll"
    assert (max_wins((0, 31, 22, 9))) == "hold"
    assert (max_wins((1, 11, 13, 21))) == "roll"
    assert (max_wins((1, 33, 16, 6))) == "roll"
    assert (max_wins((1, 12, 17, 27))) == "roll"
    assert (max_wins((1, 9, 32, 5))) == "roll"
    assert (max_wins((0, 28, 27, 5))) == "roll"
    assert (max_wins((1, 7, 26, 34))) == "hold"
    assert (max_wins((1, 20, 29, 17))) == "roll"
    assert (max_wins((0, 34, 23, 7))) == "hold"
    assert (max_wins((0, 30, 23, 11))) == "hold"
    assert (max_wins((0, 22, 36, 6))) == "roll"
    assert (max_wins((0, 21, 38, 12))) == "roll"
    assert (max_wins((0, 1, 13, 21))) == "roll"
    assert (max_wins((0, 11, 25, 14))) == "roll"
    assert (max_wins((0, 22, 4, 7))) == "roll"
    assert (max_wins((1, 28, 3, 2))) == "roll"
    assert (max_wins((0, 11, 0, 24))) == "roll"
    return 'tests pass'

# The total score required for a player to win
goal = 40

# print(test1())
# print(test2())
# print(test3())

strategies = [clueless, hold_at(goal / 4), hold_at(1 + goal / 3),
              hold_at(goal / 2), hold_at(goal), max_wins, max_difference, max_difference_2]

play_tournament(strategies, games=2000)
