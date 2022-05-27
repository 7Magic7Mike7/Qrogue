from typing import List, Tuple, Callable

from antlr4 import InputStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNodeImpl

from qrogue.game.world.dungeon_generator import parser_util
from qrogue.game.logic import Message
from qrogue.game.logic.actors import Player
from qrogue.game.world.map import Room, MetaRoom, SpawnRoom, WorldMap
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import Door, DoorOneWayState, DoorOpenState
from qrogue.util import MapConfig, PathConfig, Logger

from .world_parser.QrogueWorldLexer import QrogueWorldLexer
from .world_parser.QrogueWorldParser import QrogueWorldParser
from .world_parser.QrogueWorldVisitor import QrogueWorldVisitor


class QrogueWorldGenerator(QrogueWorldVisitor):
    @staticmethod
    def is_spawn_room(room_id: str) -> bool:
        return room_id.lower() == 'sr'

    def __init__(self, seed: int, player: Player, check_achievement_callback: Callable[[str], bool],
                 trigger_achievement_callback: Callable[[str], None],
                 load_map_callback: Callable[[str, Coordinate], None]):
        self.__seed = seed
        self.__player = player
        self.__check_achievement = check_achievement_callback
        self.__trigger_achievement = trigger_achievement_callback
        self.__load_map = load_map_callback

        self.__hallways_by_id = {}
        self.__created_hallways = {}
        self.__hallways = {}

        self.__rooms = {}
        self.__spawn_pos = None

    def _add_hallway(self, room1: Coordinate, room2: Coordinate, door: Door):
        if door:  # for simplicity door could be null so we check it here
            if room1 in self.__hallways:
                self.__hallways[room1][room2] = door
            else:
                self.__hallways[room1] = {room2: door}
            if room2 in self.__hallways:
                self.__hallways[room2][room1] = door
            else:
                self.__hallways[room2] = {room1: door}

    def generate(self, file_name: str, in_dungeon_folder: bool = True) -> Tuple[WorldMap, bool]:
        map_data = PathConfig.read_world(file_name, in_dungeon_folder)

        input_stream = InputStream(map_data)
        lexer = QrogueWorldLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueWorldParser(token_stream)
        parser.addErrorListener(parser_util.MyErrorListener())

        try:
            name, room_matrix = self.visit(parser.start())
            if name is None:
                name = file_name
        except SyntaxError as se:
            Logger.instance().error(str(se))
            return None, False

        # add empty rooms if rows don't have the same width
        max_len = 0
        for row in room_matrix:
            if len(row) > max_len:
                max_len = len(row)
        for row in room_matrix:
            if len(row) < max_len:
                row += [None] * (max_len - len(row))

        world = WorldMap(name, file_name, self.__seed, room_matrix, self.__player, self.__spawn_pos,
                         self.__check_achievement, self.__trigger_achievement)
        return world, True

    def __load_next(self):
        self.__load_map("next", None)

    ##### loading #####

    def __load_hallway(self, reference: str) -> Door:
        if reference in self.__hallways_by_id:
            return self.__hallways_by_id[reference]
        elif reference == parser_util.EMPTY_HALLWAY_CODE:
            return None
        elif reference == parser_util.DEFAULT_HALLWAY_STR:
            return Door(Direction.North)
        else:
            return Door(Direction.North)

    def __load_room(self, reference: str, x: int, y: int) -> Room:
        if reference in self.__rooms:
            if str.lower(reference) == 'sr':
                if self.__spawn_pos:
                    parser_util.warning("A second SpawnRoom was defined! Ignoring the first one "
                                        "and using this one as SpawnRoom.")
                self.__spawn_pos = Coordinate(x, y)
            room = self.__rooms[reference]
            hw_dic = parser_util.get_hallways(self.__created_hallways, self.__hallways, Coordinate(x, y))
            return room.copy(hw_dic)
        else:
            parser_util.warning(f"room_id \"{reference}\" not specified and imports not supported for worlds! "
                                "Placing an empty room instead.")
            # row.append(rooms.Placeholder.empty_room())
        return SpawnRoom(self.__load_map)

    ##### Hallway area #####

    def visitH_attributes(self, ctx: QrogueWorldParser.H_attributesContext) -> Door:
        direction = Direction.North
        door_check = None
        if ctx.OPEN_LITERAL():
            open_state = DoorOpenState.Open
        elif ctx.EVENT_LITERAL():
            if ctx.REFERENCE(0):
                event_id = parser_util.normalize_reference(ctx.REFERENCE(0).getText())

                def door_check():
                    return self.__check_achievement(event_id)
                open_state = DoorOpenState.EventLocked
            else:
                open_state = DoorOpenState.Open
                parser_util.warning("Event lock specified without an event id! Ignoring the lock and placing an open "
                                    "door instead.")
        else:
            open_state = DoorOpenState.Closed
            parser_util.warning("Invalid hallway attribute: it is neither locked nor opened nor closed!")
        return Door(direction, open_state, DoorOneWayState.NoOneWay, door_check)

    def visitHallway(self, ctx: QrogueWorldParser.HallwayContext) -> Tuple[str, Door]:
        hw_id = ctx.HALLWAY_ID().getText()
        door = self.visit(ctx.h_attributes())
        return hw_id, door

    def visitHallways(self, ctx: QrogueWorldParser.HallwaysContext) -> None:
        for hallway_ctx in ctx.hallway():
            hw_id, door = self.visit(hallway_ctx)
            self.__hallways_by_id[hw_id] = door

    ##### Room area #####

    def visitR_type(self, ctx: QrogueWorldParser.R_typeContext) -> Tuple[str, int, Direction]:
        num = 0
        for digit in ctx.DIGIT():
            num *= 10
            d = int(digit.getText())
            num += d
        direction = parser_util.direction_from_string(ctx.DIRECTION().getText())
        if ctx.WORLD_LITERAL():
            return "W", num, direction
        elif ctx.LEVEL_LITERAL():
            return "L", num, direction
        else:
            raise ValueError("Invalid r_type: " + ctx.getText())

    def visitR_visibility(self, ctx: QrogueWorldParser.R_visibilityContext) -> Tuple[bool, bool]:
        visible = False
        foggy = False
        if ctx.VISIBLE_LITERAL():
            visible = True
        elif ctx.FOGGY_LITERAL():
            foggy = True
        return visible, foggy

    def visitR_attributes(self, ctx: QrogueWorldParser.R_attributesContext) \
            -> Tuple[Tuple[bool, bool], bool, int, Direction]:
        visibility = self.visit(ctx.r_visibility())
        rtype, num, direction = self.visit(ctx.r_type())
        return visibility, rtype, num, direction

    def visitRoom_content(self, ctx) -> Tuple[str, str]:
        msg = ctx.TEXT().getText()[1:-1]  # strip encapsulating \"
        level_to_load = parser_util.normalize_reference(ctx.REFERENCE().getText())
        return msg, level_to_load

    def visitRoom(self, ctx: QrogueWorldParser.RoomContext) -> Tuple[str, MetaRoom]:
        room_id = ctx.ROOM_ID().getText()
        msg, level_to_load = self.visit(ctx.room_content())
        visibility, m_type, num, orientation = self.visit(ctx.r_attributes())

        alt_message = Message.create_with_title("load" + room_id + "Done", level_to_load + " - done", msg)
        # the (internal) level name is also the name of the event that describes whether the level was completed or not
        message = Message.create_with_alternative("load" + room_id, level_to_load, msg, level_to_load, alt_message)
        # hallways will be added later
        if self.is_spawn_room(room_id):
            room = MetaRoom(self.__load_map, orientation, message, level_to_load, m_type, num, is_spawn=True)
        else:
            room = MetaRoom(self.__load_map, orientation, message, level_to_load, m_type, num)
        visible, foggy = visibility
        if visible or self.__check_achievement(level_to_load):  # always show finished levels
            room.make_visible()
        elif foggy:
            room.in_sight()
        return room_id, room

    def visitRooms(self, ctx: QrogueWorldParser.RoomsContext):
        for room_ctx in ctx.room():
            room_id, room = self.visit(room_ctx)
            self.__rooms[room_id] = room

    ##### Layout area #####

    def visitLayout(self, ctx: QrogueWorldParser.LayoutContext) -> List[List[Room]]:
        # first setup all hallway connections
        for y, hw_row in enumerate(ctx.l_hallway_row()):
            self.__visitL_hallway_row(hw_row, y)

        room_matrix = []
        for y in range(MapConfig.max_height()):
            row_ctx = ctx.l_room_row(y)
            if row_ctx:
                room_matrix.append(self.__visitL_room_row(row_ctx, y))
            else:
                break
        if ctx.l_room_row(MapConfig.max_height()):
            parser_util.warning(
                f"Too much room rows specified. Only maps of size ({MapConfig.max_width()}, "
                f"{MapConfig.max_height()}) supported. Ignoring over-specified rows.")

        return room_matrix

    def __hallway_handling(self, ctx_children: List[TerminalNodeImpl], y: int, direction: Direction):
        x = 0
        for child in ctx_children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type, QrogueWorldParser.VERTICAL_SEPARATOR):
                parser_util.warning(
                    f"Too much room columns specified. Only maps of size ({MapConfig.max_width()}, "
                    f"{MapConfig.max_height()}) supported. Ignoring over-specified columns.")
                break
            if child.symbol.type == QrogueWorldParser.HALLWAY_ID:
                hw_id = child.symbol.text
                origin = Coordinate(x, y)
                self._add_hallway(origin, origin + direction, self.__load_hallway(hw_id))
                x += 1
            elif child.symbol.type == QrogueWorldParser.EMPTY_HALLWAY:
                x += 1

    def __visitL_hallway_row(self, ctx: QrogueWorldParser.L_hallway_rowContext, y: int) -> None:
        self.__hallway_handling(ctx.children, y, Direction.South)  # connect downwards to the next room row

    def __visitL_room_row(self, ctx: QrogueWorldParser.L_room_rowContext, y: int) -> List[Room]:
        self.__hallway_handling(ctx.children, y, Direction.East)  # connect to the right to the next room

        row = []
        x = 0
        for child in ctx.children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type, QrogueWorldParser.VERTICAL_SEPARATOR):
                parser_util.warning(f"Too much room columns specified. Only maps of size ({MapConfig.max_width()}, "
                                    f"{MapConfig.max_height()}) supported. Ignoring over-specified columns.")
                break

            if child.symbol.type == QrogueWorldParser.ROOM_ID:
                room_id = child.symbol.text  # todo make it illegal to have the same room_id twice?
                row.append(self.__load_room(room_id, x, y))
                x += 1
            elif child.symbol.type == QrogueWorldParser.EMPTY_ROOM:
                row.append(None)
                x += 1
        return row

    ##### Start area #####

    def visitStart(self, ctx: QrogueWorldParser.StartContext) -> Tuple[str, List[List[Room]]]:
        if ctx.TEXT():
            name = ctx.TEXT().getText()[1:-1]
        else:
            name = None

        # prepare hallways first because they are standalone
        self.visit(ctx.hallways())
        # next prepare the rooms because they reference hallways
        self.visit(ctx.rooms())

        # for the last step we retrieve the room matrix from layout
        return name, self.visit(ctx.layout())
