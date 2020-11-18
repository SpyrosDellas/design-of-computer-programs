# User Instructions
#
# Write a function best_wild_hand(hand) that takes as
# input a 7-card hand and returns the best 5 card hand.
# In this problem, it is possible for a hand to include
# jokers. Jokers will be treated as 'wild cards' which
# can take any rank or suit of the same color. The
# black joker, '?B', can be used as any spade or club
# and the red joker, '?R', can be used as any heart
# or diamond.
#
# Note:
# Multiple correct answers are accepted in cases
# where the best hand is ambiguous (for example, if
# we have 4 kings and 3 queens, there are three best
# hands: 4 kings along with any of the three queens).

import itertools

cards = "23456789TJQKA"
black_joker = [r + k for r in cards for k in "CS"]
red_joker = [r + k for r in cards for k in "HD"]


def replacement(card):
    if card == '?B':
        return black_joker
    elif card == '?R':
        return red_joker
    else:
        return [card]


def best_hand(hand):
    """Eliminate duplicate cards produced by some joker-card combinations."""
    return max(itertools.combinations(set(hand), 5), key=hand_rank)


def best_wild_hand(hand):
    """Try all values for jokers in all 5-card selections."""
    hands7 = map(replacement, hand)
    hands5 = [best_hand(h) for h in itertools.product(*hands7)]
    return max(hands5, key=hand_rank)


def test_best_wild_hand():
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    return 'test_best_wild_hand passes'


# ------------------
# Provided Functions

def hand_rank(hand):
    """Return a value indicating the ranking of a hand."""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return 8, max(ranks)
    elif kind(4, ranks):
        return 7, kind(4, ranks), kind(1, ranks)
    elif kind(3, ranks) and kind(2, ranks):
        return 6, kind(3, ranks), kind(2, ranks)
    elif flush(hand):
        return 5, ranks
    elif straight(ranks):
        return 4, max(ranks)
    elif kind(3, ranks):
        return 3, kind(3, ranks), ranks
    elif two_pair(ranks):
        return 2, two_pair(ranks), ranks
    elif kind(2, ranks):
        return 1, kind(2, ranks), ranks
    else:
        return 0, ranks


def card_ranks(hand):
    """Return a list of the ranks, sorted with higher first."""
    ranks = ['--23456789TJQKA'.index(r) for r, s in hand]
    ranks.sort(reverse=True)
    return [5, 4, 3, 2, 1] if (ranks == [14, 5, 4, 3, 2]) else ranks


def flush(hand):
    """Return True if all the cards have the same suit."""
    suits = [s for r, s in hand]
    return len(set(suits)) == 1


def straight(ranks):
    """Return True if the ordered ranks form a 5-card straight."""
    return (max(ranks) - min(ranks) == 4) and len(set(ranks)) == 5


def kind(n, ranks):
    """Return the first rank that this hand has exactly n-of-a-kind of.
    Return None if there is no n-of-a-kind in the hand."""
    for r in ranks:
        if ranks.count(r) == n:
            return r
    return None


def two_pair(ranks):
    """If there are two pair here, return the two ranks of the two pairs, else None."""
    pair = kind(2, ranks)
    low_pair = kind(2, list(reversed(ranks)))
    if pair and low_pair != pair:
        return pair, low_pair
    else:
        return None


test_best_wild_hand()
