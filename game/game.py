from enum import Enum

import game.actors.enemy as enemy
import game.map.tiles as tiles
from game.actors.player import DummyPlayer, Player
from game.callbacks import OnWalkCallback
from game.controls import Controls
from game.map.map import Map
from game.map.navigation import Direction
from util.logger import Logger
from util.my_random import RandomManager
from widgets.qrogue_pycui import QrogueCUI


class GameHandler:
    __MAP_WIDTH = 50
    __MAP_HEIGHT = 14

    __FIGHT_CALLBACK = None

    @staticmethod
    def fight_callback() -> OnWalkCallback:
        return GameHandler.__FIGHT_CALLBACK

    def __init__(self, seed: int):
        self.__seed = seed
        self.__randMan = RandomManager(seed)
        Logger()    # create the logger

        GameHandler.__FIGHT_CALLBACK = self.__fight_callback

        self.__renderer = QrogueCUI(seed, Controls(), self.__end_of_fight_callback)
        self.__state_machine = StateMachine(self, None, None)

        self.__player_tile = tiles.Player(DummyPlayer())
        self.__map = Map(seed, self.__MAP_WIDTH, self.__MAP_HEIGHT, self.__player_tile, self.__fight_callback)

        self.__state_machine.change_state(State.Explore)
        self.__update()

    @property
    def __player(self):
        return self.__player_tile.player

    def __init_pause_screen(self):
        Logger.instance().println("Pause", clear=True)

    def init_explore_screen(self):
        self.__renderer.switch_to_explore(self.__map, self.__player_tile)

    def init_fight_screen(self):
        self.__renderer.switch_to_fight(self.__player_tile, self.__cur_enemy)

    def __init_riddle_screen(self):
        Logger.instance().println("Riddle", clear=True)

    def __fight_callback(self, player: Player, enemy: enemy.Enemy, direction: Direction):
        self.__cur_enemy = enemy
        self.__state_machine.change_state(State.Fight)

    def __end_of_fight_callback(self):
        Logger.instance().println("You won the fight!")
        self.__state_machine.change_state(State.Explore)

    def start(self):
        self.__renderer.start()

    def __update(self):
        self.__renderer.render()


class State(Enum):
    Pause = 0
    Explore = 1
    Fight = 2
    Riddle = 3


class StateMachine:
    def __init__(self, game: GameHandler, explore_cui, fight_cui):
        self.__game = game
        self.__explore_cui = explore_cui
        self.__fight_cui = fight_cui
        self.__cur_state = None
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

        if self.__cur_state == State.Explore:
            self.__game.init_explore_screen()
        elif self.__cur_state == State.Fight:
            self.__game.init_fight_screen()
        elif self.__cur_state == State.Pause:
            self.__game.init_pause_screen()
        elif self.__cur_state == State.Riddle:
            self.__game.init_riddle_screen()
