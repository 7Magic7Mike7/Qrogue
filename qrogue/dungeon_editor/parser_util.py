from typing import Dict

from antlr4.error.ErrorListener import ErrorListener

from qrogue.game.map.navigation import Direction, Coordinate
from qrogue.game.map.rooms import Hallway
from qrogue.util.config import MapConfig

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
    print("Warning: ", text)


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
                    if door.direction not in [direction, direction.opposite()]:
                        if door.is_one_way:
                            warning("Found one way door with invalid direction! Horizontal hallways can only "
                                         "have East or West doors and vertical ones only North and South doors! "
                                         "Removing the one way aspect and setting the direction to a valid one.")
                            door = door.copy(direction)
                        else:
                            door = door.copy(direction)
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


class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        #print(f"Syntax Error: \"{offendingSymbol}\" at line {line}, column {column} - {msg}")
        raise SyntaxError(msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        print("Ambiguity")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        print("Attempting full context")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        print("Context sensitivity")


