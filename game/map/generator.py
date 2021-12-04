from enum import IntEnum

from game.actors.factory import EnemyFactory, DummyFightDifficulty
from game.callbacks import CallbackPack
from game.map.map import Map
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Hallway, WildRoom, SpawnRoom, ShopRoom
from game.map.tiles import Door, Player
from util.logger import Logger
from util.my_random import MyRandom


class _Code(IntEnum):
    # meta codes
    PriorityMul = -1
    Free = PriorityMul  # best priority for free, unbiased cells
    Blocked = 0 # all before Blocked is free, all after Blocked is already taken
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


class LayoutGenerator:
    __MIN_AREA = 10
    __MAX_WALKS = 100
    __PCM = 0.5     # priority corner multiplier
    __PRIORITY_FILTER = [
        Direction.North + Direction.West, Direction.North, Direction.North + Direction.East,
        Direction.West, Direction.East,
        Direction.South + Direction.West, Direction.South, Direction.South + Direction.East,
    ]
    __PRIORITY_WEIGHTS = [__PCM, 1, __PCM, 1, 1, __PCM, 1, __PCM]
    __MIN_NORMAL_ROOMS = 4

    def __init__(self, seed: int, width: int, height: int):
        self.__seed = seed      # todo remove
        if width * height < LayoutGenerator.__MIN_AREA:
            Logger.instance().throw(ValueError(f"width={width}, height={height} create a too small grid "
                             f"(minimal grid area = {LayoutGenerator.__MIN_AREA}). Please use bigger values!"))
        self.__rm = MyRandom(seed)
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
            direction = self.__rm.get_element(directions, remove=True)
            if direction == Direction.North or direction == Direction.South:
                y = (self.__height - 1) * (
                            direction == Direction.South)  # for North this is 0, for South self.__height-1
                xs = list(range(0, self.__width))
                while len(xs) > 0:
                    x = self.__rm.get_element(xs, remove=True)
                    pos = Coordinate(x=x, y=y)
                    if self.__get(pos) < _Code.Blocked:
                        return pos
            else:
                x = (self.__width - 1) * (direction == Direction.East)  # for North this is 0, for South self.__height-1
                ys = list(range(0, self.__height))
                while len(ys) > 0:
                    y = self.__rm.get_element(ys, remove=True)
                    pos = Coordinate(x=x, y=y)
                    if self.__get(pos) < _Code.Blocked:
                        return pos
        return None

    def __random_coordinate(self) -> Coordinate:
        val = self.__rm.get()
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
        print(self)
        #raise NotImplementedError("This line should no be reachable")
        print(f"Failed to get a random coordinate (line 193) for seed = {self.seed}")

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
            #raise NotImplementedError("This line should not be reachable!")
            print(f"Illegal prio_sum for seed = {self.seed}")
            prio_sum = -1.0

        picked_rooms = []
        for i in range(num):
            val = self.__rm.get()
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
            self.__hallways[room1][room2] = Hallway(door)
        else:
            self.__hallways[room1] = {room2: Hallway(door)}
        if room2 in self.__hallways:
            self.__hallways[room2][room1] = Hallway(door)
        else:
            self.__hallways[room2] = {room1: Hallway(door)}

    def __place_wild(self, room: Coordinate, door: Door):
        pos = room + door.direction
        self.__set(pos, _Code.Wild)
        self.__add_hallway(room, pos, door)

    def __place_special_room(self, code: _Code) -> Coordinate:
        while True:
            try:
                pos = self.__random_border()
                self.__set(pos, code)
                direction = self.__rm.get_element(self.__available_directions(pos, allow_wildrooms=True))
                if direction is None:
                    self.__set(pos, _Code.Blocked)  # position is not suited for a special room
                else:
                    wild_room = pos + direction
                    if self.__is_corner(wild_room):
                        # if the connected WildRoom is in the corner, we swap position between it and the SpecialRoom
                        self.__set(wild_room, code)
                        self.__place_wild(wild_room, Door(direction.opposite()))
                        return wild_room
                    else:
                        self.__place_wild(pos, Door(direction))
                        return pos
            except NotImplementedError:
                print("ERROR!")

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
            room = self.__rm.get_element(relevant_neighbors)
            door = Door(room[0])
            self.__add_hallway(pos, room[2], door)
            return room[2], False
        else:
            if self.__get(pos) in _Code.special_rooms():
                #raise NotImplementedError("This line should not be reachable!")
                print(f"SpecialRoom marked as dead end for seed = {self.seed}")
            return pos, True  # we found a dead end

    def __astar(self, visited: set, pos: Coordinate, target: Coordinate) -> [Coordinate]:
        """

        :param visited: Coordinates of all cells we already visited
        :param pos: position/Coordinate of the cell we currently check
        :param target: the cell we try to find
        :return: list of dead ends on the path or None if the target can be reached
        """
        dead_ends = []
        neighbors = list(self.__hallways[pos].keys())

        if target in neighbors:
            return None     # we found the target

        while neighbors:
            room = self.__rm.get_element(neighbors, remove=True)
            if room in visited:
                continue
            visited.add(room)
            ret = self.__astar(visited, pos=room, target=target)
            if ret:
                dead_ends += ret
            else:
                return None

        ret = []
        cur_pos = pos
        while True:
            # we come back from a dead end, so we check if we can connect the current cell with a non-visited neighbor
            coordinate, dead_end = self.__astar_connect_neighbors(visited, cur_pos)
            if dead_end:
                if len(self.__get_neighbors(coordinate, free_spots=True)) > 0:
                    dead_ends.append(coordinate)
                return dead_ends + ret
            else:
                visited.add(coordinate)
                ret = self.__astar(visited, pos=coordinate, target=target)
                if ret:
                    dead_ends += ret
                else:
                    return None

    def __call_astar(self, visited: set, start_pos: Coordinate, spawn_pos: Coordinate) -> bool:
        dead_ends = self.__astar(visited, start_pos, target=spawn_pos)
        if dead_ends is None:
            return True
        while dead_ends:
            dead_end = self.__rm.get_element(dead_ends, remove=True)
            relevant_pos = self.__get_neighbors(dead_end, free_spots=True)
            # and try to place a new room to connect the dead end to the rest
            while relevant_pos:
                direction, _, new_pos = self.__rm.get_element(relevant_pos, remove=True)
                self.__place_wild(dead_end, Door(direction))
                visited.add(new_pos)
                if self.__call_astar(visited, start_pos=new_pos, spawn_pos=spawn_pos):
                    return True
        return False

    def get_hallway(self, pos: Coordinate) -> "dict of Coordinate and Door":
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
        #        door = Door(direction, locked=True)
        #        self.__add_hallway(spawn_pos, new_pos, door)

        self.__new_prio()
        if len(self.__normal_rooms) < LayoutGenerator.__MIN_NORMAL_ROOMS:
            self.__prio_sum -= (len(self.__normal_rooms) + len(special_rooms))     # subtract now blocked Rooms
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
                direction, _, new_pos = self.__rm.get_element(neighbors)
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
            if debug:
                print(self)
        if success:
            return True
        else:
            for room in rooms:
                start_pos = list(self.__hallways[room].keys())[0]
                visited = set(special_rooms)
                ret = self.__astar(visited, start_pos, spawn_pos)
                if ret:
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


class DungeonGenerator:
    WIDTH = 7
    HEIGHT = 3

    def __init__(self, seed: int):
        self.__width = DungeonGenerator.WIDTH
        self.__height = DungeonGenerator.HEIGHT
        self.__layout = LayoutGenerator(seed, self.__width, self.__height)

    def generate(self, player: Player, cbp: CallbackPack) -> Map:
        rooms = [[None for x in range(self.__width)] for y in range(self.__height)]
        created_hallways = {}
        if self.__layout.generate():
            for y in range(DungeonGenerator.HEIGHT):
                for x in range(DungeonGenerator.WIDTH):
                    pos = Coordinate(x, y)
                    code = self.__layout.get_room(pos)
                    if code and code > _Code.Blocked:
                        room_hallways = {
                            Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None,
                        }
                        hallways = self.__layout.get_hallway(pos)
                        for neighbor in hallways:
                            hallway = Hallway(hallways[neighbor])   # todo create door here and only check if it should be locked or not?
                            direction = Direction.from_coordinates(pos, neighbor)
                            room_hallways[direction] = hallway
                            if neighbor not in created_hallways:
                                created_hallways[neighbor] = {}
                            created_hallways[neighbor][direction.opposite()] = hallway

                        if code == _Code.Spawn:
                            room = SpawnRoom(player,
                                             north_hallway=room_hallways[Direction.North],
                                             east_hallway=room_hallways[Direction.East],
                                             south_hallway=room_hallways[Direction.South],
                                             west_hallway=room_hallways[Direction.West],
                                             )
                        elif code == _Code.Wild:
                            room = WildRoom(EnemyFactory(cbp.start_fight, DummyFightDifficulty()),  # todo real factory and difficulty
                                             north_hallway=room_hallways[Direction.North],
                                             east_hallway=room_hallways[Direction.East],
                                             south_hallway=room_hallways[Direction.South],
                                             west_hallway=room_hallways[Direction.West],
                                             )
                        else:
                            hallway = hallways[direction]
                            #if code == _Code.Shop:
                            #    room = ShopRoom(hallway, )

                        #rooms[y][x] = room
