import random


class MyRandom:
    _MAX_INT = 1000000000

    def __init__(self, seed: int):
        seed = seed % self._MAX_INT
        self.__random = random.Random(seed)

    def get(self):
        return self.__random.random()

    def get_int(self, min: int = 0, max: int = _MAX_INT) -> int:
        """
        Random integer in the interval [min, max[
        :param min: minimum possible int (inclusive)
        :param max: maximum possible int (exclusive)
        :return: random int in the given range
        """
        return min + int(self.get() * (max - min))

    def get_element(self, iterable, remove: bool = False):
        if len(iterable) == 0:
            return None
        index = self.get_int(min=0, max=len(iterable))
        if remove:
            elem = iterable[index]
            try:
                iterable.pop(index)
            except ValueError:
                from util.logger import Logger
                Logger.instance().error(f"{iterable} doesn't contain {elem}")
            return elem
        else:
            return iterable[index]


class RandomManager(MyRandom):
    __instance = None

    def __init__(self, seed: int):
        if RandomManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__(seed)
            RandomManager.__instance = self

    @staticmethod
    def create_new() -> MyRandom:
        seed = RandomManager.instance().get_int()
        return MyRandom(seed)

    @staticmethod
    def instance() -> "RandomManager":
        if RandomManager.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return RandomManager.__instance
