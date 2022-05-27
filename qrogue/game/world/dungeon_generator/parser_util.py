from typing import Dict, Optional

from antlr4.error.ErrorListener import ErrorListener

from qrogue.game.world.map import Hallway
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import MapConfig, Logger, Config

DEFAULT_HALLWAY_STR = "=="
TEMPLATE_PREFIX = "_"
EMPTY_ROOM_CODE = "_a"
EMPTY_HALLWAY_CODE = "_0"

OBSTACLE_TILE = "o"
PLACE_HOLDER_TILE = "_"
COLLECTIBLE_TILE = "c"
TRIGGER_TILE = "t"
MESSAGE_TILE = "m"
ENERGY_TILE = "e"
RIDDLER_TILE = "r"
SHOP_KEEPER_TILE = "$"
FLOOR_TILE = " "


def warning(text: str):
    Logger.instance().println(f"Warning: {text}")
    if Config.debugging():
        print("Warning", text)


def check_for_overspecified_columns(x: int, symbol_type, ref_type):
    return x == MapConfig.max_width() and symbol_type != ref_type or x > MapConfig.max_width()


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


def get_hallways(hallway_dictionary: Dict[Coordinate, Dict[Direction, Hallway]], hallways, pos: Coordinate) \
        -> Dict[Direction, Hallway]:
    if pos in hallways:
        hallways = hallways[pos]
        if hallways:
            room_hallways = {
                Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None,
            }
            for neighbor in hallways:
                direction = Direction.from_coordinates(pos, neighbor)
                opposite = direction.opposite()
                # get hallway from neighbor if it exists, otherwise create it
                if neighbor in hallway_dictionary and opposite in hallway_dictionary[neighbor]:
                    hallway = hallway_dictionary[neighbor][opposite]
                else:
                    door = hallways[neighbor]
                    # always make a copy so we don't run into problems if we use a simple hallway multiple times
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
                    if neighbor in hallway_dictionary:
                        hallway_dictionary[neighbor][opposite] = hallway
                    else:
                        hallway_dictionary[neighbor] = {opposite: hallway}

                # store the hallway so the neighbors can find it if necessary
                if pos not in hallway_dictionary:
                    hallway_dictionary[pos] = {}
                hallway_dictionary[pos][direction] = hallway
                room_hallways[direction] = hallway
            return room_hallways
    return None


class QrogueBasics:
    @staticmethod
    def parse_integer(ctx) -> Optional[int]:
        if ctx.DIGIT():
            return int(ctx.DIGIT().getText())
        elif ctx.HALLWAY_ID():
            return int(ctx.HALLWAY_ID().getText())
        elif ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        else:
            return None

    @staticmethod
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
                num = str(QrogueBasics.parse_integer(integer_))
            else:
                num = float_.getText()
            complex_number += num

            if ctx.SIGN(1):
                complex_number += ctx.SIGN(1).symbol.text + str(imag_)
        else:
            complex_number += str(imag_)

        return complex(complex_number)


class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        #print(f"Syntax Error: \"{offendingSymbol}\" at line {line}, column {column} - {msg}")
        raise SyntaxError(msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        Config.debug_print("Ambiguity")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        Config.debug_print("Attempting full context")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        Config.debug_print("Context sensitivity")


