
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Callable, Any

from qrogue.game.actors.boss import Boss as BossActor
from qrogue.game.actors.controllable import Controllable
from qrogue.game.actors.factory import EnemyFactory
from qrogue.game.actors.robot import Robot
from qrogue.game.actors.riddle import Riddle
from qrogue.game.collectibles.collectible import Collectible as LogicalCollectible
from qrogue.game.collectibles.pickup import Energy as LogicalEnergy
from qrogue.game.logic.message import Message as LogicalMessage
from qrogue.game.map.navigation import Direction, Coordinate
from qrogue.game.save_data import SaveData
from qrogue.util import achievements
from qrogue.util.config import CheatConfig
from qrogue.util.help_texts import TutorialText, TutorialTextType, HelpText, HelpTextType
from qrogue.util.logger import Logger
from qrogue.util.my_random import RandomManager
from qrogue.widgets.my_popups import Popup, CommonPopups


class TileCode(Enum):
    Invalid = -1    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Debug = -2      # displays a digit for debugging
    Void = 7        # tile outside of the playable area
    Floor = 0       # simple floor tile without special meaning
    HallwayEntrance = 5     # depending on the hallway it refers to is either a Floor or Wall
    FogOfWar = 3    # tile of a place we cannot see yet

    Message = 6         # tile for displaying a popup message
    Trigger = 9         # tile that calls a function on walk, i.e. event tile
    Teleport = 91       # special trigger for teleporting between maps
    Decoration = 11     # simply displays a specified character

    Wall = 1
    Obstacle = 2
    Door = 4

    Controllable = 20
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
    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        pass

    def __str__(self):
        return self.get_img()


class WalkTriggerTile(Tile):
    def __init__(self, code: TileCode):
        super().__init__(code)
        self.__explanation = None
        self.__event_id = None
        self.__trigger_event = None

    @property
    def has_explanation(self) -> bool:
        return self.__explanation is not None

    def _late_trigger(self) -> Any:
        if self.__trigger_event and self.__event_id:
            return self.__trigger_event(self.__event_id)

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def set_explanation(self, message: LogicalMessage):
        self.__explanation = message

    def set_event(self, event_id: str):
        self.__event_id = event_id

    def trigger(self, direction: Direction, controllable: Controllable, trigger_event_callback: Callable[[str], Any]) \
            -> Any:
        self.__trigger_event = trigger_event_callback
        event_trigger_allowed = self._on_walk(direction, controllable)
        if self.has_explanation:
            self.__explanation.show()
            self.__explanation = None  # only display once
        if event_trigger_allowed and self.__event_id:
            return trigger_event_callback(self.__event_id)

        return None
    
    @abstractmethod
    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        """
        Event that is triggered when an actor moves onto this Tile
        :param direction: the Direction from which the actor moves onto this Tile
        :param controllable: the actor (e.g. Player) that is moving onto this Tile
        :return: True if we can trigger an event afterwards, False otherwise
        """
        pass


class Invalid(Tile):
    def __init__(self):
        super().__init__(TileCode.Invalid)

    def get_img(self):
        return "§"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False


class Debug(Tile):
    def __init__(self, num: int):
        super(Debug, self).__init__(TileCode.Debug)
        self.__num = str(num)[0]

    def get_img(self) -> str:
        return self.__num

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return self._invisible

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False


class Floor(Tile):
    @staticmethod
    def img():
        return Tile._invisible_tile()

    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return Floor.img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True


class Wall(Tile):
    @staticmethod
    def img():
        return "#"

    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return Wall.img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "o"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return False


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "~"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True


class Decoration(Tile):
    def __init__(self, decoration: str, blocking: bool = False):
        super(Decoration, self).__init__(TileCode.Decoration)
        self.__decoration = decoration
        self.__blocking = blocking

    def get_img(self):
        return self.__decoration

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return not self.__blocking


class Trigger(WalkTriggerTile):
    def __init__(self, callback: Callable[[Direction, Controllable], None]):
        super().__init__(TileCode.Trigger)
        self.__callback = callback

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        self.__callback(direction, controllable)
        return True

    def get_img(self):
        return self._invisible


class Teleport(WalkTriggerTile):
    def __init__(self, callback: Callable[[str, Coordinate], None], target_map: str, room: Coordinate):
        super().__init__(TileCode.Teleport)
        self.__callback = callback
        self.__target_map = target_map
        self.__room = room

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        self.__callback(self.__target_map, self.__room)
        return True

    def get_img(self):
        return "t"


class Message(WalkTriggerTile):
    __msg_counter = 0

    @staticmethod
    def create(text: str, title: str = "Message", popup_times: int = 1) -> "Message":
        return Message(LogicalMessage.create_with_title(f"Msg_{Message.__msg_counter}", title, text), popup_times)

    def __init__(self, message: LogicalMessage, popup_times: int = 1):
        super().__init__(TileCode.Message)
        self.__message = message
        if popup_times < 0:
            popup_times = 99999     # display "everytime" the controllable steps on it
        self.__times = popup_times

    def get_img(self):
        if self.__times > 0:
            return "."
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        self.__times -= 1
        if self.__times >= 0:
            self.__message.show()
            return True
        return False


class Riddler(WalkTriggerTile):
    def __init__(self, open_riddle_callback: "void(Player, Riddle)", riddle: Riddle):
        super().__init__(TileCode.Riddler)
        self.__open_riddle = open_riddle_callback
        self.__riddle = riddle
        self.__is_active = True

    @property
    def _is_active(self) -> bool:
        if self.__is_active:
            if not self.__riddle.is_active:
                self._late_trigger()
                self.__is_active = False
        return self.__is_active

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self._is_active:
            self.__open_riddle(controllable, self.__riddle)
        return False

    def get_img(self):
        if self._is_active:
            return "?"
        else:
            return self._invisible


class ShopKeeper(WalkTriggerTile):
    def __init__(self, visit_shop_callback, inventory: "List[ShopItem]"):
        super().__init__(TileCode.ShopKeeper)
        self.__visit_shop = visit_shop_callback
        self.__inventory = inventory

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        self.__visit_shop(controllable, self.__inventory)
        return True

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
    __INVALID_DIRECTION_IMG = Invalid().get_img()

    def __init__(self, direction: Direction, open_state: DoorOpenState = DoorOpenState.Closed,
                 one_way_state: DoorOneWayState = DoorOneWayState.NoOneWay, event_id: str = None):
        super().__init__(TileCode.Door)
        self.__direction = direction
        self.__open_state = open_state
        self.__one_way_state = one_way_state
        self.__event_id = event_id

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
                return Door.__INVALID_DIRECTION_IMG
        else:
            if self.__direction is Direction.East or self.__direction is Direction.West:
                return "|"
            else:
                return "-"

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        if self.__one_way_state is DoorOneWayState.Permanent or \
                self.__one_way_state is DoorOneWayState.Temporary and not self.is_open:
            correct_direction = direction is self.__direction
        else:
            # opposite direction is also fine for non one-way doors or opened temporary one-way doors
            correct_direction = direction in [self.__direction, self.__direction.opposite()]
        if correct_direction:
            if self.is_key_locked:
                if controllable.key_count() > 0:
                    if not SaveData.instance().achievement_manager.check_achievement(achievements.FirstDoorUnlocked):
                        SaveData.instance().achievement_manager.finished_tutorial(achievements.FirstDoorUnlocked)
                        Popup.scientist_says(TutorialText.get(TutorialTextType.LockedDoorKey))
                    return True
                else:
                    if SaveData.instance().achievement_manager.check_achievement(achievements.FirstDoorUnlocked):
                        CommonPopups.LockedDoor.show()
                    else:
                        SaveData.instance().achievement_manager.finished_tutorial(achievements.FirstDoorUnlocked)
                        Popup.scientist_says(TutorialText.get(TutorialTextType.LockedDoorNoKey))
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

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self.is_key_locked:
            if isinstance(controllable, Robot):
                if not controllable.use_key():
                    Logger.instance().error(f"Error! Walked on a door without having enough keys!\n#keys="
                                            f"{controllable.key_count()}, dir={direction}")
            else:
                Logger.instance().error(f"Error! Non-Robot walked through a locked door: {controllable}")
        self.__open_state = DoorOpenState.Open
        return True

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

    def check_event(self) -> bool:
        # don't check again if the door is already open
        if self.is_open:
            return True

        if self.__event_id is None:
            Logger.instance().error("Tried to enter event-locked door with event-id still uninitialized!")
            self.__open_state = DoorOpenState.Open
            return True
        if SaveData.instance().achievement_manager.check_achievement(self.__event_id):
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

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        # if an entangled door was opened, this one can no longer be opened/walked on
        if self.__entanglement_locked:
            CommonPopups.EntangledDoor.show()
            return False
        return super(EntangledDoor, self).is_walkable(direction, controllable)

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        for door in self.__entangled_doors:
            door.__activate_entanglement_lock()
        return True

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

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
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

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self.__active:
            if not self.has_explanation:
                name = self.__collectible.name()
                desc = self.__collectible.description()
                Popup.message(self.__collectible.name(), f"You picked up: {name}\n{desc}")
            controllable.give_collectible(self.__collectible)
            self.__active = False
            return True
        return False


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

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self.__active:
            controllable.give_collectible(LogicalEnergy(self.__amount))
            self.__active = False
            return True
        return False


class ControllableTile(Tile):
    def __init__(self, controllable: Controllable):
        super().__init__(TileCode.Controllable)
        self.__controllable = controllable

    def get_img(self):
        return self.__controllable.get_img()

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        return True # todo check

    @property
    def controllable(self) -> Controllable:
        return self.__controllable


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
        self.__enemy = None

    @property
    def eid(self) -> int:
        return self.__id

    @property
    def amplitude(self) -> float:
        return self.__amplitude

    @property
    def _state(self) -> _EnemyState:
        if self.__enemy:
            if self.__state == _EnemyState.FIGHT and not self.__enemy.is_active:
                self.__state = _EnemyState.DEAD
                self._late_trigger()
        return self.__state

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        if isinstance(controllable, Robot):
            if controllable.backpack.used_capacity > 0:
                return super(Enemy, self).is_walkable(direction, controllable)
            else:
                controllable.damage(1)
                return False
        else:
            Logger.instance().error(f"Error! Non-Robot walked over Enemy: {controllable}")

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if isinstance(controllable, Robot):
            robot = controllable
            if self._state == _EnemyState.UNDECIDED:
                if self.__measure():
                    self.__fight(robot, direction)
                else:
                    self.__state = _EnemyState.FLED
            elif self._state == _EnemyState.FIGHT:
                if CheatConfig.is_scared_rabbit():
                    self.__state = _EnemyState.FLED
                else:
                    self.__fight(robot, direction)
            elif self._state == _EnemyState.FREE:
                self.__state = _EnemyState.FLED
        return False

    def get_img(self):
        if self._state == _EnemyState.DEAD :
            return self._invisible
        elif self._state == _EnemyState.FLED:
            return self._invisible
        else:
            return str(self.__id)

    def _set_state(self, val: _EnemyState) -> None:
        if self._state == _EnemyState.UNDECIDED:
            self.__state = val
        else:
            if CheatConfig.did_cheat():     # this is a legal state if we used the "Scared Rabbit" cheat
                return
            Logger.instance().throw(RuntimeError(
                f"Illegal enemy state! Tried to set state to {val} although it is already at {self._state}."
            ))

    def __measure(self):
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

        # sometimes when there is no entanglement we have to explicitly set the state of self
        if self._state == _EnemyState.UNDECIDED:
            self.__state = state

        return state == _EnemyState.FIGHT

    def __fight(self, robot: Robot, direction: Direction):
        if self.__enemy is None:
            self.__enemy = self.__factory.produce(robot, self.__rm, flee_chance=0.5)
        self.__factory.start(robot, self.__enemy, direction)

    def __str__(self) -> str:
        return f"E({self.__id}|{self._state})"


class Boss(WalkTriggerTile):
    def __init__(self, boss: BossActor, on_walk_callback: Callable[[Robot, BossActor, Direction], None]):
        super().__init__(TileCode.Boss)
        self.__boss = boss
        self.__on_walk_callback = on_walk_callback
        self.__is_active = True

    @property
    def _is_active(self) -> bool:
        if self.__is_active:
            if not self.__boss.is_active:
                self._late_trigger()
                self.__is_active = False
        return self.__is_active

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if isinstance(controllable, Robot):
            if self._is_active:
                self.__on_walk_callback(controllable, self.__boss, direction)
        else:
            Logger.instance().error(f"Non-Robot walked on Boss! controllable = {controllable}")
        return False

    def get_img(self):
        if self._is_active:
            return "B"
        else:
            return self._invisible
