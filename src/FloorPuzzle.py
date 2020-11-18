# Hopper, Kay, Liskov, Perlis, and Ritchie live on
# different floors of a five-floor apartment building.
#
# Hopper does not live on the top floor.
# Kay does not live on the bottom floor.
# Liskov does not live on either the top or the bottom floor.
# Perlis lives on a higher floor than does Kay.
# Ritchie does not live on a floor adjacent to Liskov's.
# Liskov does not live on a floor adjacent to Kay's.
#
# Where does everyone live?
#
# Write a function floor_puzzle() that returns a list of
# five floor numbers denoting the floor of Hopper, Kay,
# Liskov, Perlis, and Ritchie.

import itertools


def floor_puzzle() -> list:
    Hopper, Kay, Liskov, Perlis, Ritchie = 0, 1, 2, 3, 4
    for floors in itertools.permutations(range(5)):
       if (floors[Hopper] != 4
               and floors[Kay] != 0
               and floors[Liskov] != 0 and floors[Liskov] != 4
               and floors[Perlis] > floors[Kay]
               and abs(floors[Ritchie] - floors[Liskov]) > 1
               and abs(floors[Liskov] - floors[Kay]) > 1):
           return list(floors)


print(floor_puzzle())