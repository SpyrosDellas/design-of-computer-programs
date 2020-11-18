"""longest_subpalindrome_slice(text) takes a string as input and returns the i and j indices that
correspond to the beginning and end indices of the longest palindrome in the string.
"""
import math


def longest_subpalindrome_slice(text):
    """Return (i, j) such that text[i:j] is the longest palindrome in text.

    Uses Manacher's algorithm to find the longest sub-palindrome in O(n) time, where n is the length
    of the input string.
    """
    # handle boundary cases
    if text is None or len(text) == 0:
        return 0, 0
    # augment the text string
    text = augment_text(text.lower())
    # initialize variables
    expansion_length = [0] * len(text)
    left, center, right = 0, 0, 0
    max_index = 0
    # scan through the text once
    for index in range(1, len(text)):
        if index > right:
            expansion_length[index] = length_from(index, text)
            center = index
            left = index - expansion_length[index]
            right = index + expansion_length[index]
        else:
            mirror = center - (index - center)
            if mirror - expansion_length[mirror] > left:
                expansion_length[index] = expansion_length[mirror]
            else:
                expansion_length[index] = length_from(index, text, right - index)
                if index + expansion_length[index] > right:
                    center = index
                    left = index - expansion_length[index]
                    right = index + expansion_length[index]
        if expansion_length[index] > expansion_length[max_index]:
            max_index = index
    return slice_from(expansion_length, max_index)


def augment_text(text):
    """Augment the given string with an '$' between characters and at both ends.

    This operation transforms any (even or odd length) string to an odd length string and simplifies the
    scanning for sub-palindromes, without affecting correctness.
    """
    return text.replace("", "$")


def length_from(index, text, expansion_length=0):
    """Find the expansion length of the sub-palindrome centered at index, by direct character comparisons."""
    start = index - expansion_length
    end = index + expansion_length
    while start > 0 and end < (len(text) - 1):
        if text[start - 1] == text[end + 1]:
            start -= 1
            end += 1
            expansion_length += 1
        else:
            break
    return expansion_length


def slice_from(expansion_length, max_index):
    """Recover the start and end indices of the longest sub-palindrome in the original text."""
    start = math.floor((max_index - expansion_length[max_index]) / 2)
    end = math.floor((max_index + expansion_length[max_index]) / 2)
    return start, end


def test():
    L = longest_subpalindrome_slice
    s1 = 'ycxabacccabaxcy'
    s2 = 'kikycxabacccabaxcyoyoyoyoyoyoyoyoyoy'
    s3 = 'kikycxabacccabaxcycycycycycycycycycy'
    assert L('racecar') == (0, 7)
    assert L('Racecar') == (0, 7)
    assert L('RacecarX') == (0, 7)
    assert L('Race carr') == (7, 9)
    assert L('') == (0, 0)
    assert L('something rac e car going') == (8, 21)
    assert L('xxxxx') == (0, 5)
    assert L('xxxx') == (0, 4)
    assert L('Mad am I ma dam.') == (0, 15)
    assert L(s1) == (0, 15)
    assert L(s2) == (17, 36)
    assert L(s3) == (16, 35)
    print('tests pass')


test()