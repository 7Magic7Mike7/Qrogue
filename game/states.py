
from enum import Enum
from util.logger import Logger


class State(Enum):
    Pause = 0
    Explore = 1
    Fight = 2
    Riddle = 3


class StateMachine:
    def __init__(self, logger: Logger):
        self.__logger = logger
        self.__cur_state = State.Explore
        self.__prev_state = None

    @property
    def cur_state(self):
        return self.__cur_state

    @property
    def prev_state(self):
        return self.__prev_state

    def change_state(self, state: State):
        self.__prev_state = self.__cur_state
        self.__cur_state = state
