from typing import List, Tuple, Callable, Optional, Dict, Set

from antlr4 import InputStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNodeImpl

from qrogue.game.logic import Message
from qrogue.game.logic.actors import Player
from qrogue.game.world.dungeon_generator import parser_util
from qrogue.game.world.map import Room, MetaRoom, SpawnRoom, WorldMap, MapMetaData
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import Door, DoorOneWayState, DoorOpenState
from qrogue.util import MapConfig, PathConfig, Logger, Config

from qrogue.game.world.dungeon_generator.world_parser.QrogueWorldLexer import QrogueWorldLexer
from qrogue.game.world.dungeon_generator.world_parser.QrogueWorldParser import QrogueWorldParser
from qrogue.game.world.dungeon_generator.world_parser.QrogueWorldVisitor import QrogueWorldVisitor
from qrogue.game.world.map.rooms import Placeholder


class _MapType:
    WORLD = "W"
    LEVEL = "L"


class QrogueWorldGenerator(QrogueWorldVisitor):
    CONNECTING_ROOM_ID = "_"

    @staticmethod
    def is_spawn_room(room_id: str) -> bool:
        return room_id.lower() == 'sr'

    def __init__(self, seed: int, player: Player, check_achievement_callback: Callable[[str], bool],
                 trigger_event_callback: Callable[[str], None],
                 load_map_callback: Callable[[str, Optional[Coordinate]], None],
                 show_message_callback: Callable[[str, str], None]):
        self.__seed = seed
        self.__player = player
        self.__check_achievement = check_achievement_callback
        self.__trigger_event = trigger_event_callback
        self.__load_map = load_map_callback
        self.__show_message = show_message_callback

        self.__default_speaker = Config.system_name()

        self.__hallways_by_id = {}
        self.__created_hallways = {}
        self.__hallways = {}

        self.__rooms: Dict[str, MetaRoom] = {}
        self.__mandatory_levels: Set[str] = set()
        self.__spawn_pos: Optional[Coordinate] = None
        self.__meta_data = MapMetaData(None, None, False, self.__show_description)

    def __show_description(self):
        if self.__meta_data.description:
            ret = self.__meta_data.description.get(self.__check_achievement)
            if ret:
                title, text = ret
                self.__show_message(title, text)

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

    def generate(self, file_name: str, in_dungeon_folder: bool = True) -> Tuple[Optional[WorldMap], bool]:
        map_data = PathConfig.read_world(file_name, in_dungeon_folder)

        input_stream = InputStream(map_data)
        lexer = QrogueWorldLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueWorldParser(token_stream)
        parser.addErrorListener(parser_util.MyErrorListener())

        try:
            meta_data, room_matrix = self.visit(parser.start())
        except SyntaxError as se:
            Logger.instance().error(str(se), from_pycui=False)
            return None, False

        # add empty rooms if rows don't have the same width
        max_len = 0
        for row in room_matrix:
            if len(row) > max_len:
                max_len = len(row)
        for row in room_matrix:
            if len(row) < max_len:
                row += [None] * (max_len - len(row))

        world = WorldMap(meta_data, file_name, self.__seed, room_matrix, self.__player, self.__spawn_pos,
                         self.__check_achievement, self.__trigger_event, self.__mandatory_levels)
        return world, True

    def __load_next(self):
        self.__load_map("next", None)

    ##### loading #####

    def __load_hallway(self, reference: str) -> Optional[Door]:
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
            if reference.lower() == 'sr':
                if self.__spawn_pos:
                    parser_util.warning("A second SpawnRoom was defined! Ignoring the first one "
                                        "and using this one as SpawnRoom.")
                self.__spawn_pos = Coordinate(x, y)
            room = self.__rooms[reference]
            hw_dic = parser_util.get_hallways(self.__created_hallways, self.__hallways, Coordinate(x, y))
            return room.copy(hw_dic)
        elif reference.startswith(QrogueWorldGenerator.CONNECTING_ROOM_ID):
            hw_dic = parser_util.get_hallways(self.__created_hallways, self.__hallways, Coordinate(x, y))
            return Placeholder.empty_room(hw_dic)
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
            return _MapType.WORLD, num, direction
        elif ctx.LEVEL_LITERAL():
            return _MapType.LEVEL, num, direction
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

    def visitRoom_content(self, ctx: QrogueWorldParser.Room_contentContext) -> Tuple[bool, str, str]:
        is_mandatory = ctx.OPTIONAL_LEVEL() is None
        # basically retrieves the description of the room - no explicit title, priority or position needed
        _, _, _, msg = parser_util.parse_message_body(ctx.message_body(), self.__default_speaker)
        level_to_load = parser_util.normalize_reference(ctx.REFERENCE().getText())
        return is_mandatory, msg, level_to_load

    def visitRoom(self, ctx: QrogueWorldParser.RoomContext) -> Tuple[str, Room]:
        room_id = ctx.ROOM_ID().getText()
        is_mandatory, msg, level_to_load = self.visit(ctx.room_content())
        visibility, m_type, num, orientation = self.visit(ctx.r_attributes())

        if is_mandatory and m_type == _MapType.LEVEL:
            self.__mandatory_levels.add(level_to_load)

        alt_message = Message.create_with_title("load" + room_id + "Done", Config.system_name(), "[DONE]\n" + msg,
                                                False, None)
        # the (internal) level name is also the name of the event that describes whether the level was completed or not
        message = Message.create_with_alternative("load" + room_id, Config.system_name(), msg, False,
                                                  alt_message.position, level_to_load, alt_message)
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
        for y in range(MapConfig.map_height()):
            row_ctx = ctx.l_room_row(y)
            if row_ctx:
                room_matrix.append(self.__visitL_room_row(row_ctx, y))
            else:
                break
        if ctx.l_room_row(MapConfig.map_height()):
            parser_util.warning(
                f"Too much room rows specified. Only maps of size ({MapConfig.map_width()}, "
                f"{MapConfig.map_height()}) supported. Ignoring over-specified rows.")

        return room_matrix

    def __hallway_handling(self, ctx_children: List[TerminalNodeImpl], y: int, direction: Direction):
        x = 0
        for child in ctx_children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type, QrogueWorldParser.VERTICAL_SEPARATOR):
                parser_util.warning(
                    f"Too much room columns specified. Only maps of size ({MapConfig.map_width()}, "
                    f"{MapConfig.map_height()}) supported. Ignoring over-specified columns.")
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
                parser_util.warning(f"Too much room columns specified. Only maps of size ({MapConfig.map_width()}, "
                                    f"{MapConfig.map_height()}) supported. Ignoring over-specified columns.")
                break

            if child.symbol.type == QrogueWorldParser.ROOM_ID:
                room_id = child.symbol.text  # todo make it illegal to have the same room_id twice?
                row.append(self.__load_room(room_id, x, y))
                x += 1
            elif child.symbol.type == QrogueWorldParser.EMPTY_ROOM:
                row.append(None)
                x += 1
        return row

    ##### Meta area #####

    def visitMeta(self, ctx: QrogueWorldParser.MetaContext) -> MapMetaData:
        if ctx.TEXT():
            name = parser_util.text_to_str(ctx)
        else:
            name = None
        if ctx.message_body():
            title, priority, position, msg = parser_util.parse_message_body(ctx.message_body(), self.__default_speaker)
            message = Message.create_with_title("_map_description", title, msg, priority, position)

            if ctx.MSG_EVENT():
                ref = parser_util.normalize_reference(ctx.REFERENCE().getText())
                if self.__check_achievement(ref):
                    message = Message.create_with_exception("_map_description", title, msg, priority, ref)
        else:
            message = None
        return MapMetaData(name, message, False, self.__show_description)

    ##### Start area #####

    def visitStart(self, ctx: QrogueWorldParser.StartContext) -> Tuple[str, List[List[Room]]]:
        self.__meta_data = self.visit(ctx.meta())

        # prepare hallways first because they are standalone
        self.visit(ctx.hallways())
        # next prepare the rooms because they reference hallways
        self.visit(ctx.rooms())

        # for the last step we retrieve the room matrix from layout
        return self.__meta_data, self.visit(ctx.layout())
