from abc import ABC, abstractmethod


class Renderable(ABC):
    __COUNTER = 0

    @staticmethod
    def count() -> str:
        """
        Utility function to find out about rendering order for debugging purposes
        :return: string representation of an globally incremented counter
        """
        Renderable.__COUNTER += 1
        return str(Renderable.__COUNTER)

    @abstractmethod
    def render(self) -> None:
        pass
