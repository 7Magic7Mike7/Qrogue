from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker

from dungeon_editor.parser.QrogueDungeonLexer import QrogueDungeonLexer
from dungeon_editor.parser.QrogueDungeonListener import QrogueDungeonListener
from dungeon_editor.parser.QrogueDungeonParser import QrogueDungeonParser
from dungeon_editor.parser.QrogueDungeonVisitor import QrogueDungeonVisitor
from game import collectibles
from game.actors.factory import EnemyFactory, TargetDifficulty, ExplicitEnemyFactory
from game.actors.robot import Robot
from game.callbacks import CallbackPack
from game.collectibles import pickup
from game.collectibles.factory import CollectibleFactory, OrderedCollectibleFactory
from game.logic.qubit import StateVector
from game.map import tiles
from game.map.generator import LayoutGenerator, DungeonGenerator
from game.map.map import Map
from game.map.navigation import Coordinate
from game.map.rooms import Room, WildRoom


class LayoutGenVisitor(QrogueDungeonVisitor):

    @staticmethod
    def warning(text: str):
        print("Warning: ", text)

    def visitCollectible(self, ctx:QrogueDungeonParser.CollectibleContext):
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

    def visitCollectibles(self, ctx:QrogueDungeonParser.CollectiblesContext):
        collectible_list = []
        for collectible in ctx.collectible():
            collectible_list.append(self.visit(collectible))
        return collectible_list

    def visitComplex_number(self, ctx:QrogueDungeonParser.Complex_numberContext):
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
                num = str(integer_.children[0])
            else:
                num = str(float_)
            complex_number += num

            if ctx.SIGN(1):
                complex_number += ctx.SIGN(1).symbol.text + str(imag_)
        else:
            complex_number += str(imag_)

        return complex(complex_number)

    def visitStv(self, ctx:QrogueDungeonParser.StvContext):
        amplitudes = []
        for cn in ctx.complex_number():
            amplitudes.append(self.visit(cn))
        return amplitudes


class GrammarLayoutGenerator(LayoutGenerator, QrogueDungeonListener):
    def __init__(self, seed: int, data: str):
        super().__init__(seed, Map.WIDTH, Map.HEIGHT)
        self.__data = data
        self.__rooms = {}
        self.__hallways = {}
        self.__stv_pools = {}
        self.__reward_pools = {}
        self.__default_reward_pool = None

        self.__cur_collectibles = None
        self.__cur_statevectors = None


        self.__cur_room = None
        self.__tile_descriptors = {}    # [room][type][index]

    def __add_tile_descriptor(self, type: str, ctx):
        if self.__cur_room not in self.__tile_descriptors:
            self.__tile_descriptors[self.__cur_room] = {}
        if type not in self.__tile_descriptors[self.__cur_room]:
            self.__tile_descriptors[self.__cur_room][type] = []
        self.__tile_descriptors[self.__cur_room][type].append(ctx)

    def tile_descriptor_data(self, room_id: str, type: str, index: int):
        try:
            return self.__tile_descriptors[room_id][type][index]
        except KeyError:
            return None
        except IndexError:
            return None
    
    def _add_hallway(self, room1: Coordinate, room2: Coordinate, data):
        # don't add empty hallways!
        if data != LayoutGenerator.EMPTY_HALLWAY_CODE:
            super(GrammarLayoutGenerator, self)._add_hallway(room1, room2, data)

    def check_special_rooms(self) -> bool:
        return True

    def generate(self, debug: bool = False) -> bool:
        input_stream = InputStream(self.__data)
        lexer = QrogueDungeonLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueDungeonParser(token_stream)

        visitor = LayoutGenVisitor()
        visitor.visit(parser.start())

        #ptw = ParseTreeWalker()
        #ptw.walk(self, parser.start())
        self.remove_redundant_areas()

        return True     # TODO: use meaningful metric, e.g. count occuring errors

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

    def warning(self, text: str):
        print("Warning: ", text)



    def enterCollectibles(self, ctx:QrogueDungeonParser.CollectiblesContext):
        self.__cur_collectibles = []

    def exitCollectible(self, ctx:QrogueDungeonParser.CollectibleContext):
        collectible = None
        if ctx.KEY_LITERAL():
            val = int(ctx.integer().getText())
            collectible = pickup.Key(val)
        elif ctx.COIN_LITERAL():
            val = int(ctx.integer().getText())
            collectible = pickup.Coin(val)
        elif ctx.HEALTH_LITERAL():
            val = int(ctx.integer().getText())
            collectible = pickup.Heart(val)
        elif ctx.GATE_LITERAL():
            val = int(ctx.integer().getText())
            # todo implement collectible gates
        else:
            self.warning("No legal collectible specified!")

        if collectible:
            self.__cur_collectibles.append(collectible)

    def exitReward_pool(self, ctx:QrogueDungeonParser.Reward_poolContext):
        self.__reward_pools[str(ctx.POOL_ID())] = CollectibleFactory(self.__cur_collectibles)
        self.__cur_collectibles = None

    def exitDefault_reward_pool(self, ctx:QrogueDungeonParser.Default_reward_poolContext):
        if ctx.POOL_ID():   # implicit definition
            pool_id = str(ctx.POOL_ID())
            if pool_id in self.__reward_pools:
                self.__default_reward_pool = self.__reward_pools[pool_id]
            else:
                self.warning("imports not supported yet!")
                # todo load from somewhere else?
        else:   # explicit definition
            self.__default_reward_pool = CollectibleFactory(self.__cur_collectibles)
            self.__cur_collectibles = None

        ordered = ctx.draw_strategy().children[0].symbol.type == QrogueDungeonParser.ORDERED_DRAW
        if ordered:
            self.__default_reward_pool = OrderedCollectibleFactory.from_factory(self.__default_reward_pool)


    """
    def exitInteger(self, ctx:QrogueDungeonParser.IntegerContext):
        if ctx.DIGIT():
            return int(ctx.DIGIT())
        if ctx.HALLWAY_ID():
            return int(ctx.HALLWAY_ID())
        if ctx.INTEGER():
            return int(ctx.INTEGER())
        self.warning(f"invalid integer found: {ctx}")
        return 0
    """


    def enterStvs(self, ctx:QrogueDungeonParser.StvsContext):
        self.__cur_statevectors = []

    def exitComplex_number(self, ctx:QrogueDungeonParser.Complex_numberContext):
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
                num = str(integer_.children[0])
            else:
                num = str(float_)
            complex_number += num

            if ctx.SIGN(1):
                complex_number += ctx.SIGN(1).symbol.text + str(imag_)
        else:
            complex_number += str(imag_)

        cn = complex(complex_number)

        debug = True

    def exitStv(self, ctx:QrogueDungeonParser.StvContext):
        amplitudes = []
        for complex_number in ctx.complex_number():
            debug = True
        self.__cur_statevectors.append(StateVector(amplitudes))




    def exitLayout(self, ctx:QrogueDungeonParser.LayoutContext):
        rows = ctx.l_room_row()
        if len(rows) > self.height:
            self.warning(f"Only {self.height} rows per dungeon supported but {len(rows)} provided.\n"
                         f"Ignoring all over-specified rows.")
            rows = rows[:self.height]   # get rid of the over-specification
        for y in range(self.height):
            if y >= len(rows):
                break
            self.handle_layout_row(y, rows[y])

    def handle_layout_row(self, y: int, ctx: QrogueDungeonParser.L_room_rowContext) -> [str]:
        room_ids = ctx.ROOM_ID()
        hallway_ids = ctx.HALLWAY_ID()
        if len(room_ids) > self.width:
            self.warning(f"Only {self.width} rooms per row supported but {len(room_ids)} provided.\n"
                         f"Ignoring all over-specified room and hallway ids.")
            room_ids = room_ids[:self.width]            # get rid of the over-specification
            hallway_ids = hallway_ids[:self.width-1]    # get rid of the over-specification

        for x, r_id in enumerate(room_ids):
            self._set(Coordinate(x, y), str(r_id))
        for x, hw_id in enumerate(hallway_ids):
            self._add_hallway(Coordinate(x, y), Coordinate(x + 1, y), str(hw_id))

    def enterRoom(self, ctx:QrogueDungeonParser.RoomContext):
        self.__cur_room = str(ctx.ROOM_ID())

    def exitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        self.__add_tile_descriptor(str(ctx.DIGIT()), ctx)

    def exitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        self.__add_tile_descriptor('c', ctx)

    def exitTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        self.__add_tile_descriptor('t', ctx)

    def exitEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        self.__add_tile_descriptor('e', ctx)

    def exitRoom(self, ctx:QrogueDungeonParser.RoomContext):
        self.__rooms[str(ctx.ROOM_ID())] = ctx
        self.__cur_room = None

    def handle_room_row(self, y: int, ctx: QrogueDungeonParser.RoomContext):
        pass

    def exitHallway(self, ctx:QrogueDungeonParser.HallwayContext):
        self.__hallways[str(ctx.HALLWAY_ID())] = ctx

    def exitStv_pool(self, ctx:QrogueDungeonParser.Stv_poolContext):
        self.__stv_pools[str(ctx.POOL_ID(0))] = ctx

    def exitStv_pools(self, ctx:QrogueDungeonParser.Stv_poolsContext):
        self.__stv_pools['default'] = ctx.statevectors()

    def exitStart(self, ctx:QrogueDungeonParser.StartContext):
        # check if all rooms and hallways are defined
        for y in range(self.height):
            for x in range(self.width):
                pos = Coordinate(x, y)
                room = self._get(pos)
                if room not in self.__rooms:
                    self.warning(f"\"{room}\" is not defined as room!")

                #room_hallways = self.get_hallways(pos, {})
                #for val in room_hallways.values():
                #    if val not in self.__hallways:
                #        self.warning(f"\"{val}\" is not defined as hallway!")


class GrammarDungeonGenerator(DungeonGenerator):
    def __init__(self, seed: int, data: str):
        self.__layout = GrammarLayoutGenerator(seed, data)
        super(GrammarDungeonGenerator, self).__init__(self.__layout)

    @property
    def _layout(self) -> GrammarLayoutGenerator:
        return self.__layout

    def __tile_from_descriptor(self, ctx) -> tiles.Tile:
        if ctx:
            type = ctx.children[0]
            #if QrogueDungeonParser.cu
        else:
            return tiles.Floor()

    def __enemy_from_descriptor(self, ctx: QrogueDungeonParser.Enemy_descriptorContext) -> tiles.Enemy:
        stv_pool_context = self.__layout.stv_pool_data(ctx.POOL_ID(0))

        #factory = ExplicitEnemyFactory(self.__cbp.start_fight, )
        #difficulty = TargetDifficulty()
        #tile = tiles.Enemy(factory, None, )


    def __collectible_from_descriptor(self, ctx: QrogueDungeonParser.Collectible_descriptorContext) -> tiles.Collectible:
        pass

    def __trigger_from_descriptor(self, ctx: QrogueDungeonParser.Trigger_descriptorContext) -> tiles.Trigger:
        pass

    def __energy_from_descriptor(self, ctx: QrogueDungeonParser.Energy_descriptorContext):
        pass

    def generate(self, robot: Robot, cbp: CallbackPack) -> (Map, bool):
        self.__robot = robot
        self.__cbp = cbp

        rooms = [[None for _ in range(self.width)] for _ in range(self.height)]
        spawn_room = None
        created_hallways = {}

        if self._layout.generate():
            for y in range(self.height):
                for x in range(self.width):
                    pos = Coordinate(x, y)
                    room_id = self._layout.get_room(pos)
                    room_ctx = self._layout.room_data(room_id)

                    tile_descriptor_indices = {}

                    tile_list = []
                    for ry in range(Room.INNER_HEIGHT):
                        room_row = room_ctx.r_row(ry)
                        if room_row is None:
                            tile_list += [tiles.Floor()] * Room.INNER_WIDTH
                            continue
                        row_tiles = room_row.children[1:-1]
                        for rx in range(Room.INNER_WIDTH):
                            if rx < len(row_tiles):
                                tile_ctx = row_tiles[rx]
                                tile_str = tile_ctx.children[0].symbol.text

                                if tile_str not in tile_descriptor_indices:
                                    tile_descriptor_indices[tile_str] = 0
                                index = tile_descriptor_indices[tile_str]
                                tile_ctx = self.__layout.tile_descriptor_data(room_id, tile_str, index)
                                tile_list.append(self.__tile_from_descriptor(tile_ctx))
                                tile_descriptor_indices[tile_str] = index + 1
                            else:
                                tile_list.append(tiles.Floor())

                    #room = Room()

                    room_attributes = room_ctx.r_attributes()
                    # if r_type == 'Spawn'
                    # if r_visibility == 'visible': room.make_visible()
                    # ...
        return None
