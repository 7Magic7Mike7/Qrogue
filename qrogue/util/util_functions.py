import enum
import math
from typing import Optional, Any

__DEFAULT_CHARACTER = " "


def is_power_of_2(n: int):
    """
    Checks if a given number is a power of 2.
    :param n: the number we want to check
    :return: True if n is a power of 2, False otherwise
    """
    if n == 0:
        return False
    return (n & (n - 1)) == 0


def clamp(val: int, minv: int, maxv: int) -> int:
    """
    Returns val if minv <= val <= maxv is True. Else either returns minv or maxv, depending on which one is closer to
    val.

    :param val: the value to clamp
    :param minv: the minimum value val should be clamped to
    :param maxv: the maximum value val should be clamped to
    :return: minv if val < minv, maxv if val > maxv, else val (minv <= val <= maxv)
    """
    return max(minv, min(val, maxv))


def to_binary_string(num: int, digits: Optional[int] = None, msb: bool = True) -> str:
    """
    Converts a given integer into its binary representation as string.

    :param num: the number we want to convert to a binary string
    :param digits: number of digits the string should show (= length), if None it is calculated to fit num
    :param msb: whether to place the most or least significant bit(s) first
    :return:
    """
    if digits is None:
        digits = int(math.ceil(math.log2(num)))
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
    """
    Tries to align text in a line by adding character to the left or right until text has the length of the given line
    width. If text is not shorter than line width it is immediately returned without any changes.

    :param text: the text to align
    :param line_width: the length text should have in the end
    :param left: whether the text should be left-aligned (True) or right-aligned (false)
    :param character: the character to add as alignment, defaults to whitespace
    :return: a left or right aligned version of text
    """
    if line_width <= len(text):
        return text
    diff = line_width - len(text)
    if left:
        return text + diff * character
    else:
        return diff * character + text


def enum_str(value: enum.Enum, skip_type_prefix: bool = True) -> str:
    text = str(value)
    if skip_type_prefix:
        index = text.index(".")
        return text[index + 1:]
    return text


def my_str(value: Any) -> str:
    """
    Just like str() but with special treatment for Enums.

    :param value:
    :return: string representation of the given value
    """
    if isinstance(value, enum.Enum):
        return enum_str(value)
    else:
        return str(value)


def int_to_fixed_len_str(value: int, length: int) -> str:
    """
    Returns a formatted string like "007" if value=7 and length=3.
    If value is too big (e.g., it has more than $length digits) length is ignored and value is just transformed to its
    normal string representation (e.g., value=123 and length=1 returns "123").

    :param value: the integer we want to represent
    :param length: the length of the formatted string
    :return: 0-padded string representation of $value with a length of $length or len(value)
    """
    if len(str(value)) > length:
        return str(value)
    return f"{{0:0{length}d}}".format(value)
