from typing import List, Tuple

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

from dungeon_editor.parser.QrogueDungeonLexer import QrogueDungeonLexer
from dungeon_editor.parser.QrogueDungeonListener import QrogueDungeonListener
from dungeon_editor.parser.QrogueDungeonParser import QrogueDungeonParser
from dungeon_editor.parser.QrogueDungeonVisitor import QrogueDungeonVisitor
from game.actors.factory import ExplicitTargetDifficulty, TargetDifficulty, EnemyFactory
from game.collectibles.collectible import Collectible, MultiCollectible
from game.actors.robot import Robot
from game.callbacks import CallbackPack
from game.collectibles import pickup
from game.collectibles import factory
from game.logic.qubit import StateVector
from game.map import tiles
from game.map.generator import LayoutGenerator, DungeonGenerator
from game.map.map import Map
from game.map.navigation import Coordinate, Direction
from game.map import rooms
from util import util_functions
from util.my_random import MyRandom
from widgets.my_popups import Popup


class TextBasedDungeonGenerator(DungeonGenerator, QrogueDungeonVisitor):
    @staticmethod
    def warning(text: str):
        print("Warning: ", text)

    def __init__(self, seed: int):
        super().__init__(seed, 0, 0)
        self.__seed = seed
        self.__cbp = None
        self.__rm = MyRandom(seed)

        self.__reward_pools = {}
        self.__default_reward_pool = None  # CollectibleFactory

        self.__stv_pools = {}
        self.__default_stv_pool = None  # ExplicitTargetDifficulty

        self.__default_enemy_factory = None

        self.__hallways_by_id = {}      # hw_id -> Door
        self._hallways = {}

        self.__enemy_groups_by_room = {}    # room_id -> dic[1-9]
        self.__rooms = {}
        self.__spawn_pos = None

        self.__created_hallways = {}    # todo check, idk why exactly we need this?

    def _add_hallway(self, room1: Coordinate, room2: Coordinate, data: tiles.Door):
        if room1 in self._hallways:
            self._hallways[room1][room2] = data
        else:
            self._hallways[room1] = {room2: data}
        if room2 in self._hallways:
            self._hallways[room2][room1] = data
        else:
            self._hallways[room2] = {room1: data}

    def get_hallways(self, pos: Coordinate, hallway_dictionary: {}) -> "dict of Direction and Hallway":
        if pos in self._hallways:
            hallways = self._hallways[pos]
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
                        hallway = rooms.Hallway(hallways[neighbor])
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

    def generate(self, robot: Robot, cbp: CallbackPack, data: str) -> (Map, bool):
        input_stream = InputStream(data)
        lexer = QrogueDungeonLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueDungeonParser(token_stream)
        parser.addErrorListener(MyErrorListener())

        self.__cbp = cbp    # needs to be accessed during creation
        try:
            room_matrix = self.visit(parser.start())
        except SyntaxError as se:
            print(se)
            return None, False


        # add empty rooms if rows don't have the same width
        max_len = 0
        for row in room_matrix:
            if len(row) > max_len:
                max_len = len(row)
        for row in room_matrix:
            if len(row) < max_len:
                row += [None] * (max_len - len(row))

        map = Map(self.__seed, room_matrix, robot, self.__spawn_pos, cbp)

        return map, True

    ##### General area

    def visitInteger(self, ctx: QrogueDungeonParser.IntegerContext) -> int:
        if ctx.DIGIT():
            return int(ctx.DIGIT().getText())
        elif ctx.HALLWAY_ID():
            return int(ctx.HALLWAY_ID().getText())
        elif ctx.INTEGER():
            return int(ctx.INTEGER().getText())
        else:
            return None

    def visitComplex_number(self, ctx: QrogueDungeonParser.Complex_numberContext) -> complex:
        if ctx.SIGN(0):
            if ctx.SIGN(0).symbol.type is QrogueDungeonParser.PLUS_SIGN:
                first_sign = "+"
            else:
                first_sign = "-"
        else:
            first_sign = "+"

        integer_ = ctx.integer()
        float_ = ctx.FLOAT()
        imag_ = ctx.IMAG_NUMBER()

        complex_number = first_sign
        if integer_ or float_:
            if integer_:
                num = str(self.visit(integer_))
            else:
                num = float_.getText()
            complex_number += num

            if ctx.SIGN(1):
                complex_number += ctx.SIGN(1).symbol.text + str(imag_)
        else:
            complex_number += str(imag_)

        return complex(complex_number)

    def visitDraw_strategy(self, ctx: QrogueDungeonParser.Draw_strategyContext) -> bool:
        """

        :param ctx:
        :return: True if strategy is 'ordered', False if it is 'random'
        """
        return ctx.ORDERED_DRAW() is not None

    ##### Reward Pool area #####

    def visitCollectible(self, ctx: QrogueDungeonParser.CollectibleContext) -> Collectible:
        if ctx.KEY_LITERAL():
            val = int(ctx.integer().getText())
            return pickup.Key(val)
        elif ctx.COIN_LITERAL():
            val = int(ctx.integer().getText())
            return pickup.Coin(val)
        elif ctx.HEALTH_LITERAL():
            val = int(ctx.integer().getText())
            return pickup.Heart(val)
        elif ctx.GATE_LITERAL():
            val = int(ctx.integer().getText())
            # todo implement collectible gates
        else:
            self.warning("No legal collectible specified!")
        return None

    def visitCollectibles(self, ctx: QrogueDungeonParser.CollectiblesContext) -> [Collectible]:
        collectible_list = []
        for collectible in ctx.collectible():
            collectible_list.append(self.visit(collectible))
        return collectible_list

    def visitReward_pool(self, ctx: QrogueDungeonParser.Reward_poolContext) -> (str, factory.CollectibleFactory):
        pool_id = ctx.POOL_ID().getText()
        collectible_list = self.visit(ctx.collectibles())
        return pool_id, collectible_list

    def visitDefault_reward_pool(self, ctx: QrogueDungeonParser.Default_reward_poolContext) \
            -> factory.CollectibleFactory:
        ordered = self.visit(ctx.draw_strategy())
        if ctx.POOL_ID():  # implicit definition
            pool_id = ctx.POOL_ID().getText()
            if pool_id in self.__reward_pools:
                if ordered:
                    return factory.OrderedCollectibleFactory(self.__reward_pools[pool_id])
                else:
                    return factory.CollectibleFactory(self.__reward_pools[pool_id])
            else:
                self.warning("imports not supported yet!")
                # todo load from somewhere else?
                return factory.CollectibleFactory([pickup.Key(999)])

        else:  # explicit definition
            collectible_list = self.visit(ctx.collectibles())
            if ordered:
                return factory.OrderedCollectibleFactory(collectible_list)
            else:
                return factory.CollectibleFactory(collectible_list)

    def visitReward_pools(self, ctx: QrogueDungeonParser.Reward_poolsContext) -> None:
        for reward_pool in ctx.reward_pool():
            pool_id, collectible_list = self.visit(reward_pool)
            self.__reward_pools[pool_id] = collectible_list
        self.__default_reward_pool = self.visit(ctx.default_reward_pool())

    ##### StateVector Pool area #####

    def visitStv(self, ctx: QrogueDungeonParser.StvContext) -> StateVector:
        amplitudes = []
        for cn in ctx.complex_number():
            amplitudes.append(self.visit(cn))
        diff = 1 - sum(amplitudes)
        # todo: instead of checking for 0 check for tolerance like in StateVector itself
        if diff == 0 and util_functions.is_power_of_2(len(amplitudes)):
            return StateVector(amplitudes)
        else:
            # todo adapt?
            return StateVector([1, 0, 0, 0])

    def visitStvs(self, ctx: QrogueDungeonParser.StvsContext) -> List[StateVector]:
        stvs = []
        for stv in ctx.stv():
            stvs.append(self.visit(stv))
        return stvs

    def visitStv_pool(self, ctx: QrogueDungeonParser.Stv_poolContext) \
            -> Tuple[List[StateVector], factory.CollectibleFactory]:
        pool_id = ctx.POOL_ID(0).getText()
        stvs = self.visit(ctx.stvs())

        reward_factory = None
        if ctx.POOL_ID(1):
            reward_pool_id = ctx.POOL_ID(1).getText()
            if reward_pool_id in self.__reward_pools:
                collectible_list = self.__reward_pools[reward_pool_id]
                if self.visit(ctx.draw_strategy()):
                    reward_factory = factory.OrderedCollectibleFactory(collectible_list)
                else:
                    reward_factory = factory.CollectibleFactory(collectible_list)
            else:
                self.warning("imports not yet supported!")

        return pool_id, stvs, reward_factory

    def visitDefault_stv_pool(self, ctx: QrogueDungeonParser.Default_stv_poolContext) -> TargetDifficulty:
        ordered = self.visit(ctx.draw_strategy())
        if ctx.POOL_ID():  # implicit definition
            pool_id = ctx.POOL_ID().getText()
            if pool_id in self.__stv_pools:
                stvs, reward_factory = self.__stv_pools[pool_id]
                return ExplicitTargetDifficulty(stvs, reward_factory, ordered)
            else:
                self.warning("imports not yet supported!")
                # todo load from somewhere else?
                temp = factory.CollectibleFactory([pickup.Key(999)])
                return ExplicitTargetDifficulty([], temp, ordered)

        else:  # explicit definition
            stv_list = self.visit(ctx.stvs())
            return ExplicitTargetDifficulty(stv_list, self.__default_reward_pool, ordered)

    def visitStv_pools(self, ctx: QrogueDungeonParser.Stv_poolsContext) -> None:
        for stv_pool in ctx.stv_pool():
            pool_id, stvs, factory = self.visit(stv_pool)
            self.__stv_pools[pool_id] = (stvs, factory)
        self.__default_stv_pool = self.visit(ctx.default_stv_pool())
        self.__default_enemy_factory = EnemyFactory(self.__cbp.start_fight, self.__default_stv_pool)

    ##### Hallway area #####

    def visitH_attributes(self, ctx: QrogueDungeonParser.H_attributesContext) -> tiles.Door:
        if ctx.DIRECTION():
            pass  # todo implement
        if ctx.OPEN_LITERAL():
            locked = False
            opened = True
        elif ctx.CLOSED_LITERAL():
            locked = False
            opened = False
        elif ctx.LOCKED_LITERAL():
            locked = True
            opened = False
        else:
            locked = False
            opened = False
            self.warning("Invalid hallway attribute: it is neither locked nor opened nor closed!")

        direction = Direction.North  # todo adapt
        # door = tiles.EntangledDoor(direction) # todo implement
        return tiles.Door(direction, locked, opened)

    def visitHallway(self, ctx: QrogueDungeonParser.HallwayContext) -> Tuple[str, rooms.Hallway]:
        hw_id = ctx.HALLWAY_ID().getText()
        door = self.visit(ctx.h_attributes())
        return hw_id, door

    def visitHallways(self, ctx: QrogueDungeonParser.HallwaysContext) -> None:
        for hallway_ctx in ctx.hallway():
            hw_id, door = self.visit(hallway_ctx)
            self.__hallways_by_id[hw_id] = door
        # todo here we could entangle the doors if needed

    ##### Room area #####

    def visitEnergy_descriptor(self, ctx: QrogueDungeonParser.Energy_descriptorContext) -> tiles.Tile:
        # todo implement energy
        return tiles.Floor()

    def visitTrigger_descriptor(self, ctx: QrogueDungeonParser.Trigger_descriptorContext) -> tiles.Trigger:
        number = self.visit(ctx.integer())

        def callback():
            Popup.message("Trigger", str(number))
        return tiles.Trigger(callback)      # todo make more useful implementation

    def visitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext) -> tiles.Collectible:
        if ctx.draw_strategy():
            ordered = self.visit(ctx.draw_strategy())
        else:
            ordered = False
        pool_id = ctx.POOL_ID().getText()
        if pool_id in self.__reward_pools:
            reward_pool = self.__reward_pools[pool_id]
            reward_factory = factory.CollectibleFactory(reward_pool)
        else:
            self.warning("Imports not yet supported! Choosing from default_reward_pool")
            reward_factory = self.__default_reward_pool

        if ordered:
            rm = None
        else:
            rm = self.__rm
        if ctx.integer():
            times = self.visit(ctx.integer())
            collectible = MultiCollectible(reward_factory.produce_multiple(rm, times))
        else:
            collectible = reward_factory.produce(rm)
        return tiles.Collectible(collectible)

    def visitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext) -> tiles.Enemy:
        enemy = None
        room_id = "1"

        def get_entangled_tiles(id: int) -> [tiles.Enemy]:
            if room_id in self.__enemy_groups_by_room:
                room_dic = self.__enemy_groups_by_room[room_id]
                return room_dic[id]
            else:
                return [enemy]

        enemy_id = int(ctx.DIGIT().getText())
        if ctx.draw_strategy(0):
            ordered = self.visit(ctx.draw_strategy(0))
        else:
            ordered = False

        pool_id = ctx.POOL_ID(0).getText()
        if pool_id in self.__stv_pools:
            stv_pool = self.__stv_pools[pool_id]
            pool_id = ctx.POOL_ID(1)
            if pool_id and pool_id in self.__reward_pools:
                reward_pool = self.__reward_pools[pool_id]
                # todo rethink draw_strategy because right now 'ordered' only affects default pools correctly
                if ctx.draw_strategy(1) and self.visit(ctx.draw_strategy(1)):
                    reward_factory = factory.OrderedCollectibleFactory(reward_pool)
                else:
                    reward_factory = factory.CollectibleFactory(reward_pool)
            else:
                reward_factory = self.__default_reward_pool
            difficulty = ExplicitTargetDifficulty(stv_pool, reward_factory, ordered)
            enemy_factory = EnemyFactory(self.__cbp.start_fight, difficulty)
        else:
            self.warning("Imports not yet supported! Choosing from default_stv_pool")
            enemy_factory = self.__default_enemy_factory

        enemy = tiles.Enemy(enemy_factory, get_entangled_tiles, id=enemy_id)
        return enemy

    def visitTile_descriptor(self, ctx:QrogueDungeonParser.Tile_descriptorContext) -> tiles.Tile:
        if ctx.enemy_descriptor():
            return self.visit(ctx.enemy_descriptor())
        elif ctx.collectible_descriptor():
            return self.visit(ctx.collectible_descriptor())
        elif ctx.trigger_descriptor():
            return self.visit(ctx.trigger_descriptor())
        elif ctx.energy_descriptor():
            return self.visit(ctx.energy_descriptor())
        else:
            self.warning("Invalid tile_descriptor! It is neither enemy, collectible, trigger or energy. "
                         "Returning tiles.Invalid() as consequence.")
            return tiles.Invalid()

    def visitTile(self, ctx:QrogueDungeonParser.TileContext) -> str:
        return ctx.getText()

    def visitR_row(self, ctx:QrogueDungeonParser.R_rowContext) -> List[str]:
        row = []
        for tile in ctx.tile():
            row.append(self.visit(tile))
        return row

    def visitR_type(self, ctx:QrogueDungeonParser.R_typeContext) -> rooms.AreaType:
        if ctx.SPAWN_LITERAL():
            return rooms.AreaType.SpawnRoom
        elif ctx.BOSS_LITERAL():
            return rooms.AreaType.BossRoom
        elif ctx.WILD_LITERAL():
            return rooms.AreaType.WildRoom
        elif ctx.SHOP_LITERAL():
            return rooms.AreaType.ShopRoom
        elif ctx.RIDDLE_LITERAL():
            return rooms.AreaType.RiddleRoom
        elif ctx.GATE_ROOM_LITERAL():
            return rooms.AreaType.GateRoom
        else:
            self.warning(f"Invalid r_type: {ctx.getText()}")
            return rooms.AreaType.Invalid

    def visitR_visibility(self, ctx:QrogueDungeonParser.R_visibilityContext) -> Tuple[bool, bool]:
        visible = False
        foggy = False
        if ctx.VISIBLE_LITERAL():
            visible = True
        elif ctx.FOGGY_LITERAL():
            foggy = True
        return visible, foggy

    def visitR_attributes(self, ctx:QrogueDungeonParser.R_attributesContext) \
            -> Tuple[Tuple[bool, bool], rooms.AreaType]:
        visibility = self.visit(ctx.r_visibility())
        type = self.visit(ctx.r_type())
        return visibility, type

    def visitRoom(self, ctx:QrogueDungeonParser.RoomContext) -> Tuple[str, rooms.CustomRoom]:
        room_id = ctx.ROOM_ID().getText()
        visibility, room_type = self.visit(ctx.r_attributes())

        # place the tiles correctly in the room
        rows = []
        for row in ctx.r_row():
            rows.append(self.visit(row))
        tile_dic = {}
        for descriptor in ctx.tile_descriptor():
            tile = self.visit(descriptor)
            if tile.code is tiles.TileCode.Enemy:
                e_id = str(tile.id)
                if e_id in tile_dic:
                    tile_dic[e_id].append(tile)
                else:
                    tile_dic[e_id] = [tile]
            else:
                if tile.code in tile_dic:
                    tile_dic[tile.code].append(tile)
                else:
                    tile_dic[tile.code] = [tile]

        def get_entangled_tiles(id: int) -> [tiles.Enemy]:
            if room_id in self.__enemy_groups_by_room:
                room_dic = self.__enemy_groups_by_room[room_id]
                return room_dic[id]
            else:
                return []

        descriptor_indices = {}
        tile_matrix = []
        for row in rows:
            matrix_row = []
            for tile_str in row:
                if tile_str in tile_dic:
                    if tile_str not in descriptor_indices:
                        descriptor_indices[tile_str] = 0
                    index = descriptor_indices[tile_str]

                    tile = tile_dic[tile_str][index]
                    if index + 1 < len(tile_dic[tile_str]):
                        descriptor_indices[tile_str] = index + 1
                else:
                    if tile_str.isdigit():
                        tile = tiles.Enemy(self.__default_enemy_factory, get_entangled_tiles, int(tile_str))
                    elif tile_str == 'c':
                        tile = tiles.Collectible(self.__default_reward_pool.produce())
                    else:
                        tile = tiles.Floor()    # todo implement the other possibilities?
                matrix_row.append(tile)
            # extended to the needed width with floors
            matrix_row += [tiles.Floor()] * (rooms.Room.INNER_WIDTH - len(matrix_row))
            tile_matrix.append(matrix_row)

        while len(tile_matrix) < rooms.Room.INNER_HEIGHT:
            tile_matrix.append([tiles.Floor()] * rooms.Room.INNER_WIDTH)

        # hallways will be added later
        room = rooms.CustomRoom(room_type, tile_matrix)
        visible, foggy = visibility
        if visible:
            room.make_visible()
        elif foggy:
            room.in_sight()
        return room_id, room

    def visitRooms(self, ctx:QrogueDungeonParser.RoomsContext):
        for room_ctx in ctx.room():
            room_id, room = self.visit(room_ctx)
            self.__rooms[room_id] = room

    ##### Layout area #####

    def visitLayout(self, ctx:QrogueDungeonParser.LayoutContext) -> List[List[rooms.Room]]:
        # first setup all hallway connections
        for y, hw_row in enumerate(ctx.l_hallway_row()):
            self.__visitL_hallway_row(hw_row, y)

        room_matrix = []
        for y in range(Map.MAX_HEIGHT):
            row_ctx = ctx.l_room_row(y)
            if row_ctx:
                room_matrix.append(self.__visitL_room_row(row_ctx, y))
            else:
                break
        if ctx.l_room_row(Map.MAX_HEIGHT):
            self.warning(f"Too much room rows specified. Only maps of size ({Map.MAX_WIDTH}, {Map.MAX_HEIGHT}) supported. "
                         f"Ignoring over-specified rows.")

        return room_matrix

    def __visitL_hallway_row(self, ctx:QrogueDungeonParser.L_hallway_rowContext, y: int) -> None:
        for x, hallway_id in enumerate(ctx.HALLWAY_ID()):
            if x >= Map.MAX_WIDTH:
                self.warning(f"Too much room columns specified. Only maps of size ({Map.MAX_WIDTH}, {Map.MAX_HEIGHT}) supported. "
                             f"Ignoring over-specified columns.")
                break
            hw_id = hallway_id.getText()
            if hw_id == '==':
                self._add_hallway(Coordinate(x, y), Coordinate(x, y + 1), tiles.Door(Direction.North))
            elif hw_id != LayoutGenerator.EMPTY_HALLWAY_CODE:
                self._add_hallway(Coordinate(x, y), Coordinate(x, y + 1), self.__hallways_by_id[hw_id])

    def __visitL_room_row(self, ctx:QrogueDungeonParser.L_room_rowContext, y: int) -> List[rooms.Room]:
        for x, hallway_id in enumerate(ctx.HALLWAY_ID()):
            if x >= Map.MAX_WIDTH:
                self.warning(f"Too much room columns specified. Only maps of size ({Map.MAX_WIDTH}, {Map.MAX_HEIGHT}) supported. "
                             f"Ignoring over-specified columns.")
                break
            hw_id = hallway_id.getText()
            if hw_id == '==':
                self._add_hallway(Coordinate(x, y), Coordinate(x + 1, y), tiles.Door(Direction.West))
            elif hw_id != LayoutGenerator.EMPTY_HALLWAY_CODE:
                self._add_hallway(Coordinate(x, y), Coordinate(x + 1, y), self.__hallways_by_id[hw_id])

        row = []
        for x, room_id in enumerate(ctx.ROOM_ID()):
            room_id = room_id.getText()
            if room_id in self.__rooms:
                room = self.__rooms[room_id]
                hw_dic = self.get_hallways(Coordinate(x, y), self.__created_hallways)
                row.append(room.copy(hw_dic))
                if room.type is rooms.AreaType.SpawnRoom:
                    if self.__spawn_pos:
                        self.warning("A second SpawnRoom was defined! Ignoring the first one "
                                     "and using this one as SpawnRoom.")
                    self.__spawn_pos = Coordinate(x, y)
            elif room_id == 'SR':
                hw_dic = self.get_hallways(Coordinate(x, y), self.__created_hallways)
                room = rooms.SpawnRoom(None, hw_dic[Direction.North], hw_dic[Direction.East], hw_dic[Direction.South],
                                       hw_dic[Direction.West])
                row.append(room)
                if self.__spawn_pos:
                    self.warning("A second SpawnRoom was defined! Ignoring the first one "
                                 "and using this one as SpawnRoom.")
                self.__spawn_pos = Coordinate(x, y)
            else:
                self.warning("room_id not specified and imports not yet supported! "
                             "Placing an empty room instead.")
                #row.append(rooms.Placeholder.empty_room())
                row.append(rooms.SpawnRoom())
        return row

    ##### Start area #####

    def visitStart(self, ctx:QrogueDungeonParser.StartContext) -> List[List[rooms.Room]]:
        # prepare reward pools first because they are standalone
        self.visit(ctx.reward_pools())
        # prepare state vector pools next because they can only reference reward pools
        self.visit(ctx.stv_pools())

        # prepare hallways next because they are standalone but thematically more connected to rooms
        self.visit(ctx.hallways())
        # now prepare the rooms because they can reference everything above
        self.visit(ctx.rooms())

        # for the last step we retrieve the room matrix from layout
        return self.visit(ctx.layout())


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


class GrammarLayoutGenerator(QrogueDungeonListener):
    def exitRoom(self, ctx:QrogueDungeonParser.RoomContext):
        print("test")


    def remove_redundant_areas(self):
        """
        Trims the map to its minimal size without removing or adding ways to
        access any room. Is useful if a small map is specified that would otherwise
        be displayed on the top left of the screen because of all the empty rooms
        in the bottom right.
        :return:
        """
        redundant_rows = [True] * self.height
        redundant_cols = [True] * self.width

        for y in range(self.height):
            for x in range(self.width):
                room = self._get(Coordinate(x, y))
                if str(room) != LayoutGenerator.EMPTY_ROOM_CODE:
                    redundant_rows[y] = False
                    redundant_cols[x] = False

        new_height = redundant_rows.count(False)
        new_width = redundant_cols.count(False)
        new_map = [[LayoutGenerator.EMPTY_ROOM_CODE] * new_width for _ in range(new_height)]
        new_y = 0
        for y in range(self.height):
            if not redundant_rows[y]:
                new_x = 0
                for x in range(self.width):
                    if not redundant_cols[x]:
                        new_map[new_y][new_x] = self._get(Coordinate(new_x, new_y))
                        new_x += 1
                new_y += 1
        self._reset_map(new_map)

    def layout_string(self) -> str:
        text = ""
        for y in range(self.height):
            for x in range(self.width):
                val = self._get(Coordinate(x, y))
                text += f"{val} "
            text += "\n"
        return text
