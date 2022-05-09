import time
from abc import abstractmethod, ABC
from typing import List, Callable, Optional

import py_cui
from py_cui.widget_set import WidgetSet


from qrogue.game.logic import StateVector
from qrogue.game.logic.actors import Boss, Enemy, Riddle, Robot
from qrogue.game.logic.actors.puzzles import Target
from qrogue.game.logic.collectibles import ShopItem
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.graphics.popups import Popup
from qrogue.graphics.rendering import ColorRules
from qrogue.util import CommonPopups, Config, Controls, GameplayConfig, HelpText, HelpTextType, Logger, PathConfig, \
    RandomManager, AchievementManager, Keys

from qrogue.graphics.widgets import Renderable
from qrogue.graphics.widgets.my_widgets import SelectionWidget, CircuitWidget, MapWidget, SimpleWidget, HudWidget, \
    MyBaseWidget, Widget, CurrentStateVectorWidget, StateVectorWidget, CircuitMatrixWidget


class MyWidgetSet(WidgetSet, Renderable, ABC):
    """
    Class that handles different sets of widgets so we can easily switch between different screens.
    """

    NUM_OF_ROWS = 9
    NUM_OF_COLS = 9
    BACK_STRING = "-Back-"

    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None]):
        super().__init__(MyWidgetSet.NUM_OF_ROWS, MyWidgetSet.NUM_OF_COLS, logger, root)
        self.init_widgets(controls)
        self.__base_render = base_render_callback

    def add_block_label(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0, center=True)\
            -> MyBaseWidget:
        """Function that adds a new block label to the CUI grid

                Parameters
                ----------
                title : str
                    The title of the block label
                row : int
                    The row value, from the top down
                column : int
                    The column value from the top down
                row_span=1 : int
                    The number of rows to span accross
                column_span=1 : int
                    the number of columns to span accross
                padx=1 : int
                    number of padding characters in the x direction
                pady=0 : int
                    number of padding characters in the y direction
                center : bool
                    flag to tell label to be centered or left-aligned.

                Returns
                -------
                new_widget : MyBaseWidget
                    A reference to the created widget object.
                """
        wid = 'Widget{}'.format(len(self._widgets.keys()))
        new_widget = MyBaseWidget(wid,
                                       title,
                                       self._grid,
                                       row,
                                       column,
                                       row_span,
                                       column_span,
                                       padx,
                                       pady,
                                       center,
                                       self._logger)
        self._widgets[wid] = new_widget
        self._logger.info('Adding widget {} w/ ID {} of type {}'.format(title, id, str(type(new_widget))))
        return new_widget

    def render(self) -> None:
        self.__base_render(self.get_widget_list())

    @abstractmethod
    def init_widgets(self, controls: Controls) -> None:
        pass

    @abstractmethod
    def get_widget_list(self) -> List[Widget]:
        pass

    @abstractmethod
    def get_main_widget(self) -> MyBaseWidget:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


_ascii_art = """


           _______           
          / _____ \          
         | |     | |         
         | |     | |         
         | |     | |         
         | |     | |         
         | |_____| |         
          \______\_\         

 
  _ __ ___   __ _ _   _  ___  
 | '__/ _ \ / _` | | | |/ _ \ 
 | | | (_) | (_| | |_| |  __/ 
 |_|  \___/ \__, |\__,_|\___| 
             __/ |            
            |___/             

"""
class MenuWidgetSet(MyWidgetSet):
    __MAP_WIDTH = 50
    __MAP_HEIGHT = 14

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 start_playing_callback: Callable[[], None], stop_callback: Callable[[], None],
                 start_simulation_callback: Callable[[str], None]):
        self.__seed = 0
        self.__start_playing = start_playing_callback
        self.__stop = stop_callback
        self.__start_simulation = start_simulation_callback
        super().__init__(controls, logger, root, render)

    def init_widgets(self, controls: Controls) -> None:
        height = 5
        width = 3
        selection = self.add_block_label("", 2, 0, row_span=height, column_span=width, center=True)
        self.__selection = SelectionWidget(selection, controls, 1)
        if Config.debugging():
            self.__selection.set_data(data=(
                ["PLAY\n", "SIMULATOR\n", "OPTIONS\n", "EXIT\n"],
                [self.__start_playing, self.__simulate, self.__options, self.__exit]
            ))
        else:
            self.__selection.set_data(data=(
                ["PLAY\n", "OPTIONS\n", "EXIT\n"],
                [self.__start_playing, self.__options, self.__exit]
            ))

        seed = self.add_block_label("Seed", MyWidgetSet.NUM_OF_ROWS-1, 0, row_span=1, column_span=width, center=False)
        self.__seed_widget = SimpleWidget(seed)

        title = self.add_block_label("Qrogue", 0, width, row_span=MyWidgetSet.NUM_OF_ROWS-1,
                                     column_span=MyWidgetSet.NUM_OF_COLS-width, center=True)
        self.__title = SimpleWidget(title)
        self.__title.set_data(_ascii_art)

    def new_seed(self) -> None:
        self.__seed = RandomManager.instance().get_seed(msg="MenuWS.new_seed()")
        self.__seed_widget.set_data(f"Seed: {self.__seed}")
        self.__seed_widget.render()

    def set_seed(self, new_seed: int):
        self.__seed = new_seed
        RandomManager.force_seed(new_seed)
        self.__seed_widget.set_data(f"Seed: {self.__seed}")
        self.__seed_widget.render()

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__title,
            self.__selection
        ]

    def get_main_widget(self) -> MyBaseWidget:
        return self.__selection.widget

    def reset(self) -> None:
        self.__selection.render_reset()

    @property
    def selection(self) -> SelectionWidget:
        return self.__selection

    def __simulate(self) -> None:
        self.__start_simulation()

    def __options(self) -> None:
        Popup.generic_info("Gameplay Config", GameplayConfig.to_file_text())

    def __exit(self) -> None:
        self.__stop()


class PauseMenuWidgetSet(MyWidgetSet):
    __HELP_TEXTS = (
        [
            "Game",
            "Controls", "Fight",
            "Riddle", "Shop",
            "Boss Fight", "Pause",
            "Options",
        ],
        [
            HelpText.get(HelpTextType.Game),
            HelpText.get(HelpTextType.Controls), HelpText.get(HelpTextType.Fight),
            HelpText.get(HelpTextType.Riddle), HelpText.get(HelpTextType.Shop),
            HelpText.get(HelpTextType.BossFight), HelpText.get(HelpTextType.Pause),
            HelpText.get(HelpTextType.Options),
         ]
    )

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_callback: Callable[[], None], save_callback: Callable[[], CommonPopups],
                 exit_run_callback: Callable[[], None]):
        super().__init__(controls, logger, root, render)
        self.__continue_callback = continue_callback
        self.__save_callback = save_callback
        self.__exit_run = exit_run_callback
        self.__achievement_manager = None

    def init_widgets(self, controls: Controls) -> None:
        hud = self.add_block_label('HUD', 0, 0, row_span=1, column_span=MyWidgetSet.NUM_OF_COLS, center=False)
        hud.toggle_border()
        self.__hud = HudWidget(hud)

        choices = self.add_block_label('Choices', 1, 0, row_span= MyWidgetSet.NUM_OF_ROWS-1, column_span=3, center=True)
        self.__choices = SelectionWidget(choices, controls, stay_selected=True)
        self.__choices.set_data(data=(
            ["Continue", "Save", "Manual", "Achievements", "Options", "Exit"],
            [self.__continue, self.__save, self.__help, self.__achievements, self.__options, self.__exit]
        ))

        details = self.add_block_label('Details', 1, 3, row_span=MyWidgetSet.NUM_OF_ROWS-1,
                                       column_span=MyWidgetSet.NUM_OF_COLS-3, center=True)
        self.__details = SelectionWidget(details, controls, is_second=True)

    @property
    def choices(self) -> SelectionWidget:
        return self.__choices

    @property
    def details(self) -> SelectionWidget:
        return self.__details

    def __continue(self) -> bool:
        self.__continue_callback()
        return False

    def __save(self) -> bool:
        common_popup = self.__save_callback()
        common_popup.show()
        return False

    def __help(self) -> bool:
        self.__details.set_data(data=(
            PauseMenuWidgetSet.__HELP_TEXTS[0] + [MyWidgetSet.BACK_STRING],
            [self.__help_text]
        ))
        return True

    def __help_text(self, index: int = 0) -> bool:
        if index < len(PauseMenuWidgetSet.__HELP_TEXTS[0]):
            Popup.generic_info(f"{PauseMenuWidgetSet.__HELP_TEXTS[0][index]}", PauseMenuWidgetSet.__HELP_TEXTS[1][index])
            return False
        return True

    def __achievements(self) -> bool:
        if self.__achievement_manager:
            text = self.__achievement_manager.to_display_string()
            Popup.generic_info("Current Achievement status", text)
        else:
            Popup.generic_info("Error", "No achievements available yet!")
        return False

    def __options(self) -> bool:
        self.__details.set_data(data=(
            ["Gameplay Config", MyWidgetSet.BACK_STRING],
            [self.__options_text]
        ))
        return True

    def __options_text(self, index: int = 0) -> bool:
        if index == 0:
            path = PathConfig.user_data_path(Config.game_config_file())
            Popup.generic_info(f"Configuration located at {path}", GameplayConfig.to_file_text())
            return False
        else:
            return True

    def __exit(self) -> bool:
        self.__exit_run()
        return True

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self.__choices,
            self.__details,
        ]

    def get_main_widget(self) -> MyBaseWidget:
        return self.__choices.widget

    def set_data(self, robot: Optional[Robot], map_name: str, achievement_manager: AchievementManager):
        self.__hud.set_data((robot, map_name))
        self.__achievement_manager = achievement_manager

    def reset(self) -> None:
        self.__choices.render_reset()
        self.__details.render_reset()


class WorkbenchWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI, available_robots: List[Robot],
                 render: Callable[[List[Renderable]], None], continue_callback: Callable[[], None]):
        self.__continue = continue_callback
        self.__available_robots = available_robots
        super().__init__(controls, logger, root, render)

    def init_widgets(self, controls: Controls) -> None:
        robot_selection = self.add_block_label('Robot Selection', 0, 0, row_span=MyWidgetSet.NUM_OF_COLS, center=False)
        self.__robot_selection = SelectionWidget(robot_selection, controls, stay_selected=True)
        self.__robot_selection.set_data((
            [robot.name for robot in self.__available_robots] + [MyWidgetSet.BACK_STRING],
            [self.__details]
        ))

        robot_details = self.add_block_label('Robot Details', 0, 1, 3, 4, center=True)
        self.__robot_info = SimpleWidget(robot_details)

        available_upgrades = self.add_block_label('Upgrades', 4, 1, 2, 2, center=True)
        self.__available_upgrades = SelectionWidget(available_upgrades, controls, 4, is_second=True, stay_selected=False)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__robot_selection,
            self.__robot_info,
            self.__available_upgrades,
        ]

    def get_main_widget(self) -> MyBaseWidget:
        return self.__robot_selection.widget

    def reset(self) -> None:
        pass

    @property
    def selection(self) -> SelectionWidget:
        return self.__robot_selection

    @property
    def upgrades(self) -> SelectionWidget:
        return self.__available_upgrades

    def __details(self, index: int) -> bool:
        if self.__save_data:    # todo fix
            robot = self.__save_data.get_robot(index)
            if robot:
                self.__robot_info.set_data(robot.description())
                self.__available_upgrades.set_data(data=(
                    ["Test", "Fuel"],
                    [self.__upgrade],
                ))
            else:
                self.__continue()
        return True

    def __upgrade(self, index: int) -> bool:
        return True


class ExploreWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI):
        super().__init__(controls, logger, root, render)

    def init_widgets(self, controls: Controls) -> None:
        hud = self.add_block_label('HUD', 0, 0, row_span=1, column_span=MyWidgetSet.NUM_OF_COLS, center=False)
        hud.toggle_border()
        self.__hud = HudWidget(hud)

        map_widget = self.add_block_label('MAP', 1, 0, row_span=MyWidgetSet.NUM_OF_ROWS-1,
                                          column_span=MyWidgetSet.NUM_OF_COLS, center=True)
        map_widget.add_key_command(controls.get_keys(Keys.MoveUp), self.move_up)
        map_widget.add_key_command(controls.get_keys(Keys.MoveRight), self.move_right)
        map_widget.add_key_command(controls.get_keys(Keys.MoveDown), self.move_down)
        map_widget.add_key_command(controls.get_keys(Keys.MoveLeft), self.move_left)
        ColorRules.apply_map_rules(map_widget)
        self.__map_widget = MapWidget(map_widget)

    def get_main_widget(self) -> MyBaseWidget:
        return self.__map_widget.widget

    def set_data(self, map: Map) -> None:
        controllable = map.controllable_tile.controllable
        if isinstance(controllable, Robot):
            self.__hud.set_data((controllable, map.name))
        else:
            self.__hud.reset_data()
        self.__map_widget.set_data(map)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self.__map_widget
        ]

    def render(self) -> None:
        start = time.time()
        super(ExploreWidgetSet, self).render()
        duration = time.time() - start
        self.__hud.update_render_duration(duration)
        self.__hud.render()

    def reset(self) -> None:
        self.__map_widget.render_reset()

    def move_up(self) -> None:
        if self.__map_widget.move(Direction.Up):
            self.render()

    def move_right(self) -> None:
        if self.__map_widget.move(Direction.Right):
            self.render()

    def move_down(self) -> None:
        if self.__map_widget.move(Direction.Down):
            self.render()

    def move_left(self) -> None:
        if self.__map_widget.move(Direction.Left):
            self.render()


class NavigationWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None]):

        super().__init__(controls, logger, root, base_render_callback)

    def init_widgets(self, controls: Controls) -> None:
        map_widget = self.add_block_label('MAP', 1, 0, row_span=MyWidgetSet.NUM_OF_ROWS - 1,
                                          column_span=MyWidgetSet.NUM_OF_COLS, center=True)
        map_widget.add_key_command(controls.get_keys(Keys.MoveUp), self.move_up)
        map_widget.add_key_command(controls.get_keys(Keys.MoveRight), self.move_right)
        map_widget.add_key_command(controls.get_keys(Keys.MoveDown), self.move_down)
        map_widget.add_key_command(controls.get_keys(Keys.MoveLeft), self.move_left)
        self.__map_widget = MapWidget(map_widget)
        ColorRules.apply_navigation_rules(map_widget)

    def get_main_widget(self) -> MyBaseWidget:
        return self.__map_widget.widget

    def set_data(self, map: Map) -> None:
        self.__map_widget.set_data(map)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__map_widget
        ]

    def reset(self) -> None:
        self.__map_widget.render_reset()

    def move_up(self) -> None:
        #MapManager.instance().move_on_cur_map(Direction.Up)
        if self.__map_widget.move(Direction.Up):
            self.render()

    def move_right(self) -> None:
        if self.__map_widget.move(Direction.Right):
            self.render()

    def move_down(self) -> None:
        if self.__map_widget.move(Direction.Down):
            self.render()

    def move_left(self) -> None:
        if self.__map_widget.move(Direction.Left):
            self.render()


class ReachTargetWidgetSet(MyWidgetSet, ABC):
    __CHOICE_COLUMNS = 2
    __DETAILS_COLUMNS = 2

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: "()", flee_choice: str = "Flee"):
        self.__choice_strings = SelectionWidget.wrap_in_hotkey_str(["Add/Remove", "Reset", "Help",
                                                                    flee_choice])
        super().__init__(controls, logger, root, render)
        self._continue_exploration_callback = continue_exploration_callback
        self._robot = None
        self._target = None

    def init_widgets(self, controls: Controls) -> None:
        hud = self.add_block_label('HUD', 0, 0, row_span=1, column_span=MyWidgetSet.NUM_OF_COLS, center=False)
        hud.toggle_border()
        self.__hud = HudWidget(hud)

        stv_row = 1
        row_span = 3

        stv = self.add_block_label('Input StV', stv_row, 0, row_span=row_span, column_span=1, center=True)
        self.__input_stv = StateVectorWidget(stv, "Input")

        multiplication = self.add_block_label('Mul sign', stv_row, 1, row_span=row_span, column_span=1, center=True)
        self.__mul_widget = SimpleWidget(multiplication)

        matrix = self.add_block_label('Circuit Matrix', stv_row, 2, row_span=row_span, column_span=3, center=True)
        self.__circuit_matrix = CircuitMatrixWidget(matrix)

        result = self.add_block_label('Eq sign', stv_row, 5, row_span=1, column_span=1, center=True)
        self.__result_widget = SimpleWidget(result)

        stv = self.add_block_label('Player StV', stv_row, 6, row_span=row_span, column_span=1, center=True)
        self.__stv_robot = CurrentStateVectorWidget(stv, "Output State")

        equality = self.add_block_label('Eq sign', stv_row, 7, row_span=1, column_span=1, center=True)
        self.__eq_widget = SimpleWidget(equality)

        stv = self.add_block_label('Target StV', stv_row, 8, row_span=row_span, column_span=1, center=True)
        self.__stv_target = StateVectorWidget(stv, "Target State")



        circuit = self.add_block_label('Circuit', 6, 0, row_span=1, column_span=MyWidgetSet.NUM_OF_COLS, center=True)
        self.__circuit = CircuitWidget(circuit)

        choices = self.add_block_label('Choices', 7, 0, row_span=2, column_span=3, center=True)
        choices.toggle_border()
        self._choices = SelectionWidget(choices, controls, columns=self.__CHOICE_COLUMNS)
        self._choices.set_data(data=(
            self.__choice_strings,
            [self.__choices_adapt, self.__choices_reset, self.__choices_help, self._choices_flee]
        ))

        details = self.add_block_label('Details', 7, 3, row_span=2, column_span=6, center=True)
        details.toggle_border()
        self._details = SelectionWidget(details, controls, columns=self.__DETAILS_COLUMNS, is_second=True)

        # commit shortcut
        def choices_commit():
            controls.handle(Keys.HotKey1)
            controls.handle(Keys.Action)

        def details_commit():
            controls.handle(Keys.Cancel)
            choices_commit()
        self._choices.widget.add_key_command(controls.get_keys(Keys.HotKeyCommit), choices_commit)
        self._details.widget.add_key_command(controls.get_keys(Keys.HotKeyCommit), details_commit)

    def get_main_widget(self) -> MyBaseWidget:
        return self._choices.widget

    def set_data(self, robot: Robot, target: Target) -> None:
        # from a code readers perspective the reset would make more sense in switch_to_fight() etc. but then we would
        # have to add it to multiple locations and have the risk of forgetting to add it for new ReachTargetWidgetSets
        if GameplayConfig.auto_reset_circuit():
            robot.reset_circuit()

        self._robot = robot
        self._target = target

        self.__hud.set_data((robot, None))  # don't overwrite the current map name
        self.__circuit.set_data(robot)

        sign_offset = "\n" * (2**(self._robot.num_of_qubits - 1))   # 1 (headline) + middle of actual Stv

        self.__input_stv.set_data(StateVector.create_zero_state_vector(self._robot.num_of_qubits))
        self.__mul_widget.set_data(sign_offset + "x")
        self.__result_widget.set_data(sign_offset + "=")
        self.__update_calculation(False)
        self.__stv_target.set_data(target.state_vector)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self.__input_stv,
            self.__mul_widget,
            self.__circuit_matrix,
            self.__result_widget,
            self.__stv_robot,
            self.__eq_widget,
            self.__stv_target,
            self.__circuit,
            self._choices,
            self._details
        ]

    def reset(self) -> None:
        self.choices.render_reset()
        self.details.render_reset()

    @property
    def choices(self) -> SelectionWidget:
        return self._choices

    @property
    def details(self) -> SelectionWidget:
        return self._details

    def __update_calculation(self, target_reached: bool):
        diff_stv = self._target.state_vector.get_diff(self._robot.state_vector)

        self.__circuit_matrix.set_data(self._robot.circuit_matrix)
        self.__stv_robot.set_data((self._robot.state_vector, diff_stv), target_reached=target_reached)

        sign_offset = "\n" * (2**(self._robot.num_of_qubits - 1))   # 1 (headline) + middle of actual Stv
        if diff_stv.is_zero:
            self.__eq_widget.set_data(sign_offset + "===")
        else:
            self.__eq_widget.set_data(sign_offset + "=/=")

    def __choices_adapt(self) -> bool:
        options = [instruction.selection_str() for instruction in self._robot.backpack]
        self._details.set_data(data=(
            SelectionWidget.wrap_in_hotkey_str(options) + [MyWidgetSet.BACK_STRING],
            [self.__choose_instruction]
        ))
        return True

    def __choose_instruction(self, index: int):
        if 0 <= index < self._robot.backpack.used_capacity:
            self.__cur_instruction = self._robot.get_instruction(index)
            if self.__cur_instruction is not None:
                if self.__cur_instruction.is_used():
                    options = [f"Position {i}" for i in range(self._robot.circuit_space)] + ["Remove"]
                    self.details.set_data(data=(
                        SelectionWidget.wrap_in_hotkey_str(options),
                        [self.__choose_position]
                    ))
                else:
                    if self._robot.is_space_left:
                        options = [self.__cur_instruction.preview_str(i) for i in range(self._robot.num_of_qubits)]
                        self.details.set_data(data=(
                            SelectionWidget.wrap_in_hotkey_str(options),
                            [self.__choose_qubit]
                        ))
                    else:
                        CommonPopups.NoCircuitSpace.show()
                self.render()
            else:
                Logger.instance().error("Error! The selected instruction/index is out of range!")
            return False
        else:
            return True

    def __choose_qubit(self, index: int = 0):
        selection = list(range(self._robot.num_of_qubits))
        for q in self.__cur_instruction.qargs_iter():
            selection.remove(q)
        if len(selection) > index and self.__cur_instruction.use_qubit(selection[index]):
            selection.pop(index)
            options = [self.__cur_instruction.preview_str(i) for i in selection]
            self.details.set_data(data=(
                SelectionWidget.wrap_in_hotkey_str(options),
                [self.__choose_qubit]
            ))
        else:
            options = [f"Position {i}" for i in range(self._robot.circuit_space)] + ["Remove"]
            self._details.set_data(data=(
                SelectionWidget.wrap_in_hotkey_str(options),# + [MyWidgetSet.BACK_STRING],
                [self.__choose_position]
            ))
        self.render()
        return False

    def __choose_position(self, index: int = 0):
        if not self._robot.use_instruction(self.__cur_instruction, index):
            CommonPopups.NoCircuitSpace.show()
        options = [instruction.selection_str() for instruction in self._robot.backpack]
        self._details.set_data(data=(
            SelectionWidget.wrap_in_hotkey_str(options) + [MyWidgetSet.BACK_STRING],
            [self.__choose_instruction]
        ))
        self.__choices_commit()     # immediately commit on change
        self.render()
        return False

    def __choices_commit(self) -> bool:
        if self._target is None:
            from qrogue.util.logger import Logger
            Logger.instance().error("Error! Target is not set!")
            return False
        self._robot.update_statevector()
        success, reward = self._target.is_reached(self._robot.state_vector)
        self.__update_calculation(success)
        self.render()
        if success:
            self._robot.give_collectible(reward)
            self._details.set_data(data=(
                [f"Congratulations! You received: {reward.to_string()}"],
                [self._continue_exploration_callback]
            ))
            #Popup.generic_info("Congratulations!", f"You received: {reward.to_string()}")
            #self._continue_exploration_callback()
            return True
        else:
            return self._on_commit_fail()

    def __choices_reset(self) -> bool:
        if self._robot.has_empty_circuit:
            self._details.set_data(data=(
                ["Nothing to reset"],
                [self._empty_callback]
            ))
            return True
        else:
            self._robot.reset_circuit()
            self.__update_calculation(False)
            self.render()
            return False

    def __choices_items(self) -> bool:
        if self._robot.backpack.num_of_available_items > 0:
            options = [consumable.to_string() for consumable in self._robot.backpack.pouch_iterator()]
            self._details.set_data(data=(
                SelectionWidget.wrap_in_hotkey_str(options) + [MyWidgetSet.BACK_STRING],
                [self.__choose_item]
            ))
        else:
            self._details.set_data(data=(
                ["Currently you do not have any items you could use."],
                [self._empty_callback]
            ))
        return True

    def __continue_consuming(self) -> bool:
        # leave if there are no more consumables left, stay if we could consume another one
        if self._robot.backpack.num_of_available_items > 0:
            options = [consumable.to_string() for consumable in self._robot.backpack.pouch_iterator()]
            self._details.set_data(data=(
                SelectionWidget.wrap_in_hotkey_str(options) + [MyWidgetSet.BACK_STRING],
                [self.__choose_item]
            ))
            self._details.render()
            return False
        else:
            return True

    def __choose_item(self, index: int = 0) -> bool:
        if 0 <= index < self._robot.backpack.consumables_in_pouch:
            consumable = self._robot.backpack.get_from_pouch(index)
            if consumable is not None:
                if consumable.consume(self._robot):
                    if consumable.charges_left() > 0:
                        text = f"You partially consumed {consumable.name()} and there "
                        if consumable.charges_left() > 1:
                            text += f"are {consumable.charges_left()} portions "
                        else:
                            text += "is only 1 more portion "
                        text += "left to consume. "
                    else:
                        self._robot.backpack.remove_from_pouch(consumable)
                        text = f"You fully consumed {consumable.name()}. "
                    text += f"\nYou gained the following effect:\n{consumable.effect_description()}"
                    self._details.set_data(data=([text], [self.__continue_consuming]))
                else:
                    Popup.generic_info(consumable.name(), f"Failed to consume {consumable.name()}")
                self.render()
                return False
            else:
                Logger.instance().error("Error! The selected consumable/index is out of range!")
        return True

    def __choices_help(self) -> bool:
        options = [instruction.name() for instruction in self._robot.backpack]
        self._details.set_data(data=(
            SelectionWidget.wrap_in_hotkey_str(options) + [MyWidgetSet.BACK_STRING],
            [self.__show_help_popup]
        ))
        return True

    def __show_help_popup(self, index: int = 0) -> bool:
        if 0 <= index < self._robot.backpack.used_capacity:
            instruction = self._robot.backpack.get(index)
            Popup.generic_info(instruction.name(), instruction.description())
            return False
        return True

    @abstractmethod
    def _on_commit_fail(self) -> bool:
        pass

    @abstractmethod
    def _choices_flee(self) -> bool:
        pass

    def _empty_callback(self) -> None:
        pass


class FightWidgetSet(ReachTargetWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[], None], game_over_callback: Callable[[], None]):
        super(FightWidgetSet, self).__init__(controls, render, logger, root, continue_exploration_callback)
        self.__game_over_callback = game_over_callback
        self.__flee_check = None

    def set_data(self, robot: Robot, target: Enemy):
        super(FightWidgetSet, self).set_data(robot, target)
        self.__flee_check = target.flee_check

    def _on_commit_fail(self) -> bool:
        damage_taken, deadly = self._robot.damage()
        if deadly:
            self._details.set_data(data=(
                [f"Oh no, you took {damage_taken} damage and died!"],
                [self.__game_over_callback]
            ))
        else:
            self._details.set_data(data=(
                [f"Wrong, you took {damage_taken} damage. Remaining energy = {self._robot.cur_energy}"],
                [self._empty_callback]
            ))
        return True

    def _choices_flee(self) -> bool:
        if self.__flee_check():
            self._details.set_data(data=(
                ["You successfully fled!"],
                [self._continue_exploration_callback]
            ))
        else:
            damage_taken, deadly = self._robot.damage(amount=1)
            if deadly:
                self._details.set_data(data=(
                    ["Failed to flee. You have no more HP left and die."],
                    [self.__game_over_callback]
                ))
            else:
                self._details.set_data(data=(
                    ["Failed to flee. Your Robot lost some Energy."],
                    [self._empty_callback]
                ))
        return True


class BossFightWidgetSet(FightWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[], None], game_over_callback: Callable[[], None]):
        self.__continue_exploration_callback = continue_exploration_callback
        super().__init__(controls, render, logger, root, self.__continue_exploration, game_over_callback)

    def set_data(self, robot: Robot, target: Boss):
        super(BossFightWidgetSet, self).set_data(robot, target)

    def __continue_exploration(self):
        if self._target.is_defeated:
            Logger.instance().info("Defeated boss.", from_pycui=False)    # todo
        else:
            self.__continue_exploration_callback()


class ShopWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: "()"):
        super().__init__(controls, logger, root, render)
        self.__continue_exploration = continue_exploration_callback
        self.__robot = None
        self.__items = None

    def init_widgets(self, controls: Controls) -> None:
        hud = self.add_block_label("HUD", 0, 0, row_span=1, column_span=MyWidgetSet.NUM_OF_COLS, center=False)
        self.__hud = HudWidget(hud)

        inv_width = 4
        inventory = self.add_block_label("Inventory", 1, 0, row_span=7, column_span=inv_width)
        self.__inventory = SelectionWidget(inventory, controls, stay_selected=True)

        details = self.add_block_label("Details", 1, inv_width, row_span=4, column_span=MyWidgetSet.NUM_OF_COLS - inv_width)
        self.__details = SimpleWidget(details)
        buy = self.add_block_label("Buy", 4, inv_width, row_span=1, column_span=MyWidgetSet.NUM_OF_COLS - inv_width)
        self.__buy = SelectionWidget(buy, controls, is_second=True)

    @property
    def inventory(self) -> SelectionWidget:
        return self.__inventory

    @property
    def buy(self) -> SelectionWidget:
        return self.__buy

    @property
    def details(self) -> SimpleWidget:
        return self.__details

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self.__inventory,
            self.__details,
            self.__buy,
        ]

    def get_main_widget(self) -> MyBaseWidget:
        return self.__inventory.widget

    def reset(self) -> None:
        self.__inventory.render_reset()

    def set_data(self, robot: Robot, items: List[ShopItem]) -> None:
        self.__robot = robot
        self.__hud.set_data((robot, None))    # don't overwrite the current map name
        self.__update_inventory(items)

    def __update_inventory(self, items: List[ShopItem]):
        self.__items = items
        self.__inventory.set_data(data=(
            [si.to_string() for si in items] + ["-Leave-"],
            [self.__select_item]
        ))

    def __select_item(self, index: int = 0) -> bool:
        if index >= len(self.__items):
            self.__continue_exploration()
            return False

        shop_item = self.__items[index]
        self.__cur_item = shop_item
        self.__details.set_data(shop_item.collectible.description())
        if self.__robot.backpack.can_afford(shop_item.price):
            self.__buy.set_data(data=(
                ["Buy!", "No thanks"],
                [self.__buy_item, self.__back_to_inventory]
            ))
        else:
            self.__buy.set_data(data=(
                ["You can't afford that!"],
                [self.__back_to_inventory]
            ))
        return True

    def __buy_item(self) -> bool:
        if self.__robot.backpack.use_coins(self.__cur_item.price):
            self.__robot.give_collectible(self.__cur_item.collectible)
            self.__hud.render()
            self.__items.remove(self.__cur_item)
            self.__update_inventory(self.__items)
            return True
        else:
            return False

    def __back_to_inventory(self) -> bool:
        self.__cur_item = None
        return True


class RiddleWidgetSet(ReachTargetWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[None], None]):
        super().__init__(controls, render, logger, root, continue_exploration_callback, "Give Up")

    def set_data(self, robot: Robot, target: Riddle) -> None:
        super(RiddleWidgetSet, self).set_data(robot, target)

    def _on_commit_fail(self) -> bool:
        if self._target.attempts <= 0:
            self._details.set_data(data=(
                [f"You couldn't solve the riddle within the given attempts. It vanishes together with its reward."],
                [self._continue_exploration_callback]
            ))
        else:
            self._details.set_data(data=(
                [f"Wrong! Remaining attempts: {self._target.attempts}"],
                [self._empty_callback]
            ))
        return True

    def _choices_flee(self) -> bool:
        if self._target.attempts > 0:
            self._details.set_data(data=(
                [f"Abort - you can still try again later", "Continue"],
                [self._continue_exploration_callback, self._empty_callback]
            ))
        else:
            self._details.set_data(data=(
                ["Abort - but you don't have any attempts left to try again later!", "Continue"],
                [self._continue_exploration_callback, self._empty_callback]
            ))
        return True
