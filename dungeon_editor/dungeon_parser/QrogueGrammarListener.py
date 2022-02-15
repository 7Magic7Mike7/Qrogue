from typing import Callable, List, Tuple, Dict

from antlr4.tree.Tree import TerminalNodeImpl
from antlr4 import InputStream, CommonTokenStream

from dungeon_editor import parser_util
from dungeon_editor.dungeon_parser.QrogueDungeonLexer import QrogueDungeonLexer
from dungeon_editor.dungeon_parser.QrogueDungeonParser import QrogueDungeonParser
from dungeon_editor.dungeon_parser.QrogueDungeonVisitor import QrogueDungeonVisitor
from game.achievements import AchievementManager
from game.actors.factory import ExplicitTargetDifficulty, TargetDifficulty, EnemyFactory
from game.actors.riddle import Riddle
from game.actors.robot import Robot, TestBot
from game.callbacks import CallbackPack
from game.collectibles import pickup, factory
from game.collectibles.collectible import Collectible, MultiCollectible, ShopItem
from game.logic import instruction
from game.logic.qubit import StateVector
from game.map import rooms
from game.map import tiles
from game.map.generator import DungeonGenerator
from game.map.level_map import LevelMap
from game.map.map import Map
from game.map.navigation import Coordinate, Direction
from util import util_functions
from util.config import Config, PathConfig
from util.my_random import MyRandom
from widgets.my_popups import Popup


class TextBasedDungeonGenerator(DungeonGenerator, QrogueDungeonVisitor):
    __DEFAULT_NUM_OF_SHOP_ITEMS = 3
    __DEFAULT_NUM_OF_RIDDLE_ATTEMPTS = 7

    @staticmethod
    def warning(text: str):
        parser_util.warning(text)

    @staticmethod
    def __normalize_reference(reference: str) -> str:
        return parser_util.normalize_reference(reference)

    @staticmethod
    def __tile_str_to_code(tile_str: str) -> tiles.TileCode:
        if tile_str.isdigit():
            return tiles.TileCode.Enemy

        elif tile_str == parser_util.COLLECTIBLE_TILE:
            return tiles.TileCode.Collectible
        elif tile_str == parser_util.TRIGGER_TILE:
            return tiles.TileCode.Trigger
        elif tile_str == parser_util.MESSAGE_TILE:
            return tiles.TileCode.Message
        elif tile_str == parser_util.ENERGY_TILE:
            return tiles.TileCode.Energy
        elif tile_str == parser_util.RIDDLER_TILE:
            return tiles.TileCode.Riddler
        elif tile_str == parser_util.SHOP_KEEPER_TILE:
            return tiles.TileCode.ShopKeeper
        elif tile_str == parser_util.FLOOR_TILE:
            return tiles.TileCode.Floor
        else:
            return tiles.TileCode.Invalid

    @staticmethod
    def __tile_code_to_str(tile_code: tiles.TileCode) -> str:
        if tile_code is tiles.TileCode.Enemy:
            # todo print warning?
            return "0"
        elif tile_code is tiles.TileCode.Collectible:
            return parser_util.COLLECTIBLE_TILE
        elif tile_code is tiles.TileCode.Trigger:
            return parser_util.TRIGGER_TILE
        elif tile_code is tiles.TileCode.Message:
            return parser_util.MESSAGE_TILE
        elif tile_code is tiles.TileCode.Energy:
            return parser_util.ENERGY_TILE
        elif tile_code is tiles.TileCode.Riddler:
            return parser_util.RIDDLER_TILE
        elif tile_code is tiles.TileCode.ShopKeeper:
            return parser_util.SHOP_KEEPER_TILE
        elif tile_code is tiles.TileCode.Floor:
            return parser_util.FLOOR_TILE
        else:
            # todo print warning?
            return None

    def __init__(self, seed: int, load_map_callback: Callable[[str, Coordinate], None],
                 achievement_manager: AchievementManager):
        super().__init__(seed, 0, 0)
        self.__seed = seed
        self.__load_map = load_map_callback
        self.__achievement_manager = achievement_manager

        self.__cbp = None
        self.__robot = None
        self.__rm = MyRandom(seed)

        self.__messages = {}        # str -> str

        self.__reward_pools = {}
        self.__default_reward_factory = None  # CollectibleFactory

        self.__stv_pools = {}           # str -> Tuple[List[StateVector], CollectibleFactory] (latter may be None)
        self.__default_target_difficulty = None  # ExplicitTargetDifficulty

        self.__default_enemy_factory = None     # needed to create default_tile enemies

        self.__hallways_by_id = {}      # hw_id -> Door
        self.__hallways = {}            # stores the

        #self.__template_events = PathConfig.read()
        self.__events = []

        self.__enemy_groups_by_room = {}    # room_id -> dic[1-9]
        self.__cur_room_id = None   # needed for enemy groups
        self.__rooms = {}
        self.__spawn_pos = None

        # holds references to already created hallways so that neighbors can use it instead of
        # creating their own, redundant hallway
        self.__created_hallways = {}

    def _add_hallway(self, room1: Coordinate, room2: Coordinate, door: tiles.Door):
        if door:    # for simplicity door could be null so we check it here
            if room1 in self.__hallways:
                self.__hallways[room1][room2] = door
            else:
                self.__hallways[room1] = {room2: door}
            if room2 in self.__hallways:
                self.__hallways[room2][room1] = door
            else:
                self.__hallways[room2] = {room1: door}

    def __get_hallways(self, pos: Coordinate) -> "dict of Direction and Hallway":
        return parser_util.get_hallways(self.__created_hallways, self.__hallways, pos)

    def __get_default_tile(self, tile_str: str, enemy_dic: Dict[int, List[tiles.Enemy]],
                           get_entangled_tiles: Callable[[int], List[tiles.Tile]]) -> tiles.Tile:
        if tile_str == parser_util.PLACE_HOLDER_TILE:
            return tiles.Floor()

        tile_code = TextBasedDungeonGenerator.__tile_str_to_code(tile_str)
        if tile_code is tiles.TileCode.Enemy:
            enemy_id = int(tile_str)
            enemy = tiles.Enemy(self.__default_enemy_factory, get_entangled_tiles, enemy_id)
            if enemy_id not in enemy_dic:
                enemy_dic[enemy_id] = []
            enemy_dic[enemy_id].append(enemy)
            return enemy

        elif tile_code is tiles.TileCode.Collectible:
            return tiles.Collectible(self.__default_reward_factory.produce(self.__rm))

        elif tile_code is tiles.TileCode.Trigger:
            return self.__load_trigger("*defaultTrigger")

        elif tile_code is tiles.TileCode.Message:
            # todo is it okay to print this?
            return tiles.Message(Popup(Config.scientist_name(), "Hmm, I don't know what to say.", show=False))

        elif tile_code is tiles.TileCode.Energy:
            return tiles.Collectible(pickup.Energy())

        elif tile_code is tiles.TileCode.Riddler:
            stv = self.__default_target_difficulty.create_statevector(self.__robot, self.__rm)
            reward = self.__default_reward_factory.produce(self.__rm)
            riddle = Riddle(stv, reward, self.__DEFAULT_NUM_OF_RIDDLE_ATTEMPTS)
            return tiles.Riddler(self.__cbp.open_riddle, riddle)

        elif tile_code is tiles.TileCode.ShopKeeper:
            items = self.__default_reward_factory.produce_multiple(self.__rm, self.__DEFAULT_NUM_OF_SHOP_ITEMS)
            return tiles.ShopKeeper(self.__cbp.visit_shop, [ShopItem(item) for item in items])

        elif tile_code is tiles.TileCode.Floor:
            return tiles.Floor()

        else:
            self.warning(f"Unknown tile specified: {tile_str}. Using a Floor-Tile instead.")
            return tiles.Floor()

    def generate(self, cbp: CallbackPack, file_name: str) -> Tuple[LevelMap, bool]:
        map_data = PathConfig.read_level(file_name)

        input_stream = InputStream(map_data)
        lexer = QrogueDungeonLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueDungeonParser(token_stream)
        parser.addErrorListener(parser_util.MyErrorListener())

        self.__cbp = cbp        # needs to be accessed during creation
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

        map = LevelMap(file_name, self.__seed, room_matrix, self.__robot, self.__spawn_pos, self.__achievement_manager)
        return map, True

    ##### load from references #####

    def __load_reward_pool(self, reference: str) -> List[Collectible]:
        if reference in self.__reward_pools:
            return self.__reward_pools[reference]

        ref = self.__normalize_reference(reference)
        if ref in ['coin', 'coins']:
            return [pickup.Coin(1)]
        elif ref in ['key', 'keys']:
            return [pickup.Key(1)]
        elif ref in ['hp', 'health', 'heart', 'hearts', 'healthPoints']:
            return [pickup.Heart(1)]
        else:
            self.warning(f"Imports not yet supported: {reference}")
            # todo load from somewhere else?
            return [pickup.Key(0)]

    def __load_stv_pool(self, reference: str, ordered: bool = False) -> TargetDifficulty:
        if reference in self.__stv_pools:
            stv_list, reward_factory = self.__stv_pools[reference]
            if not reward_factory:
                reward_factory = self.__default_reward_factory
            return ExplicitTargetDifficulty(stv_list, reward_factory, ordered)
        else:
            # todo implement imports

            return self.__default_target_difficulty

    def __load_gate(self, reference: str) -> instruction.Instruction:
        ref = self.__normalize_reference(reference)
        if ref in ['x', 'xgate']:
            return instruction.XGate()
        elif ref in ['y', 'ygate']:
            return instruction.YGate()
        elif ref in ['z', 'zgate']:
            return instruction.ZGate()
        elif ref in ['h', 'hgate', 'hadamard', 'hadamarggate']:
            return instruction.HGate()
        elif ref in ['cx', 'cxgate']:
            return instruction.CXGate()
        elif ref in ['swap', 'swapgate']:
            return instruction.SwapGate()

        elif ref not in ['i', 'igate']:
            self.warning(f"Unknown gate reference: {reference}. Returning I Gate instead.")
        return instruction.IGate()

    def __load_trigger(self, reference: str) -> tiles.Trigger:
        if reference.startswith("tp"):
            # teleport trigger
            ref = reference[2:]
            if ref.startswith("l"):
                level = ref[1:]
            elif ref.startswith("w"):
                world = ref[1:]

        # todo implement
        def callback(direction: Direction, robot: Robot):
            Popup.message("Trigger", str(reference))


        return tiles.Trigger(callback)

    def __load_message(self, reference: str) -> str:
        if reference in self.__messages:
            return self.__messages[reference]
        norm_ref = self.__normalize_reference(reference)
        if norm_ref in self.__messages:
            return self.__messages[norm_ref]
        else:
            self.warning(f"Unknown text reference: {reference}. Returning \"Message not found!\"")
            return "Message not found!"

    def __load_hallway(self, reference: str) -> tiles.Door:
        if reference in self.__hallways_by_id:
            return self.__hallways_by_id[reference]
        elif reference == parser_util.EMPTY_HALLWAY_CODE:
            return None
        elif reference == parser_util.DEFAULT_HALLWAY_STR:
            return tiles.Door(Direction.North)
        else:
            # todo implement hallway imports
            return tiles.Door(Direction.North)

    def __load_room(self, reference: str, x: int, y: int) -> rooms.Room:
        if reference in self.__rooms:
            room = self.__rooms[reference]
            if room.type is rooms.AreaType.SpawnRoom:
                if self.__spawn_pos:
                    self.warning("A second SpawnRoom was defined! Ignoring the first one "
                                 "and using this one as SpawnRoom.")
                self.__spawn_pos = Coordinate(x, y)
            hw_dic = self.__get_hallways(Coordinate(x, y))
            return room.copy(hw_dic)
        elif self.__normalize_reference(reference) == 'sr':
            hw_dic = self.__get_hallways(Coordinate(x, y))
            room = rooms.SpawnRoom(self.__load_map, None, hw_dic[Direction.North], hw_dic[Direction.East],
                                   hw_dic[Direction.South], hw_dic[Direction.West])
            if self.__spawn_pos:
                self.warning("A second SpawnRoom was defined! Ignoring the first one and using this one as "
                             "SpawnRoom.")
            self.__spawn_pos = Coordinate(x, y)
            return room
        elif reference[0] == '_':
            # todo handle templates
            pass
        else:
            self.warning(f"room_id \"{reference}\" not specified and imports not yet supported! "
                         "Placing an empty room instead.")
            # row.append(rooms.Placeholder.empty_room())
        return rooms.SpawnRoom(self.__load_map)

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

    ##### Message area ######

    def visitMessages(self, ctx:QrogueDungeonParser.MessagesContext):
        self.__messages.clear()
        for i, ref in enumerate(ctx.REFERENCE()):
            ref = self.__normalize_reference(ref.getText())
            text = ctx.TEXT(i).getText()[1:-1]  # skip the encapsulating \"
            self.__messages[ref] = text

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
            reference = ctx.REFERENCE().getText()
            return self.__load_gate(reference)
        else:
            self.warning("No legal collectible specified!")
        return None

    def visitCollectibles(self, ctx: QrogueDungeonParser.CollectiblesContext) -> [Collectible]:
        collectible_list = []
        for collectible in ctx.collectible():
            collectible_list.append(self.visit(collectible))
        return collectible_list

    def visitReward_pool(self, ctx: QrogueDungeonParser.Reward_poolContext) -> (str, factory.CollectibleFactory):
        pool_id = ctx.REFERENCE().getText()
        collectible_list = self.visit(ctx.collectibles())
        return pool_id, collectible_list

    def visitDefault_reward_pool(self, ctx: QrogueDungeonParser.Default_reward_poolContext) \
            -> factory.CollectibleFactory:
        ordered = self.visit(ctx.draw_strategy())
        if ctx.REFERENCE():  # implicit definition
            pool_id = ctx.REFERENCE().getText()
            reward_pool = self.__load_reward_pool(pool_id)
            if ordered:
                return factory.OrderedCollectibleFactory(reward_pool)
            else:
                return factory.CollectibleFactory(reward_pool)

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
        self.__default_reward_factory = self.visit(ctx.default_reward_pool())

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
            return StateVector([1, 0, 0, 0, 0, 0, 0, 0])

    def visitStvs(self, ctx: QrogueDungeonParser.StvsContext) -> List[StateVector]:
        stvs = []
        for stv in ctx.stv():
            stvs.append(self.visit(stv))
        return stvs

    def visitStv_pool(self, ctx: QrogueDungeonParser.Stv_poolContext) \
            -> Tuple[str, List[StateVector], factory.CollectibleFactory]:
        pool_id = ctx.REFERENCE(0).getText()
        stvs = self.visit(ctx.stvs())

        reward_factory = None
        if ctx.REFERENCE(1):
            reward_pool_id = ctx.REFERENCE(1).getText()
            if reward_pool_id in self.__reward_pools:
                collectible_list = self.__reward_pools[reward_pool_id]
            else:
                collectible_list = self.__load_reward_pool(reward_pool_id)
            if self.visit(ctx.draw_strategy()):
                reward_factory = factory.OrderedCollectibleFactory(collectible_list)
            else:
                reward_factory = factory.CollectibleFactory(collectible_list)

        return pool_id, stvs, reward_factory

    def visitDefault_stv_pool(self, ctx: QrogueDungeonParser.Default_stv_poolContext) -> TargetDifficulty:
        ordered = self.visit(ctx.draw_strategy())
        if ctx.REFERENCE():  # implicit definition
            pool_id = ctx.REFERENCE().getText()
            return self.__load_stv_pool(pool_id, ordered)

        else:  # explicit definition
            stv_list = self.visit(ctx.stvs())
            return ExplicitTargetDifficulty(stv_list, self.__default_reward_factory, ordered)

    def visitStv_pools(self, ctx: QrogueDungeonParser.Stv_poolsContext) -> None:
        for stv_pool in ctx.stv_pool():
            pool_id, stvs, reward_factory = self.visit(stv_pool)
            self.__stv_pools[pool_id] = (stvs, reward_factory)
        self.__default_target_difficulty = self.visit(ctx.default_stv_pool())
        self.__default_enemy_factory = EnemyFactory(self.__cbp.start_fight, self.__default_target_difficulty)

    ##### Hallway area #####

    def visitH_attributes(self, ctx: QrogueDungeonParser.H_attributesContext) -> tiles.Door:
        direction = Direction.North  # todo adapt
        one_way_state = tiles.DoorOneWayState.NoOneWay
        if ctx.DIRECTION():
            dir_str = ctx.DIRECTION().getText()
            if dir_str == "North":
                direction = Direction.North
            elif dir_str == "East":
                direction = Direction.East
            elif dir_str == "South":
                direction = Direction.South
            elif dir_str == "West":
                direction = Direction.West
            if ctx.PERMANENT_LITERAL():
                one_way_state = tiles.DoorOneWayState.Permanent
            else:
                one_way_state = tiles.DoorOneWayState.Temporary

        event_id = None
        if ctx.OPEN_LITERAL():
            open_state = tiles.DoorOpenState.Open
        elif ctx.CLOSED_LITERAL():
            open_state = tiles.DoorOpenState.Closed
        elif ctx.LOCKED_LITERAL():
            open_state = tiles.DoorOpenState.KeyLocked
        elif ctx.EVENT_LITERAL():
            # todo implement
            if ctx.REFERENCE():
                event_id = TextBasedDungeonGenerator.__normalize_reference(ctx.REFERENCE().getText())
                open_state = tiles.DoorOpenState.EventLocked
            else:
                open_state = tiles.DoorOpenState.Closed
                self.warning("Event lock specified without an event id! Ignoring the lock and placing a closed door "
                             "instead.")
        else:
            open_state = tiles.DoorOpenState.Closed
            self.warning("Invalid hallway attribute: it is neither locked nor opened nor closed!")

        # door = tiles.EntangledDoor(direction) # todo implement
        return tiles.Door(direction, open_state, one_way_state, event_id)

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

    def visitShop_descriptor(self, ctx:QrogueDungeonParser.Shop_descriptorContext) -> tiles.ShopKeeper:
        if ctx.REFERENCE():
            pool_id = ctx.REFERENCE().getText()
            item_pool = self.__load_reward_pool(pool_id)
        else:
            item_pool = self.visit(ctx.collectibles())

        num_of_items = self.visit(ctx.integer())
        shop_factory = factory.CollectibleFactory(item_pool)
        items = shop_factory.produce_multiple(self.__rm, num_of_items)
        return tiles.ShopKeeper(self.__cbp.visit_shop, [ShopItem(item) for item in items])

    def visitRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext) -> tiles.Riddler:
        ref_index = 0
        if ctx.stv():
            stv = self.visit(ctx.stv())
        else:
            pool_id = ctx.REFERENCE(ref_index).getText()
            ref_index = 1
            difficulty = self.__load_stv_pool(pool_id, ordered=False)
            stv = difficulty.create_statevector(self.__robot, self.__rm)

        if ctx.collectible():
            reward = self.visit(ctx.collectible())
        else:
            pool_id = ctx.REFERENCE(ref_index).getText()
            reward_pool = self.__load_reward_pool(pool_id)
            reward = self.__rm.get_element(reward_pool)     # todo check if we should wrap it in a factory?

        riddle = Riddle(stv, reward)
        return tiles.Riddler(self.__cbp.open_riddle, riddle)

    def visitEnergy_descriptor(self, ctx: QrogueDungeonParser.Energy_descriptorContext) -> tiles.Tile:
        amount = self.visit(ctx.integer())
        return tiles.Energy(amount)

    def visitTrigger_descriptor(self, ctx: QrogueDungeonParser.Trigger_descriptorContext) -> tiles.Trigger:
        reference = ctx.REFERENCE().getText()
        return self.__load_trigger(reference)

    def visitMessage_descriptor(self, ctx: QrogueDungeonParser.Message_descriptorContext) -> tiles.Message:
        times = self.visit(ctx.integer())
        reference = ctx.REFERENCE().getText()
        text = self.__load_message(reference)
        popup = Popup(Config.scientist_name(), text, show=False)
        return tiles.Message(popup, times)

    def visitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext) -> tiles.Collectible:
        # only draw ordered if it is explicitly stated like this
        if ctx.draw_strategy() and self.visit(ctx.draw_strategy()):
            rm = None
        else:
            rm = self.__rm

        pool_id = ctx.REFERENCE().getText()
        reward_pool = self.__load_reward_pool(pool_id)
        reward_factory = factory.CollectibleFactory(reward_pool)

        times = 1
        if ctx.integer():
            times = self.visit(ctx.integer())
        if times > 1:
            collectible = MultiCollectible(reward_factory.produce_multiple(rm, times))
        else:
            collectible = reward_factory.produce(rm)
        return tiles.Collectible(collectible)

    def visitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext) -> tiles.Enemy:
        enemy = None
        if self.__cur_room_id:
            room_id = self.__cur_room_id
        else:
            raise NotImplementedError()     # todo better check

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

        pool_id = ctx.REFERENCE(0).getText()
        if pool_id in self.__stv_pools:
            stv_pool, reward_factory = self.__stv_pools[pool_id]
            pool_id = ctx.REFERENCE(1)
            if pool_id and pool_id in self.__reward_pools:
                reward_pool = self.__reward_pools[pool_id]
                # todo rethink draw_strategy because right now 'ordered' only affects default pools correctly
                if ctx.draw_strategy(1) and self.visit(ctx.draw_strategy(1)):
                    reward_factory = factory.OrderedCollectibleFactory(reward_pool)
                else:
                    reward_factory = factory.CollectibleFactory(reward_pool)
            elif not reward_factory:
                reward_factory = self.__default_reward_factory
            difficulty = ExplicitTargetDifficulty(stv_pool, reward_factory, ordered)
            enemy_factory = EnemyFactory(self.__cbp.start_fight, difficulty)
        else:
            self.warning("Imports not yet supported! Choosing from default_stv_pool")
            enemy_factory = self.__default_enemy_factory

        enemy = tiles.Enemy(enemy_factory, get_entangled_tiles, id=enemy_id)
        if room_id not in self.__enemy_groups_by_room:
            self.__enemy_groups_by_room[room_id] = {}
        if enemy_id not in self.__enemy_groups_by_room[room_id]:
            self.__enemy_groups_by_room[room_id][enemy_id] = []
        self.__enemy_groups_by_room[room_id][enemy_id].append(enemy)
        return enemy

    def visitTile_descriptor(self, ctx:QrogueDungeonParser.Tile_descriptorContext) -> tiles.Tile:
        if ctx.trigger_descriptor():
            return self.visit(ctx.trigger_descriptor())

        if ctx.enemy_descriptor():
            tile = self.visit(ctx.enemy_descriptor())
        elif ctx.collectible_descriptor():
            tile = self.visit(ctx.collectible_descriptor())
        elif ctx.energy_descriptor():
            tile = self.visit(ctx.energy_descriptor())
        elif ctx.riddle_descriptor():
            tile = self.visit(ctx.riddle_descriptor())
        elif ctx.shop_descriptor():
            tile = self.visit(ctx.shop_descriptor())
        elif ctx.message_descriptor():
            tile = self.visit(ctx.message_descriptor())
        else:
            self.warning("Invalid tile_descriptor! It is neither enemy, collectible, trigger or energy. "
                         "Returning tiles.Invalid() as consequence.")
            return tiles.Invalid()

        if ctx.REFERENCE() and isinstance(tile, tiles.WalkTriggerTile):
            event_id = TextBasedDungeonGenerator.__normalize_reference(ctx.REFERENCE().getText())
            tile.set_event(event_id)
        return tile

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
        self.__cur_room_id = ctx.ROOM_ID().getText()
        visibility, room_type = self.visit(ctx.r_attributes())

        # place the tiles correctly in the room
        rows = []
        for row in ctx.r_row():
            rows.append(self.visit(row))
        tile_dic = {}
        for descriptor in ctx.tile_descriptor():
            tile = self.visit(descriptor)
            if tile.code is tiles.TileCode.Enemy:
                tile_str = str(tile.id)
            else:
                tile_str = TextBasedDungeonGenerator.__tile_code_to_str(tile.code)
            if tile_str in tile_dic:
                tile_dic[tile_str].append(tile)
            else:
                tile_dic[tile_str] = [tile]

        # this local method is needed here for not explicitely defined enemies
        # but since we are already in a room we don't have to reference to global data
        enemy_dic = {}
        def get_entangled_tiles(id: int) -> List[tiles.Enemy]:
            if id in enemy_dic:
                return enemy_dic[id]
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
                    tile = self.__get_default_tile(tile_str, enemy_dic, get_entangled_tiles)
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
        return self.__cur_room_id, room

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

    def __hallway_handling(self, ctx_children: List[TerminalNodeImpl], y: int, direction: Direction):
        x = 0
        for child in ctx_children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type, QrogueDungeonParser.VERTICAL_SEPARATOR):
                self.warning(
                    f"Too much room columns specified. Only maps of size ({Map.MAX_WIDTH}, {Map.MAX_HEIGHT}) supported. "
                    f"Ignoring over-specified columns.")
                break
            if child.symbol.type == QrogueDungeonParser.HALLWAY_ID:
                hw_id = child.symbol.text
                origin = Coordinate(x, y)
                self._add_hallway(origin, origin + direction, self.__load_hallway(hw_id))
                x += 1
            elif child.symbol.type == QrogueDungeonParser.EMPTY_HALLWAY:
                x += 1

    def __visitL_hallway_row(self, ctx:QrogueDungeonParser.L_hallway_rowContext, y: int) -> None:
        self.__hallway_handling(ctx.children, y, Direction.South)    # connect downwards to the next room row

    def __visitL_room_row(self, ctx:QrogueDungeonParser.L_room_rowContext, y: int) -> List[rooms.Room]:
        self.__hallway_handling(ctx.children, y, Direction.East)     # connect to the right to the next room

        row = []
        x = 0
        for child in ctx.children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type, QrogueDungeonParser.VERTICAL_SEPARATOR):
                self.warning( f"Too much room columns specified. Only maps of size ({Map.MAX_WIDTH}, {Map.MAX_HEIGHT}) "
                              "supported. Ignoring over-specified columns.")
                break

            if child.symbol.type == QrogueDungeonParser.ROOM_ID:
                room_id = child.symbol.text     # todo make it illegal to have the same room_id twice?
                row.append(self.__load_room(room_id, x, y))
                x += 1
            elif child.symbol.type == QrogueDungeonParser.EMPTY_ROOM:
                row.append(None)
                x += 1
        return row

    ##### Robot area #####

    def visitRobot(self, ctx:QrogueDungeonParser.RobotContext) -> None:
        num_of_qubits = int(ctx.DIGIT().getText())
        gates = []
        for ref in ctx.REFERENCE():
            gates.append(self.__load_gate(ref.getText()))  # todo what about pickups?

        self.__robot = TestBot(num_of_qubits, gates)

    ##### Start area #####

    def visitStart(self, ctx:QrogueDungeonParser.StartContext) -> List[List[rooms.Room]]:
        # prepare the robot
        self.visit(ctx.robot())

        # prepare messages
        self.visit(ctx.messages())

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
