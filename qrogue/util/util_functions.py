
__DEFAULT_CHARACTER = " "


def is_power_of_2(n: int):
    if n == 0:
        return False
    return (n & (n - 1)) == 0


def to_binary_string(num: int, digits: int = -1, msb: bool = True) -> str:
    """
    Converts a given integer into its binary representation as string.
    :param num: the number we want to convert to a binary string
    :param digits: number of digits the string should show (= length)
    :param msb: whether to place the most or least significant bit(s) first
    :return:
    """
    str_rep = ""
    i = 0
    while True:
        str_rep += str(num % 2)
        num = int(num / 2)
        i += 1
        if digits <= i:
            break
        elif digits < 0 and num <= 0:
            break
    if msb:
        return str_rep[::-1]    # reverse the string
    else:
        return str_rep


def center_string(text: str, line_width: int, uneven_left: bool = True, character: str = __DEFAULT_CHARACTER) -> str:
    """
    Prepends and appends the given character to the text in such a way that the text is centered as good as possible
    in a line with the given line width. If the number of characters to add is uneven (i.e. number of prepended and
    appended characters cannot be the same) the flag uneven_left decides whether to prepend (= left, default) or
    append (= right) should be bigger.
    :param text: the text to center in the line
    :param line_width: width of the line the text should be centered in
    :param uneven_left: whether to prepend or append one character more in case of imbalance, defaults to True
    :param character: the character to add, defaults to whitespace " "
    :return: centered version of text
    """
    if line_width <= len(text):
        return text
    diff = line_width - len(text)
    half1 = int(diff / 2)
    half2 = diff - half1

    if uneven_left:
        return half2 * character + text + half1 * character
    else:
        return half1 * character + text + half2 * character


def align_string(text: str, line_width: int, left: bool = True, character: str = __DEFAULT_CHARACTER) -> str:
    if line_width <= len(text):
        return text
    diff = line_width - len(text)
    if left:
        return text + diff * character
    else:
        return diff * character + text
