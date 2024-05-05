from typing import Dict, Optional, Tuple

from qrogue.game.logic import Message
from qrogue.game.world.map import Hallway
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import Door
from qrogue.util import MapConfig, Logger, Config

DEFAULT_HALLWAY_STR = "=="
TEMPLATE_PREFIX = "_"
EMPTY_ROOM_CODE = "_a"
EMPTY_HALLWAY_CODE = "_0"

# how the tiles look in the editor is not necessarily the same as they look in the game
OBSTACLE_TILE = "o"
PLACE_HOLDER_TILE = "_"
COLLECTIBLE_TILE = "c"
TRIGGER_TILE = "t"
TELEPORT_TILE = "t"
MESSAGE_TILE = "m"
ENERGY_TILE = "e"
BOSS_TILE = "b"
RIDDLER_TILE = "r"
CHALLENGER_TILE = "!"
FLOOR_TILE = " "


def warning(text: str, location: str):
    Logger.instance().warn(f"@{location}: {text}", from_pycui=False)


def error(text: str):
    Logger.instance().error(text, show=False, from_pycui=False)
    raise SyntaxError(text)


def check_for_overspecified_columns(x: int, symbol_type, ref_type):
    return x == MapConfig.map_width() and symbol_type != ref_type or x > MapConfig.map_width()


def normalize_reference(reference: str) -> str:
    if reference[0] == '*':
        return reference[1:].lower()
    else:
        return reference.lower()


def direction_from_string(dir_str: str) -> Direction:
    direction = None
    if dir_str == "North":
        direction = Direction.North
    elif dir_str == "East":
        direction = Direction.East
    elif dir_str == "South":
        direction = Direction.South
    elif dir_str == "West":
        direction = Direction.West
    return direction


def get_hallways(hallway_dict: Dict[Coordinate, Dict[Direction, Hallway]],
                 door_dict: Dict[Coordinate, Dict[Coordinate, Door]], pos: Coordinate) \
        -> Optional[Dict[Direction, Hallway]]:
    if pos in door_dict:
        doors = door_dict[pos]
        if doors:
            room_hallways = {
                Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None,
            }
            for neighbor in doors:
                direction = Direction.from_coordinates(pos, neighbor)
                opposite = direction.opposite()
                # get hallway from neighbor if it exists, otherwise create it
                if neighbor in hallway_dict and opposite in hallway_dict[neighbor]:
                    hallway = hallway_dict[neighbor][opposite]
                else:
                    door = doors[neighbor]
                    # always make a copy, so we don't run into problems if we use a simple hallway multiple times
                    if door.is_one_way:
                        if door.direction not in [direction, direction.opposite()]:
                            warning("Found one way door with invalid direction! Horizontal hallways can only "
                                    "have East or West doors and vertical ones only North and South doors! "
                                    "Removing the one way aspect and setting the direction to a valid one.")
                            door = door.copy_and_adapt(direction, reset_one_way=True)
                        else:
                            door = door.copy()
                    else:
                        door = door.copy_and_adapt(direction)
                    hallway = Hallway(door)
                    if neighbor in hallway_dict:
                        hallway_dict[neighbor][opposite] = hallway
                    else:
                        hallway_dict[neighbor] = {opposite: hallway}

                # store the hallway so the neighbors can find it if necessary
                if pos not in hallway_dict:
                    hallway_dict[pos] = {}
                hallway_dict[pos][direction] = hallway
                room_hallways[direction] = hallway
            return room_hallways
    return None


def text_to_str(ctx_text, index: int = None) -> str:
    if index is None:
        text = ctx_text.TEXT()
    else:
        text = ctx_text.TEXT(index)
    return text.getText()[1:-1]


def parse_integer(ctx) -> Optional[int]:
    if ctx.DIGIT():
        return int(ctx.DIGIT().getText())
    elif ctx.HALLWAY_ID():
        return int(ctx.HALLWAY_ID().getText())
    elif ctx.INTEGER():
        return int(ctx.INTEGER().getText())
    else:
        return None


def parse_complex(ctx) -> complex:
    if ctx.SIGN(0):
        first_sign = ctx.SIGN(0).symbol.text
    else:
        first_sign = "+"

    integer_ = ctx.integer()
    float_ = ctx.FLOAT()
    imag_ = ctx.IMAG_NUMBER()

    complex_number = first_sign
    if integer_ or float_:
        if integer_:
            num = str(parse_integer(integer_))
        else:
            num = float_.getText()
        complex_number += num

        if ctx.SIGN(1):
            complex_number += ctx.SIGN(1).symbol.text + str(imag_)
    else:
        complex_number += str(imag_)

    return complex(complex_number)


def parse_message(ctx, default_speaker: str = Config.system_name()) -> Message:
    m_id = normalize_reference(ctx.REFERENCE(0).getText())

    title, priority, position, msg = parse_message_body(ctx.message_body(), default_speaker)

    if ctx.MSG_EVENT():
        event = normalize_reference(ctx.REFERENCE(1).getText())
        msg_ref = normalize_reference(ctx.REFERENCE(2).getText())
        return Message(m_id, title, msg, priority, position, event, msg_ref)
    else:
        return Message.create_with_title(m_id, title, msg, priority, position)


def parse_speaker(ctx, text_index: Optional[int] = 0) -> str:
    title = text_to_str(ctx, text_index)
    if title.isdigit():
        title = Config.get_name(int(title[0]))
    return title


def parse_message_body(ctx, default_speaker: str) -> Tuple[str, bool, int, str]:
    if ctx.MSG_SPEAKER():
        title = parse_speaker(ctx, 0)
        start = 1
    else:
        title = default_speaker
        start = 0
    priority = ctx.MSG_PRIORITY() is not None
    if ctx.DIGIT():
        position = int(ctx.DIGIT().getText())
    else:
        position = None
    msg = ""
    for i in range(start, len(ctx.TEXT())):
        msg += text_to_str(ctx, i) + "\n"

    return title, priority, position, msg