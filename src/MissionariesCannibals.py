import heapq


def mc_problem(start=(3, 3, 1, 0, 0, 0), goal=None):
    """Solve the missionaries and cannibals problem.

    A state is a tuple with six entries: (M1, C1, B1, M2, C2, B2), where
    M1 and C1 are the numbers of missionaries and cannibals in the left side of the river
    M2 and C2 are the numbers of missionaries and cannibals in the right sideof the river
    B1 == 1 and B2 == 0 if the boat is in the left side of the river
    B1 == 0 and B2 == 1 if the boat is in the right side of the river

    If the goal is not specified, it defaults to no people or boats in the left side

    Returns the solution with the least number of river crossings.
    """
    if not goal:
        M1, C1, B1, M2, C2, B2 = start
        goal = (0, 0, 0, M1, C1, B1)
    # the path from the previous state to this state
    path_to = dict()
    path_to[start] = None
    # the action from the previous state to this state
    action_to = dict()
    action_to[start] = None
    # min oriented priority queue of states to explore; priority is by time to reach each state
    frontier = []
    heapq.heappush(frontier, (0, start))
    while frontier:
        current_cost, current_state = heapq.heappop(frontier)
        if current_state == goal:
            return recover_path(current_state, path_to, action_to)
        for (successor, action) in csuccessors(current_state).items():
            if successor not in path_to:
                path_to[successor] = current_state
                action_to[successor] = action
                heapq.heappush(frontier, (current_cost + 1, successor))
    return []


def csuccessors(state: tuple) -> dict:
    """Take a state (as defined below) as input and return a dictionary of {state:action} pairs.

    An action is one of the following ten strings:
    'MM->', 'MC->', 'CC->', 'M->', 'C->', '<-MM', '<-MC', '<-M', '<-C', '<-CC',
    where 'MM->' means two missionaries travel to the right side.

    Generates successor states (including those that result in dining) to this
    state. But a state where the cannibals can dine (i.e. C > M) has no successors.
    """
    M1, C1, B1, M2, C2, B2 = state
    if (M1 < C1 and B1 == 0) or (M2 < C2 and B2 == 0):
        return dict()
    if B1:
        return right_successors(state)
    else:
        return left_successors(state)


def right_successors(state: tuple) -> dict:
    M1, C1, B1, M2, C2, B2 = state
    successors = dict()
    if M1 > 0:
        successors[(M1 - 1, C1, 0, M2 + 1, C2, 1)] = 'M->'
    if M1 > 1:
        successors[(M1 - 2, C1, 0, M2 + 2, C2, 1)] = 'MM->'
    if C1 > 0:
        successors[(M1, C1 - 1, 0, M2, C2 + 1, 1)] = 'C->'
    if C1 > 1:
        successors[(M1, C1 - 2, 0, M2, C2 + 2, 1)] = 'CC->'
    if M1 > 0 and C1 > 0:
        successors[(M1 - 1, C1 - 1, 0, M2 + 1, C2 + 1, 1)] = 'MC->'
    return successors


def left_successors(state: tuple) -> dict:
    M1, C1, B1, M2, C2, B2 = state
    successors = dict()
    if M2 > 0:
        successors[(M1 + 1, C1, 1, M2 - 1, C2, 0)] = '<-M'
    if M2 > 1:
        successors[(M1 + 2, C1, 1, M2 - 2, C2, 0)] = '<-MM'
    if C2 > 0:
        successors[(M1, C1 + 1, 1, M2, C2 - 1, 0)] = '<-C'
    if C2 > 1:
        successors[(M1, C1 + 2, 1, M2, C2 - 2, 0)] = '<-CC'
    if M2 > 0 and C2 > 0:
        successors[(M1 + 1, C1 + 1, 1, M2 - 1, C2 - 1, 0)] = '<-MC'
    return successors


def recover_path(goal: tuple, path_to: dict, action_to: dict) -> list:
    """Recover and return the path from start to goal."""
    path = [goal, action_to[goal]]
    previous = path_to[goal]
    while previous:
        path.append(previous)
        if action_to[previous]:
            path.append(action_to[previous])
        previous = path_to[previous]
    path.reverse()
    return path


print(mc_problem())