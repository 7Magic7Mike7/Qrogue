from game.actors.player import Player
from widgets.qrogue_pycui import QroguePyCUI
from game.controls import Controls
from game.states import StateMachine, State
from game.map.map import Map
from game.map.navigation import Direction


class GameHandler:
    __MAP_WIDTH = 50
    __MAP_HEIGHT = 14

    def __init__(self, seed: int):
        self.__seed = seed
        self.__renderer = QroguePyCUI(seed)

        self.__logger = self.__renderer.logger
        self.__state_machine = StateMachine(self.__logger)
        self.__map = Map(seed, self.__MAP_WIDTH, self.__MAP_HEIGHT)
        self.__renderer.map_widget.set_map(self.__map)

        player = Player()
        self.__renderer.circuit_widget.set_title(player.circuit.__str__())

        self.__init_keys()

        self.__renderer.render()

    def __init_keys(self):
        self.__controls = Controls()
        # Add the key binding to the PyCUI object itself for overview mode.
        self.__renderer.add_key_command(self.__controls.move_up(), self.__move_up)
        self.__renderer.add_key_command(self.__controls.move_right(), self.__move_right)
        self.__renderer.add_key_command(self.__controls.move_down(), self.__move_down)
        self.__renderer.add_key_command(self.__controls.move_left(), self.__move_left)
        # self.__renderer.add_key_command(self.__controls.render(), self.__renderer.render())

    def __move_up(self):
        if self.__map.move(Direction.Up):
            self.__renderer.render()

    def __move_right(self):
        if self.__map.move(Direction.Right):
            self.__renderer.render()

    def __move_down(self):
        if self.__map.move(Direction.Down):
            self.__renderer.render()

    def __move_left(self):
        if self.__map.move(Direction.Left):
            self.__renderer.render()

    def log(self, msg: str):
        self.__logger.println(msg)

    def start(self):
        self.__renderer.start()