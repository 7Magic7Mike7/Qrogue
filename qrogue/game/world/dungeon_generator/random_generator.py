from enum import IntEnum
from typing import Callable, Dict

from qrogue.game.logic.actors import Robot
from qrogue.game.logic.collectibles import GateFactory, ShopFactory, EnergyRefill, Coin, Key, instruction
from qrogue.game.world.map import CallbackPack, LevelMap, Hallway, WildRoom, SpawnRoom, ShopRoom, RiddleRoom, BossRoom, \
    TreasureRoom, ExpeditionMap
from qrogue.game.target_factory import TargetDifficulty, BossFactory, EnemyFactory, RiddleFactory
from qrogue.game.world.navigation import Coordinate, Direction
from qrogue.game.world.tiles import Boss, Collectible, Door, DoorOpenState
from qrogue.util import Logger, RandomManager


from .generator import DungeonGenerator


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
        self.__map = [[_Code.Free] * self.__width for y in range(self.__height)]
        self.__normal_rooms = set()
        self.__hallways = {}
        self.__prio_sum = self.__width * self.__height
        self.__prio_mean = 1.0

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

    def __get_neighbors(self, pos: Coordinate, free_spots: bool = False) -> [(Direction, _Code, Coordinate)]:
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

    def __random_border(self) -> Coordinate:
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

    def __random_free_wildroom_neighbors(self, num: int = 1) -> [Coordinate]:
        rooms = self.__normal_rooms
        room_prios = {}
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
                neighbor_distance = max_distance
                for other in rooms:
                    if room is not other:   # check distance to other WRs and SR (except the WR we know is a neighbor)
                        neighbor_distance = min(neighbor_distance, Coordinate.distance(neighbor[2], other))
                # high isolation of room and low isolation of neighbor means high priority
                prio = min_distance * (max_distance - neighbor_distance)
                prio_sum += prio
                room_prios[neighbor] = (prio, room)

        if prio_sum == 0:
            Logger.instance().error(f"Illegal prio_sum for seed = {self.seed} in generator.py\nThis should not be "
                                    "possible to occur but aside from the randomness during layout generation this "
                                    "doesn't break anything. Please consider reporting!")
            prio_sum = -1.0

        picked_rooms = []
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

    def __add_hallway(self, room1: Coordinate, room2: Coordinate, door: Door):
        if room1 in self.__hallways:
            self.__hallways[room1][room2] = door
        else:
            self.__hallways[room1] = {room2: door}
        if room2 in self.__hallways:
            self.__hallways[room2][room1] = door
        else:
            self.__hallways[room2] = {room1: door}

    def __place_wild(self, room: Coordinate, door: Door):
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
                        self.__place_wild(wild_room, Door(direction.opposite(), DoorOpenState.KeyLocked))
                        return wild_room
                    else:
                        self.__place_wild(pos, Door(direction, DoorOpenState.KeyLocked))
                        return pos
            except NotImplementedError:
                Logger.instance().error("Unimplemented case happened!")

    def __astar_connect_neighbors(self, visited: set, pos: Coordinate) -> (Coordinate, bool):
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
            door = Door(room[0])
            self.__add_hallway(pos, room[2], door)
            return room[2], False
        else:
            if self.__get(pos) in _Code.special_rooms():
                Logger.instance().debug(f"SpecialRoom marked as dead end for seed = {self.seed}", from_pycui=False)
            return pos, True  # we found a dead end

    def __astar(self, visited: set, pos: Coordinate, target: Coordinate) -> ([Coordinate], bool):
        """

        :param visited: Coordinates of all cells we already visited
        :param pos: position/Coordinate of the cell we currently check
        :param target: the cell we try to find
        :return: list of dead ends on the path and False if the target cannot be reached, otherwise True
        """
        dead_ends = set()
        neighbors = list(self.__hallways[pos].keys())

        if target in neighbors:
            return None, True  # we found the target

        while neighbors:
            room = self.__rm.get_element(neighbors, remove=True, msg="RandomGen_astarRoom")
            if room in visited:
                continue
            visited.add(room)
            ret, success = self.__astar(visited, pos=room, target=target)
            if ret:
                dead_ends.update(ret)
            if success:
                return dead_ends, True

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
                if ret:
                    dead_ends.update(ret)
                if success:
                    return dead_ends, True

    def __call_astar(self, visited: set, start_pos: Coordinate, spawn_pos: Coordinate) -> bool:
        dead_ends, success = self.__astar(visited, start_pos, target=spawn_pos)
        if success:
            return True
        dead_ends = list(dead_ends)
        while dead_ends:
            dead_end = self.__rm.get_element(dead_ends, remove=True, msg="RandomGen_astarDeadEnd")
            relevant_pos = self.__get_neighbors(dead_end, free_spots=True)
            # and try to place a new room to connect the dead end to the rest
            while relevant_pos:
                direction, _, new_pos = self.__rm.get_element(relevant_pos, remove=True, msg="RandomGen_astarRelevantPos")
                self.__place_wild(dead_end, Door(direction))
                visited.add(new_pos)
                if self.__call_astar(visited, start_pos=new_pos, spawn_pos=spawn_pos):
                    return True
        return False

    def get_hallway(self, pos: Coordinate) -> Dict[Coordinate, Door]:
        if pos in self.__hallways:
            return self.__hallways[pos]
        return None

    def get_room(self, pos: Coordinate) -> _Code:
        if self.__is_valid_pos(pos):
            return self.__get(pos)
        return None

    def check_special_rooms(self) -> bool:
        for y in range(self.__height):
            for x in range(self.__width):
                pos = Coordinate(x, y)
                code = self.__get(pos)
                if code in [_Code.Boss, _Code.Shop, _Code.Riddle, _Code.Gate]:
                    connections = self.__hallways[pos]
                    if len(connections) != 1:
                        return False
        return True

    def generate(self, debug: bool = False) -> bool:
        # place the spawn room
        spawn_pos = self.__random_coordinate()
        self.__set(spawn_pos, _Code.Spawn)

        # special case if SpawnRoom is in a corner
        corner = self.__is_corner(spawn_pos)
        if corner:
            if self.__get(spawn_pos + corner[0]) < _Code.Blocked:
                self.__place_wild(spawn_pos, Door(corner[0]))
            if self.__get(spawn_pos + corner[1]) < _Code.Blocked:
                self.__place_wild(spawn_pos, Door(corner[1]))

        # place the special rooms
        special_rooms = [
            self.__place_special_room(_Code.Shop),
            self.__place_special_room(_Code.Riddle),
            self.__place_special_room(_Code.Boss),
            self.__place_special_room(_Code.Gate),
        ]

        # create a locked hallway to spawn_pos-neighboring WildRooms if they lead to SpecialRooms
        #directions = self.__available_directions(spawn_pos, allow_wildrooms=True)
        #for direction in directions:
        #    new_pos = spawn_pos + direction
        #    if self.__get(new_pos) == _Code.Wild:
        #        #wild_directions = self.__available_directions(spawn_pos, allow_wildrooms=True)
        #        door = tiles.Door(direction, locked=True)
        #        self.__add_hallway(spawn_pos, new_pos, door)

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
                self.__add_hallway(pos, new_pos, Door(direction))

        # add a connection if the SpawnRoom is not connected to a WildRoom
        if spawn_pos not in self.__hallways:
            neighbors = self.__get_neighbors(spawn_pos)
            if len(neighbors) > 0:
                direction, _, new_pos = self.__rm.get_element(neighbors, msg="RandomGen_neighbor")
                self.__add_hallway(spawn_pos, new_pos, Door(direction))

        success = True
        # as last step, add missing Hallways and WildRooms to connect every SpecialRoom with the SpawnRoom
        rooms = list(special_rooms)
        while rooms:
            room = rooms.pop(0)
            visited = set(special_rooms)
            start_pos = list(self.__hallways[room].keys())[0]
            visited.add(start_pos)
            if not self.__call_astar(visited, start_pos, spawn_pos):
                success = False
                break
        if success:
            return True
        else:
            for room in rooms:
                start_pos = list(self.__hallways[room].keys())[0]
                visited = set(special_rooms)
                dead_ends, success = self.__astar(visited, start_pos, spawn_pos)
                if not success:
                    return False
            return True

    def __str__(self):
        cell_width = 5
        __empty = "     "
        __row_sep = "_" * (cell_width + 1) * self.__width
        str_rep = " " + __row_sep + "\n"
        for y in range(self.__height):
            rows = ["|"] * 3
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
    __MIN_ENEMY_FACTORY_CHANCE = 0.45
    __MAX_ENEMY_FACTORY_CHANCE = 0.7

    def __init__(self, seed: int, check_achievement: Callable[[str], bool], trigger_event: Callable[[str], None],
                 load_map_callback: Callable[[str], None], width: int = DungeonGenerator.WIDTH,
                 height: int = DungeonGenerator.HEIGHT):
        super(ExpeditionGenerator, self).__init__(seed, width, height)
        self.__check_achievement = check_achievement
        self.__trigger_event = trigger_event
        self.__load_map = load_map_callback
        self.__layout = RandomLayoutGenerator(seed, width, height)

    def generate(self, data: Robot) -> (LevelMap, bool):
        # Testing: seeds from 0 to 500_000 were successful
        robot = data
        if len(robot.get_available_instructions()) <= 0:

            gates = [instruction.HGate(), instruction.XGate(), instruction.CXGate()]
            for gate in gates:
                robot.give_collectible(gate)

        rm = RandomManager.create_new()     # needed for WildRooms
        gate_factory = GateFactory.default()
        shop_factory = ShopFactory.default()
        riddle_factory = RiddleFactory.default(robot)
        boss_factory = BossFactory.default(robot)

        gate = gate_factory.produce(rm)
        riddle = riddle_factory.produce(rm)
        shop_items = shop_factory.produce(rm, num_of_items=3)
        dungeon_boss = boss_factory.produce([gate])  # todo based on chance also add gates from riddle or shop_items?

        enemy_factories = [
            EnemyFactory(CallbackPack.instance().start_fight, TargetDifficulty(
                2, [Coin(2), EnergyRefill()]
            )),
            EnemyFactory(CallbackPack.instance().start_fight, TargetDifficulty(
                2, [Coin(1), Coin(2), Coin(2), Coin(3), Key(), EnergyRefill(15)]
            )),
            EnemyFactory(CallbackPack.instance().start_fight, TargetDifficulty(
                3, [Coin(1), Coin(5), Key(), EnergyRefill(20)]
            )),
            EnemyFactory(CallbackPack.instance().start_fight, TargetDifficulty(
                3, [Coin(1), Coin(1), EnergyRefill(3)]
            )),
        ]
        enemy_factory_priorities = [0.25, 0.35, 0.3, 0.1]

        rooms = [[None for _ in range(self.width)] for _ in range(self.height)]
        spawn_room = None
        created_hallways = {}
        if self.__layout.generate():
            for y in range(self.height):
                for x in range(self.width):
                    pos = Coordinate(x, y)
                    code = self.__layout.get_room(pos)
                    if code and code > _Code.Blocked:
                        room_hallways = {
                            Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None,
                        }
                        hallways = self.__layout.get_hallway(pos)
                        if hallways is None:
                            if code == _Code.Wild:
                                # it is completely fine if it happens that an isolated WildRoom was generated
                                continue
                            else:
                                Logger.instance().throw(NotImplementedError(
                                    f"Found a SpecialRoom ({code}) without connecting Hallways for seed = "
                                    f"{self.seed}. Please do report this error as this should not be "
                                    "possible to occur! :("))
                        for neighbor in hallways:
                            direction = Direction.from_coordinates(pos, neighbor)
                            opposite = direction.opposite()
                            # get hallway from neighbor if it exists, otherwise create it
                            if neighbor in created_hallways and opposite in created_hallways[neighbor]:
                                hallway = created_hallways[neighbor][opposite]
                            else:
                                hallway = Hallway(hallways[neighbor])   # todo create door here and only check if it should be locked or not?
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
                                )
                        elif code == _Code.Wild:
                            enemy_factory = rm.get_element_prioritized(enemy_factories, enemy_factory_priorities,
                                                                       msg="RandomDG_elemPrioritized")
                            room = WildRoom(
                                enemy_factory,
                                chance=rm.get(ExpeditionGenerator.__MIN_ENEMY_FACTORY_CHANCE,
                                              ExpeditionGenerator.__MAX_ENEMY_FACTORY_CHANCE,
                                              msg="RandomDG_WRPuzzleDistribution"),
                                north_hallway=room_hallways[Direction.North],
                                east_hallway=room_hallways[Direction.East],
                                south_hallway=room_hallways[Direction.South],
                                west_hallway=room_hallways[Direction.West],
                            )
                        else:
                            # special rooms have exactly 1 neighbor which is already stroed in direction
                            hw = room_hallways[direction]
                            if code == _Code.Shop:
                                room = ShopRoom(hw, direction, shop_items, CallbackPack.instance().visit_shop)
                            elif code == _Code.Riddle:
                                room = RiddleRoom(hw, direction, riddle, CallbackPack.instance().open_riddle)
                            elif code == _Code.Gate:
                                room = TreasureRoom(Collectible(gate), hw, direction)
                            elif code == _Code.Boss:
                                room = BossRoom(hw, direction, Boss(dungeon_boss,
                                                                          CallbackPack.instance().start_boss_fight))
                        if room:
                            rooms[y][x] = room
            if spawn_room:
                my_map = ExpeditionMap(self.seed, rooms, robot, spawn_room, self.__check_achievement,
                                       self.__trigger_event)
                return my_map, True
            else:
                return None, False
        else:
            return None, False

    def __load_next(self):
        #MapManager.instance().load_next()
        pass

    def __str__(self) -> str:
        return str(self.__layout)
