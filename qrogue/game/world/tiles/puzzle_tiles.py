from enum import Enum
from typing import Callable, List

from qrogue.game.logic.actors import Controllable, Robot, Boss as BossActor
from qrogue.game.target_factory import EnemyFactory
from qrogue.game.world.navigation import Direction
from qrogue.util import RandomManager, Logger, CheatConfig, PuzzleConfig

from qrogue.game.world.tiles import Tile, TileCode, WalkTriggerTile


class _EnemyState(Enum):
    UNDECIDED = 0
    # FREE = 1
    FIGHT = 2
    DEAD = 3
    FLED = 4


class Enemy(WalkTriggerTile):
    def __init__(self, factory: EnemyFactory, get_entangled_tiles: Callable[[int], List["Enemy"]],
                 update_entangled_groups: Callable[["Enemy"], None], e_id: int = 0):
        super().__init__(TileCode.Enemy)
        self.__factory = factory
        self.__state = _EnemyState.UNDECIDED
        self.__get_entangled_tiles = get_entangled_tiles
        self.__update_entangled_groups = update_entangled_groups
        self.__id = e_id
        self.__rm = RandomManager.create_new()
        self.__enemy = None

    @property
    def eid(self) -> int:
        return self.__id

    @property
    def _state(self) -> _EnemyState:
        if self.__enemy:
            if self.__state == _EnemyState.FIGHT and not self.__enemy.is_active:
                self.__state = _EnemyState.DEAD
                self._explicit_trigger()
        return self.__state

    def is_walkable(self, direction: Direction, controllable: Controllable) -> bool:
        if isinstance(controllable, Robot):
            if controllable.backpack.used_capacity > 0:
                return super(Enemy, self).is_walkable(direction, controllable)
            else:
                # noting happens in case the robot doesn't have any gates
                return False
        else:
            Logger.instance().error(f"Error! Non-Robot walked over Enemy: {controllable}", from_pycui=False)

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if isinstance(controllable, Robot):
            robot = controllable
            if self._state == _EnemyState.UNDECIDED:
                if self.__measure():
                    self.__fight(robot, direction)
            elif self._state == _EnemyState.FIGHT:
                self.__fight(robot, direction)
        return False

    def get_img(self):
        if self._state == _EnemyState.DEAD:
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
        # since self will also be part of what get_entangled_tiles() returns, we act upon self via entangled_tiles
        if 0 < self.__id <= 9:
            entangled_tiles = self.__get_entangled_tiles(self.__id)
        else:
            entangled_tiles = [self]

        # first do the randomness check because otherwise cheating could mess with some overall randomness
        if self.__rm.get(msg="Target.__measure()") >= PuzzleConfig.calculate_appearance_chance(self.__id) \
                or CheatConfig.is_scared_rabbit():
            state = _EnemyState.FLED
        else:
            state = _EnemyState.FIGHT
        for enemy in entangled_tiles:
            enemy._set_state(state)     # this will also set self.__state

        return self.__state is _EnemyState.FIGHT

    def __fight(self, robot: Robot, direction: Direction):
        if self.__enemy is None:
            # the higher the amplitude the easier it should be to flee
            self.__enemy = self.__factory.produce(robot, self.__rm, self.__id)
        self.__factory.start(robot, self.__enemy, direction)

    def _copy(self) -> "Tile":
        enemy = Enemy(self.__factory, self.__get_entangled_tiles, self.__update_entangled_groups, self.__id)
        self.__update_entangled_groups(enemy)
        return enemy

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
                self._explicit_trigger()
                self.__is_active = False
        return self.__is_active

    def _on_walk(self, direction: Direction, controllable: Controllable) -> bool:
        if isinstance(controllable, Robot):
            if self._is_active:
                self.__on_walk_callback(controllable, self.__boss, direction)
        else:
            Logger.instance().error(f"Non-Robot walked on Boss! controllable = {controllable}", from_pycui=False)
        return False

    def get_img(self):
        if self._is_active:
            return "B"
        else:
            return self._invisible

    def _copy(self) -> "Tile":
        # Bosses should not be duplicated in a level anyways, so it doesn't matter if we reference the same BossActor
        return Boss(self.__boss, self.__on_walk_callback)
