from typing import Callable, List, Tuple, Dict, Optional, Set

from antlr4 import InputStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNodeImpl
from qiskit import QuantumCircuit

from qrogue.game.logic import Message, StateVector
from qrogue.game.logic.actors import Controllable, Riddle, Robot, robot
from qrogue.game.logic.actors.puzzles import Challenge
from qrogue.game.logic.collectibles import Collectible, pickup, instruction, MultiCollectible, Qubit, ShopItem, \
    CollectibleFactory, OrderedCollectibleFactory
from qrogue.game.logic.collectibles.instruction import MultiQubitGate, SingleQubitGate, InstructionManager, Instruction
from qrogue.game.target_factory import EnemyFactory, ExplicitTargetDifficulty
from qrogue.game.world import tiles
from qrogue.game.world.map import CallbackPack, LevelMap, rooms, MapMetaData
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import Config, HelpText, MapConfig, PathConfig, Logger, CommonQuestions, RandomManager

from qrogue.game.world.dungeon_generator import parser_util
from qrogue.game.world.dungeon_generator.dungeon_parser.QrogueDungeonLexer import QrogueDungeonLexer
from qrogue.game.world.dungeon_generator.dungeon_parser.QrogueDungeonParser import QrogueDungeonParser
from qrogue.game.world.dungeon_generator.dungeon_parser.QrogueDungeonVisitor import QrogueDungeonVisitor
from qrogue.game.world.dungeon_generator.generator import DungeonGenerator


class QrogueLevelGenerator(DungeonGenerator, QrogueDungeonVisitor):
    __DEFAULT_NUM_OF_SHOP_ITEMS = 3
    __DEFAULT_NUM_OF_RIDDLE_ATTEMPTS = 7
    __ROBOT_NO_GATES = "none"
    __SPAWN_ROOM_ID = "SR"
    __DEFAULT_SPEAKER = Config.examiner_name()  # todo but later in the game it should default to scientist_name()
    __QUICK_MSG_ID = 0
    __QUICK_MSG_PREFIX = "_qumsg"
    __HELP_TEXT_PREFIX = "helptext"

    class _StaticTemplates:
        @staticmethod
        def is_pickup_none(ref: str) -> bool:
            return ref == 'none'

        @staticmethod
        def is_pickup_score(ref: str) -> bool:
            return ref in ['score']

        @staticmethod
        def is_pickup_coin(ref: str) -> bool:
            return ref in ['coin', 'coins']

        @staticmethod
        def is_pickup_key(ref: str) -> bool:
            return ref in ['key', 'keys']

        @staticmethod
        def is_pickup_energy(ref: str) -> bool:
            return ref in ['energy']

        @staticmethod
        def is_gate_x(ref: str) -> bool:
            return ref in ['x', 'xgate']

        @staticmethod
        def is_gate_y(ref: str) -> bool:
            return ref in ['y', 'ygate']

        @staticmethod
        def is_gate_z(ref: str) -> bool:
            return ref in ['z', 'zgate']

        @staticmethod
        def is_gate_h(ref: str) -> bool:
            return ref in ['h', 'hgate', 'hadamard', 'hadamardgate']

        @staticmethod
        def is_gate_cx(ref: str) -> bool:
            return ref in ['cx', 'cxgate']

        @staticmethod
        def is_gate_swap(ref: str) -> bool:
            return ref in ['swap', 'swapgate']

        @staticmethod
        def is_gate_i(ref: str) -> bool:
            return ref in ['i', 'igate']

        @staticmethod
        def is_dir_north(dir_str: str) -> bool:
            return dir_str == "North"

        @staticmethod
        def is_dir_east(dir_str: str) -> bool:
            return dir_str == "East"

        @staticmethod
        def is_dir_south(dir_str: str) -> bool:
            return dir_str == "South"

        @staticmethod
        def is_dir_west(dir_str: str) -> bool:
            return dir_str == "West"

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
        elif tile_code is tiles.TileCode.Teleport:
            return parser_util.TELEPORT_TILE
        elif tile_code is tiles.TileCode.Message:
            return parser_util.MESSAGE_TILE
        elif tile_code is tiles.TileCode.Energy:
            return parser_util.ENERGY_TILE
        elif tile_code is tiles.TileCode.Riddler:
            return parser_util.RIDDLER_TILE
        elif tile_code is tiles.TileCode.Challenger:
            return parser_util.CHALLENGER_TILE
        elif tile_code is tiles.TileCode.ShopKeeper:
            return parser_util.SHOP_KEEPER_TILE
        elif tile_code is tiles.TileCode.Floor:
            return parser_util.FLOOR_TILE
        else:
            # todo print warning?
            return None

    def __init__(self, seed: int, check_achievement: Callable[[str], bool], trigger_event: Callable[[str], None],
                 load_map_callback: Callable[[str, Coordinate], None],
                 show_message_callback: Callable[[str, str, Optional[bool], Optional[int]], None]):
        super(QrogueLevelGenerator, self).__init__(seed, 0, 0)
        self.__seed = seed
        self.__check_achievement = check_achievement
        self.__trigger_event = trigger_event
        self.__load_map = load_map_callback
        self.__show_message = show_message_callback
        self.__meta_data = MapMetaData(None, None, True, self.__show_description)

        self.__warnings = 0
        self.__level: Optional[LevelMap] = None
        self.__robot: Optional[Robot] = None
        self.__rm = RandomManager.create_new(seed)

        self.__default_speaker = QrogueLevelGenerator.__DEFAULT_SPEAKER
        self.__messages: Dict[str, Message] = {}

        # "collectible factory" refers to "reward pool" in grammar due to the original purpose, simplicity & readability
        self.__collectible_factories: Dict[str, CollectibleFactory] = {}
        self.__default_collectible_factory: Optional[CollectibleFactory] = None

        # "target difficulty" refers to "stv pool" in grammar due to the original purpose, simplicity and readability
        self.__target_difficulties: Dict[str, ExplicitTargetDifficulty] = {}
        self.__default_target_difficulty: Optional[ExplicitTargetDifficulty] = None

        self.__default_enemy_factory: Optional[EnemyFactory] = None     # needed to create default_tile enemies

        self.__hallways_by_id: Dict[str, tiles.Door] = {}      # hw_id -> Door
        self.__doors: Dict[Coordinate, Dict[Coordinate, tiles.Door]] = {}   # for later hallway generation
        self.__entanglement_locks: Set[str] = set()     # stores hw_id of activated entanglement_locks

        self.__enemy_groups_by_room: Dict[str, Dict[int, List[tiles.Enemy]]] = {}    # room_id -> Dict[1-9] -> enemies
        self.__cur_room_id: Optional[str] = None   # needed for enemy groups
        self.__rooms: Dict[str, rooms.CopyAbleRoom] = {}
        self.__spawn_pos: Optional[Coordinate] = None

        # holds references to already created hallways so that neighbors can use it instead of
        # creating their own redundant hallway
        self.__created_hallways: Dict[Coordinate, Dict[Direction, rooms.Hallway]] = {}

    @property
    def __cbp(self) -> CallbackPack:
        return CallbackPack.instance()

    def __show_description(self):
        if self.__meta_data.description:
            ret = self.__meta_data.description.get(self.__check_achievement)
            if ret:
                title, text = ret
                self.__show_message(title, text, None, self.__meta_data.description.position)

    def warning(self, text: str, loc_details: Optional[str] = None):
        loc_details = "" if loc_details is None else "~" + loc_details
        level_name = "[meta_data uninitialized]" if self.__meta_data is None else self.__meta_data.name
        parser_util.warning(text, f"{level_name}{loc_details}")
        self.__warnings += 1

    def generate(self, file_name: str, in_dungeon_folder: bool = True) -> Tuple[Optional[LevelMap], bool]:
        map_data = PathConfig.read_level(file_name, in_dungeon_folder)

        input_stream = InputStream(map_data)
        lexer = QrogueDungeonLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = QrogueDungeonParser(token_stream)
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

        if self.__spawn_pos is None:
            raise SyntaxError("No SpawnRoom provided! Make sure to place 'SR' in the layout and if you defined a "
                              "custom SpawnRoom make sure to tag it as (Spawn).")
        self.__level = LevelMap(meta_data, file_name, self.__seed, room_matrix, self.__robot, self.__spawn_pos,
                                self.__check_achievement, self.__trigger_event)
        return self.__level, True

    def _add_hallway(self, room1: Coordinate, room2: Coordinate, door: tiles.Door):
        if door:    # for simplicity door could be null so we check it here
            if room1 in self.__doors:
                self.__doors[room1][room2] = door
            else:
                self.__doors[room1] = {room2: door}
            if room2 in self.__doors:
                self.__doors[room2][room1] = door
            else:
                self.__doors[room2] = {room1: door}

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
            return tiles.Collectible(self.__default_collectible_factory.produce(self.__rm))

        elif tile_code is tiles.TileCode.Energy:
            return tiles.Collectible(pickup.Energy())

        elif tile_code is tiles.TileCode.Riddler:
            stv = self.__default_target_difficulty.create_statevector(self.__robot, self.__rm)
            reward = self.__default_collectible_factory.produce(self.__rm)
            riddle = Riddle(stv, reward, self.__DEFAULT_NUM_OF_RIDDLE_ATTEMPTS)
            return tiles.Riddler(self.__cbp.open_riddle, riddle)

        elif tile_code is tiles.TileCode.ShopKeeper:
            items = self.__default_collectible_factory.produce_multiple(self.__rm, self.__DEFAULT_NUM_OF_SHOP_ITEMS)
            return tiles.ShopKeeper(self.__cbp.visit_shop, [ShopItem(item) for item in items])

        elif tile_code is tiles.TileCode.Floor:
            return tiles.Floor()
        elif tile_code is tiles.TileCode.Obstacle:
            return tiles.Obstacle()
        else:
            self.warning(f"Unknown tile without default-value specified: {tile_str}. Using a Floor-Tile instead.")
            return tiles.Floor()

    def __get_draw_strategy(self, ctx: QrogueDungeonParser.Draw_strategyContext):
        if ctx:
            return self.visit(ctx)
        return False    # default value is "random"

    def __teleport_callback(self, map_name: str, spawn_pos: Coordinate):
        def cb(confirm: int):
            if confirm == 0:
                self.__load_map(map_name, spawn_pos)
        CommonQuestions.GoingBack.ask(cb)

    def __tunnel_callback(self, room_id: str, pos_in_room: Coordinate):
        self.__level.tunnel(self.__spawn_pos, pos_in_room)  # todo implement correctly

    ##### load from references #####

    def __load_collectible_factory(self, reference: QrogueDungeonParser.REFERENCE) -> CollectibleFactory:
        ref = reference.getText()
        if ref in self.__collectible_factories:
            return self.__collectible_factories[ref]

        ref = parser_util.normalize_reference(ref)
        if QrogueLevelGenerator._StaticTemplates.is_pickup_none(ref):
            return CollectibleFactory.empty()
        elif QrogueLevelGenerator._StaticTemplates.is_pickup_score(ref):
            pool = [pickup.Score()]
        elif QrogueLevelGenerator._StaticTemplates.is_pickup_coin(ref):
            pool = [pickup.Coin()]
        elif QrogueLevelGenerator._StaticTemplates.is_pickup_key(ref):
            pool = [pickup.Key()]
        elif QrogueLevelGenerator._StaticTemplates.is_pickup_energy(ref):
            pool = [pickup.Energy()]
        else:
            self.warning(f"Imports not yet supported: {ref}. Choosing from default_reward_factory!")
            # todo implement imports
            return self.__default_collectible_factory
        return CollectibleFactory(pool)

    def __load_target_difficulty(self, reference: QrogueDungeonParser.REFERENCE, allow_default: bool = True) \
            -> Optional[ExplicitTargetDifficulty]:
        ref = reference.getText()
        if ref in self.__target_difficulties:
            return self.__target_difficulties[ref]
        elif allow_default:
            # todo implement imports
            self.warning(f"Imports not yet supported: {ref}. Choosing default_target_difficulty!")
            return self.__default_target_difficulty
        else:
            return None

    def __load_gate(self, reference: QrogueDungeonParser.REFERENCE) -> instruction.Instruction:
        ref = parser_util.normalize_reference(reference.getText())
        if QrogueLevelGenerator._StaticTemplates.is_gate_x(ref):
            return instruction.XGate()
        elif QrogueLevelGenerator._StaticTemplates.is_gate_y(ref):
            return instruction.YGate()
        elif QrogueLevelGenerator._StaticTemplates.is_gate_z(ref):
            return instruction.ZGate()
        elif QrogueLevelGenerator._StaticTemplates.is_gate_h(ref):
            return instruction.HGate()
        elif QrogueLevelGenerator._StaticTemplates.is_gate_cx(ref):
            return instruction.CXGate()
        elif QrogueLevelGenerator._StaticTemplates.is_gate_swap(ref):
            return instruction.SwapGate()

        elif not QrogueLevelGenerator._StaticTemplates.is_gate_i(ref):
            self.warning(f"Unknown gate reference: {reference}. Returning I Gate instead.")
        return instruction.IGate()

    def __load_message(self, reference: QrogueDungeonParser.REFERENCE) -> Message:
        ref = reference.getText()
        if ref in self.__messages:
            return self.__messages[ref]
        norm_ref = parser_util.normalize_reference(ref)
        if norm_ref in self.__messages:
            return self.__messages[norm_ref]
        elif norm_ref.startswith(QrogueLevelGenerator.__HELP_TEXT_PREFIX):
            help_text_type = norm_ref[len(QrogueLevelGenerator.__HELP_TEXT_PREFIX):]
            help_text = HelpText.load(help_text_type)
            if help_text:
                # todo check if we really want to prioritize help texts
                return Message.create_with_title(norm_ref, Config.system_name(), help_text, True, None)
        self.warning(f"Unknown text reference: {ref}. Returning \"Message not found!\"")
        return Message.error("Message not found!")

    def __load_hallway(self, hw_id: str) -> Optional[tiles.Door]:
        if hw_id in self.__hallways_by_id:
            return self.__hallways_by_id[hw_id]
        elif hw_id == parser_util.EMPTY_HALLWAY_CODE:
            return None
        elif hw_id == parser_util.DEFAULT_HALLWAY_STR:
            return tiles.Door(Direction.North)
        else:
            # todo implement hallway imports
            return tiles.Door(Direction.North)

    def __load_room(self, room_id: str, x: int, y: int) -> rooms.CopyAbleRoom:
        hw_dic = parser_util.get_hallways(self.__created_hallways, self.__doors, Coordinate(x, y))
        if room_id in self.__rooms:
            room = self.__rooms[room_id]
            if room.type is rooms.AreaType.SpawnRoom:
                spawn_pos = Coordinate(x, y)
                if self.__spawn_pos is not None:
                    self.warning(f"A second SpawnRoom was defined! Ignoring the first one @{self.__spawn_pos} and "
                                 f"using the new one @{spawn_pos} instead.")
                self.__spawn_pos = spawn_pos
            return room.copy(hw_dic)
        elif room_id == self.__SPAWN_ROOM_ID:
            room = rooms.SpawnRoom(self.__load_map, None, hw_dic[Direction.North], hw_dic[Direction.East],
                                   hw_dic[Direction.South], hw_dic[Direction.West],
                                   place_teleporter=self.__meta_data.has_teleporter)
            spawn_pos = Coordinate(x, y)
            if self.__spawn_pos is not None:
                self.warning(f"A second SpawnRoom was defined! Ignoring the first one @{self.__spawn_pos} and "
                             f"using the new one @{spawn_pos} instead.")
            self.__spawn_pos = spawn_pos
            return room
        elif room_id[0] == '_':
            # todo handle templates
            room = rooms.CustomRoom(rooms.AreaType.Placeholder, None, hw_dic[Direction.North], hw_dic[Direction.East],
                                    hw_dic[Direction.South], hw_dic[Direction.West])
            self.__rooms[room_id] = room
            return room
        else:
            self.warning(f"room_id \"{room_id}\" not specified and imports not yet supported! "
                         "Placing an empty room instead.")
            room = rooms.Placeholder.empty_room(hw_dic)
            self.__rooms[room_id] = room
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
        return parser_util.parse_message(ctx, self.__default_speaker)

    def visitMessages(self, ctx: QrogueDungeonParser.MessagesContext):
        self.__messages.clear()
        if ctx.MSG_SPEAKER():
            self.__default_speaker = parser_util.parse_speaker(ctx, text_index=None)
        else:
            self.__default_speaker = QrogueLevelGenerator.__DEFAULT_SPEAKER
        for msg in ctx.message():
            message = self.visit(msg)
            self.__messages[message.id] = message
        for message in self.__messages.values():
            if message.alt_message_ref and message.alt_message_ref in self.__messages:
                alt_message = self.__messages[message.alt_message_ref]
                try:
                    message.resolve_message_ref(alt_message)
                except ValueError as ve:
                    self.warning("Message-cycle found: " + str(ve), message.id)

    ##### Reward Pool area #####

    def visitCollectible(self, ctx: QrogueDungeonParser.CollectibleContext) -> Optional[Collectible]:
        if ctx.SCORE_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Score(val)
        elif ctx.KEY_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Key(val)
        elif ctx.COIN_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Coin(val)
        elif ctx.ENERGY_LITERAL():
            val = self.visit(ctx.integer())
            return pickup.Energy(val)
        elif ctx.GATE_LITERAL():
            return self.__load_gate(ctx.REFERENCE())
        elif ctx.QUBIT_LITERAL():
            if ctx.integer():
                return Qubit(self.visit(ctx.integer()))
            else:
                return Qubit(1)
        elif ctx.NONE_LITERAL():
            return None
        else:
            self.warning("No legal collectible specified!")
        return None

    def visitCollectibles(self, ctx: QrogueDungeonParser.CollectiblesContext) -> List[Collectible]:
        collectible_list = []
        for collectible in ctx.collectible():
            collectible_list.append(self.visit(collectible))
        return collectible_list

    def visitReward_pool(self, ctx: QrogueDungeonParser.Reward_poolContext) -> Tuple[str, CollectibleFactory]:
        factory_id = ctx.REFERENCE().getText()
        ordered = self.__get_draw_strategy(ctx.draw_strategy())
        collectible_list = self.visit(ctx.collectibles())
        if ordered:
            return factory_id, OrderedCollectibleFactory(collectible_list)
        else:
            return factory_id, CollectibleFactory(collectible_list)

    def visitDefault_reward_pool(self, ctx: QrogueDungeonParser.Default_reward_poolContext) -> CollectibleFactory:
        if ctx.REFERENCE():  # implicit definition
            return self.__load_collectible_factory(ctx.REFERENCE())

        else:  # explicit definition
            ordered = self.__get_draw_strategy(ctx.draw_strategy())
            collectible_list = self.visit(ctx.collectibles())
            if ordered:
                return OrderedCollectibleFactory(collectible_list)
            else:
                return CollectibleFactory(collectible_list)

    def visitReward_pools(self, ctx: QrogueDungeonParser.Reward_poolsContext) -> None:
        for reward_pool in ctx.reward_pool():
            factory_id, collectible_factory = self.visit(reward_pool)
            self.__collectible_factories[factory_id] = collectible_factory
        self.__default_collectible_factory = self.visit(ctx.default_reward_pool())

    ##### StateVector Pool area #####

    def visitCircuit_gate_single(self, ctx: QrogueDungeonParser.Circuit_gate_singleContext) -> List[Instruction]:
        qubit_index = int(ctx.QUBIT_SPECIFIER().getText()[1:])
        gates: List[Instruction] = []
        for gate_spec in ctx.GATE_SPECIFIER():
            name = gate_spec.getText()[1:]
            gate = InstructionManager.from_name(name)
            if gate is None:
                parser_util.error(f"Invalid gate name: {name}")
                continue
            gate.use_qubit(qubit_index)
            gates.append(gate)
        return gates

    def visitCircuit_gate_multi(self, ctx: QrogueDungeonParser.Circuit_gate_multiContext) -> Optional[Instruction]:
        name = ctx.GATE_SPECIFIER().getText()[1:]
        gate = InstructionManager.from_name(name)
        if gate is None:
            parser_util.error(f"Invalid gate name: {name}")
            return None

        num_provided_qubits = len(ctx.QUBIT_SPECIFIER())
        if gate.num_of_qubits > num_provided_qubits:
            parser_util.error(f"Not enough qubits provided! {gate.num_of_qubits} are needed but only "
                              f"{num_provided_qubits} are specified.")
            return None
        elif gate.num_of_qubits < num_provided_qubits:
            self.warning(f"Too much qubits provided. {gate.num_of_qubits} are needed but {num_provided_qubits} "
                         f"are specified. The last {num_provided_qubits - gate.num_of_qubits} qubits are "
                         f"ignored.", name)

        for qubit_spec in ctx.QUBIT_SPECIFIER():
            qubit = int(qubit_spec.getText()[1:])
            gate.use_qubit(qubit)

        return gate

    def visitCircuit_stv(self, ctx: QrogueDungeonParser.Circuit_stvContext) -> StateVector:
        num_qubits = parser_util.parse_integer(ctx)

        gates: List[Instruction] = []
        for single_spec in ctx.circuit_gate_single():
            gates += self.visit(single_spec)
        for multi_spec in ctx.circuit_gate_multi():
            gate = self.visit(multi_spec)
            if gate is not None: gates.append(gate)

        return StateVector.from_gates(gates, num_qubits)

    def visitStv(self, ctx: QrogueDungeonParser.StvContext) -> StateVector:
        if ctx.circuit_stv():
            return self.visit(ctx.circuit_stv())
        else:
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
            difficulty = self.__load_target_difficulty(ctx.REFERENCE(), allow_default=False)
            if difficulty:
                return difficulty.copy_pool()
            else:
                diff_id = ctx.REFERENCE().getText()
                self.warning(f"Illegal diff_id: {diff_id}. Make sure to only reference previously defined pool ids!")
                return []

    def visitStvs(self, ctx: QrogueDungeonParser.StvsContext) -> List[StateVector]:
        stvs = []
        for stv_ref in ctx.stv_ref():
            stvs += self.visit(stv_ref)
        return stvs

    def visitStv_pool(self, ctx: QrogueDungeonParser.Stv_poolContext) -> Tuple[str, ExplicitTargetDifficulty]:
        diff_id = ctx.REFERENCE(0).getText()
        ordered = self.__get_draw_strategy(ctx.draw_strategy())
        stvs = self.visit(ctx.stvs())

        if ctx.REFERENCE(1):
            reward_factory = self.__load_collectible_factory(ctx.REFERENCE(1))
        else:
            reward_factory = self.__default_collectible_factory

        return diff_id, ExplicitTargetDifficulty(stvs, reward_factory, ordered)

    def visitDefault_stv_pool(self, ctx: QrogueDungeonParser.Default_stv_poolContext) -> ExplicitTargetDifficulty:
        if ctx.REFERENCE():  # implicit definition
            return self.__load_target_difficulty(ctx.REFERENCE())

        else:  # explicit definition
            ordered = self.__get_draw_strategy(ctx.draw_strategy())
            stv_list = self.visit(ctx.stvs())
            return ExplicitTargetDifficulty(stv_list, self.__default_collectible_factory, ordered)

    def visitStv_pools(self, ctx: QrogueDungeonParser.Stv_poolsContext) -> None:
        for stv_pool in ctx.stv_pool():
            diff_id, target_difficulty = self.visit(stv_pool)
            self.__target_difficulties[diff_id] = target_difficulty
        self.__default_target_difficulty = self.visit(ctx.default_stv_pool())
        self.__default_enemy_factory = EnemyFactory(self.__cbp.start_fight, self.__default_target_difficulty, 1)

    ##### Hallway area #####

    def visitH_attributes(self, ctx: QrogueDungeonParser.H_attributesContext) -> Tuple[tiles.Door, List[str]]:
        direction = Direction.North  # todo adapt
        one_way_state = tiles.DoorOneWayState.NoOneWay
        if ctx.DIRECTION():
            dir_str = ctx.DIRECTION().getText()
            if QrogueLevelGenerator._StaticTemplates.is_dir_north(dir_str):
                direction = Direction.North
            elif QrogueLevelGenerator._StaticTemplates.is_dir_east(dir_str):
                direction = Direction.East
            elif QrogueLevelGenerator._StaticTemplates.is_dir_south(dir_str):
                direction = Direction.South
            elif QrogueLevelGenerator._StaticTemplates.is_dir_west(dir_str):
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
        entangled_ids = []
        for hw_id in ctx.HALLWAY_ID():
            entangled_ids.append(hw_id.symbol.text)

        def door_check():
            return self.__check_achievement(event_id)
        door = tiles.Door(direction, open_state, one_way_state, door_check)

        # todo move tutorial and trigger from attributes to hallway?
        if ctx.TUTORIAL_LITERAL():
            message = self.__load_message(ctx.REFERENCE(ref_index))
            door.set_explanation(message)
            ref_index += 1
        if ctx.TRIGGER_LITERAL():
            event_to_trigger = parser_util.normalize_reference(ctx.REFERENCE(ref_index).getText())
            door.set_event(event_to_trigger)
        return door, entangled_ids  # ctx.ENTANGLED_LITERAL() is not None

    def visitHallway(self, ctx: QrogueDungeonParser.HallwayContext) -> Tuple[str, rooms.Hallway]:
        hw_id = ctx.HALLWAY_ID().getText()
        door, entangled_ids = self.visit(ctx.h_attributes())

        if len(entangled_ids) > 0:
            def check_entanglement_lock() -> bool:
                """

                :return: True if this door is locked via entanglement, False otherwise
                """
                for eid in entangled_ids:
                    if eid in self.__entanglement_locks:
                        return True
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
            shop_factory = self.__load_collectible_factory(ctx.REFERENCE())
        else:
            shop_factory = CollectibleFactory(self.visit(ctx.collectibles()))

        items = shop_factory.produce_multiple(self.__rm, num_of_items)
        return tiles.ShopKeeper(self.__cbp.visit_shop, [ShopItem(item) for item in items])

    def visitPuzzle_parameter(self, ctx: QrogueDungeonParser.Puzzle_parameterContext) \
            -> Tuple[StateVector, Collectible]:
        ref_index = 0
        if ctx.stv():
            stv = self.visit(ctx.stv())
        else:
            difficulty = self.__load_target_difficulty(ctx.REFERENCE(ref_index))
            ref_index += 1
            stv = difficulty.create_statevector(self.__robot, self.__rm)

        if ctx.collectible():
            reward = self.visit(ctx.collectible())
        else:
            reward_factory = self.__load_collectible_factory(ctx.REFERENCE(ref_index))
            reward = reward_factory.produce(self.__rm)
        return stv, reward

    def visitInput_stv(self, ctx: QrogueDungeonParser.Input_stvContext) -> StateVector:
        if ctx.REFERENCE():
            difficulty = self.__load_target_difficulty(ctx.REFERENCE())
            return difficulty.create_statevector(self.__robot, self.__rm)
        else:
            return self.visit(ctx.stv())

    def visitRiddle_descriptor(self, ctx: QrogueDungeonParser.Riddle_descriptorContext) -> tiles.Riddler:
        attempts = self.visit(ctx.integer())
        stv, reward = self.visit(ctx.puzzle_parameter())
        riddle = Riddle(stv, reward, attempts)
        return tiles.Riddler(self.__cbp.open_riddle, riddle)

    def visitChallenge_descriptor(self, ctx: QrogueDungeonParser.Challenge_descriptorContext) -> tiles.Challenger:
        min_gates = self.visit(ctx.integer(0))
        if ctx.integer(1):
            max_gates = self.visit(ctx.integer(1))
        else:
            max_gates = min_gates

        stv, reward = self.visit(ctx.puzzle_parameter())
        challenge = Challenge(stv, reward, min_gates, max_gates)
        return tiles.Challenger(self.__cbp.open_challenge, challenge)

    def visitEnergy_descriptor(self, ctx: QrogueDungeonParser.Energy_descriptorContext) -> tiles.Tile:
        amount = self.visit(ctx.integer())
        return tiles.Energy(amount)

    def visitTrigger_descriptor(self, ctx: QrogueDungeonParser.Trigger_descriptorContext) -> tiles.Trigger:
        if ctx.GLOBAL_ACHIEVEMENT():
            ref = MapConfig.global_event_prefix() + parser_util.normalize_reference(ctx.REFERENCE().getText())
        elif ctx.UNLOCK():
            ref = MapConfig.unlock_prefix() + parser_util.normalize_reference(ctx.REFERENCE().getText())
        else:   # ctx.LEVEL_ACHIEVEMENT() is the default value so we don't have to check for it
            ref = parser_util.normalize_reference(ctx.REFERENCE().getText())

        def callback(_: Direction, __: Controllable):
            self.__trigger_event(ref)

        return tiles.Trigger(callback)

    def visitTeleport_descriptor(self, ctx: QrogueDungeonParser.Teleport_descriptorContext) -> tiles.Teleport:
        if ctx.GLOBAL_TELEPORT():
            ref = parser_util.normalize_reference(ctx.REFERENCE().getText())
            return tiles.Teleport(self.__load_map, ref, None)
        elif ctx.LOCAL_TUNNEL():
            room_id = ctx.ROOM_ID().getText()
            if ctx.integer():
                num = self.visit(ctx.integer())
                x = num % MapConfig.room_width()
                y = int(num / MapConfig.room_height())
            else:
                x, y = MapConfig.room_mid()
            return tiles.Tunnel(self.__tunnel_callback, room_id, Coordinate(x, y))
        else:
            parser_util.error("Invalid Teleport description!")

    def visitT_descriptor(self, ctx: QrogueDungeonParser.T_descriptorContext) -> tiles.Tile:
        if ctx.trigger_descriptor():
            return self.visit(ctx.trigger_descriptor())
        elif ctx.teleport_descriptor():
            return self.visit(ctx.teleport_descriptor())
        else:
            parser_util.error("Invalid T-descriptor! Neither trigger nor teleporter was provided")

    def visitMessage_descriptor(self, ctx: QrogueDungeonParser.Message_descriptorContext) -> tiles.Message:
        if ctx.integer():
            times = self.visit(ctx.integer())
        else:
            times = -1      # = always show
        if ctx.REFERENCE() is None:
            message = Message.create_with_title(f"{self.__QUICK_MSG_PREFIX}{self.__QUICK_MSG_ID}",
                                                title=self.__default_speaker, text=parser_util.text_to_str(ctx),
                                                priority=False)
            self.__QUICK_MSG_ID += 1
        else:
            message = self.__load_message(ctx.REFERENCE())
        return tiles.Message(message, times)

    def visitCollectible_descriptor(self, ctx: QrogueDungeonParser.Collectible_descriptorContext) -> tiles.Collectible:
        if ctx.REFERENCE():
            collectible_factory = self.__load_collectible_factory(ctx.REFERENCE())
            times = 1
            if ctx.integer():
                times = self.visit(ctx.integer())
            if times > 1:
                collectible = MultiCollectible(collectible_factory.produce_multiple(self.__rm, times))
            else:
                collectible = collectible_factory.produce(self.__rm)
        else:
            collectible = self.visit(ctx.collectible())
            if collectible is None:
                self.warning("Wrongly described collectible! Creating one of the default pool instead.")
                collectible = self.__default_collectible_factory.produce(self.__rm)
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
            reward_factory = self.__load_collectible_factory(ctx.REFERENCE(ref_index))
        else:
            # if neither a collectible nor a reference to a reward_factory is given we use the default one
            reward_factory = None

        if ctx.stv():
            stv = self.visit(ctx.stv())
            if reward_factory is None:
                reward_factory = self.__default_collectible_factory    # set reward factory here to not set a custom one
            difficulty = ExplicitTargetDifficulty([stv], reward_factory)
        else:
            # don't use ref_index here because it will always be 0 if present
            difficulty = self.__load_target_difficulty(ctx.REFERENCE(0))

        input_stv = self.visit(ctx.input_stv()) if ctx.input_stv() else None

        enemy_factory = EnemyFactory(self.__cbp.start_fight, difficulty, 1, input_stv)
        if reward_factory:  # if a reward pool was specified we use it
            enemy_factory.set_custom_reward_factory(reward_factory)
        # else we use the default one either of the loaded difficulty or it already is default_collectible_factory

        enemy = tiles.Enemy(enemy_factory, get_entangled_tiles, update_entangled_room_groups, enemy_id)
        #   update_entangled_room_groups(enemy) # by commenting this the original (copied from) tile is not in the list
        return enemy

    def visitTile_descriptor(self, ctx: QrogueDungeonParser.Tile_descriptorContext) -> tiles.Tile:
        if ctx.t_descriptor():
            tile = self.visit(ctx.t_descriptor())
        elif ctx.enemy_descriptor():
            tile = self.visit(ctx.enemy_descriptor())
        elif ctx.collectible_descriptor():
            tile = self.visit(ctx.collectible_descriptor())
        elif ctx.energy_descriptor():
            tile = self.visit(ctx.energy_descriptor())
        elif ctx.riddle_descriptor():
            tile = self.visit(ctx.riddle_descriptor())
        elif ctx.challenge_descriptor():
            tile = self.visit(ctx.challenge_descriptor())
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
            if ctx.TUTORIAL_LITERAL():
                msg = self.__load_message(ctx.REFERENCE(ref_index))
                tile.set_explanation(msg)
                ref_index += 1
            if ctx.TRIGGER_LITERAL():
                if ctx.GLOBAL_EVENT_REFERENCE():
                    event_id = parser_util.normalize_reference(ctx.GLOBAL_EVENT_REFERENCE().getText())
                elif ctx.UNLOCK_REFERENCE():
                    event_id = parser_util.normalize_reference(ctx.UNLOCK_REFERENCE().getText())
                else:
                    event_id = parser_util.normalize_reference(ctx.REFERENCE(ref_index).getText())
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
        elif ctx.CHALLENGE_LITERAL():
            return rooms.AreaType.ChallengeRoom
        elif ctx.PAUSE_LITERAL():
            return rooms.AreaType.PauseRoom
        elif ctx.STORY_LITERAL():
            return rooms.AreaType.StoryRoom
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

    def visitLayout(self, ctx: QrogueDungeonParser.LayoutContext) -> List[List[Optional[rooms.Room]]]:
        # first setup all hallway connections
        for y, hw_row in enumerate(ctx.l_hallway_row()):
            self.__visitL_hallway_row(hw_row, y)

        room_matrix: List[List[Optional[rooms.Room]]] = []
        for y in range(MapConfig.map_height()):
            row_ctx = ctx.l_room_row(y)
            if row_ctx:
                room_matrix.append(self.__visitL_room_row(row_ctx, y))
            else:
                break
        if ctx.l_room_row(MapConfig.map_height()):
            self.warning(f"Too much room rows specified. Only maps of size ({MapConfig.map_width()}, "
                         f"{MapConfig.map_height()}) supported. Ignoring over-specified rows.")

        return room_matrix

    def __hallway_handling(self, ctx_children: List[TerminalNodeImpl], y: int, direction: Direction):
        x = 0
        for child in ctx_children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type,
                                                           QrogueDungeonParser.VERTICAL_SEPARATOR):
                self.warning(
                    f"Too much room columns specified. Only maps of size ({MapConfig.map_width()}, "
                    f"{MapConfig.map_height()}) supported. Ignoring over-specified columns.")
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

    def __visitL_room_row(self, ctx: QrogueDungeonParser.L_room_rowContext, y: int) -> List[Optional[rooms.Room]]:
        self.__hallway_handling(ctx.children, y, Direction.East)     # connect to the right to the next room

        row: List[Optional[rooms.Room]] = []
        x = 0
        for child in ctx.children:
            if parser_util.check_for_overspecified_columns(x, child.symbol.type,
                                                           QrogueDungeonParser.VERTICAL_SEPARATOR):
                self.warning(f"Too much room columns specified. Only maps of size ({MapConfig.map_width()}, "
                             f"{MapConfig.map_height()}) supported. Ignoring over-specified columns.")
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
            gates.append(self.__load_gate(ref))  # todo what about pickups?

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

        self.__robot = robot.BaseBot(CallbackPack.instance().game_over, num_of_qubits, gates, circuit_space,
                                     backpack_space, max_energy, start_energy)

    ##### Meta area #####

    def visitMeta(self, ctx: QrogueDungeonParser.MetaContext) -> MapMetaData:
        if ctx.TEXT():
            name = parser_util.text_to_str(ctx)
        else:
            name = None
        if ctx.message_body():
            title, priority, position, msg = parser_util.parse_message_body(ctx.message_body(), self.__default_speaker)
            message = Message.create_with_title("_map_description", title, msg, priority, position)
        elif ctx.REFERENCE():
            message = self.__load_message(ctx.REFERENCE())
        else:
            message = None
        return MapMetaData(name, message, ctx.NO_TELEPORTER() is None, self.__show_description,
                           ctx.SHOW_INDIV_QUBITS() is not None)

    ##### Start area #####

    def visitStart(self, ctx: QrogueDungeonParser.StartContext) -> Tuple[MapMetaData, List[List[Optional[rooms.Room]]]]:
        # prepare messages (needs to be done first since metadata might reference it
        self.visit(ctx.messages())

        # retrieve the map's meta data
        self.__meta_data = self.visit(ctx.meta())

        # prepare the robot
        self.visit(ctx.robot())

        # prepare reward pools first because they are standalone
        self.visit(ctx.reward_pools())
        # prepare state vector pools next because they can only reference reward pools
        self.visit(ctx.stv_pools())

        # prepare hallways next because they are standalone but thematically more connected to rooms
        self.visit(ctx.hallways())
        # now prepare the rooms because they can reference everything above
        self.visit(ctx.rooms())

        # for the last step we retrieve the room matrix from layout
        return self.__meta_data, self.visit(ctx.layout())
