from game.actors.controllable import Controllable
from game.collectibles import pickup
from game.collectibles.collectible import Collectible
from util.config import Config


class Player(Controllable):
    def __init__(self):
        super().__init__(Config.player_name())
        self.__key_count = 0

    def get_img(self):
        return "M"

    def description(self) -> str:
        return f"The student that eagerly helps Professor {Config.scientist_name()} with his research. "

    def key_count(self) -> int:
        return self.__key_count

    def use_key(self) -> bool:
        if self.key_count() > 0:
            self.__key_count -= 1
            return True
        return False

    def give_collectible(self, collectible: Collectible):
        if isinstance(collectible, pickup.Key):
            self.__key_count += 1
