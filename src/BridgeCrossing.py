import itertools
import heapq
from collections.abc import Iterable


def bridge_problem(here: Iterable) -> list:
    # A state is a (here, there) tuple, where here and there are frozen sets of people
    # indicated by their crossing times) and/or the 'light'
    here = frozenset(here).union(['light'])
    there = frozenset()
    start_state = (here, there)
    # the path from the previous state to this state
    path_to = dict()
    path_to[start_state] = None
    # the action from the previous state to this state
    action_to = dict()
    action_to[start_state] = None
    # the shortest time to reach this state
    time_to = dict()
    time_to[start_state] = 0
    # min oriented priority queue of states to explore; priority is by time to reach each state
    frontier = []
    heapq.heappush(frontier, (time_to[start_state], start_state))
    solution = None
    while frontier:
        current_time, current_state = heapq.heappop(frontier)
        if solution and current_time >= time_to[solution]:
            return recover_path(solution, path_to, action_to, time_to)
        elif not current_state[0]:
            solution = current_state
        for (successor, action) in bsuccessors(current_state).items():
            successor_time = current_time + max(action[0:2])
            if (successor not in path_to) or (successor_time < time_to[successor]):
                path_to[successor] = current_state
                action_to[successor] = action
                time_to[successor] = successor_time
                heapq.heappush(frontier, (successor_time, successor))
    return []


def bsuccessors(state: tuple) -> dict:
    """Return a dictionary of {state:action} pairs.

    A state is a (here, there) tuple, where here and there are frozen sets of people
    indicated by their crossing times) and/or the 'light'.

    An action is represented as a tuple (person1, person2, arrow), where arrow is '->' for here to there
    and '<-' for there to here. When only one person crosses, person two will be the same as person one, so the
    action (2, 2, '->') means that the person with a travel time of 2 crossed from here to there alone.
    """
    here, there = state
    successors = dict()
    if 'light' in here:
        arrow = '->'
        reverse = False
    else:
        arrow = '<-'
        reverse = True
        here, there = there, here
    here = here.difference(['light'])
    there = there.union(['light'])
    for persons in itertools.product(here, repeat=2):
        next_here = here.difference(persons)
        next_there = there.union(persons)
        if not reverse:
            state = (next_here, next_there)
        else:
            state = (next_there, next_here)
        action = (persons[0], persons[1], arrow)
        successors[state] = action
    return successors


def recover_path(shortest_path: tuple, path_to: dict, action_to: dict, time_to: dict) -> list:
    """Recover and return the path from start to goal."""
    path = [time_to[shortest_path], shortest_path, action_to[shortest_path]]
    previous = path_to[shortest_path]
    while previous:
        path.append(previous)
        if action_to[previous]:
            path.append(action_to[previous])
        previous = path_to[previous]
    path.reverse()
    return path


def path_states(path):
    """Return a list of states in this path.

    A path is a list of the form [state, action, state, action, ... ]
    """
    return path[0: len(path) - 1: 2]


def path_actions(path):
    """Return a list of actions in this path.

    A path is a list of the form [state, action, state, action, ... ]
    """
    return path[1: len(path) - 1: 2]


def test_successors():
    assert bsuccessors((frozenset([1, 'light']), frozenset([]))) == {
        (frozenset([]), frozenset([1, 'light'])): (1, 1, '->')}

    assert bsuccessors((frozenset([]), frozenset([2, 'light']))) == {
        (frozenset([2, 'light']), frozenset([])): (2, 2, '<-')}

    return 'tests pass'


def test(here: Iterable):
    path = bridge_problem(here)
    states = path_states(path)
    actions = path_actions(path)
    print("Problem = %s" % here)
    print("Time to fastest solution =", path[-1])
    print("States to fastest solution:")
    print(*states, sep='\n')
    print("Actions to fastest solution:")
    print(*actions, sep='\n')


# print(test_successors())
here = [1, 2, 5, 10]
test(here)
here = [1, 1, 2, 3, 5, 8, 13, 21]
test(here)
here = [1, 1000]
test(here)
