
from qrogue.game.logic.actors.controllables import Controllable
from qrogue.game.logic.collectibles import Collectible, Key
from qrogue.util import Config, Logger


class Player(Controllable):
    """
    Player is the Controllable used by the game's player outside of levels.
    """

    def __init__(self):
        super().__init__(Config.player_name())
        self.__key_count = 0

    def game_over_check(self) -> bool:
        """
        Checks whether the Controllable is game over or not.
        In case of Player this always returns False since the Player can't be game over.

        :return: always False
        """
        return False

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
        """
        Gives the provided Collectible to the Controllable (e.g. adding it to its inventory).
        In case of Player, only Keys can be given. Other Collectibles are ignored.

        :param collectible: a Collectible to give the Controllable
        :return: None
        """
        if isinstance(collectible, Key):
            self.__key_count += 1
        else:
            Logger.instance().error(f"Tried to give player non-key collectible: {collectible}.", show=False,
                                    from_pycui=False)
