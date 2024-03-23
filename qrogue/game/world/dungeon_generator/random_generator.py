from enum import IntEnum
from typing import Callable, Dict, Optional, Tuple, List, Any, Set, Union

from qrogue.game.logic.actors import Robot
from qrogue.game.logic.collectibles import GateFactory, Key, instruction, Score, CollectibleType, \
    CollectibleFactory, Instruction
from qrogue.game.target_factory import PuzzleDifficulty, BossFactory, EnemyFactory, RiddleFactory, EnemyPuzzleFactory
from qrogue.game.world import tiles
from qrogue.game.world.dungeon_generator.wave_function_collapse import WFCRoomGenerator, WFCEmptyRoomGenerator
from qrogue.game.world.map import CallbackPack, Hallway, WildRoom, SpawnRoom, ShopRoom, RiddleRoom, BossRoom, \
    TreasureRoom, ExpeditionMap, Room
from qrogue.game.world.map.rooms import Placeholder, AreaType, DefinedWildRoom, EmptyRoom
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.util import Logger, RandomManager, MapConfig, Config

from qrogue.game.world.dungeon_generator.generator import DungeonGenerator


class _Code(IntEnum):
    # meta codes
    PriorityMul = -1
    Free = PriorityMul  # best priority for free, unbiased cells
    Blocked = 0  # all before Blocked is free, all after Blocked is already taken
    # room codes
    Spawn = 10
    Shop = 40
    Riddle = 50
    Boss = 60
    Gate = 70
    Phantom = 80
    Wild = 100
    # hallway codes
    North = 1
    East = 2
    South = 4
    West = 8

    @staticmethod
    def normal_rooms() -> "[_Code]":
        return [_Code.Wild, _Code.Spawn]

    @staticmethod
    def special_rooms() -> "[_Code]":
        return [_Code.Shop, _Code.Riddle, _Code.Boss, _Code.Gate]

    @staticmethod
    def get_priority(code: "_Code", inverse: bool) -> float:
        if inverse:
            if code < _Code.Blocked:
                return 20
        elif code > _Code.Blocked:
            if code == _Code.Spawn:
                return 200
            if code == _Code.Wild:
                return 12
            if code in [_Code.Shop, _Code.Riddle, _Code.Gate]:
                return 5
        return 0

    @staticmethod
    def to_string(code: "_Code", justify: bool = False):
        if justify:
            return _Code.__to_string(code).rjust(4, " ").ljust(5, " ")
        else:
            return _Code.__to_string(code)

    @staticmethod
    def __to_string(code: "_Code"):
        if code < _Code.Blocked:
            str_rep = str(int(code))[1:]
            if len(str_rep) < 4:
                return str_rep
            else:
                return str_rep[0:4]
        if code == _Code.Blocked:
            return "x"
        if code == _Code.Spawn:
            return "S"
        if code == _Code.Shop:
            return "$"
        if code == _Code.Riddle:
            return "?"
        if code == _Code.Boss:
            return "B"
        if code == _Code.Gate:
            return "G"
        if code == _Code.Wild:
            return "W"
        if code == _Code.Phantom:
            return "%"
        return "#"

    @staticmethod
    def from_enum_string(enum_string: str) -> "_Code":
        if enum_string.startswith("_Code"):
            enum_string = enum_string[enum_string.index(".") + 1:]
        return _Code[enum_string]


class RandomLayoutGenerator:
    __MIN_AREA = 10
    __MIN_NORMAL_ROOMS = 4

    def __init__(self, seed: int, width: int, height: int):
        self.__seed = seed
        if width * height < RandomLayoutGenerator.__MIN_AREA:
            Logger.instance().throw(ValueError(f"width={width}, height={height} create a too small grid "
                                               f"(minimal grid area = {RandomLayoutGenerator.__MIN_AREA}). Please use bigger values!"))
        self.__rm = RandomManager.create_new(seed)
        self.__width = width
        self.__height = height
        # generate empty map
        self.__map = [[_Code.Free] * self.__width for _ in range(self.__height)]
        self.__normal_rooms: Set[Coordinate] = set()
        self.__hallways: Dict[Coordinate, Dict[Coordinate, tiles.Door]] = {}
        self.__prio_sum = self.__width * self.__height
        self.__prio_mean = 1.0
        self.__spawn_pos: Optional[Coordinate] = None

    @property
    def seed(self) -> int:
        return self.__seed

    def __get(self, pos: Coordinate) -> _Code:
        return self.__map[pos.y][pos.x]

    def __set(self, pos: Coordinate, code: _Code):
        if code in [_Code.Spawn, _Code.Wild]:
            self.__normal_rooms.add(pos)
        self.__map[pos.y][pos.x] = code

    def __new_prio(self):
        prio_sum = 0
        for y in range(self.__height):
            for x in range(self.__width):
                pos = Coordinate(x, y)
                code = self.__get(pos)
                if code < _Code.Blocked:
                    prio_sum += 1
        self.__prio_sum = prio_sum

    def __is_valid_pos(self, pos: Coordinate) -> bool:
        return 0 <= pos.x < self.__width and 0 <= pos.y < self.__height

    def __is_corner(self, pos: Coordinate) -> (Direction, Direction):
        if pos.x == 0 and pos.y == 0:
            return Direction.East, Direction.South
        if pos.x == 0 and pos.y == self.__height - 1:
            return Direction.East, Direction.North
        if pos.x == self.__width - 1 and pos.y == 0:
            return Direction.West, Direction.South
        if pos.x == self.__width - 1 and pos.y == self.__height - 1:
            return Direction.West, Direction.North
        return None

    def __available_directions(self, pos: Coordinate, allow_wildrooms: bool = False) -> [Direction]:
        directions = []
        # check if going into a direction leaves you still in the grid and on a free spot
        for direction in Direction.values():
            new_pos = pos + direction
            if self.__is_valid_pos(new_pos):
                code = self.__get(new_pos)
                if code < _Code.Blocked or allow_wildrooms and code == _Code.Wild:
                    directions.append(direction)
        return directions

    def __get_neighbors(self, pos: Coordinate, free_spots: bool = False) -> List[Tuple[Direction, _Code, Coordinate]]:
        neighbors = []
        for direction in Direction.values():
            new_pos = pos + direction
            if self.__is_valid_pos(new_pos):
                code = self.__get(new_pos)
                if free_spots:
                    if code < _Code.Blocked:
                        neighbors.append((direction, code, new_pos))
                elif code in _Code.normal_rooms():
                    neighbors.append((direction, code, new_pos))
        return neighbors

    def __random_border(self) -> Optional[Coordinate]:
        directions = Direction.values()
        while len(directions) > 0:
            direction = self.__rm.get_element(directions, remove=True, msg="RandomGen_borderDirection")
            if direction == Direction.North or direction == Direction.South:
                y = (self.__height - 1) * (
                            direction == Direction.South)  # for North this is 0, for South self.__height-1
                xs = list(range(0, self.__width))
                while len(xs) > 0:
                    x = self.__rm.get_element(xs, remove=True, msg="RandomGen_borderX")
                    pos = Coordinate(x=x, y=y)
                    if self.__get(pos) < _Code.Blocked:
                        return pos
            else:
                x = (self.__width - 1) * (direction == Direction.East)  # for North this is 0, for South self.__height-1
                ys = list(range(0, self.__height))
                while len(ys) > 0:
                    y = self.__rm.get_element(ys, remove=True, msg="RandomGen_borderY")
                    pos = Coordinate(x=x, y=y)
                    if self.__get(pos) < _Code.Blocked:
                        return pos
        return None

    def __random_coordinate(self) -> Coordinate:
        val = self.__rm.get(msg="RandomDG_coordinate")
        cur_val = 0.0
        for y in range(self.__height):
            for x in range(self.__width):
                pos = Coordinate(x, y)
                code = self.__get(pos)
                # if there is already something at this position, we continue with the next
                if code >= _Code.Blocked:
                    continue
                code = code * _Code.PriorityMul
                cur_val += code / self.__prio_sum
                if val < cur_val:
                    return pos
        Logger.instance().throw(NotImplementedError(f"Failed to get a random coordinate (generator.py) for seed = "
                                                    f"{self.seed}. Please do report this error as this should not be "
                                                    "possible to occur! :("))

    def __random_free_wildroom_neighbors(self, num: int = 1) -> List[Tuple[Tuple[Direction, _Code, Coordinate], Coordinate]]:
        rooms: Set[Coordinate] = self.__normal_rooms
        room_prios: Dict[Tuple[Direction, _Code, Coordinate], Tuple[int, Coordinate]] = {}
        max_distance = self.__width + self.__height - 2
        prio_sum = 0
        # calculate the priorities of WR neighbors based on the "isolation" (distance to other WR or SR) of the WR and
        # inverse of the isolation of the neighbor (except its original WR of course)
        for room in rooms:
            min_distance = max_distance
            for other in rooms:
                if room is not other:   # check distance to other WRs and SR except itself
                    min_distance = min(min_distance, Coordinate.distance(room, other))
            neighbors = self.__get_neighbors(room, free_spots=True)
            for neighbor in neighbors:
                _, _, neighbor_pos = neighbor
                neighbor_distance = max_distance
                for other in rooms:
                    if room is not other:   # check distance to other WRs and SR (except the WR we know is a neighbor)
                        neighbor_distance = min(neighbor_distance, Coordinate.distance(neighbor_pos, other))
                # high isolation of room and low isolation of neighbor means high priority
                prio = min_distance * (max_distance - neighbor_distance)
                prio_sum += prio
                room_prios[neighbor] = (prio, room)

        if prio_sum == 0:
            Logger.instance().error(f"Illegal prio_sum for seed = {self.seed} in generator.py\nThis should not be "
                                    "possible to occur but aside from the randomness during layout generation this "
                                    "doesn't break anything. Please consider reporting!", from_pycui=False)
            prio_sum = -1.0

        picked_rooms: List[Tuple[Tuple[Direction, _Code, Coordinate], Coordinate]] = []
        for i in range(num):
            val = self.__rm.get(msg="RandomDG_WRNeighbors")
            cur_val = 0.0
            for room in room_prios:
                prio, rp = room_prios[room]
                cur_val += prio / prio_sum    # both values have the same sign so their fraction is positive
                if val < cur_val:
                    picked_rooms.append((room, rp))
                    room_prios.pop(room)
                    break
        return picked_rooms

    def __add_hallway(self, room1: Coordinate, room2: Coordinate, door: tiles.Door):
        if room1 in self.__hallways:
            self.__hallways[room1][room2] = door
        else:
            self.__hallways[room1] = {room2: door}
        if room2 in self.__hallways:
            self.__hallways[room2][room1] = door
        else:
            self.__hallways[room2] = {room1: door}

    def __place_wild(self, room: Coordinate, door: tiles.Door):
        pos = room + door.direction
        self.__set(pos, _Code.Wild)
        self.__add_hallway(room, pos, door)

    def __place_special_room(self, code: _Code) -> Coordinate:
        while True:
            try:
                pos = self.__random_border()
                self.__set(pos, code)
                direction = self.__rm.get_element(self.__available_directions(pos, allow_wildrooms=True), msg="RandomGen_dirSpecialR")
                if direction is None:
                    self.__set(pos, _Code.Blocked)  # position is not suited for a special room
                else:
                    wild_room = pos + direction
                    if self.__is_corner(wild_room):
                        # if the connected WildRoom is in the corner, we swap position between it and the SpecialRoom
                        self.__set(wild_room, code)
                        self.__place_wild(wild_room, tiles.Door(direction.opposite(), tiles.DoorOpenState.KeyLocked))
                        return wild_room
                    else:
                        self.__place_wild(pos, tiles.Door(direction, tiles.DoorOpenState.KeyLocked))
                        return pos
            except NotImplementedError:
                Logger.instance().error("Unimplemented case happened!", from_pycui=False)

    def __astar_connect_neighbors(self, visited: set, pos: Coordinate) -> Tuple[Coordinate, bool]:
        """

        :param visited:
        :param pos: the position of a cell that has no Hallways that could lead to the target
        :return:
        """
        relevant_neighbors = []
        # only consider the neighbors we haven't visited yet
        for room in self.__get_neighbors(pos):
            _, _, new_pos = room
            if new_pos not in visited:
                relevant_neighbors.append(room)

        if len(relevant_neighbors) > 0:
            # there are neighbors we can connect to
            room = self.__rm.get_element(relevant_neighbors, msg="RandomGen_astarNeighbor")
            door = tiles.Door(room[0])
            self.__add_hallway(pos, room[2], door)
            return room[2], False
        else:
            if self.__get(pos) in _Code.special_rooms():
                Logger.instance().debug(f"SpecialRoom marked as dead end for seed = {self.seed}", from_pycui=False)
            return pos, True  # we found a dead end

    def __astar(self, visited: Set[Coordinate], pos: Coordinate, target: Coordinate, connect: bool = True) \
            -> Tuple[Optional[Set[Coordinate]], bool]:
        """

        :param visited: Coordinates of all cells we already visited
        :param pos: position/Coordinate of the cell we currently check
        :param target: the cell we try to find
        :param connect: whether we try to create new connection(s) in case we cannot find target
        :return: list of dead ends on the path and False if the target cannot be reached, otherwise True
        """
        dead_ends: Set[Coordinate] = set()
        neighbors = list(self.__hallways[pos].keys())

        if target in neighbors:
            return None, True  # we found the target

        while neighbors:
            room = self.__rm.get_element(neighbors, remove=True, msg="RandomGen_astarRoom")
            if room in visited:
                continue
            visited.add(room)
            ret, success = self.__astar(visited, pos=room, target=target, connect=connect)
            if ret:
                dead_ends.update(ret)
            if success:
                return dead_ends, True

        if connect:
            cur_pos = pos
            while True:
                # we come back from a dead end, so we check if we can connect the current cell with a non-visited neighbor
                coordinate, dead_end = self.__astar_connect_neighbors(visited, cur_pos)
                if dead_end:
                    if len(self.__get_neighbors(coordinate, free_spots=True)) > 0:
                        dead_ends.add(coordinate)
                    return dead_ends, False
                else:
                    visited.add(coordinate)
                    ret, success = self.__astar(visited, pos=coordinate, target=target)
                    if ret is not None:
                        dead_ends.update(ret)
                    if success:
                        return dead_ends, True
        else:
            return dead_ends, False

    def __call_astar(self, visited: Set[Coordinate], start_pos: Coordinate, target_pos: Coordinate,
                     connect: bool = True) -> bool:
        dead_ends, success = self.__astar(visited, start_pos, target=target_pos, connect=connect)
        if success:
            return True
        if connect:
            dead_ends = list(dead_ends)
            while dead_ends:
                dead_end = self.__rm.get_element(dead_ends, remove=True, msg="RandomGen_astarDeadEnd")
                relevant_pos = self.__get_neighbors(dead_end, free_spots=True)
                # and try to place a new room to connect the dead end to the rest
                while relevant_pos:
                    direction, _, new_pos = self.__rm.get_element(relevant_pos, remove=True, msg="RandomGen_astarRelevantPos")
                    self.__place_wild(dead_end, tiles.Door(direction))
                    visited.add(new_pos)
                    if self.__call_astar(visited, start_pos=new_pos, target_pos=target_pos):
                        return True
        return False

    def get_hallway(self, pos: Coordinate) -> Optional[Dict[Coordinate, tiles.Door]]:
        if pos in self.__hallways:
            return self.__hallways[pos]
        return None

    def get_room(self, pos: Coordinate) -> Optional[_Code]:
        if self.__is_valid_pos(pos):
            return self.__get(pos)
        return None

    def generate(self, debug: bool = False) -> bool:
        # place the spawn room
        self.__spawn_pos = self.__random_coordinate()
        self.__set(self.__spawn_pos, _Code.Spawn)

        # special case if SpawnRoom is in a corner
        corner = self.__is_corner(self.__spawn_pos)
        if corner:
            if self.__get(self.__spawn_pos + corner[0]) < _Code.Blocked:
                self.__place_wild(self.__spawn_pos, tiles.Door(corner[0]))
            if self.__get(self.__spawn_pos + corner[1]) < _Code.Blocked:
                self.__place_wild(self.__spawn_pos, tiles.Door(corner[1]))

        # place the special rooms
        special_rooms = [
            self.__place_special_room(_Code.Shop),
            self.__place_special_room(_Code.Riddle),
            self.__place_special_room(_Code.Boss),
            self.__place_special_room(_Code.Gate),
        ]

        # create a locked hallway to spawn_pos-neighboring WildRooms if they lead to SpecialRooms
        #directions = self.__available_directions(self.__spawn_pos, allow_wildrooms=True)
        #for direction in directions:
        #    new_pos = self.__spawn_pos + direction
        #    if self.__get(new_pos) == _Code.Wild:
        #        #wild_directions = self.__available_directions(self.__spawn_pos, allow_wildrooms=True)
        #        door = tiles.Door(direction, locked=True)
        #        self.__add_hallway(self.__spawn_pos, new_pos, door)

        self.__new_prio()
        if len(self.__normal_rooms) < RandomLayoutGenerator.__MIN_NORMAL_ROOMS:
            self.__prio_sum -= (len(self.__normal_rooms) + len(special_rooms))  # subtract now blocked Rooms
            pos = self.__random_coordinate()
            self.__set(pos, _Code.Wild)

        if debug:
            print(self)

        # fill up the rest with a couple of WildRooms
        for num in [3, 2, 1, 1]:
            rooms = self.__random_free_wildroom_neighbors(num)
            for room in rooms:
                direction, code, new_pos = room[0]
                pos = room[1]
                self.__set(new_pos, _Code.Wild)
                self.__add_hallway(pos, new_pos, tiles.Door(direction))

        # add a connection if the SpawnRoom is not connected to a WildRoom
        if self.__spawn_pos not in self.__hallways:
            neighbors = self.__get_neighbors(self.__spawn_pos)
            if len(neighbors) > 0:
                direction, _, new_pos = self.__rm.get_element(neighbors, msg="RandomGen_neighbor")
                self.__add_hallway(self.__spawn_pos, new_pos, tiles.Door(direction))

        success = True
        # as last step, add missing Hallways and WildRooms to connect every SpecialRoom with the SpawnRoom
        rooms = list(special_rooms)
        while rooms:
            room = rooms.pop(0)
            visited: Set[Coordinate] = set(special_rooms)
            start_pos = list(self.__hallways[room].keys())[0]
            visited.add(start_pos)
            if not self.__call_astar(visited, start_pos, self.__spawn_pos):
                success = False
                break
        if success:
            return True
        else:
            # try to create a connection to solve the issue
            for room in rooms:
                start_pos = list(self.__hallways[room].keys())[0]
                visited = set(special_rooms)
                dead_ends, success = self.__astar(visited, start_pos, self.__spawn_pos)
                if not success:
                    return False
            return True

    def validate(self) -> bool:
        # first check if all SpecialRooms have exactly 1 connection
        for y in range(self.__height):
            for x in range(self.__width):
                pos = Coordinate(x, y)
                code = self.__get(pos)
                if code in [_Code.Boss, _Code.Shop, _Code.Riddle, _Code.Gate]:
                    connections = self.__hallways[pos]
                    if len(connections) != 1:
                        return False

        # second check if hallways are symmetric and contain the same doors
        for pos in self.__hallways:
            for neigh in self.__hallways[pos]:
                if pos not in self.__hallways[neigh] or self.__hallways[pos][neigh] != self.__hallways[neigh][pos]:
                    print(self)
                    return False

        # third check if we can reach the spawn room from every room with a hallway
        for pos in self.__hallways:
            visited = set()
            if not self.__call_astar(visited, start_pos=pos, target_pos=self.__spawn_pos, connect=False):
                # now we either found a faulty connection or some "phantom rooms" which are only connected to themselves
                self.__map[pos.y][pos.x] = _Code.Phantom
                new_visited = set()
                # we only have to check immediate neighbors since the neighbors are also checked in the outer loop,
                # therefore, also their neighbors and ultimately any of these "phantom rooms" are checked
                for neigh in self.__hallways[pos]:
                    # see if a neighbor can reach spawn_pos (= neighbor is not a "phantom room" and hence the connection
                    # is faulty)
                    if self.__call_astar(new_visited, start_pos=neigh, target_pos=self.__spawn_pos, connect=False):
                        print(self)
                        return False
        return True

    def __str__(self):
        cell_width = 5
        __empty = "     "
        __row_sep = "_" * (cell_width + 1) * self.__width
        str_rep = " " + __row_sep + "\n"
        for y in range(self.__height):
            rows: List[str] = ["|"] * 3
            for x in range(self.__width):
                pos = Coordinate(x, y)
                if pos in self.__hallways:
                    hws = self.__hallways[pos]
                    if pos + Direction.North in hws:
                        rows[0] += "  ^  "
                    else:
                        rows[0] += __empty
                    code = self.__get(pos)
                    if code < _Code.Blocked:
                        rows[1] += f"{_Code.to_string(code, justify=True)}"
                    else:
                        if pos + Direction.West in hws:
                            rows[1] += " <"
                        else:
                            rows[1] += "  "
                        rows[1] += _Code.to_string(code)
                        if pos + Direction.East in hws:
                            rows[1] += "> "
                        else:
                            rows[1] += "  "
                    if pos + Direction.South in hws:
                        rows[2] += "  ~  "
                    else:
                        rows[2] += __empty
                    for i in range(len(rows)):
                        rows[i] += "|"
                else:
                    rows[0] += __empty + "|"
                    rows[1] += f"{_Code.to_string(self.__get(pos), justify=True)}|"
                    rows[2] += __empty + "|"
            str_rep += "\n".join(rows) + "\n"
            str_rep += " " + __row_sep + " \n"
        return str_rep


class ExpeditionGenerator(DungeonGenerator):
    __MAX_ROOM_GEN_TRIES = 10
    __BLOCKING_WEIGHT = 2
    __INVALID_WEIGHT = 1_000_000

    @staticmethod
    def __create_enemy(enemy_id: int, room_pos: Coordinate, enemy_factory: EnemyFactory,
                       enemy_groups_by_room: Dict[Coordinate, Dict[int, List[tiles.Enemy]]],
                       next_tile_id: Callable[[], int]) -> tiles.Enemy:
        enemy: Optional[tiles.Enemy] = None

        def get_entangled_tiles(id_: int) -> List[tiles.Enemy]:
            if room_pos in enemy_groups_by_room:
                room_dic = enemy_groups_by_room[room_pos]
                return room_dic[id_]
            else:
                return [enemy]

        def update_entangled_room_groups(new_enemy: tiles.Enemy):
            if room_pos not in enemy_groups_by_room:
                enemy_groups_by_room[room_pos] = {}
            if enemy_id not in enemy_groups_by_room[room_pos]:
                enemy_groups_by_room[room_pos][enemy_id] = []
            enemy_groups_by_room[room_pos][enemy_id].append(new_enemy)

        enemy = tiles.Enemy(enemy_factory, get_entangled_tiles, update_entangled_room_groups, enemy_id, next_tile_id)
        update_entangled_room_groups(enemy)
        return enemy

    def __init__(self, seed: int, check_achievement: Callable[[str], bool], trigger_event: Callable[[str], None],
                 load_map_callback: Callable[[str, Optional[Coordinate]], None], callback_pack: CallbackPack,
                 width: int = DungeonGenerator.WIDTH, height: int = DungeonGenerator.HEIGHT):
        super(ExpeditionGenerator, self).__init__(seed, width, height)
        self.__check_achievement = check_achievement
        self.__trigger_event = trigger_event
        self.__load_map = load_map_callback
        self.__cbp = callback_pack
        self.__rm = RandomManager.create_new(seed)
        self.__next_target_id = 0
        self.__next_tile_id = 0

        self.__remaining_keys = 0
        self.__room_has_key = False

        if Config.skip_learning():
            self.__wild_room_generator = WFCEmptyRoomGenerator()
        else:
            self.__wild_room_generator = WFCRoomGenerator(seed, WFCRoomGenerator.get_level_list()[2:], AreaType.WildRoom)

    def _next_target_id(self) -> int:
        val = self.__next_target_id
        self.__next_target_id += 1
        return val

    def _next_tile_id(self) -> int:
        val = self.__next_tile_id
        self.__next_tile_id += 1
        return val

    def generate(self, data: Union[Robot, Tuple[Robot, int]]) -> Tuple[Optional[ExpeditionMap], bool]:
        if isinstance(data, Robot):
            robot = data
            seed = self.__rm.get_seed("seed for generating with ExpeditionGenerator")
        else:
            robot, seed = data
            assert seed is not None, "Did not provide a seed!"

        if len(robot.get_available_instructions()) <= 0:
            gates = [instruction.HGate(), instruction.SGate(), instruction.XGate(), instruction.CXGate()]
            for gate in gates:
                robot.give_collectible(gate)

        rm = RandomManager.create_new(seed)  # needed for WildRooms
        gate_factory = GateFactory.quantum()
        riddle_factory = RiddleFactory.default(robot)
        boss_factory = BossFactory.default(robot)
        typed_collectible_factory: Dict[Optional[CollectibleType], CollectibleFactory] = {
            None: CollectibleFactory([Score(100)]),    # default factory
            CollectibleType.Gate: CollectibleFactory([Score(200)]),
            CollectibleType.Pickup: CollectibleFactory([Score(150)])
        }
        self.__remaining_keys = 3
        self.__room_has_key = False

        def get_collectible_factory(type_: CollectibleType) -> CollectibleFactory:
            if type_ in typed_collectible_factory:
                return typed_collectible_factory[type_]
            return typed_collectible_factory[None]

        gate: Instruction = gate_factory.produce(rm)
        riddle = riddle_factory.produce(rm)
        dungeon_boss = boss_factory.produce(include_gates=[], input_gates=[gate])

        # Difficulties can be misleading since picking one gate can result in CX Gate which does nothing if it's the
        # only gate on a zero-state. Also picking multiple gates where one is CX has a higher probability of doing
        # nothing the more qubits we have.
        enemy_factories = [
            EnemyPuzzleFactory(self.__cbp.start_fight, self._next_target_id, PuzzleDifficulty(1, 3)),
            EnemyPuzzleFactory(self.__cbp.start_fight, self._next_target_id, PuzzleDifficulty(2, 2)),
            EnemyPuzzleFactory(self.__cbp.start_fight, self._next_target_id, PuzzleDifficulty(2, 3)),
            EnemyPuzzleFactory(self.__cbp.start_fight, self._next_target_id, PuzzleDifficulty(1, 2)),
        ]
        # factories are picked room-wise
        enemy_factory_priorities = [0.25, 0.35, 0.3, 0.1]
        enemy_groups_by_room = {}

        rooms: List[List[Optional[Room]]] = [[None for _ in range(self.width)] for _ in range(self.height)]
        spawn_room = None
        created_hallways = {}
        layout = RandomLayoutGenerator(seed, self.width, self.height)
        if layout.generate() and layout.validate():
            for y in range(self.height):
                for x in range(self.width):
                    self.__room_has_key = False
                    pos = Coordinate(x, y)
                    code = layout.get_room(pos)
                    if code is not None and code > _Code.Blocked:
                        room_hallways = {
                            Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None,
                        }
                        hallways = layout.get_hallway(pos)
                        if hallways is None:
                            if code == _Code.Wild:
                                # it is completely fine if it happens that an isolated WildRoom was generated
                                continue
                            else:
                                Logger.instance().throw(NotImplementedError(
                                    f"Found a SpecialRoom ({code}) without connecting Hallways for seed = "
                                    f"{self.seed}. Please do report this error as this should not be "
                                    "possible to occur! :("))

                        direction: Optional[Direction] = None
                        for neighbor in hallways:
                            direction = Direction.from_coordinates(pos, neighbor)
                            opposite = direction.opposite()
                            # get hallway from neighbor if it exists, otherwise create it
                            if neighbor in created_hallways and opposite in created_hallways[neighbor]:
                                hallway = created_hallways[neighbor][opposite]
                            else:
                                hallway = Hallway(hallways[
                                                      neighbor])  # todo create door here and only check if it should be locked or not?
                                if neighbor in created_hallways:
                                    created_hallways[neighbor][opposite] = hallway
                                else:
                                    created_hallways[neighbor] = {opposite: hallway}

                            # store the hallway so the neighbors can find it if necessary
                            if pos not in created_hallways:
                                created_hallways[pos] = {}
                            created_hallways[pos][direction] = hallway
                            room_hallways[direction] = hallway

                        room = None
                        if code == _Code.Spawn:
                            spawn_room = pos
                            room = SpawnRoom(self.__load_map,
                                             north_hallway=room_hallways[Direction.North],
                                             east_hallway=room_hallways[Direction.East],
                                             south_hallway=room_hallways[Direction.South],
                                             west_hallway=room_hallways[Direction.West],
                                             place_teleporter=False)
                        elif code == _Code.Wild:
                            enemy_factory = rm.get_element_prioritized(enemy_factories, enemy_factory_priorities,
                                                                       msg="RandomDG_elemPrioritized")

                            def tile_from_tile_data(tile_code: tiles.TileCode, tile_data: Any) -> tiles.Tile:
                                if tile_code == tiles.TileCode.Enemy:
                                    return self.__create_enemy(tile_data, pos, enemy_factory, enemy_groups_by_room,
                                                               self._next_tile_id)
                                elif tile_code == tiles.TileCode.CollectibleScore:
                                    return tiles.Collectible(Score(tile_data))
                                elif tile_code == tiles.TileCode.Collectible:
                                    if self.__remaining_keys > 0 and not self.__room_has_key \
                                            and rm.get(msg="key placement") > 0.6:
                                        self.__remaining_keys -= 1
                                        self.__room_has_key = True
                                        return tiles.Collectible(Key())
                                    return tiles.Collectible(get_collectible_factory(tile_data).produce(rm))
                                elif tile_code == tiles.TileCode.Wall:
                                    return tiles.Wall()
                                elif tile_code == tiles.TileCode.Obstacle:
                                    return tiles.Obstacle()
                                else:
                                    return tiles.Floor()

                            # todo: should this be optional based on difficulty/progress (#tunneling)?
                            # fourth check if we can reach every door from every door of this room (= doors are
                            # reachable for player, implies that the previous layout reachability-check still holds)
                            gen_tries = 0
                            while gen_tries < ExpeditionGenerator.__MAX_ROOM_GEN_TRIES:
                                tile_matrix: List[List["TileData"]] = self.__wild_room_generator.generate(
                                    seed=rm.get_seed("generating a room in ExpeditionGenerator")
                                )
                                tile_list = [tile_from_tile_data(entry.code, entry.data)
                                             for row in tile_matrix for entry in row]

                                if self.correct_tile_list(tile_list, room_hallways) >= 0:
                                    break
                                Logger.instance().warn(f"Failed to generate a room: try #{gen_tries}, seed={seed}")
                                gen_tries += 1
                            if gen_tries >= ExpeditionGenerator.__MAX_ROOM_GEN_TRIES:
                                # todo don't care about potentially impossible Expedition?
                                Logger.instance().error(
                                    "Failed to validate generated room! Expedition might be "
                                    "impossible to clear.", from_pycui=False)

                            room = DefinedWildRoom(
                                tile_list,
                                north_hallway=room_hallways[Direction.North],
                                east_hallway=room_hallways[Direction.East],
                                south_hallway=room_hallways[Direction.South],
                                west_hallway=room_hallways[Direction.West]
                            )
                            """
                            room = WildRoom(
                                enemy_factory,
                                chance=rm.get(ExpeditionGenerator.__MIN_ENEMY_FACTORY_CHANCE,
                                              ExpeditionGenerator.__MAX_ENEMY_FACTORY_CHANCE,
                                              msg="RandomDG_WRPuzzleDistribution"),
                                north_hallway=room_hallways[Direction.North],
                                east_hallway=room_hallways[Direction.East],
                                south_hallway=room_hallways[Direction.South],
                                west_hallway=room_hallways[Direction.West],
                            )"""
                        elif code == _Code.Phantom:
                            room = EmptyRoom(room_hallways)
                        elif direction is not None:
                            # special rooms have exactly 1 neighbor which is already stored in direction
                            hw = room_hallways[direction]
                            if code == _Code.Shop:
                                # since there was no shop introduction yet, we have to skip creating one.
                                room = EmptyRoom(room_hallways)  # ShopRoom(hw, direction, shop_items, self.__cbp.visit_shop)
                            elif code == _Code.Riddle:
                                room = RiddleRoom(hw, direction, riddle, self.__cbp.open_riddle)
                            elif code == _Code.Gate:
                                room = TreasureRoom(tiles.Collectible(gate), hw, direction)
                            elif code == _Code.Boss:
                                def end_level():
                                    self.__load_map(MapConfig.back_map_string(), None)
                                boss = tiles.Boss(dungeon_boss, self.__cbp.start_boss_fight, end_level)
                                room = BossRoom(hw, direction, boss)
                        if room:
                            rooms[y][x] = room
            if spawn_room:
                my_map = ExpeditionMap(seed, rooms, robot, spawn_room, self.__check_achievement,
                                       self.__trigger_event)
                return my_map, True
            else:
                return None, False
        else:
            return None, False

    @staticmethod
    def correct_tile_list(tile_list: List[tiles.Tile], hallways: Dict[Direction, Optional[Hallway]]) \
            -> int:
        """
        Corrects a given list of tiles (interpreted as Room.INNER_WIDTH * Room.INNER_HEIGHT tile matrix) such that
        robot is able to reach every Hallway from every other Hallway. This way it is guaranteed that a Room with the
        given tile_list and hallways does not block off access to one of its neighboring Rooms.
        Potentially modifies tile_list by removing Obstacles!

        :param tile_list: a Room's tile matrix in list form (interpreted as concatenation of its rows)
        :param hallways: a dictionary of Directions and the Hallways that connect to other Rooms in this Direction
        :return: how many changes were made on tile_list, with -1 indicating that the tile_list cannot be corrected
        """
        if len(hallways) <= 0:
            return 0

        def is_blocking(t: tiles.Tile) -> bool:
            return t.code in [tiles.TileCode.Obstacle, tiles.TileCode.Wall]

        # gather positions of all possibly blocking tiles
        blocking_tiles: Dict[Coordinate, tiles.Tile] = {}
        for i, tile in enumerate(tile_list):
            if is_blocking(tile):
                blocking_tiles[Room.index_to_coordinate(i)] = tile

        num_of_changes = 0
        # calculate weights for every position
        weight_matrix: Dict[Coordinate, int] = {}
        for x in range(Room.INNER_WIDTH):
            for y in range(Room.INNER_HEIGHT):
                coor = Coordinate(x, y)
                # initialize weight with the minimum distance to one of the hallway entrances
                weight = min([Coordinate.distance(coor, Room.direction_to_hallway_entrance_pos(direction))
                             for direction in hallways.keys()])
                if weight > 0 and is_blocking(tile_list[Room.coordinate_to_index(coor)]):
                    # if weight is 0 (i.e. coor is an entrance) it should stay 0 because it will be a search target
                    weight += ExpeditionGenerator.__BLOCKING_WEIGHT     # increase weight if something is blocking
                weight_matrix[coor] = weight

        def get_weight(position: Coordinate) -> int:
            if position in weight_matrix:
                return weight_matrix[position]
            return ExpeditionGenerator.__INVALID_WEIGHT

        direction: Optional[Direction] = None
        for other_dir in hallways.keys():
            if direction is None:
                direction = other_dir
            elif other_dir is not None:
                start_pos = Room.direction_to_hallway_entrance_pos(direction)
                target_pos = Room.direction_to_hallway_entrance_pos(other_dir)

                # which positions need to be cleared to reach exit from key
                forth = ExpeditionGenerator.path_search(tile_list, is_blocking, get_weight, set(), target_pos,
                                                        start_pos)
                # check the result from searching the other way around
                back = ExpeditionGenerator.path_search(tile_list, is_blocking, get_weight, set(), start_pos,
                                                       target_pos)
                if forth[0] and back[0]:
                    # if both succeeded we use the one that removes less (resulting in a less empty room)
                    if len(forth[1]) < len(back[1]):
                        tiles_to_remove = forth[1]
                    else:
                        tiles_to_remove = back[1]
                elif forth[0]:
                    tiles_to_remove = forth[1]
                elif back[0]:
                    tiles_to_remove = back[1]
                else:
                    # return error code if both directions failed to find a path
                    return -1

                for pos in tiles_to_remove:
                    tile_list[Room.coordinate_to_index(pos)] = tiles.Floor()
                num_of_changes += len(tiles_to_remove)
        return num_of_changes

    @staticmethod
    def path_search(tile_list: List[tiles.Tile], is_blocking: Callable[[tiles.Tile], bool],
                    get_weight: Callable[[Coordinate], int], visited: Set[Coordinate],
                    target_pos: Coordinate, cur_pos: Coordinate) -> Tuple[bool, List[Coordinate]]:
        """
        Searches for a path in tile_list (interpreted as Room.INNER_WIDTH * Room.INNER_HEIGHT tile matrix) from cur_pos
        to target_pos based on positional weights.

        :param tile_list: a Room's tile matrix in list form (interpreted as concatenation of its rows)
        :param is_blocking: tells us whether a given tile is blocking or free to move
        :param get_weight: provides a weight for every room position with lower values being more favourable to move to
        :param visited: set of already visited positions so we don't double check
        :param target_pos: end of the path we search
        :param cur_pos: current position in the path we search
        :return: True and a list of Coordinates of the Obstacles we have to remove to get a valid path, False and a
                 meaningless list if no such path exists (e.g. target is blocked by walls)
        """
        if cur_pos == target_pos:
            return True, []

        # max_ is inclusive
        neighbors = cur_pos.get_neighbors(Coordinate(0, 0), Coordinate(Room.INNER_WIDTH - 1, Room.INNER_HEIGHT - 1))
        neighbors.sort(key=lambda val: get_weight(val))  # continue with the better neighbors first
        for pos in neighbors:
            if pos in visited:
                continue
            visited.add(pos)
            success, tiles_to_remove = ExpeditionGenerator.path_search(tile_list, is_blocking, get_weight,
                                                                       visited, target_pos, pos)
            if success:
                tile = tile_list[pos.x + pos.y * Room.INNER_WIDTH]
                if is_blocking(tile):       # todo theoretically expandable to also take the direction as parameter
                    tiles_to_remove = [pos] + tiles_to_remove
                return True, tiles_to_remove

        return False, []
