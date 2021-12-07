import random

from util.logger import Logger


class MyRandom:
    _MAX_INT = 1000000000

    def __init__(self, seed: int):
        seed = seed % self._MAX_INT
        self.__random = random.Random(seed)

    def get(self, min: float = 0.0, max: float = 1.0):
        return min + self.__random.random() * (max - min)

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
        elem = iterable[index]
        if remove:
            try:
                iterable.pop(index)
            except ValueError:
                from util.logger import Logger
                Logger.instance().error(f"{iterable} doesn't contain {elem}")
        return elem

    def get_element_prioritized(self, iterable, priorities: "list of float"):
        if len(iterable) == 0:
            return None
        if len(priorities) == 0:
            return self.get_element(iterable)
        try:
            prio_sum = sum(priorities)
        except:
            Logger.instance().error("No valid priorities provided! Returning a random element to avoid crashing.")
            return self.get_element(iterable, remove=False)
        # elements without a given priority will be less than the minimum given priority by the number of prioritized
        # elements divided by the number of all elements, e.g. [1, 2, 1], 4 elements -> 3/4
        unknown_prio = min(priorities) * len(priorities) / len(iterable)

        val = self.get()
        cur_val = 0.0
        index = 0
        for elem in iterable:
            if index < len(priorities):
                cur_val += priorities[index] / prio_sum
            else:
                cur_val += unknown_prio / prio_sum
            if val < cur_val:
                return elem
            index += 1
        Logger.instance().throw(ValueError("This line should not be reachable. Please report this error so it can be "
                                           "fixed as soon as possible!"))


class RandomManager(MyRandom):
    __instance = None

    @staticmethod
    def create_new() -> MyRandom:
        seed = RandomManager.instance().get_int()
        return MyRandom(seed)

    @staticmethod
    def instance() -> MyRandom:
        if RandomManager.__instance is None:
            Logger.instance().throw(Exception("This singleton has not been initialized yet!"))
        return RandomManager.__instance

    @staticmethod
    def force_seed(new_seed: int) -> None:
        if RandomManager.__instance is None:
            RandomManager(new_seed)
        else:
            RandomManager.__instance = MyRandom(new_seed)

    def __init__(self, seed: int):
        if RandomManager.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            super().__init__(seed)
            RandomManager.__instance = self
