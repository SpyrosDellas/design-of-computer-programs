import heapq
import doctest


def pour_problem(first_capacity: int, second_capacity: int, goal: int, start=(0, 0)) -> list:
    """Solve the water pour problem for two glasses.

    We have two glasses with specified capacities, a start state and a goal state.
    The goal state is specified as a volume of water that can be in either glass.
    We need to find a shortest path from the start to the goal state.

    >>> print(pour_problem(9, 4, 6))
    [(0, 0), (9, 0), (5, 4), (5, 0), (1, 4), (1, 0), (0, 1), (9, 1), (6, 4)]

    >>> print(pour_problem(7, 9, 8))
    [(0, 0), (0, 9), (7, 2), (0, 2), (2, 0), (2, 9), (7, 4), (0, 4),
    (4, 0), (4, 9), (7, 6), (0, 6), (6, 0), (6, 9), (7, 8)]

    >>> test(10)
    Exploring parameter space for glass capacities and goal in [1, 10]...
    One of the problems with longest solution is: (first_capacity=8, second_capacity=9, goal=4), number of steps = 14
    Solution:  [(0, 0), (0, 9), (8, 1), (0, 1), (1, 0), (1, 9), (8, 2), (0, 2), (2, 0), (2, 9), (8, 3), (0, 3),
    (3, 0), (3, 9), (8, 4)]

    >>> test(20)
    Exploring parameter space for glass capacities and goal in [1, 20]...
    One of the problems with longest solution is: (first_capacity=17, second_capacity=19, goal=18), number of steps = 34
    Solution:  [(0, 0), (0, 19), (17, 2), (0, 2), (2, 0), (2, 19), (17, 4), (0, 4), (4, 0), (4, 19), (17, 6), (0, 6),
    (6, 0), (6, 19), (17, 8), (0, 8), (8, 0), (8, 19), (17, 10), (0, 10), (10, 0), (10, 19), (17, 12), (0, 12), (12, 0),
    (12, 19), (17, 14), (0, 14), (14, 0), (14, 19), (17, 16), (0, 16), (16, 0), (16, 19), (17, 18)]
    """
    # the path from the previous state to each state visited
    path_to = dict()
    path_to[start] = None
    # min oriented priority queue of states to visit; represented as tuples (path length, state)
    frontier = []
    heapq.heappush(frontier, (0, start))

    while frontier:
        current = heapq.heappop(frontier)
        if goal in current[1]:
            return recover_path(current[1], path_to)
        for successor in successors(current[1], first_capacity, second_capacity):
            if successor not in path_to:
                heapq.heappush(frontier, (current[0] + 1, successor))
                path_to[successor] = current[1]
    return []


def recover_path(goal: tuple, path_to: dict) -> list:
    """Recover and return the path from start to goal."""
    path = [goal]
    previous = path_to[goal]
    while previous:
        path.append(previous)
        previous = path_to[previous]
    path.reverse()
    return path


def successors(current: tuple, first_capacity: int, second_capacity: int) -> list:
    result = []
    level1, level2 = current
    # empty the glasses
    result.append((0, level2))
    result.append((level1, 0))
    # fill the glasses
    result.append((first_capacity, level2))
    result.append((level1, second_capacity))
    # transfer between glasses
    remainder = first_capacity - level1
    level1 = min(first_capacity, level1 + level2)
    level2 = max(0, level2 - remainder)
    result.append((level1, level2))
    level1, level2 = current
    remainder = second_capacity - level2
    level2 = min(second_capacity, level1 + level2)
    level1 = max(0, level1 - remainder)
    result.append((level1, level2))
    return result


def path_length(triplet: tuple):
    cap1, cap2, goal = triplet
    return len(pour_problem(cap1, cap2, goal))


def test(limit):
    print("Exploring parameter space for glass capacities and goal in [1, %d]..." % limit)
    parameter_set = set([(cap1, cap2, goal) for cap1 in range(1, limit) for cap2 in range(cap1, limit)
                       for goal in range(1, max(cap1, cap2))])
    max_solution = max([args for args in parameter_set], key=path_length)
    max_path = pour_problem(*max_solution)
    print("One of the problems with longest solution is: "
          "(first_capacity=%d, second_capacity=%d, goal=%d), number of steps = %d"
          % (*max_solution, len(max_path) - 1))
    print("Solution: ", max_path)


if __name__ == "__main__":
    print(doctest.testmod(verbose=True, optionflags=doctest.NORMALIZE_WHITESPACE))
