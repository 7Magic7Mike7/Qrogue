from game.actors.enemy import Enemy
from game.actors.player import Player
from game.map.navigation import Direction


class OnWalkCallback:
    def __call__(self, *args: (Player, Enemy, Direction), **kwds: dict) -> None:
        pass
