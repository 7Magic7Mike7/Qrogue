from typing import Callable, List, Tuple, Dict, Optional

from antlr4 import InputStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNodeImpl

from qrogue.game.logic import Message, StateVector
from qrogue.game.logic.actors import Controllable, Riddle
from qrogue.game.logic.actors.controllables import TestBot
from qrogue.game.logic.collectibles import Collectible, pickup, instruction, MultiCollectible, Qubit, ShopItem, \
    CollectibleFactory, OrderedCollectibleFactory
from qrogue.game.target_factory import EnemyFactory, ExplicitTargetDifficulty
from qrogue.game.world import tiles
from qrogue.game.world.map import CallbackPack, LevelMap, rooms
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import Config, HelpText, MapConfig, PathConfig, Logger, CommonQuestions, RandomManager

from . import parser_util
from .generator import DungeonGenerator
from .dungeon_parser.QrogueDungeonLexer import QrogueDungeonLexer
from .dungeon_parser.QrogueDungeonParser import QrogueDungeonParser
from .dungeon_parser.QrogueDungeonVisitor import QrogueDungeonVisitor


class QrogueLevelGenerator(DungeonGenerator, QrogueDungeonVisitor):
    __DEFAULT_NUM_OF_SHOP_ITEMS = 3
    __DEFAULT_NUM_OF_RIDDLE_ATTEMPTS = 7
    __ROBOT_NO_GATES = "none"
    __SPAWN_ROOM_ID = "SR"

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
        elif tile_str == parser_util.OBSTACLE_TILE:
            return tiles.TileCode.Obstacle
        else:
            return tiles.TileCode.Invalid

    @staticmethod
    def __tile_code_to_str(tile_code: tiles.TileCode) -> Optional[str]:
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

    def __init__(self, seed: int, check_achievement: Callable[[str], bool], trigger_event: Callable[[str], None],
                 load_map_callback: Callable[[str, Coordinate], None]):
        super(QrogueLevelGenerator, self).__init__(seed, 0, 0)
        self.__seed = seed
        self.__check_achievement = check_achievement
        self.__trigger_event = trigger_event
        self.__load_map = load_map_callback
        self.__place_sr_teleporter = True

        self.__warnings = 0
        self.__robot = None
        self.__rm = RandomManager.create_new(seed)

        self.__messages = {}        # str -> str

        self.__reward_pools = {}
        self.__default_reward_factory = None  # CollectibleFactory

        self.__stv_pools = {}           # str -> Tuple[List[StateVector], CollectibleFactory] (latter may be None)
        self.__default_target_difficulty = None  # ExplicitTargetDifficulty

        self.__default_enemy_factory = None     # needed to create default_tile enemies

        self.__hallways_by_id = {}      # hw_id -> Door
        self.__hallways = {}            # stores the
        self.__entanglement_locks = set()     # stores hw_id of activated entanglement_locks

        #self.__template_events = PathConfig.read()
        self.__events = []

        self.__enemy_groups_by_room = {}    # room_id -> Dict[1-9] -> List[tiles.Enemy]
        self.__cur_room_id = None   # needed for enemy groups
        self.__rooms = {}
        self.__spawn_pos = None

        # holds references to already created hallways so that neighbors can use it instead of
        # creating their own, redundant hallway
        self.__created_hallways = {}

    @property
    def __cbp(self) -> CallbackPack:
        return CallbackPack.instance()

    def warning(self, text: str):
        parser_util.warning(text)
        self.__warnings += 1

    def generate(self, file_name: str, in_dungeon_folder: bool = True) -> Tuple[Optional[LevelMap], bool]:
        map_data = PathConfig.read_level(file_name, in_dungeon_folder)

        input_stream = InputStream(map_data)
        lexer = QrogueDungeonLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueDungeonParser(token_stream)
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

        if self.__spawn_pos is None:
            raise SyntaxError("No SpawnRoom provided! Make sure to place 'SR' in the layout and if you defined a "
                              "custom SpawnRoom make sure to tag it as (Spawn).")
        level = LevelMap(name, file_name, self.__seed, room_matrix, self.__robot, self.__spawn_pos,
                         self.__check_achievement, self.__trigger_event)
        return level, True

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

    def __get_default_tile(self, tile_str: str, enemy_dic: Dict[int, List[tiles.Enemy]],
                           get_entangled_enemies: Callable[[int], List[tiles.Enemy]],
                           update_entangled_groups: Callable[[tiles.Enemy], None]) -> tiles.Tile:
        if tile_str == parser_util.PLACE_HOLDER_TILE:
            return tiles.Floor()

        tile_code = QrogueLevelGenerator.__tile_str_to_code(tile_str)
        if tile_code is tiles.TileCode.Enemy:
            enemy_id = int(tile_str)
            enemy = tiles.Enemy(self.__default_enemy_factory, get_entangled_enemies, update_entangled_groups, enemy_id)
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
            return tiles.Message.create("Hmm, I don't know what to say.", Config.scientist_name())

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
        elif tile_code is tiles.TileCode.Obstacle:
            return tiles.Obstacle()
        else:
            self.warning(f"Unknown tile specified: {tile_str}. Using a Floor-Tile instead.")
            return tiles.Floor()

    def __get_draw_strategy(self, ctx: QrogueDungeonParser.Draw_strategyContext):
        if ctx:
            return self.visit(ctx)
        return False    # default value is "random"

    def __teleport_callback(self, map_name: str, spawn_pos: Coordinate):
        def cb(confirm: bool):
            if confirm:
                self.__load_map(map_name, spawn_pos)
        CommonQuestions.GoingBack.ask(cb)

    ##### load from references #####

    def __load_reward_pool(self, reference: str) -> CollectibleFactory:
        if reference in self.__reward_pools:
            return self.__reward_pools[reference]

        ref = parser_util.normalize_reference(reference)
        if ref in ['coin', 'coins']:
            pool = [pickup.Coin(1)]
        elif ref in ['key', 'keys']:
            pool = [pickup.Key(1)]
        elif ref in ['energy']:
            pool = [pickup.Energy()]
        else:
            self.warning(f"Imports not yet supported: {reference}. Choosing from default_reward_factory!")
            # todo implement imports
            return self.__default_reward_factory
        return CollectibleFactory(pool)

    def __load_stv_pool(self, reference: str, allow_default: bool = True) -> Optional[ExplicitTargetDifficulty]:
        if reference in self.__stv_pools:
            return self.__stv_pools[reference]
        elif allow_default:
            # todo implement imports
            self.warning(f"Imports not yet supported: {reference}. Choosing from default_stv_pool!")
            return self.__default_target_difficulty
        else:
            return None

    def __load_gate(self, reference: str) -> instruction.Instruction:
        ref = parser_util.normalize_reference(reference)
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
        def callback(direction: Direction, controllable: Controllable):
            #Popup.message("Trigger", str(reference))
            pass

        return tiles.Trigger(callback)

    def __load_message(self, reference: str) -> Message:
        if reference in self.__messages:
            return self.__messages[reference]
        norm_ref = parser_util.normalize_reference(reference)
        if norm_ref in self.__messages:
            return self.__messages[norm_ref]
        elif norm_ref.startswith("helptext"):
            help_text_type = norm_ref[len("helptext"):]
            help_text = HelpText.load(help_text_type)
            if help_text:
                return Message.create_with_title(norm_ref, Config.system_name(), help_text)
        self.warning(f"Unknown text reference: {reference}. Returning \"Message not found!\"")
        return Message.error("Message not found!")

    def __load_hallway(self, reference: str) -> Optional[tiles.Door]:
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
        hw_dic = parser_util.get_hallways(self.__created_hallways, self.__hallways, Coordinate(x, y))
        if reference in self.__rooms:
            room = self.__rooms[reference]
            if room.type is rooms.AreaType.SpawnRoom:
                if self.__spawn_pos:
                    self.warning("A second SpawnRoom was defined! Ignoring the first one "
                                 "and using this one as SpawnRoom.")
                self.__spawn_pos = Coordinate(x, y)
            return room.copy(hw_dic)
        elif reference == self.__SPAWN_ROOM_ID:
            room = rooms.SpawnRoom(self.__load_map, None, hw_dic[Direction.North], hw_dic[Direction.East],
                                   hw_dic[Direction.South], hw_dic[Direction.West],
                                   place_teleporter=self.__place_sr_teleporter)
            if self.__spawn_pos:
                self.warning("A second SpawnRoom was defined! Ignoring the first one and using this one as "
                             "SpawnRoom.")
            self.__spawn_pos = Coordinate(x, y)
            return room
        elif reference[0] == '_':
            # todo handle templates
            room = rooms.CustomRoom(rooms.AreaType.Placeholder, None, hw_dic[Direction.North], hw_dic[Direction.East],
                                    hw_dic[Direction.South], hw_dic[Direction.West])
            self.__rooms[reference] = room
            return room
        else:
            self.warning(f"room_id \"{reference}\" not specified and imports not yet supported! "
                         "Placing an empty room instead.")
            room = rooms.Placeholder.empty_room(hw_dic[Direction.North], hw_dic[Direction.East],
                                                hw_dic[Direction.South], hw_dic[Direction.West])
            self.__rooms[reference] = room
            return room

    ##### General area

    def visitInteger(self, ctx: QrogueDungeonParser.IntegerContext) -> int:
        return parser_util.parse_integer(ctx)

    def visitComplex_number(self, ctx: QrogueDungeonParser.Complex_numberContext) -> complex:
        return parser_util.parse_complex(ctx)

    def visitDraw_strategy(self, ctx: QrogueDungeonParser.Draw_strategyContext) -> bool:
        """

        :param ctx:
        :return: True if strategy is 'ordered', False if it is 'random'
        """
        return ctx.ORDERED_DRAW() is not None

    ##### Message area ######

    def visitMessage(self, ctx: QrogueDungeonParser.MessageContext) -> Message:
        return parser_util.parse_message(ctx)

    def visitMessages(self, ctx: QrogueDungeonParser.MessagesContext):
        self.__messages.clear()
        for msg in ctx.message():
            message = self.visit(msg)
            self.__messages[message.id] = message
        for message in self.__messages.values():
            if message.alt_message_ref and message.alt_message_ref in self.__messages:
                alt_message = self.__messages[message.alt_message_ref]
                try:
                    message.resolve_message_ref(alt_message)
                except ValueError as ve:
                    self.warning("Message-cycle found: " + str(ve))

    ##### Reward Pool area #####

    def visitCollectible(self, ctx: QrogueDungeonParser.CollectibleContext) -> Optional[Collectible]:
        if ctx.KEY_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Key(val)
        elif ctx.COIN_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Coin(val)
        elif ctx.ENERGY_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Energy(val)
        elif ctx.GATE_LITERAL():
            reference = ctx.REFERENCE().getText()
            return self.__load_gate(reference)
        elif ctx.QUBIT_LITERAL():
            if ctx.integer():
                return Qubit(self.visit(ctx.integer()))
            else:
                return Qubit(1)
        else:
            self.warning("No legal collectible specified!")
        return None

    def visitCollectibles(self, ctx: QrogueDungeonParser.CollectiblesContext) -> List[Collectible]:
        collectible_list = []
        for collectible in ctx.collectible():
            collectible_list.append(self.visit(collectible))
        return collectible_list

    def visitReward_pool(self, ctx: QrogueDungeonParser.Reward_poolContext) -> Tuple[str, CollectibleFactory]:
        pool_id = ctx.REFERENCE().getText()
        ordered = self.__get_draw_strategy(ctx.draw_strategy())
        collectible_list = self.visit(ctx.collectibles())
        if ordered:
            return pool_id, OrderedCollectibleFactory(collectible_list)
        else:
            return pool_id, CollectibleFactory(collectible_list)

    def visitDefault_reward_pool(self, ctx: QrogueDungeonParser.Default_reward_poolContext) -> CollectibleFactory:
        if ctx.REFERENCE():  # implicit definition
            pool_id = ctx.REFERENCE().getText()
            return self.__load_reward_pool(pool_id)

        else:  # explicit definition
            ordered = self.__get_draw_strategy(ctx.draw_strategy())
            collectible_list = self.visit(ctx.collectibles())
            if ordered:
                return OrderedCollectibleFactory(collectible_list)
            else:
                return CollectibleFactory(collectible_list)

    def visitReward_pools(self, ctx: QrogueDungeonParser.Reward_poolsContext) -> None:
        for reward_pool in ctx.reward_pool():
            pool_id, collectible_factory = self.visit(reward_pool)
            self.__reward_pools[pool_id] = collectible_factory
        self.__default_reward_factory = self.visit(ctx.default_reward_pool())

    ##### StateVector Pool area #####

    def visitStv(self, ctx: QrogueDungeonParser.StvContext) -> StateVector:
        amplitudes = []
        for cn in ctx.complex_number():
            amplitudes.append(self.visit(cn))
        if not StateVector.check_amplitudes(amplitudes):
            self.warning(f"Invalid amplitudes for StateVector: {amplitudes}! Using 0-only basis state instead.")
            amplitudes = [1] + [0] * (2 ** self.__robot.num_of_qubits - 1)
        return StateVector(amplitudes)

    def visitStv_ref(self, ctx: QrogueDungeonParser.Stv_refContext) -> List[StateVector]:
        if ctx.stv():
            return [self.visit(ctx.stv())]
        else:
            pool_id = ctx.REFERENCE().getText
            difficulty = self.__load_stv_pool(pool_id, allow_default=False)
            if difficulty:
                return difficulty.copy_pool()
            else:
                self.warning(f"Illegal pool_id: {pool_id}. Make sure to only reference previously defined pool ids!")
                return []

    def visitStvs(self, ctx: QrogueDungeonParser.StvsContext) -> List[StateVector]:
        stvs = []
        for stv_ref in ctx.stv_ref():
            stvs += self.visit(stv_ref)
        return stvs

    def visitStv_pool(self, ctx: QrogueDungeonParser.Stv_poolContext) -> Tuple[str, ExplicitTargetDifficulty]:
        pool_id = ctx.REFERENCE(0).getText()
        ordered = self.__get_draw_strategy(ctx.draw_strategy())
        stvs = self.visit(ctx.stvs())

        if ctx.REFERENCE(1):
            reward_pool_id = ctx.REFERENCE(1).getText()
            reward_factory = self.__load_reward_pool(reward_pool_id)
        else:
            reward_factory = self.__default_reward_factory

        return pool_id, ExplicitTargetDifficulty(stvs, reward_factory, ordered)

    def visitDefault_stv_pool(self, ctx: QrogueDungeonParser.Default_stv_poolContext) -> ExplicitTargetDifficulty:
        if ctx.REFERENCE():  # implicit definition
            pool_id = ctx.REFERENCE().getText()
            return self.__load_stv_pool(pool_id)

        else:  # explicit definition
            ordered = self.__get_draw_strategy(ctx.draw_strategy())
            stv_list = self.visit(ctx.stvs())
            return ExplicitTargetDifficulty(stv_list, self.__default_reward_factory, ordered)

    def visitStv_pools(self, ctx: QrogueDungeonParser.Stv_poolsContext) -> None:
        for stv_pool in ctx.stv_pool():
            pool_id, target_difficulty = self.visit(stv_pool)
            self.__stv_pools[pool_id] = target_difficulty
        self.__default_target_difficulty = self.visit(ctx.default_stv_pool())
        self.__default_enemy_factory = EnemyFactory(self.__cbp.start_fight, self.__default_target_difficulty, 1)

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

        ref_index = 0
        event_id = None
        if ctx.OPEN_LITERAL():
            open_state = tiles.DoorOpenState.Open
        elif ctx.CLOSED_LITERAL():
            open_state = tiles.DoorOpenState.Closed
        elif ctx.LOCKED_LITERAL():
            open_state = tiles.DoorOpenState.KeyLocked
        elif ctx.EVENT_LITERAL():
            if ctx.REFERENCE(ref_index):
                event_id = parser_util.normalize_reference(ctx.REFERENCE(ref_index).getText())
                open_state = tiles.DoorOpenState.EventLocked
                ref_index += 1
            else:
                open_state = tiles.DoorOpenState.Closed
                self.warning("Event lock specified without an event id! Ignoring the lock and placing a closed door "
                             "instead.")
        else:
            open_state = tiles.DoorOpenState.Closed
            self.warning("Invalid hallway attribute: it is neither locked nor opened nor closed!")
        # due to antlr4 version mismatch we currently cannot use the adapted grammar
        entangled = len(ctx.HALLWAY_ID()) > 0 #ctx.ENTANGLED_LITERAL() is not None

        def door_check():
            return self.__check_achievement(event_id)
        door = tiles.Door(direction, open_state, one_way_state, door_check, entangled)

        # todo move tutorial and trigger from attributes to hallway?
        if ctx.TUTORIAL_LITERAL():
            message = self.__load_message(ctx.REFERENCE(ref_index).getText())
            door.set_explanation(message)
            ref_index += 1
        if ctx.TRIGGER_LITERAL():
            event_to_trigger = parser_util.normalize_reference(ctx.REFERENCE(ref_index).getText())
            door.set_event(event_to_trigger)
        return door

    def visitHallway(self, ctx: QrogueDungeonParser.HallwayContext) -> Tuple[str, rooms.Hallway]:
        hw_id = ctx.HALLWAY_ID().getText()
        door = self.visit(ctx.h_attributes())

        if door.is_entangled:
            def check_entanglement_lock() -> bool:
                if hw_id in self.__entanglement_locks:
                    return True
                else:
                    self.__entanglement_locks.add(hw_id)
                    return False
            door.set_entanglement(check_entanglement_lock)

        return hw_id, door

    def visitHallways(self, ctx: QrogueDungeonParser.HallwaysContext) -> None:
        for hallway_ctx in ctx.hallway():
            hw_id, door = self.visit(hallway_ctx)
            self.__hallways_by_id[hw_id] = door

    ##### Room area #####

    def visitShop_descriptor(self, ctx: QrogueDungeonParser.Shop_descriptorContext) -> tiles.ShopKeeper:
        num_of_items = self.visit(ctx.integer())

        if ctx.REFERENCE():
            pool_id = ctx.REFERENCE().getText()
            item_pool = self.__load_reward_pool(pool_id)
        else:
            item_pool = self.visit(ctx.collectibles())

        shop_factory = CollectibleFactory(item_pool)
        items = shop_factory.produce_multiple(self.__rm, num_of_items)
        return tiles.ShopKeeper(self.__cbp.visit_shop, [ShopItem(item) for item in items])

    def visitRiddle_descriptor(self, ctx: QrogueDungeonParser.Riddle_descriptorContext) -> tiles.Riddler:
        attempts = self.visit(ctx.integer())

        ref_index = 0
        if ctx.stv():
            stv = self.visit(ctx.stv())
        else:
            pool_id = ctx.REFERENCE(ref_index).getText()
            ref_index += 1
            difficulty = self.__load_stv_pool(pool_id)
            stv = difficulty.create_statevector(self.__robot, self.__rm)

        if ctx.collectible():
            reward = self.visit(ctx.collectible())
        else:
            pool_id = ctx.REFERENCE(ref_index).getText()
            reward_pool = self.__load_reward_pool(pool_id)
            reward = reward_pool.produce(self.__rm)

        riddle = Riddle(stv, reward, attempts)
        return tiles.Riddler(self.__cbp.open_riddle, riddle)

    def visitEnergy_descriptor(self, ctx: QrogueDungeonParser.Energy_descriptorContext) -> tiles.Tile:
        amount = self.visit(ctx.integer())
        return tiles.Energy(amount)

    def visitTrigger_descriptor(self, ctx: QrogueDungeonParser.Trigger_descriptorContext) -> tiles.Trigger:
        reference = ctx.REFERENCE().getText()
        return self.__load_trigger(reference)

    def visitMessage_descriptor(self, ctx: QrogueDungeonParser.Message_descriptorContext) -> tiles.Message:
        if ctx.integer():
            times = self.visit(ctx.integer())
        else:
            times = -1      # = always show
        reference = ctx.REFERENCE().getText()
        message = self.__load_message(reference)
        return tiles.Message(message, times)

    def visitCollectible_descriptor(self, ctx: QrogueDungeonParser.Collectible_descriptorContext) -> tiles.Collectible:
        pool_id = ctx.REFERENCE().getText()
        reward_factory = self.__load_reward_pool(pool_id)

        times = 1
        if ctx.integer():
            times = self.visit(ctx.integer())
        if times > 1:
            collectible = MultiCollectible(reward_factory.produce_multiple(self.__rm, times))
        else:
            collectible = reward_factory.produce(self.__rm)
        return tiles.Collectible(collectible)

    def visitEnemy_descriptor(self, ctx: QrogueDungeonParser.Enemy_descriptorContext) -> tiles.Enemy:
        enemy = None
        if self.__cur_room_id:
            room_id = self.__cur_room_id
        else:
            raise NotImplementedError()     # todo better check

        def get_entangled_tiles(id_: int) -> List[tiles.Enemy]:
            if room_id in self.__enemy_groups_by_room:
                room_dic = self.__enemy_groups_by_room[room_id]
                return room_dic[id_]
            else:
                return [enemy]

        def update_entangled_room_groups(new_enemy: tiles.Enemy):
            if room_id not in self.__enemy_groups_by_room:
                self.__enemy_groups_by_room[room_id] = {}
            if enemy_id not in self.__enemy_groups_by_room[room_id]:
                self.__enemy_groups_by_room[room_id][enemy_id] = []
            self.__enemy_groups_by_room[room_id][enemy_id].append(new_enemy)

        enemy_id = int(ctx.DIGIT().getText())

        # reward factory is needed to create the enemy factory so we have to create it first and find out where to look
        if ctx.stv():
            # since a state vector was defined instead of referenced, a reward factory reference can only be the first
            ref_index = 0       # reference occurrence
        else:
            # otherwise a stv was referenced and therefore, a reward factory can only be the second reference
            ref_index = 1

        if ctx.collectible():
            reward = self.visit(ctx.collectible())
            reward_factory = CollectibleFactory([reward])
        elif ctx.REFERENCE(ref_index):
            pool_id = ctx.REFERENCE(ref_index).getText()
            reward_factory = self.__load_collectible_factory(pool_id)
        else:
            # if neither a collectible nor a reference to a reward_factory is given we use the default one
            reward_factory = self.__default_reward_factory

        if ctx.stv():
            stv = self.visit(ctx.stv())
            difficulty = ExplicitTargetDifficulty([stv], reward_factory)
        else:
            pool_id = ctx.REFERENCE(0).getText()    # don't use ref_index here because it will always be 0 if present
            difficulty = self.__load_stv_pool(pool_id)

        enemy_factory = EnemyFactory(self.__cbp.start_fight, difficulty, 1)
        enemy = tiles.Enemy(enemy_factory, get_entangled_tiles, update_entangled_room_groups, enemy_id)
        #   update_entangled_room_groups(enemy) # by commenting this the original (copied from) tile is not in the list
        return enemy

    def visitTile_descriptor(self, ctx: QrogueDungeonParser.Tile_descriptorContext) -> tiles.Tile:
        if ctx.trigger_descriptor():
            tile = self.visit(ctx.trigger_descriptor())
        elif ctx.enemy_descriptor():
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

        if isinstance(tile, tiles.WalkTriggerTile):
            ref_index = 0
            if ctx.TILE_MESSAGE_LITERAL():
                ref = ctx.REFERENCE(ref_index).getText()
                msg = self.__load_message(ref)
                tile.set_explanation(msg)
                ref_index += 1
            if ctx.TILE_EVENT_LITERAL():
                ref = ctx.REFERENCE(ref_index).getText()
                event_id = parser_util.normalize_reference(ref)
                tile.set_event(event_id)
        return tile

    def visitTile(self, ctx: QrogueDungeonParser.TileContext) -> str:
        return ctx.getText()

    def visitR_row(self, ctx: QrogueDungeonParser.R_rowContext) -> List[str]:
        row = []
        for tile in ctx.tile():
            row.append(self.visit(tile))
        return row

    def visitR_type(self, ctx: QrogueDungeonParser.R_typeContext) -> rooms.AreaType:
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
        elif ctx.TREASURE_LITERAL():
            return rooms.AreaType.TreasureRoom
        else:
            self.warning(f"Invalid r_type: {ctx.getText()}")
            return rooms.AreaType.Invalid

    def visitR_visibility(self, ctx: QrogueDungeonParser.R_visibilityContext) -> Tuple[bool, bool]:
        visible = False
        foggy = False
        if ctx.VISIBLE_LITERAL():
            visible = True
        elif ctx.FOGGY_LITERAL():
            foggy = True
        return visible, foggy

    def visitR_attributes(self, ctx: QrogueDungeonParser.R_attributesContext) \
            -> Tuple[Tuple[bool, bool], rooms.AreaType]:
        visibility = self.visit(ctx.r_visibility())
        rtype = self.visit(ctx.r_type())
        return visibility, rtype

    def visitRoom_content(self, ctx) -> Tuple[List[str], Dict[str, List[tiles.Tile]]]:
        # place the tiles correctly in the room
        rows = []
        for row in ctx.r_row():
            rows.append(self.visit(row))
        tile_dic = {}
        for descriptor in ctx.tile_descriptor():
            tile = self.visit(descriptor)
            if tile.code is tiles.TileCode.Enemy:
                tile_str = str(tile.eid)
            else:
                tile_str = QrogueLevelGenerator.__tile_code_to_str(tile.code)
            if tile_str in tile_dic:
                tile_dic[tile_str].append(tile)
            else:
                tile_dic[tile_str] = [tile]
        return rows, tile_dic

    def visitRoom(self, ctx: QrogueDungeonParser.RoomContext) -> Tuple[str, rooms.CustomRoom]:
        self.__cur_room_id = ctx.ROOM_ID().getText()
        visibility, room_type = self.visit(ctx.r_attributes())

        rows, tile_dic = self.visit(ctx.room_content())

        # this local method is needed here for not explicitly defined enemies
        # but since we are already in a room we don't have to reference to global data
        enemy_dic = {}

        def get_entangled_enemies(eid: int) -> List[tiles.Enemy]:
            if eid in enemy_dic:
                return enemy_dic[eid]
            else:
                return []

        def update_entangled_room_groups(new_enemy: tiles.Enemy):
            if new_enemy.eid not in enemy_dic:
                enemy_dic[new_enemy.eid] = []
            enemy_dic[new_enemy.eid].append(new_enemy)

        descriptor_indices = {}
        tile_matrix = []
        for row in rows:
            matrix_row = []
            for tile_str in row:
                if tile_str in tile_dic:
                    if tile_str not in descriptor_indices:
                        descriptor_indices[tile_str] = 0
                    index = descriptor_indices[tile_str]

                    # we need to copy it because in case we have less descriptors than tiles we reuse the latest
                    # descriptor
                    tile = tile_dic[tile_str][index].copy()
                    if index + 1 < len(tile_dic[tile_str]):
                        descriptor_indices[tile_str] = index + 1
                elif tile_str == tiles.Teleport.Img() and room_type is rooms.AreaType.SpawnRoom:
                    tile = tiles.Teleport(self.__teleport_callback, MapConfig.back_map_string(), None)
                else:
                    tile = self.__get_default_tile(tile_str, enemy_dic, get_entangled_enemies,
                                                   update_entangled_room_groups)
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

    def visitRooms(self, ctx: QrogueDungeonParser.RoomsContext):
        for room_ctx in ctx.room():
            room_id, room = self.visit(room_ctx)
            self.__rooms[room_id] = room

    ##### Layout area #####

    def visitLayout(self, ctx: QrogueDungeonParser.LayoutContext) -> List[List[rooms.Room]]:
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
            self.warning(f"Too much room rows specified. Only maps of size ({MapConfig.max_width()}, "
                         f"{MapConfig.max_height()}) supported. Ignoring over-specified rows.")

        return room_matrix

    def __hallway_handling(self, ctx_children: List[TerminalNodeImpl], y: int, direction: Direction):
        x = 0
        for child in ctx_children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type,
                                                           QrogueDungeonParser.VERTICAL_SEPARATOR):
                self.warning(
                    f"Too much room columns specified. Only maps of size ({MapConfig.max_width()}, "
                    f"{MapConfig.max_height()}) supported. Ignoring over-specified columns.")
                break
            if child.symbol.type == QrogueDungeonParser.HALLWAY_ID:
                hw_id = child.symbol.text
                origin = Coordinate(x, y)
                self._add_hallway(origin, origin + direction, self.__load_hallway(hw_id))
                x += 1
            elif child.symbol.type == QrogueDungeonParser.EMPTY_HALLWAY:
                x += 1

    def __visitL_hallway_row(self, ctx: QrogueDungeonParser.L_hallway_rowContext, y: int) -> None:
        self.__hallway_handling(ctx.children, y, Direction.South)    # connect downwards to the next room row

    def __visitL_room_row(self, ctx: QrogueDungeonParser.L_room_rowContext, y: int) -> List[rooms.Room]:
        self.__hallway_handling(ctx.children, y, Direction.East)     # connect to the right to the next room

        row = []
        x = 0
        for child in ctx.children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type,
                                                           QrogueDungeonParser.VERTICAL_SEPARATOR):
                self.warning(f"Too much room columns specified. Only maps of size ({MapConfig.max_width()}, "
                             f"{MapConfig.max_height()}) supported. Ignoring over-specified columns.")
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

    def visitRobot(self, ctx: QrogueDungeonParser.RobotContext) -> None:
        num_of_qubits = int(ctx.DIGIT().getText())
        gates = []
        for ref in ctx.REFERENCE():
            if parser_util.normalize_reference(ref.getText()) == self.__ROBOT_NO_GATES:
                continue
            gates.append(self.__load_gate(ref.getText()))  # todo what about pickups?

        integer_index = 0
        circuit_space, backpack_space = None, None
        max_energy, start_energy = None, None

        if ctx.CIRCUIT_SPACE():
            circuit_space = parser_util.parse_integer(ctx.integer(integer_index))
            integer_index += 1
        if ctx.BACKPACK_SPACE():
            backpack_space = parser_util.parse_integer(ctx.integer(integer_index))
            integer_index += 1

        if ctx.MAX_ENERGY():
            max_energy = parser_util.parse_integer(ctx.integer(integer_index))
            integer_index += 1
            if ctx.START_ENERGY():
                start_energy = parser_util.parse_integer(ctx.integer(integer_index))

        self.__robot = TestBot(CallbackPack.instance().game_over, num_of_qubits, gates, circuit_space, backpack_space,
                               max_energy, start_energy)

    ##### Meta area #####

    def visitMeta(self, ctx: QrogueDungeonParser.MetaContext) -> Tuple[Optional[str], bool]:
        if ctx.TEXT():
            name = parser_util.text_to_str(ctx)
        else:
            name = None
        return name, ctx.NO_TELEPORTER() is None

    ##### Start area #####

    def visitStart(self, ctx: QrogueDungeonParser.StartContext) -> Tuple[str, List[List[rooms.Room]]]:
        name, self.__place_sr_teleporter = self.visit(ctx.meta())

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
        return name, self.visit(ctx.layout())
