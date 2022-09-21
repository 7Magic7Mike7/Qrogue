from enum import Enum
from typing import Callable

from qrogue.game.logic.actors import Controllable, Robot
from qrogue.game.world.navigation import Direction
from qrogue.util import CommonPopups, Logger, CheatConfig

from qrogue.game.world.tiles import Invalid, TileCode, Tile, Wall, Floor, WalkTriggerTile


class DoorOpenState(Enum):
    Open = 0
    Closed = 1
    KeyLocked = 2
    EventLocked = 3
    EntanglementLocked = 4


class DoorOneWayState(Enum):
    NoOneWay = 0
    Temporary = 1
    Permanent = 2


class DoorEntanglementState(Enum):
    NotEntangled = 0
    Undecided = 1
    Locked = 2
    Unlocked = 3


class Door(WalkTriggerTile):
    __INVALID_DIRECTION_IMG = Invalid().get_img()

    def __init__(self, direction: Direction, open_state: DoorOpenState = DoorOpenState.Closed,
                 one_way_state: DoorOneWayState = DoorOneWayState.NoOneWay, event_check: Callable[[], bool] = None,
                 entanglement_state: DoorEntanglementState = DoorEntanglementState.NotEntangled):
        super().__init__(TileCode.Door)
        self.__direction = direction
        self.__open_state = open_state
        self.__one_way_state = one_way_state
        self.__entanglement_state = entanglement_state
        self.__event_check = event_check
        self.__check_entanglement_lock_callback = None

    def set_entanglement(self, check_entanglement_lock: Callable[[], None]):
        self.__check_entanglement_lock_callback = check_entanglement_lock
        self.__entanglement_state = DoorEntanglementState.Undecided

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
        if CheatConfig.ignore_obstacles():
            return True

        if self.__one_way_state is DoorOneWayState.Permanent or \
                self.__one_way_state is DoorOneWayState.Temporary and not self.is_open:
            correct_direction = direction is self.__direction
        else:
            # opposite direction is also fine for non one-way doors or opened temporary one-way doors
            correct_direction = direction in [self.__direction, self.__direction.opposite()]
        if correct_direction:
            if self.is_open:
                can_walk = True
            elif self.is_key_locked:
                if controllable.key_count() > 0:
                    can_walk = True
                else:
                    CommonPopups.LockedDoor.show()
                    can_walk = False
            elif self.is_event_locked:
                if self.check_event():
                    can_walk = True
                else:
                    CommonPopups.EventDoor.show()
                    can_walk = False
            elif self.is_entanglement_locked:
                CommonPopups.EntangledDoor.show()
                can_walk = False
            else:
                can_walk = True
            if self.has_explanation:
                WalkTriggerTile._show_explanation(self._explanation, overwrite=True)  # we overwrite a common popup that may be shown
            self._explicit_trigger()
            return can_walk
        else:
            CommonPopups.WrongDirectionDoor.show()
            return False

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if self.is_key_locked:
            if isinstance(controllable, Robot):
                if not controllable.use_key():
                    Logger.instance().error(f"Error! Walked on a door without having enough keys!\n#keys="
                                            f"{controllable.key_count()}, dir={direction}", from_pycui=False)
            else:
                Logger.instance().error(f"Error! Non-Robot walked through a locked door: {controllable}",
                                        from_pycui=False)
        self.__open_state = DoorOpenState.Open
        return True

    @property
    def direction(self) -> Direction:
        return self.__direction

    @property
    def is_open(self) -> bool:
        return self.__open_state is DoorOpenState.Open and self.__entanglement_state is not DoorEntanglementState.Locked

    @property
    def is_key_locked(self) -> bool:
        return self.__open_state is DoorOpenState.KeyLocked

    @property
    def is_event_locked(self) -> bool:
        return self.__open_state is DoorOpenState.EventLocked

    @property
    def is_entanglement_locked(self) -> bool:
        if self.__entanglement_state is DoorEntanglementState.NotEntangled or \
                self.__check_entanglement_lock_callback is None:
            return False

        if self.__entanglement_state is DoorEntanglementState.Undecided:
            if self.__check_entanglement_lock_callback():
                self.__entanglement_state = DoorEntanglementState.Locked
            else:
                self.__entanglement_state = DoorEntanglementState.Unlocked

        return self.__entanglement_state is DoorEntanglementState.Locked

    @property
    def is_one_way(self) -> bool:
        return self.__one_way_state is not DoorOneWayState.NoOneWay

    def check_event(self) -> bool:
        # don't check again if the door is already open
        if self.is_open:
            return True

        if self.__event_check is None:
            Logger.instance().error("Tried to enter event-locked door with event_check still uninitialized!",
                                    from_pycui=False)
            self.__open_state = DoorOpenState.Closed
            return True
        if self.__event_check():
            self.__open_state = DoorOpenState.Closed
            return True
        return False

    def _copy(self) -> "Tile":
        door = Door(self.__direction, self.__open_state, self.__one_way_state, self.__event_check)
        door.set_entanglement(self.__check_entanglement_lock_callback)
        return door

    def copy_and_adapt(self, new_direction: Direction, reset_one_way: bool = False) -> "Door":
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
        door = Door(new_direction, self.__open_state, one_way_state, self.__event_check)
        door.set_explanation(self._explanation)
        door.set_event(self._event_id)
        door.set_entanglement(self.__check_entanglement_lock_callback)
        return door


class HallwayEntrance(Tile):
    __WALL_IMG = Wall.img()
    __FLOOR_IMG = Floor.img()

    def __init__(self, door_ref: Door):
        super().__init__(TileCode.HallwayEntrance)
        self.__door_ref = door_ref

    def get_img(self):
        if self.__door_ref.is_event_locked and not self.__door_ref.check_event():
            return self.__WALL_IMG
        return self.__FLOOR_IMG

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        if CheatConfig.ignore_obstacles():
            return True

        return not self.__door_ref.is_event_locked

    def copy(self) -> "Tile":
        return HallwayEntrance(self.__door_ref)
