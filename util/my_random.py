import random


class RandomManager:
    __instance = None

    def __init__(self, seed: int):
        if RandomManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__random = random.Random(seed)
            RandomManager.__instance = self

    def get(self):
        return self.__random.random()

    def get_int(self, max: int, min: int = 0):
        return min + int(self.get() * (max - min))

    def get_element(self, iterable, remove: bool = False):
        index = self.get_int(len(iterable))
        if remove:
            elem = iterable[index]
            iterable.remove(index)
            return elem
        else:
            return iterable[index]

    @staticmethod
    def instance():
        if RandomManager.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return RandomManager.__instance
