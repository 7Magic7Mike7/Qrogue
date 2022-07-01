import random
from typing import List

from qrogue.util.config import Config
from qrogue.util.logger import Logger


class MyRandom:
    COUNTER = 0
    _MAX_INT = 1000000000
    __Next_Id = 0

    def __init__(self, seed: int):
        seed = seed % Config.MAX_SEED
        self.__random = random.Random(seed)
        self.__id = MyRandom.__Next_Id
        MyRandom.__Next_Id += 1

    def get(self, min: float = 0.0, max: float = 1.0, msg: str = ""):
        msg = f"{msg}@{self.__id}_{MyRandom.COUNTER}"
        MyRandom.COUNTER += 1
        val = min + self.__random.random() * (max - min)
        #PathConfig.write("random_debug.txt", f"{val} | {msg}\n", append=True)
        return val

    def get_int(self, min: int, max: int, msg: str = str(COUNTER)) -> int:
        """
        Random integer in the interval [min, max[
        :param min: minimum possible int (inclusive)
        :param max: maximum possible int (exclusive)
        :return: random int in the given range
        """
        return min + int(self.get(msg=msg) * (max - min))

    def get_seed(self, msg: str = str(COUNTER)) -> int:
        return self.get_int(min=0, max=Config.MAX_SEED, msg=msg)

    def get_element(self, iterable, remove: bool = False, msg: str = str(COUNTER)):
        if len(iterable) == 0:
            return None
        index = self.get_int(min=0, max=len(iterable), msg=msg)
        elem = iterable[index]
        if remove:
            try:
                iterable.pop(index)
            except ValueError:
                from qrogue.util.logger import Logger
                Logger.instance().error(f"{iterable} doesn't contain {elem}", from_pycui=False)
        return elem

    def get_element_prioritized(self, iterable, priorities: List[float], msg: str = str(COUNTER)):
        if len(iterable) == 0:
            return None
        if len(priorities) == 0:
            return self.get_element(iterable, msg=msg)
        try:
            prio_sum = sum(priorities)
        except:
            Logger.instance().error("No valid priorities provided! Returning a random element to avoid crashing.",
                                    from_pycui=False)
            return self.get_element(iterable, remove=False, msg=msg)
        # elements without a given priority will be less than the minimum given priority by the number of prioritized
        # elements divided by the number of all elements, e.g. [1, 2, 1], 4 elements -> 3/4
        unknown_prio = min(priorities) * len(priorities) / len(iterable)

        val = self.get(msg=msg)
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
    def create_new(seed: int = None) -> MyRandom:
        if seed is None:
            seed = RandomManager.instance().get_seed(msg=f"RM.create_new{MyRandom.COUNTER}")
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
            RandomManager.__instance = RandomManager.create_new(new_seed)
            #PathConfig.write("random_debug.txt", f"RandomManager.init({new_seed})\n", append=True)

    def __init__(self, seed: int):
        if RandomManager.__instance is not None:
            Logger.instance().throw(Exception("This class is a singleton!"))
        else:
            super().__init__(seed)
            RandomManager.__instance = self
            #PathConfig.write("random_debug.txt", f"RandomManager.init({seed})\n", append=True)
