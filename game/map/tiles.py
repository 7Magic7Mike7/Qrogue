
from abc import ABC, abstractmethod
from enum import Enum

from game.actors.boss import Boss as BossActor
from game.actors.factory import EnemyFactory
from game.actors.robot import Robot
from game.actors.riddle import Riddle
from game.callbacks import OnWalkCallback
from game.collectibles.collectible import Collectible as LogicalCollectible
from game.map.navigation import Direction
from util.config import CheatConfig
from util.logger import Logger
from util.my_random import RandomManager
from widgets.my_popups import Popup, CommonPopups


class TileCode(Enum):
    Invalid = -1    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Debug = -2      # displays a digit for debugging
    Void = 7        # tile outside of the playable area
    Floor = 0       # simple floor tile without special meaning
    FogOfWar = 3    # tile of a place we cannot see yet

    Message = 6     # tile for displaying a popup message
    Trigger = 9     # tile that calls a function on walk, i.e. event tile

    Wall = 1
    Obstacle = 2
    Door = 4

    Robot = 20
    Enemy = 30
    Boss = 40

    Collectible = 50
    Riddler = 51
    ShopKeeper = 52

    SpaceshipBlock = 70
    SpaceshipWalk = 71
    SpaceshipTrigger = 72
    OuterSpace = 73


class Tile(ABC):
    def __init__(self, code: TileCode):
        self.__code = code

    @property
    def code(self) -> TileCode:
        return self.__code

    @property
    def _invisible(self) -> str:
        return " "

    @abstractmethod
    def get_img(self):
        pass

    @abstractmethod
    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        pass

    def __str__(self):
        return self.get_img()


class WalkTriggerTile(Tile):
    def __init__(self, code: TileCode):
        super().__init__(code)

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True
    
    @abstractmethod
    def on_walk(self, direction: Direction, robot: Robot) -> None:
        """
        Event that is triggered when an actor moves onto this Tile
        :param direction: the Direction from which the actor moves onto this Tile
        :param robot: the actor (e.g. Player) that is moving onto this Tile
        :return: None
        """
        pass


class Invalid(Tile):
    def __init__(self):
        super().__init__(TileCode.Invalid)

    def get_img(self):
        return "§"

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False


class Debug(Tile):
    def __init__(self, num: int):
        super(Debug, self).__init__(TileCode.Debug)
        self.__num = str(num)[0]

    def get_img(self) -> str:
        return self.__num

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False


class Floor(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True


class Wall(Tile):
    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return "#"

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "o"

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return False


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "~"

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True


class Trigger(WalkTriggerTile):
    def __init__(self, callback: "(Direction, Robot)"):
        super().__init__(TileCode.Trigger)
        self.__callback = callback

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        self.__callback(direction, robot)

    def get_img(self):
        return self._invisible


class Message(WalkTriggerTile):
    def __init__(self, popup: Popup, popup_times: int = 1):
        super().__init__(TileCode.Message)
        self.__popup = popup
        if popup_times < 0:
            popup_times = 99999     # display "everytime" the robot steps on it
        self.__times = popup_times

    def get_img(self):
        if self.__times > 0:
            return "."
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__times > 0:
            self.__popup.show()
        self.__times -= 1


class Riddler(WalkTriggerTile):
    def __init__(self, open_riddle_callback: "void(Player, Riddle)", riddle: Riddle):
        super().__init__(TileCode.Riddler)
        self.__open_riddle = open_riddle_callback
        self.__riddle = riddle

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__riddle.is_active:
            self.__open_riddle(robot, self.__riddle)

    def get_img(self):
        if self.__riddle.is_active:
            return "?"
        else:
            return self._invisible


class ShopKeeper(WalkTriggerTile):
    def __init__(self, visit_shop_callback, inventory: "list of ShopItems"):
        super().__init__(TileCode.ShopKeeper)
        self.__visit_shop = visit_shop_callback
        self.__inventory = inventory

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        self.__visit_shop(robot, self.__inventory)

    def get_img(self):
        return "$"


class Door(WalkTriggerTile):
    def __init__(self, direction: Direction, locked: bool = False, opened: bool = False):   # todo entangled door as extra class?
        super().__init__(TileCode.Door)
        self.__direction = direction
        self.__locked = locked
        self.__opened = opened

    def get_img(self):
        if self.__opened:
            return self._invisible
        if self.__direction is Direction.East or self.__direction is Direction.West:
            return "|"
        else:
            return "-"

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        if direction == self.__direction or direction == self.__direction.opposite():
            if self.__locked:
                if robot.key_count > 0:
                    return True
                else:
                    CommonPopups.LockedDoor.show()
                    return False
            else:
                return True
        else:
            return False

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__locked:
            if robot.use_key():
                self.__locked = False
                self.__opened = True
            else:
                Logger.instance().error(f"Error! walked on a door without having enough keys!\n#keys={robot.key_count}"
                                        f", dir={direction}")
        else:
            self.__opened = True

    @property
    def direction(self) -> Direction:
        return self.__direction

    @property
    def opened(self) -> bool:
        return self.__opened

    @property
    def locked(self) -> bool:
        return self.__locked


class EntangledDoor(Door):
    @staticmethod
    def entangle(door1: "EntangledDoor", door2: "EntangledDoor"):
        door1.__entangled_door = door2
        door2.__entangled_door = door1

    def __init__(self, direction: Direction):
        super().__init__(direction)
        self.__entangled_door = None
        self.__closed = False

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        # if the entangled door is open, this one can no longer we opened/walked on
        if self.__entangled_door.opened:
            CommonPopups.EntangledDoor.show()
            return False
        return super(EntangledDoor, self).is_walkable(direction, robot)


class Collectible(WalkTriggerTile):
    def __init__(self, collectible: LogicalCollectible):
        super().__init__(TileCode.Collectible)
        self.__collectible = collectible
        self.__active = True

    def get_img(self):
        if self.__active:
            return "c"
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__active:
            #robot = robot
            name = self.__collectible.name()
            desc = self.__collectible.description()
            Popup.message(self.__collectible.name(), f"You picked up a {name}.\n{desc}")
            robot.give_collectible(self.__collectible)
            self.__active = False


class RobotTile(Tile):
    def __init__(self, robot: Robot):
        super().__init__(TileCode.Robot)
        self.__robot = robot

    def get_img(self):
        return self.__robot.get_img()

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True # todo check

    @property
    def robot(self) -> Robot:
        return self.__robot


class _EnemyState(Enum):
    UNDECIDED = 0
    FREE = 1
    FIGHT = 2
    DEAD = 3
    FLED = 4
class Enemy(WalkTriggerTile):
    def __init__(self, factory: EnemyFactory, get_entangled_tiles, id: int = 0, amplitude: float = 0.5):
        super().__init__(TileCode.Enemy)
        self.__factory = factory
        self.__state = _EnemyState.UNDECIDED
        self.__get_entangled_tiles = get_entangled_tiles
        self.__id = id
        self.__amplitude = amplitude
        self.__rm = RandomManager.create_new()

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        if isinstance(robot, Robot):
            if self.__state == _EnemyState.UNDECIDED:
                if self.measure():
                    enemy = self.__factory.produce(robot, self.__rm, self.__amplitude)
                    self.__factory.start(robot, enemy, direction)
                    self.__state = _EnemyState.DEAD
                else:
                    self.__state = _EnemyState.FLED
            elif self.__state == _EnemyState.FIGHT:
                if CheatConfig.is_scared_rabbit():
                    self.__state = _EnemyState.FLED
                else:
                    enemy = self.__factory.produce(robot, self.__rm, self.__amplitude)
                    self.__factory.start(robot, enemy, direction)
                    self.__state = _EnemyState.DEAD # todo check if this makes sense? couldn't it also be "robot fled"?
            elif self.__state == _EnemyState.FREE:
                self.__state = _EnemyState.FLED

    def get_img(self):
        if self.__state == _EnemyState.DEAD :
            return self._invisible
        elif self.__state == _EnemyState.FLED:
            return self._invisible
        else:
            return str(self.__id)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def amplitude(self) -> float:
        return self.__amplitude

    def set_entangled_tile_callback(self, callback: "(int, )") -> bool: # todo delete
        if self.__get_entangled_tiles is None:
            self.__get_entangled_tiles = callback
            return True
        return False

    def _set_state(self, val: _EnemyState) -> None:
        if self.__state == _EnemyState.UNDECIDED:
            self.__state = val
        else:
            if CheatConfig.did_cheat():     # this is a legal state if we used the "Scared Rabbit" cheat
                return
            Logger.instance().throw(RuntimeError("Illegal program state!"))

    def measure(self):
        if CheatConfig.is_scared_rabbit():
            return False

        if 0 < self.__id <= 9:
            entangled_tiles = self.__get_entangled_tiles(self.__id)
        else:
            entangled_tiles = [self]

        state = _EnemyState.FREE
        if self.__rm.get() < self.amplitude:
            state = _EnemyState.FIGHT
        for enemy in entangled_tiles:
            enemy._set_state(state)

        # sometimes when there is no entanglement we have to explicitely set the state of self
        if self.__state == _EnemyState.UNDECIDED:
            self.__state = state

        return state == _EnemyState.FIGHT

    def copy(self):
        enemy = Enemy(self.__factory, self.__get_entangled_tiles, self.__id, self.__amplitude)
        enemy._set_state(self.__state)
        return enemy

    def __str__(self) -> str:
        return f"E({self.__id}|{self.__state})"


class Boss(WalkTriggerTile):
    def __init__(self, boss: BossActor, on_walk_callback: OnWalkCallback):
        super().__init__(TileCode.Boss)
        self.__boss = boss
        self.__on_walk_callback = on_walk_callback

    def on_walk(self, direction: Direction, robot: Robot) -> None:
        if not self.__boss.is_defeated:
            self.__on_walk_callback(robot, self.__boss, direction)

    def get_img(self):
        if self.__boss.is_defeated:
            return self._invisible
        else:
            return "B"
