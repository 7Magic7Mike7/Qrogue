import sys

from qrogue.util import PathConfig


def normalize_text(text: str) -> str:
    """
    Removes all QRogue color codes from the given text.

    :param text: the text to normalize
    :return: a string representing text without QRogue color codes
    """
    new_text, index = "", 0
    while index < len(text):
        hl_start = text.find("//", index)
        if hl_start < 0: break
        hl_end = text.find("//", hl_start+2)
        if hl_end < 0: break

        new_text += text[index:hl_start] + text[hl_start+4:hl_end]
        index = hl_end + 2
    return new_text + text[index:]


def normalize_messages(messages: str) -> str:
    """
    Removes all QRogue color codes from all message texts within messages.

    :param messages: content of a [Messages] area of a QRogue level.
    :return: a string representation of all message texts in messages but without QRogue color codes
    """
    new_text = ""
    index = 0
    while True:
        text_start = messages.find("\"", index)
        if text_start < 0: break
        text_end = messages.find("\"", text_start + 1)
        if text_end < 0: break

        new_text += messages[index:text_start] + normalize_text(messages[text_start:text_end+1])
        index = text_end + 1
    return new_text + messages[index:]


if __name__ == "__main__":
    lvl_name = sys.argv[1]
    lvl_text = PathConfig.read_level(lvl_name)

    desc_start = lvl_text.find("Description =")
    desc_end = lvl_text.find("TELEPORTER", desc_start)
    print(normalize_text(lvl_text[desc_start:desc_end]))

    msg_start = lvl_text.find("[Messages]")
    msg_start = lvl_text.find("default Speaker", msg_start)
    print(normalize_messages(lvl_text[msg_start:]))
