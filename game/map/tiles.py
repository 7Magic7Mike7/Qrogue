
from abc import ABC, abstractmethod
from enum import Enum

from game.actors.boss import Boss as BossActor
from game.actors.factory import EnemyFactory
from game.actors.player import Player as PlayerActor
from game.actors.riddle import Riddle
from game.callbacks import OnWalkCallback
from game.collectibles.factory import CollectibleFactory
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

    Wall = 1
    Obstacle = 2
    Door = 4

    Player = 20
    Enemy = 30
    Boss = 40

    Collectible = 50
    Riddler = 51
    ShopKeeper = 52


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
    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        pass


class WalkTriggerTile(Tile):
    def __init__(self, code: TileCode):
        super().__init__(code)

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True
    
    @abstractmethod
    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        """
        Event that is triggered when an actor moves onto this Tile
        :param direction: the Direction from which the actor moves onto this Tile
        :param player: the actor (e.g. Player) that is moving onto this Tile
        :return: None
        """
        pass


class Invalid(Tile):
    def __init__(self):
        super().__init__(TileCode.Invalid)

    def get_img(self):
        return "§"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Debug(Tile):
    def __init__(self, num: int):
        super(Debug, self).__init__(TileCode.Debug)
        self.__num = str(num)[0]

    def get_img(self) -> str:
        return self.__num

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return self._invisible

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Floor(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return self._invisible

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True


class Wall(Tile):
    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return "#"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "o"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "~"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True


class Message(WalkTriggerTile):
    def __init__(self, popup: Popup, popup_times: int = 1):
        super().__init__(TileCode.Message)
        self.__popup = popup
        if popup_times < 0:
            popup_times = 99999     # display "everytime" the player steps on it
        self.__times = popup_times

    def get_img(self):
        if self.__times > 0:
            return "."
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__times > 0:
            self.__popup.show()
        self.__times -= 1


class Riddler(WalkTriggerTile):
    def __init__(self, open_riddle_callback: "void(Player, Riddle)", riddle: Riddle):
        super().__init__(TileCode.Riddler)
        self.__open_riddle = open_riddle_callback
        self.__riddle = riddle

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__riddle.is_active:
            self.__open_riddle(player, self.__riddle)

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

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        self.__visit_shop(player, self.__inventory)

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

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        if direction == self.__direction or direction == self.__direction.opposite():
            if self.__locked:
                if player.key_count > 0:
                    return True
                else:
                    CommonPopups.LockedDoor.show()
                    return False
            else:
                return True
        else:
            return False

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__locked:
            if player.use_key():
                self.__locked = False
                self.__opened = True
            else:
                Logger.instance().error(f"Error! walked on a door without having enough keys!\n#keys={player.key_count}"
                                        f", dir={direction}")
        else:
            self.__opened = True

    @property
    def direction(self) -> Direction:
        return self.__direction

    @property
    def opened(self) -> bool:
        return self.__opened


class EntangledDoor(Door):
    @staticmethod
    def entangle(door1: "EntangledDoor", door2: "EntangledDoor"):
        door1.__entangled_door = door2
        door2.__entangled_door = door1

    def __init__(self, direction: Direction):
        super().__init__(direction)
        self.__entangled_door = None
        self.__closed = False

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        # if the entangled door is open, this one can no longer we opened/walked on
        if self.__entangled_door.opened:
            CommonPopups.EntangledDoor.show()
            return False
        return super(EntangledDoor, self).is_walkable(direction, player)


class Collectible(WalkTriggerTile):
    def __init__(self, factory: CollectibleFactory):
        super().__init__(TileCode.Collectible)
        self.__factory = factory
        self.__active = True

    def get_img(self):
        if self.__active:
            return "c"
        else:
            return self._invisible

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__active:
            player = player
            collectible = self.__factory.produce()
            name = collectible.name()
            desc = collectible.description()
            Popup.message(collectible.name(), f"You picked up a {name}.\n{desc}")
            player.give_collectible(collectible)
            self.__active = False


class Player(Tile):
    def __init__(self, player: PlayerActor):
        super().__init__(TileCode.Player)
        self.__player = player

    def get_img(self):
        return "P"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
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
        super().__init__(TileCode.Enemy)
        self.__factory = factory
        self.__state = _EnemyState.UNDECIDED
        self.__get_entangled_tiles = get_entangled_tiles
        self.__id = id
        self.__amplitude = amplitude

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if isinstance(player, PlayerActor):
            if self.__state == _EnemyState.UNDECIDED:
                if self.measure():
                    enemy = self.__factory.get_enemy(player, 1 - self.__amplitude)
                    self.__factory.callback(player, enemy, direction)
                    self.__state = _EnemyState.DEAD
                else:
                    self.__state = _EnemyState.FLED
            elif self.__state == _EnemyState.FIGHT:
                if CheatConfig.is_scared_rabbit():
                    self.__state = _EnemyState.FLED
                else:
                    enemy = self.__factory.get_enemy(player, 1 - self.__amplitude)
                    self.__factory.callback(player, enemy, direction)
                    self.__state = _EnemyState.DEAD
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
    def amplitude(self) -> float:
        return self.__amplitude

    def _set_state(self, val: _EnemyState) -> None:
        if self.__state == _EnemyState.UNDECIDED:
            self.__state = val
        else:
            if CheatConfig.did_cheat():
                return
            raise RuntimeError("Illegal program state!")

    def measure(self):
        if CheatConfig.is_scared_rabbit():
            return False

        if 0 < self.__id <= 9:
            entangled_tiles = self.__get_entangled_tiles(self.__id)
        else:
            entangled_tiles = [self]

        state = _EnemyState.FREE
        if RandomManager.instance().get() < self.amplitude:
            state = _EnemyState.FIGHT
        for enemy in entangled_tiles:
            enemy._set_state(state)

        return state == _EnemyState.FIGHT

    def __str__(self) -> str:
        return f"E({self.__id}|{self.__state})"


class Boss(WalkTriggerTile):
    def __init__(self, boss: BossActor, on_walk_callback: OnWalkCallback):
        super().__init__(TileCode.Boss)
        self.__boss = boss
        self.__on_walk_callback = on_walk_callback

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if not self.__boss.is_defeated:
            self.__on_walk_callback(player, self.__boss, direction)

    def get_img(self):
        if self.__boss.is_defeated:
            return self._invisible
        else:
            return "B"
