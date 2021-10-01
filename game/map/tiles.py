
from abc import ABC, abstractmethod
from enum import Enum

import py_cui

from game.actors.boss import Boss as BossActor
from game.actors.factory import EnemyFactory
from game.actors.player import Player as PlayerActor
from game.callbacks import OnWalkCallback
from game.map.navigation import Direction
from util.my_random import RandomManager


class TileCode(Enum):
    Invalid = -1    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Void = 7        # tile outside of the playable area
    Floor = 0       # simple floor tile without special meaning
    FogOfWar = 3    # tile of a place we cannot see yet

    Wall = 1
    Obstacle = 2
    Door = 4

    Player = 20
    Enemy = 30
    Boss = 40

    Item = 50


class Tile(ABC):
    def __init__(self, code: TileCode):
        self.__code = code

    @property
    def code(self):
        return self.__code

    @abstractmethod
    def get_img(self):
        pass

    @abstractmethod
    def is_walkable(self, direction: Direction, actor):
        pass


class WalkTriggerTile(Tile):
    def __init__(self, code: TileCode, on_walk_callback: OnWalkCallback):
        super().__init__(code)
        self._on_walk_callback = on_walk_callback
    
    @abstractmethod
    def on_walk(self, direction: Direction, actor):
        pass


class Invalid(Tile):
    def __init__(self):
        super().__init__(TileCode.Invalid)

    def get_img(self):
        return "§"

    def is_walkable(self, direction: Direction, actor):
        return False


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return " "

    def is_walkable(self, direction: Direction, actor):
        return False


class Floor(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return " "

    def is_walkable(self, direction: Direction, actor):
        return True


class Wall(Tile):
    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return "#"

    def is_walkable(self, direction: Direction, actor):
        return False


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "o"

    def is_walkable(self, direction: Direction, actor):
        return False


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "~"

    def is_walkable(self, direction: Direction, actor):
        return True


class Door(Tile):
    def __init__(self, direction: Direction, locked: bool = False):   # todo entangled door as extra class?
        super().__init__(TileCode.Door)
        self.__direction = direction
        self.__locked = locked

    def get_img(self):
        return "D"

    def is_walkable(self, direction: Direction, actor):
        if direction == self.__direction or direction == self.__direction.opposite():
            return not self.__locked
        else:
            return False

    @property
    def direction(self):
        return self.__direction

    def unlock(self):   # todo
        self.__locked = False


class Item(Tile):
    def __init__(self): # TODO add item
        super().__init__(TileCode.Item)

    def get_img(self):
        return "I"

    def is_walkable(self, direction: Direction, actor):
        return True


class Player(Tile):
    def __init__(self, player: PlayerActor):
        super().__init__(TileCode.Player)
        self.__player = player

    def get_img(self):
        return "P"

    def is_walkable(self, direction: Direction, actor):
        return True # todo check

    @property
    def player(self) -> PlayerActor:
        return self.__player


class _EnemyState(Enum):
    UNDECIDED = 0
    FREE = 1
    FIGHT = 2
    DEAD = 3
    FLED = 4
class Enemy(WalkTriggerTile):
    def __init__(self, factory: EnemyFactory, get_entangled_tiles,
                 id: int = 0, amplitude: float = 0.5):
        super().__init__(TileCode.Enemy, factory.callback)
        self.__factory = factory
        self.__state = _EnemyState.UNDECIDED
        self.__get_entangled_tiles = get_entangled_tiles
        self.__id = id
        self.__amplitude = amplitude

    def on_walk(self, direction: Direction, actor):
        if isinstance(actor, PlayerActor):
            if self.__state == _EnemyState.UNDECIDED:
                if self.measure():
                    enemy = self.__factory.get_enemy()
                    self._on_walk_callback(actor, enemy, direction)
                    self.__state = _EnemyState.DEAD
                else:
                    self.__state = _EnemyState.FLED
            elif self.__state == _EnemyState.FIGHT:
                enemy = self.__factory.get_enemy()
                self._on_walk_callback(actor, enemy, direction)
                self.__state = _EnemyState.DEAD
            elif self.__state == _EnemyState.FREE:
                self.__state = _EnemyState.FLED

    def get_img(self):
        if self.__state == _EnemyState.DEAD :
            return "x"
        elif self.__state == _EnemyState.FLED:
            return "."
        else:
            return str(self.__id)

    def is_walkable(self, direction: Direction, actor):
        return True

    @property
    def amplitude(self):
        return self.__amplitude

    def set_state(self, val: _EnemyState):
        if self.__state == _EnemyState.UNDECIDED:
            self.__state = val
        else:
            raise RuntimeError("Illegal program state!")

    def measure(self):
        if 0 < self.__id <= 9:
            entangled_tiles = self.__get_entangled_tiles(self.__id)
        else:
            entangled_tiles = [self]

        state = _EnemyState.FREE
        if RandomManager.instance().get() < self.amplitude:
            state = _EnemyState.FIGHT
        for enemy in entangled_tiles:
            enemy.set_state(state)

        return state == _EnemyState.FIGHT


class Boss(WalkTriggerTile):
    def __init__(self, boss: BossActor, on_walk_callback: OnWalkCallback):
        super().__init__(TileCode.Boss, on_walk_callback)
        self.__boss = boss

    def on_walk(self, direction: Direction, actor):
        if isinstance(actor, PlayerActor):
            self._on_walk_callback(actor, self.boss, direction)

    def get_img(self):
        return "B"

    def is_walkable(self, direction: Direction, actor):
        return True

    @property
    def boss(self):
        return self.__boss


__color_manager = {
    TileCode.Invalid: py_cui.RED_ON_BLUE,
    TileCode.Void: py_cui.CYAN_ON_BLACK,
    TileCode.Floor: py_cui.CYAN_ON_BLACK,
    TileCode.Wall: py_cui.BLACK_ON_CYAN,
    TileCode.Obstacle: py_cui.CYAN_ON_BLACK,
    TileCode.FogOfWar: py_cui.CYAN_ON_BLACK,
    TileCode.Door: py_cui.CYAN_ON_BLACK,
    TileCode.Item: py_cui.CYAN_ON_BLACK,
    TileCode.Player: py_cui.GREEN_ON_BLACK,
    TileCode.Enemy: py_cui.RED_ON_BLACK,
    TileCode.Boss: py_cui.BLACK_ON_RED,
}
def get_color(tile: TileCode) -> int:
    return __color_manager[tile]
