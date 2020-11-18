import time


class Anchor(set):
    """An anchor is where a new word can be placed; has a set of allowable letters."""


# -----------------------------------------------------------------------------------------------------------------

LETTERS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ANY = Anchor(LETTERS)  # The anchor that can be any letter

POINTS = dict(A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3, N=1, O=1, P=3, Q=10, R=1, S=1,
              T=1, U=1, V=4, W=4, X=8, Y=4, Z=10, _=0)

HAND_PREFIXES_CACHE = dict()

ACROSS, DOWN = (1, 0), (0, 1)  # Directions that words can go

NOPLAY = None


def bonus_template(quadrant):
    """Make a board from the upper-left quadrant."""
    return mirror(map(mirror, quadrant.split()))


def mirror(sequence):
    return sequence + sequence[-2:: -1]


SCRABBLE = bonus_template("""
|||||||||
|3..:...3
|.2...;..
|..2...:.
|:..2...:
|....2...
|.;...;..
|..:...:.
|3..:...*
""")

WWF = bonus_template("""
|||||||||
|...3..;.
|..:..2..
|.:..:...
|3..;...2
|..:...:.
|.2...3..
|;...:...
|...:...*
""")

BONUS = WWF

DW, TW, DL, TL = '23:;'


def show(board):
    """Print the board and the BONUS[j][i] entries if no letter in the board."""
    for (row_index, row) in enumerate(board):
        squares = []
        for (col_index, square) in enumerate(row):
            if is_letter(square):
                squares.append(square)
            else:
                squares.append(BONUS[row_index][col_index])
        print(" ".join(squares))


# -----------------------------------------------------------------------------------------------------------------


def readwordlist(filename):
    """Read the words from a file and return a set of the words and a set of the prefixes."""
    with open(filename) as file:
        text = file.read().upper()
    words = text.split()
    wordset = set()
    prefixset = set()
    for word in words:
        wordset.add(word)
        prefixset.update(set(prefixes(word)))
    return wordset, prefixset


def prefixes(word):
    """A list of the initial sequences of a word, not including the complete word."""
    return [word[:i] for i in range(len(word))]


WORDS, PREFIXES = readwordlist('words4k.txt')


def find_words(letters, prefix='', results=None):
    """Return all words in the dictionary WORDS that can be constructed from the specified letters.

    Note: This function ignores the game board
    """
    if results is None:
        results = set()
    if prefix in WORDS:
        results.add(prefix)
    if prefix not in PREFIXES:
        return
    for L in letters:
        find_words(letters.replace(L, '', 1), prefix + L, results)
    return results

# -----------------------------------------------------------------------------------------------------------------


def best_play(hand, board):
    """Return the highest-scoring play, or None."""
    plays = all_plays(hand, board)
    if not plays:
        return NOPLAY
    return sorted(plays, reverse=True)[0]


def make_play(play, board):
    """Put the word down on the board."""
    (score, (i, j), (di, dj), word) = play
    for letter in word:
        board[j][i] = letter
        i += di
        j += dj
    return board


# -----------------------------------------------------------------------------------------------------------------


def all_plays(hand, board):
    """Find all word plays in both directions.

    A play is a (score, pos, dir, word) tuple, where pos is an (i, j) pair, and dir is ACROSS or DOWN.
    """
    hplays = horizontal_plays(hand, board)             # set of ((i, j), word)
    vplays = horizontal_plays(hand, transpose(board))  # set of ((j, i), word)
    results = set()
    for (score, position, word) in hplays:
        results.add((score, position, ACROSS, word))
    for (score, position, word) in vplays:
        results.add((score, (position[1], position[0]), DOWN, word))
    return results


def transpose(matrix):
    """Transpose the board.

    e.g. [[1,2,3], [4,5,6]] is transposed to [[1, 4], [2, 5], [3, 6]]
    """
    # or [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]
    return map(list, zip(*matrix))


# -----------------------------------------------------------------------------------------------------------------


def calculate_score(board, pos, direction, hand, word):
    """Return the total score for this play."""
    total, cross_total, word_multiplier = 0, 0, 1
    starti, startj = pos
    di, dj = direction
    other_direction = DOWN if direction == ACROSS else ACROSS
    for (n, L) in enumerate(word):
        i, j = starti + n * di, startj + n * dj
        sq = board[j][i]
        b = BONUS[j][i]
        word_multiplier *= (1 if is_letter(sq) else
                      3 if b == TW else 2 if b in (DW, '*') else 1)
        letter_mult = (1 if is_letter(sq) else
                       3 if b == TL else 2 if b == DL else 1)
        total += POINTS[L] * letter_mult
        if isinstance(sq, set) and sq is not ANY and direction is not DOWN:
            cross_total += cross_word_score(board, L, (i, j), other_direction)
    return cross_total + word_multiplier * total


def cross_word_score(board, L, pos, direction):
    """Return the score of a word made in the other direction from the main word."""
    i, j = pos
    (j2, word) = find_cross_word(board, i, j)
    return calculate_score(board, (i, j2), DOWN, L, word.replace('.', L))


# -----------------------------------------------------------------------------------------------------------------


def horizontal_plays(hand, board):
    """Find all horizontal plays -- (score, (i, j), word) triplets -- across all rows."""
    results = set()
    for (j, row) in enumerate(board[1:-1], 1):
        set_anchors(row, j, board)
        for (i, word) in row_plays(hand, row):
            score = calculate_score(board, (i, j), ACROSS, hand, word)
            results.add((score, (i, j), word))
    return results


def set_anchors(row, j, board):
    """Update the board with available anchor squares for horizontal plays in row j.

    Anchors are empty squares with a neighboring letter. Some are restricted
    by cross-words to be only a subset of letters in the alphabet.
    """
    for (i, sq) in enumerate(row[1: -1], start=1):
        neighbor_list = (N, S, E, W) = neighbors(board, i, j)
        # Anchors are squares adjacent to a letter.  Plus the '*' square.
        if sq == '*' or (is_empty(sq) and any(map(is_letter, neighbor_list))):
            if is_letter(N) or is_letter(S):
                # Find letters that fit with the cross (vertical) word
                (j2, w) = find_cross_word(board, i, j)
                row[i] = Anchor(L for L in LETTERS if w.replace('.', L) in WORDS)
            # Unrestricted empty square -- any letter will fit.
            else:
                row[i] = ANY


def neighbors(board, i, j):
    """Return a list of the contents of the four neighboring squares, in the order N,S,E,W."""
    return [board[j-1][i], board[j+1][i], board[j][i+1], board[j][i-1]]


def find_cross_word(board, i, j):
    """Find the vertical word that crosses board[j][i].

    Return (j2, w), where j2 is the starting row, and w is the word
    """
    sq = board[j][i]
    w = sq if is_letter(sq) else '.'
    for j2 in range(j, 0, -1):
        sq2 = board[j2 - 1][i]
        if is_letter(sq2):
            w = sq2 + w
        else:
            break
    for j3 in range(j + 1, len(board)):
        sq3 = board[j3][i]
        if is_letter(sq3):
            w = w + sq3
        else:
            break
    return j2, w


# -----------------------------------------------------------------------------------------------------------------


def row_plays(hand, row):
    """Return the set of legal plays in the specified row.

    A row play is a (start, 'WORD') pair,
    """
    results = set()
    # for each anchor and for each legal prefix, add all legal suffixes and save any valid words in results
    for (i, square) in enumerate(row[1: -1], start=1):
        if isinstance(square, Anchor):
            prefix, max_size = legal_prefix(i, row)
            # there are already letters in the board, to the left of this anchor
            if prefix:
                start = i - len(prefix)
                add_suffixes(hand, prefix, start, row, results, anchored=False)
            # the board is empty to the left of this anchor
            else:
                for prefix in find_prefixes(hand):
                    if len(prefix) <= max_size:
                        start = i - len(prefix)
                        add_suffixes(removed(hand, prefix), prefix, start, row, results, anchored=False)
    return results


def legal_prefix(i, row):
    """A legal prefix of an anchor at row[i] is either a string of letters already on the board,
    or new letters that fit into an empty space.

    Return the tuple (prefix_on_board, maxsize) to indicate this.
    """
    start = i
    while is_letter(row[start - 1]):
        start -= 1
    # There is a prefix consisting of letters from the board
    if start < i:
        return ''.join(row[start: i]), i - start
    while is_empty(row[start - 1]) and not isinstance(row[start - 1], set):
        start -= 1
    return '', i - start


def is_letter(sq):
    return isinstance(sq, str) and sq in LETTERS


def is_empty(sq):
    """Is this an empty square (no letters, but a valid position on board; excludes the border)."""
    return sq == '.' or sq == '*' or isinstance(sq, set)


def add_suffixes(hand, pre, start, row, results, anchored=True):
    """Add all possible suffixes, and accumulate (start, word) pairs in results."""
    i = start + len(pre)
    if pre in WORDS and anchored and not is_letter(row[i]):
        results.add((start, pre))
    if pre in PREFIXES:
        sq = row[i]
        if is_letter(sq):
            add_suffixes(hand, pre + sq, start, row, results)
        elif is_empty(sq):
            possibilities = sq if isinstance(sq, set) else ANY
            for L in hand:
                if L in possibilities:
                    add_suffixes(hand.replace(L, '', 1), pre + L, start, row, results)
    return results


# -----------------------------------------------------------------------------------------------------------------


def longest_words(hand, board_letters):
    """Return all word plays, longest first."""
    words = word_plays(hand, board_letters)
    return sorted(words, key=len, reverse=True)


def topn(hand, board_letters, n=10):
    """Return a list of the top n words that hand can play, sorted by word score."""
    words = word_plays(hand, board_letters)
    return sorted(words, key=word_score, reverse=True)[: n]


def word_score(word):
    """The sum of the individual letter point scores for this word."""
    return sum(POINTS[letter] for letter in word)


def word_plays(hand, board_letters):
    """Find all word plays from hand that can be made to abut with a letter on board.

    Find prefix + L + suffix; L from board_letters, rest from hand
    """
    results = set()
    for prefix in find_prefixes(hand, '', set()):
        for L in board_letters:
            add_suffixes(removed(hand, prefix), prefix + L, results)
    return results


def removed(letters, remove):
    """Return a string of letters, but with each letter in remove removed once."""
    for L in remove:
        letters = letters.replace(L, '', 1)
    return letters


def find_prefixes(hand, prefix='', results=None):
    """Find all prefixes (of words) that can be made from letters in hand.

    The set of prefixes from the last hand is cached to speed-up searching of valid word plays
    across the set of anchor positions in the board.
    """
    global HAND_PREFIXES_CACHE

    if prefix == '' and (hand in HAND_PREFIXES_CACHE):
        return HAND_PREFIXES_CACHE[hand]
    if prefix in PREFIXES:
        results.add(prefix)
        for L in hand:
            find_prefixes(hand.replace(L, '', 1), prefix + L, results)
    if prefix == '':
        HAND_PREFIXES_CACHE = {hand: results}
    return results


def add_suffixes(hand, prefix, results):
    """Return the set of words that can be formed by extending pre with letters in hand."""
    if prefix in WORDS:
        results.add(prefix)
    if prefix not in PREFIXES:
        return
    for L in hand:
        add_suffixes(hand.replace(L, '', 1), prefix + L, results)
    return results

























