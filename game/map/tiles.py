
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Callable, Any

from game.actors.boss import Boss as BossActor
from game.actors.factory import EnemyFactory
from game.actors.robot import Robot
from game.actors.riddle import Riddle
from game.callbacks import OnWalkCallback
from game.collectibles.collectible import Collectible as LogicalCollectible
from game.collectibles.pickup import Energy as LogicalEnergy
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
    HallwayEntrance = 5     # depending on the hallway it refers to is either a Floor or Wall
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
    Energy = 53

    SpaceshipBlock = 70
    SpaceshipWalk = 71
    SpaceshipTrigger = 72
    OuterSpace = 73


class Tile(ABC):
    @staticmethod
    def _invisible_tile():
        return " "

    def __init__(self, code: TileCode):
        self.__code = code

    @property
    def code(self) -> TileCode:
        return self.__code

    @property
    def _invisible(self):
        return Tile._invisible_tile()

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
        self.__event_id = None

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True

    def set_event(self, event_id: str):
        self.__event_id = event_id

    def trigger(self, direction: Direction, robot: Robot, trigger_event_callback: Callable[[str], Any]) -> Any:
        self._on_walk(direction, robot)
        if self.__event_id:
            return trigger_event_callback(self.__event_id)
        return None
    
    @abstractmethod
    def _on_walk(self, direction: Direction, robot: Robot) -> None:
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
    @staticmethod
    def img():
        return Tile._invisible_tile()

    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return Floor.img()

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True


class Wall(Tile):
    @staticmethod
    def img():
        return "#"

    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return Wall.img()

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
    def __init__(self, callback: Callable[[Direction, Robot], None]):
        super().__init__(TileCode.Trigger)
        self.__callback = callback

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
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

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__times > 0:
            self.__popup.show()
        self.__times -= 1


class Riddler(WalkTriggerTile):
    def __init__(self, open_riddle_callback: "void(Player, Riddle)", riddle: Riddle):
        super().__init__(TileCode.Riddler)
        self.__open_riddle = open_riddle_callback
        self.__riddle = riddle

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__riddle.is_active:
            self.__open_riddle(robot, self.__riddle)

    def get_img(self):
        if self.__riddle.is_active:
            return "?"
        else:
            return self._invisible


class ShopKeeper(WalkTriggerTile):
    def __init__(self, visit_shop_callback, inventory: "List[ShopItem]"):
        super().__init__(TileCode.ShopKeeper)
        self.__visit_shop = visit_shop_callback
        self.__inventory = inventory

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        self.__visit_shop(robot, self.__inventory)

    def get_img(self):
        return "$"


class DoorOpenState(Enum):
    Open = 0
    Closed = 1
    KeyLocked = 2
    EventLocked = 3
class DoorOneWayState(Enum):
    NoOneWay = 0
    Temporary = 1
    Permanent = 2
class Door(WalkTriggerTile):
    def __init__(self, direction: Direction, open_state: DoorOpenState = DoorOpenState.Closed,
                 one_way_state: DoorOneWayState = DoorOneWayState.NoOneWay, event_id: str = None):
        super().__init__(TileCode.Door)
        self.__direction = direction
        self.__open_state = open_state
        self.__one_way_state = one_way_state
        self.__event_id = event_id
        self.__check_event = None

    def get_img(self):
        if self.is_open and self.__one_way_state is not DoorOneWayState.Permanent:
            return self._invisible

        if self.is_one_way:
            if self.__direction is Direction.North:
                return "^"
            elif self.__direction is Direction.East:
                return ">"
            elif self.__direction is Direction.South:
                return "v"
            elif self.__direction is Direction.West:
                return "<"
            else:
                return Invalid().get_img()  # todo use something else?
        else:
            if self.__direction is Direction.East or self.__direction is Direction.West:
                return "|"
            else:
                return "-"

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        if self.__one_way_state is DoorOneWayState.Permanent or \
                self.__one_way_state is DoorOneWayState.Temporary and not self.is_open:
            correct_direction = direction is self.__direction
        else:
            # opposite direction is also fine for non one-way doors or opened temporary one-way doors
            correct_direction = direction in [self.__direction, self.__direction.opposite()]
        if correct_direction:
            if self.is_key_locked:
                if robot.key_count > 0:
                    return True
                else:
                    CommonPopups.LockedDoor.show()
                    return False
            elif self.is_event_locked:
                if self.check_event():
                    return True
                else:
                    CommonPopups.EventDoor.show()
                    return False
            else:
                return True
        else:
            CommonPopups.WrongDirectionDoor.show()
            return False

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.is_key_locked and not robot.use_key():
            Logger.instance().error(f"Error! walked on a door without having enough keys!\n#keys={robot.key_count}"
                                    f", dir={direction}")
        self.__open_state = DoorOpenState.Open

    @property
    def direction(self) -> Direction:
        return self.__direction

    @property
    def is_open(self) -> bool:
        return self.__open_state is DoorOpenState.Open

    @property
    def is_key_locked(self) -> bool:
        return self.__open_state is DoorOpenState.KeyLocked

    @property
    def is_event_locked(self) -> bool:
        return self.__open_state is DoorOpenState.EventLocked

    @property
    def is_one_way(self) -> bool:
        return self.__one_way_state is not DoorOneWayState.NoOneWay

    def set_check_event_callback(self, check_event: Callable[[str], bool]):
        self.__check_event = check_event

    def check_event(self) -> bool:
        # don't check again if the door is already open
        if self.is_open:
            return True

        if self.__check_event is None or self.__event_id is None:
            Logger.instance().error("Tried to enter event-locked door with event-callback or event-id still "
                                    "uninitialized!")
            self.__open_state = DoorOpenState.Open
            return True
        if self.__check_event(self.__event_id):
            self.__open_state = DoorOpenState.Open
            return True
        return False

    def copy(self, new_direction: Direction, reset_one_way: bool = True) -> "Door":
        """
        Copies a door and assigns a new direction to it. Needed to create Hallways in the text based dungeon creator.
        Since one-way doors already have their direction set normally it doesn't make sense to give them a new one.
        Hence a copy of a one-way door will by default no longer be a one-way door.
        :param new_direction: new direction for the copied door
        :param reset_one_way: whether the door is forced to be one-way or if it should keep its one-way flag unchanged
        :return: a new door with the same attributes except for a new direction
        """
        if new_direction is None:
            Logger.instance().throw(ValueError("Tried to copy a door with new_direction being None!"))
        if reset_one_way:
            one_way_state = DoorOneWayState.NoOneWay
        else:
            one_way_state = self.__one_way_state
        return Door(new_direction, self.__open_state, one_way_state, self.__event_id)


class EntangledDoor(Door):
    @staticmethod
    def entangle(door1: "EntangledDoor", door2: "EntangledDoor"):
        door1.__entangled_doors.append(door2)
        door2.__entangled_doors.append(door1)

    def __init__(self, direction: Direction):
        super().__init__(direction)
        self.__entangled_doors = []
        self.__entanglement_locked = False

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        # if an entangled door was opened, this one can no longer be opened/walked on
        if self.__entanglement_locked:
            CommonPopups.EntangledDoor.show()
            return False
        return super(EntangledDoor, self).is_walkable(direction, robot)

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        for door in self.__entangled_doors:
            door.__activate_entanglement_lock()

    def __activate_entanglement_lock(self):
        self.__entanglement_locked = True


class HallwayEntrance(Tile):
    def __init__(self, door_ref: Door):
        super().__init__(TileCode.HallwayEntrance)
        self.__door_ref = door_ref

    def get_img(self):
        if self.__door_ref.is_event_locked and not self.__door_ref.check_event():
            return Wall.img()
        return Floor.img()

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return not self.__door_ref.is_event_locked


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

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__active:
            name = self.__collectible.name()
            desc = self.__collectible.description()
            Popup.message(self.__collectible.name(), f"You picked up: {name}\n{desc}")
            robot.give_collectible(self.__collectible)
            self.__active = False


class Energy(WalkTriggerTile):
    def __init__(self, amount: int):
        super().__init__(TileCode.Energy)
        self.__amount = amount
        self.__active = True

    def get_img(self):
        if self.__active:
            return "e"
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, robot: Robot) -> bool:
        return True

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if self.__active:
            robot.give_collectible(LogicalEnergy(self.__amount))
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

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if isinstance(robot, Robot):
            if robot.backpack.used_capacity > 0:
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
            else:
                robot.damage(amount=1)

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
            Logger.instance().throw(RuntimeError(
                f"Illegal enemy state! Tried to set state to {val} although it is already at {self.__state}."
            ))

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

    def __str__(self) -> str:
        return f"E({self.__id}|{self.__state})"


class Boss(WalkTriggerTile):
    def __init__(self, boss: BossActor, on_walk_callback: OnWalkCallback):
        super().__init__(TileCode.Boss)
        self.__boss = boss
        self.__on_walk_callback = on_walk_callback

    def _on_walk(self, direction: Direction, robot: Robot) -> None:
        if not self.__boss.is_defeated:
            self.__on_walk_callback(robot, self.__boss, direction)

    def get_img(self):
        if self.__boss.is_defeated:
            return self._invisible
        else:
            return "B"
