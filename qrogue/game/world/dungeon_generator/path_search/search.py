from typing import Set, Tuple, Optional, Callable, List, Dict, Union

from qrogue.game.world.map import rooms
from qrogue.game.world.navigation import Coordinate
from qrogue.game.world.tiles import TileCode


class Search:
    class _PriorityQueue:
        @staticmethod
        def from_list(data: List[Coordinate], compute_weight: Callable[[Coordinate], float]):
            queue = Search._PriorityQueue()
            for val in data:
                queue.push(val, compute_weight(val))
            return queue

        def __init__(self):
            self.__queue: List[Tuple[Coordinate, float]] = []

        def pop(self) -> Coordinate:
            assert len(self) > 0, "Cannot pop from empty queue!"
            return self.__queue.pop(0)[0]

        def push(self, elem: Coordinate, weight: float):
            # search position to place it in
            # todo improve by using bin-search?
            for i in range(len(self)):
                if weight < self.__queue[i][1]:
                    self.__queue.insert(i, (elem, weight))
                    return
            # append to end if no fitting position was found
            self.__queue.append((elem, weight))

        def __len__(self):
            return len(self.__queue)

        def __iter__(self):
            return iter(self.__queue)

    @staticmethod
    def get_weighted_obstacles_matrix(pos: Coordinate, get_tile_code: Callable[[Coordinate], TileCode]) \
            -> List[List[float]]:
        min_, max_ = Coordinate(0, 0), Coordinate(rooms.Room.INNER_WIDTH - 1, rooms.Room.INNER_HEIGHT - 1)
        # to encourage paths without obstacles we increase the weight by more than the maximum distance between two
        # points in an empty room
        obstacle_weight = rooms.Room.INNER_HEIGHT + rooms.Room.INNER_WIDTH
        weight_matrix: List[List[int]] = [[None] * rooms.Room.INNER_WIDTH for _ in range(rooms.Room.INNER_HEIGHT)]

        def update_weight(coordinate: Coordinate):
            neighbors = coordinate.get_neighbors(min_, max_)
            # find minimum weight among all neighbors
            base_weight = None
            for n in neighbors:
                n_weight = weight_matrix[n.y][n.x]
                if n_weight is None: continue   # weight not yet calculated
                if base_weight is None or n_weight < base_weight:
                    base_weight = n_weight

            # the weight of the tile at coordinate depends on whether it's free to walk or not (at least 1 since
            # distance increases)
            own_weight = obstacle_weight if get_tile_code(coordinate) in [TileCode.Obstacle, TileCode.Wall] else 1

            # the weight at coordinate depends on its neighbors and its own weight
            weight_matrix[coordinate.y][coordinate.x] = base_weight + own_weight

            for n in neighbors:
                n_weight = weight_matrix[n.y][n.x]
                if n_weight is None:
                    update_weight(n)

        weight_matrix[pos.y][pos.x] = 0     # start position has weight 0 because it has distance 0 to itself
        for neighbor in pos.get_neighbors(min_, max_):
            update_weight(neighbor)

        return weight_matrix

    @staticmethod
    def simple_room_visit(pos: Coordinate, get_weight: Callable[[Coordinate], float],
                          is_goal: Union[Callable[[Coordinate], bool], Coordinate]):
        if isinstance(is_goal, Coordinate):
            goal_coordinate = is_goal

            def is_goal(c: Coordinate):
                return c == goal_coordinate

        visited: Set[Coordinate] = set()
        min_, max_ = Coordinate(0, 0), Coordinate(rooms.Room.INNER_WIDTH - 1, rooms.Room.INNER_HEIGHT - 1)

        def can_visit(from_: Coordinate, to: Coordinate) -> bool:
            if not to.is_between(min_, max_):
                return False  # to is not a valid position
            return to not in visited  # we haven't visited "to" yet

        def on_visit(coordinate: Coordinate):
            visited.add(coordinate)

        return Search.__find(pos, can_visit, is_goal, get_weight, on_visit, min_, max_)

    @staticmethod
    def __find(pos: Coordinate, can_visit: Callable[[Coordinate, Coordinate], bool],
               is_goal: Callable[[Coordinate], bool], get_weight: Callable[[Coordinate], float],
               on_visit: Callable[[Coordinate], None], min_: Optional[Coordinate] = None,
               max_: Optional[Coordinate] = None) -> Optional[List[Coordinate]]:
        """

        Args:
            pos: current position to work with
            can_visit: callback to tell us if we can visit Coordinate2 coming from Coordinate1
            is_goal: callback to tell us whether we reached the goal or not
            get_weight: heuristic to tell us how far we are from a goal (the lower, the closer)
            on_visit: action to perform on every Coordinate we visit

        Returns: list of all Coordinates forming a path from pos to the nearest goal

        """

        queue = Search._PriorityQueue()
        path_dic: Dict[Coordinate, Coordinate] = {}     # key: position, val: previous position

        queue.push(pos, get_weight(pos))
        while len(queue) > 0:
            cur_pos = queue.pop()
            if is_goal(cur_pos):
                # reconstruct path
                path = []
                while cur_pos != pos:
                    path.append(cur_pos)
                    cur_pos = path_dic[cur_pos]     # follow path back to where we came from
                path.append(pos)    # lastly append where we initially started from
                path.reverse()
                return path
            else:
                on_visit(cur_pos)

            cur_weight = get_weight(cur_pos)
            # check out every neighbor that can be visited
            for neighbor in filter(lambda n: can_visit(cur_pos, n), cur_pos.get_neighbors(min_, max_)):
                # store path to neighbor
                if neighbor in path_dic:
                    # check if cur_weight is lower than the weight of the previous path to neighbor
                    if cur_weight < get_weight(path_dic[neighbor]):
                        path_dic[neighbor] = cur_pos
                else:
                    path_dic[neighbor] = cur_pos

                queue.push(neighbor, get_weight(neighbor))

        return None     # no path found

    def __init__(self, can_visit: Callable[[Coordinate, Coordinate], bool], is_goal: Callable[[Coordinate], bool],
                 compute_weight: Callable[[Coordinate], float], on_visit: Callable[[Coordinate], None],
                 min_: Optional[Coordinate] = None, max_: Optional[Coordinate] = None):
        self.__can_visit = can_visit
        self.__is_goal = is_goal
        self.__compute_weight = compute_weight
        self.__on_visit = on_visit
        self.__min = min_
        self.__max = max_

    def find_path(self, pos: Coordinate) -> Optional[List[Coordinate]]:
        return Search.__find(pos, self.__can_visit, self.__is_goal, self.__compute_weight, self.__on_visit, self.__min,
                             self.__max)
