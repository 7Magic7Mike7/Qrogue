from typing import Callable


class Pausing:
    __instance = None

    @staticmethod
    def pause():
        if Pausing.__instance:
            Pausing.__instance.__pause_now()

    def __init__(self, callback: Callable[[], None]):
        self.__callback = callback
        Pausing.__instance = self

    def __pause_now(self):
        self.__callback()