from enum import Enum
from widgets.qrogue_pycui import QroguePyCUI
from game.actors.player import Player
from game.controls import Controls
from game.map.map import Map
from game.map.navigation import Direction


class GameHandler:
    __MAP_WIDTH = 50
    __MAP_HEIGHT = 14

    def __init__(self, seed: int):
        self.__seed = seed
        self.__renderer = QroguePyCUI(seed)
        self.__controls = Controls()
        self.__state_machine = StateMachine(self) # (self.__renderer, self.__controls)

        self.__map = Map(seed, self.__MAP_WIDTH, self.__MAP_HEIGHT)
        self.__player = Player()

        self.__logger = self.__renderer.logger
        self.__renderer.map_widget.set_map(self.__map)
        self.__renderer.circuit_widget.set_player(self.__player)    # todo maybe only set player.circuit?
        self.__renderer.player_info_widget.set_player(self.__player)
        self.__renderer.player_qubits_widget.set_player(self.__player)

        self.__update()

    def init_move_keys(self):  # note: only 1 command per key is possible, overriding however is no problem
        # Add the key binding to the PyCUI object itself for overview mode.
        self.__renderer.add_key_command(self.__controls.move_up, self.__move_up)
        self.__renderer.add_key_command(self.__controls.move_right, self.__move_right)
        self.__renderer.add_key_command(self.__controls.move_down, self.__move_down)
        self.__renderer.add_key_command(self.__controls.move_left, self.__move_left)
        self.__renderer.add_key_command(self.__controls.action, self.__dummy())
        # self.__renderer.add_key_command(self.__controls.render(), self.__renderer.render())

    def __dummy(self):
        print("dummy")  # todo remove when I figured out, how to remove a key command

    def init_fight_keys(self):
        self.__renderer.add_key_command(self.__controls.selection_up, self.__selection_up)
        self.__renderer.add_key_command(self.__controls.selection_right, self.__selection_right)
        self.__renderer.add_key_command(self.__controls.selection_down, self.__selection_down)
        self.__renderer.add_key_command(self.__controls.selection_left, self.__selection_left)
        self.__renderer.add_key_command(self.__controls.action, self.__attack)

    def log(self, msg: str):
        self.__logger.println(msg)

    def start(self):
        self.__renderer.start()

    def __update(self):
        self.__renderer.render()
        self.__fight()  # todo handle differently later

    def __fight(self):
        self.__cur_enemy = self.__map.in_enemy_range()
        if self.__cur_enemy is not None:
            self.__logger.clear()
            self.__logger.println(self.__cur_enemy.__str__())
            self.__state_machine.change_state(State.Fight)
        self.__renderer.event_info_widget.set_enemy(self.__cur_enemy)  # is none if there is no enemy, and this is okay
        self.__renderer.event_targets_widget.set_enemy(self.__cur_enemy)  # is none if there is no enemy, and this is okay

    def __move_up(self):
        if self.__map.move(Direction.Up):
            self.__update()

    def __move_right(self):
        if self.__map.move(Direction.Right):
            self.__update()

    def __move_down(self):
        if self.__map.move(Direction.Down):
            self.__update()

    def __move_left(self):
        if self.__map.move(Direction.Left):
            self.__update()

    def __selection_up(self):
        self.__renderer.player_info_widget.prev()
        self.__update()

    def __selection_right(self):
        self.__logger.clear()
        self.__logger.println("selection right")

    def __selection_down(self):
        self.__renderer.player_info_widget.next()
        self.__update()

    def __selection_left(self):
        self.__logger.clear()
        self.__logger.println("selection left")

    def __attack(self):
        if self.__cur_enemy is None:
            self.__logger.println("Error! Enemy is not set!")
            return

        self.__player.use_instruction(self.__renderer.player_info_widget.circuit)
        result = self.__player.measure()
        for r in result:
            self.__cur_enemy.damage(r, 1)
        result = self.__player.defend(input=[])
        self.__logger.clear()
        self.__logger.println(result.__str__())
        self.__update()


class State(Enum):
    Pause = 0
    Explore = 1
    Fight = 2
    Riddle = 3


class StateMachine:
    def __init__(self, game: GameHandler):
        self.__game = game
        # self.__renderer = renderer
        # self.__controls = controls
        self.__cur_state = None
        self.__prev_state = None
        self.change_state(State.Explore)

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
            self.__game.init_move_keys()
        elif self.__cur_state == State.Fight:
            self.__game.init_fight_keys()