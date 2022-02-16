
def is_power_of_2(n: int):
    if n == 0:
        return False
    return (n & (n - 1)) == 0


def center_string(text: str, line_width: int, uneven_left: bool = True, character: str = " ") -> str:
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
