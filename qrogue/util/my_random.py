import random
from random import Random
from typing import List, Any

from qrogue.util.config import Config
from qrogue.util.logger import Logger


class MyRandom:
    COUNTER: int = 0
    _MAX_INT: int = 1000000000
    __Next_Id: int = 0

    def __init__(self, seed: int):
        self.__seed = seed % Config.MAX_SEED
        self.__random: Random = Random(seed)
        self.__id: int = MyRandom.__Next_Id
        MyRandom.__Next_Id += 1

    @property
    def seed(self) -> int:
        return self.__seed

    def get(self, min_: float = 0.0, max_: float = 1.0, msg: str = ""):
        MyRandom.COUNTER += 1
        val = min_ + self.__random.random() * (max_ - min_)
        # msg = f"{msg}@{self.__id}_{MyRandom.COUNTER}"
        # PathConfig.write("random_debug.txt", f"{val} | {msg}\n", append=True)
        return val

    def get_int(self, min_: int, max_: int, msg: str = str(COUNTER)) -> int:
        """
        Random integer in the interval [min, max[
        :param msg: a message describing the usage of this method (e.g. caller)
        :param min_: minimum possible int (inclusive)
        :param max_: maximum possible int (exclusive)
        :return: random int in the given range
        """
        return min_ + int(self.get(msg=msg) * (max_ - min_))

    def get_bool(self, msg: str = str(COUNTER)) -> bool:
        return self.get(msg=msg) < 0.5

    def get_seed(self, msg: str = str(COUNTER)) -> int: # todo: introduce class, method, location, sublocation arguments for more consisten messages?
        return self.get_int(min_=0, max_=Config.MAX_SEED, msg=msg)

    def get_element(self, list_: List[Any], remove: bool = False, msg: str = str(COUNTER)) -> Any:
        if len(list_) == 0:
            return None
        index = self.get_int(min_=0, max_=len(list_), msg=msg)
        elem = list_[index]
        if remove:
            try:
                list_.pop(index)
            except ValueError:
                Logger.instance().error(f"{list_} doesn't contain {elem}", show=False, from_pycui=False)
        return elem

    def get_element_prioritized(self, list_: List[Any], priorities: List[float], msg: str = str(COUNTER)) -> Any:
        if len(list_) == 0:
            return None
        if len(list_) == 1:
            return list_[0]
        if len(priorities) == 0:
            return self.get_element(list_, msg=msg)
        if len(priorities) > len(list_):
            # crop priorities if too many values were given
            priorities = priorities[:len(list_)]
        try:
            prio_sum = sum(priorities)
        except:
            Logger.instance().error("No valid priorities provided! Returning a random element to avoid crashing.",
                                    show=False, from_pycui=False)
            return self.get_element(list_, remove=False, msg=msg)
        # elements without a given priority will be less than the minimum given priority by the number of prioritized
        # elements divided by the number of all elements, e.g. [1, 2, 1], 4 elements -> 3/4
        unknown_prio = min(priorities) * len(priorities) / len(list_)

        val = self.get(msg=msg)
        cur_val = 0.0
        index = 0
        for elem in list_:
            if index < len(priorities):
                cur_val += priorities[index] / prio_sum
            else:
                cur_val += unknown_prio / prio_sum
            if val < cur_val:
                return elem
            index += 1
        Logger.instance().throw(ValueError("This line should not be reachable. Please report this error so it can be "
                                           "fixed as soon as possible!"))

    def shuffle_list(self, list_: List[Any]) -> None:
        """
        Shuffles in place.
        """
        self.__random.shuffle(list_)


class RandomManager:
    @staticmethod
    def create_new(seed: int) -> MyRandom:
        if seed is None:
            Logger.instance().throw(Exception("No seed was provided for RandomManager.create_new()!"))
        return MyRandom(seed)
