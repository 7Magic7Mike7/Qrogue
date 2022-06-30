import time
from abc import abstractmethod, ABC
from typing import List, Callable, Optional, Tuple

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
from qrogue.graphics.widget_base import WidgetWrapper
from qrogue.util import CommonPopups, Config, Controls, GameplayConfig, HelpText, HelpTextType, Logger, PathConfig, \
    RandomManager, AchievementManager, Keys, UIConfig, HudConfig, ColorConfig
from qrogue.util.achievements import Ach, Unlocks

from qrogue.graphics.widgets import Renderable, Widget, MyBaseWidget
from qrogue.graphics.widgets.my_widgets import SelectionWidget, CircuitWidget, MapWidget, SimpleWidget, HudWidget, \
    OutputStateVectorWidget, CircuitMatrixWidget, TargetStateVectorWidget, InputStateVectorWidget


class MyWidgetSet(WidgetSet, Renderable, ABC):
    """
    Class that handles different sets of widgets so we can easily switch between different screens.
    """

    @staticmethod
    def create_hud_row(widget_set: "MyWidgetSet") -> HudWidget:
        hud = widget_set.add_block_label('HUD', 0, 0, row_span=UIConfig.HUD_HEIGHT, column_span=UIConfig.WINDOW_WIDTH,
                                         center=False)
        hud.toggle_border()
        return HudWidget(hud)

    BACK_STRING = "-Back-"

    def __init__(self, logger, root: py_cui.PyCUI, base_render_callback: Callable[[List[Renderable]], None]):
        super().__init__(UIConfig.WINDOW_HEIGHT, UIConfig.WINDOW_WIDTH, logger, root)
        self.__base_render = base_render_callback
        self.__progress = 0

    @property
    def _progress(self) -> int:
        return self.__progress

    def add_block_label(self, title, row, column, row_span=1, column_span=1, padx=1, pady=0, center=True)\
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
        row_span : int
            The number of rows to span across
        column_span : int
            the number of columns to span across
        padx : int
            number of padding characters in the x direction
        pady : int
            number of padding characters in the y direction
        center : bool
            flag to tell label to be centered or left-aligned.

        Returns
        -------
        new_widget : MyBaseWidget
            A reference to the created widget object.
        """
        wid = 'Widget{}'.format(len(self._widgets.keys()))
        new_widget = MyBaseWidget(wid, title, self._grid, row, column, row_span, column_span, padx, pady, center,
                                  self._logger)
        self._widgets[wid] = new_widget
        self._logger.info('Adding widget {} w/ ID {} of type {}'.format(title, id, str(type(new_widget))))
        return new_widget

    def update_story_progress(self, progress: int):
        self.__progress = progress
        # globally update HUD based on the progress
        HudConfig.ShowMapName = True
        HudConfig.ShowKeys = True
        HudConfig.ShowEnergy = Ach.check_unlocks(Unlocks.ShowEnergy, progress)

    def render(self) -> None:
        self.__base_render(self.get_widget_list())

    @abstractmethod
    def get_widget_list(self) -> List[Widget]:
        pass

    @abstractmethod
    def get_main_widget(self) -> WidgetWrapper:
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
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 quick_start_callback: Callable[[], None], start_playing_callback: Callable[[], None],
                 stop_callback: Callable[[], None], choose_simulation_callback: Callable[[], None]):
        self.__seed = 0
        self.__quick_start = quick_start_callback
        self.__start_playing = start_playing_callback
        self.__stop = stop_callback
        self.__choose_simulation = choose_simulation_callback
        super().__init__(logger, root, render)

        width = UIConfig.WINDOW_WIDTH - UIConfig.ASCII_ART_WIDTH
        selection = self.add_block_label("", UIConfig.MAIN_MENU_ROW, 0, row_span=UIConfig.MAIN_MENU_HEIGHT,
                                         column_span=width, center=True)
        self.__selection = SelectionWidget(selection, controls, 1)
        self.__update_selection()

        show_controls = self.add_block_label("Show Controls", UIConfig.WINDOW_HEIGHT-2, 0, row_span=2,
                                             column_span=width, center=False)
        self.__show_controls = SimpleWidget(show_controls)
        self.__show_controls.set_data("Select with WASD\nConfirm selection with Space or Enter")

        title = self.add_block_label("Ascii Art", 0, width, row_span=UIConfig.WINDOW_HEIGHT-1,
                                     column_span=UIConfig.ASCII_ART_WIDTH, center=True)
        self.__title = SimpleWidget(title)
        self.__title.set_data(_ascii_art)

        seed = self.add_block_label("Seed", UIConfig.WINDOW_HEIGHT-1, width, row_span=1,
                                    column_span=UIConfig.ASCII_ART_WIDTH, center=True)
        self.__seed_widget = SimpleWidget(seed)

        self.__selection.widget.add_key_command(controls.action, self.__selection.use)

    def __update_selection(self):
        choices = []
        callbacks = []
        if Ach.check_unlocks(Unlocks.MainMenuPlay, self._progress):
            choices.append("CONTINUE\n")
            callbacks.append(self.__quick_start)
            choices.append("PLAY\n")
            callbacks.append(self.__start_playing)

            if Config.debugging():  # add simulator option
                choices.append("SIMULATOR\n")
                callbacks.append(self.__choose_simulation)

        elif Ach.check_unlocks(Unlocks.MainMenuContinue, self._progress):
            choices.append("CONTINUE\n")
            callbacks.append(self.__quick_start)

        else:
            choices.append("START YOUR JOURNEY\n")
            callbacks.append(self.__start_playing)

        choices += ["OPTIONS\n", "EXIT\n"]  # for more space between the rows we add "\n"
        callbacks += [self.__options, self.__stop]
        self.__selection.set_data(data=(choices, callbacks))

    def new_seed(self) -> None:
        self.__seed = RandomManager.instance().get_seed(msg="MenuWS.new_seed()")
        self.__seed_widget.set_data(f"Seed: {self.__seed}")
        self.__seed_widget.render()

    def update_story_progress(self, progress: int):
        super(MenuWidgetSet, self).update_story_progress(progress)
        self.__update_selection()

    def set_data(self, new_seed: int):
        self.__seed = new_seed
        RandomManager.force_seed(new_seed)
        self.__seed_widget.set_data(f"Seed: {self.__seed}")
        #self.__seed_widget.render()

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__selection,
            self.__show_controls,
            self.__title,
            self.__seed_widget,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__selection.widget

    def reset(self) -> None:
        self.__selection.render_reset()

    def __options(self) -> None:
        Popup.generic_info("Gameplay Config", GameplayConfig.to_file_text())


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
                 continue_callback: Callable[[], None], save_callback: Callable[[], Tuple[bool, CommonPopups]],
                 exit_run_callback: Callable[[], None]):
        super().__init__(logger, root, render)
        self.__continue_callback = continue_callback
        self.__save_callback = save_callback
        self.__exit_run = exit_run_callback
        self.__achievement_manager = None

        self.__hud = MyWidgetSet.create_hud_row(self)

        choices = self.add_block_label('Choices', UIConfig.HUD_HEIGHT, 0,
                                       row_span=UIConfig.NON_HUD_HEIGHT,
                                       column_span=UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__choices = SelectionWidget(choices, controls, stay_selected=True)
        self.__choices.set_data(data=(
            ["Continue", "Save", "Manual", "Achievements", "Options", "Exit"],
            [self.__continue, self.__save, self.__help, self.__achievements, self.__options, self.__exit]
        ))

        details = self.add_block_label('Details', UIConfig.HUD_HEIGHT, UIConfig.PAUSE_CHOICES_WIDTH,
                                       row_span=UIConfig.WINDOW_HEIGHT-UIConfig.HUD_HEIGHT,
                                       column_span=UIConfig.WINDOW_WIDTH-UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__details = SelectionWidget(details, controls, is_second=True)

        # add action key commands
        def use_choices():
            if self.__choices.use():
                Widget.move_focus(self.__details, self)
                self.__choices.render()
                self.__details.render()
        self.__choices.widget.add_key_command(controls.action, use_choices)

        def use_details():
            if self.__details.use():
                Widget.move_focus(self.__choices, self)
                self.__details.render_reset()
                self.render()
        self.__details.widget.add_key_command(controls.action, use_details)

    def __continue(self) -> bool:
        self.__continue_callback()
        return False

    def __save(self) -> bool:
        _, common_popup = self.__save_callback()
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
            Popup.generic_info(f"{PauseMenuWidgetSet.__HELP_TEXTS[0][index]}",
                               PauseMenuWidgetSet.__HELP_TEXTS[1][index])
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

    def get_main_widget(self) -> WidgetWrapper:
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
        super().__init__(logger, root, render)

        robot_selection = self.add_block_label('Robot Selection', 0, 0, row_span=UIConfig.WINDOW_HEIGHT, center=False)
        self.__robot_selection = SelectionWidget(robot_selection, controls, stay_selected=True)
        self.__robot_selection.set_data((
            [robot.name for robot in self.__available_robots] + [MyWidgetSet.BACK_STRING],
            [self.__details]
        ))

        robot_details = self.add_block_label('Robot Details', 0, 1, 3, 4, center=True)
        self.__robot_info = SimpleWidget(robot_details)

        available_upgrades = self.add_block_label('Upgrades', 4, 1, 2, 2, center=True)
        self.__available_upgrades = SelectionWidget(available_upgrades, controls, 4, is_second=True,
                                                    stay_selected=False)

        # init action key commands
        def use_selection():
            if self.__robot_selection.use():
                Widget.move_focus(self.__available_upgrades, self)
                self.__robot_selection.render()
                self.__available_upgrades.render()
        self.__robot_selection.widget.add_key_command(controls.action, use_selection)

        def use_upgrades():
            if self.__available_upgrades.use():
                Widget.move_focus(self.__robot_selection, self)
                self.render()
        self.__available_upgrades.widget.add_key_command(controls.action, use_upgrades)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__robot_selection,
            self.__robot_info,
            self.__available_upgrades,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__robot_selection.widget

    def reset(self) -> None:
        pass

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
        super().__init__(logger, root, render)
        self.__hud = MyWidgetSet.create_hud_row(self)

        map_widget = self.add_block_label('MAP', UIConfig.HUD_HEIGHT, 0, row_span=UIConfig.NON_HUD_HEIGHT,
                                          column_span=UIConfig.WINDOW_WIDTH, center=True)
        self.__map_widget = MapWidget(map_widget)
        ColorRules.apply_map_rules(self.__map_widget.widget)

        # init movement keys
        def move_up() -> None:
            if self.__map_widget.move(Direction.Up):
                self.render()

        def move_right() -> None:
            if self.__map_widget.move(Direction.Right):
                self.render()

        def move_down() -> None:
            if self.__map_widget.move(Direction.Down):
                self.render()

        def move_left() -> None:
            if self.__map_widget.move(Direction.Left):
                self.render()

        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveUp), move_up)
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveRight), move_right)
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveDown), move_down)
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveLeft), move_left)

    def get_main_widget(self) -> WidgetWrapper:
        return self.__map_widget.widget

    def set_data(self, map_: Map) -> None:
        controllable = map_.controllable_tile.controllable
        if isinstance(controllable, Robot):
            self.__hud.set_data((controllable, map_.name))
        else:
            self.__hud.reset_data()
        self.__map_widget.set_data(map_)
        # map_.start()  # we cannot start the map here because the widget_set has not been applied yet

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self.__map_widget
        ]

    def update_story_progress(self, progress: int):
        super(ExploreWidgetSet, self).update_story_progress(progress)
        self.__map_widget.try_to_start_map()

    def render(self) -> None:
        start = time.time()
        super(ExploreWidgetSet, self).render()
        duration = time.time() - start
        self.__hud.update_render_duration(duration)
        self.__hud.render()

    def reset(self) -> None:
        self.__map_widget.render_reset()


class NavigationWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None]):
        super().__init__(logger, root, base_render_callback)

        map_widget = self.add_block_label('MAP', UIConfig.HUD_HEIGHT, 0, row_span=UIConfig.NON_HUD_HEIGHT,
                                          column_span=UIConfig.WINDOW_WIDTH, center=True)
        self.__map_widget = MapWidget(map_widget)
        ColorRules.apply_navigation_rules(self.__map_widget.widget)

        # init movement keys
        def move_up() -> None:
            # MapManager.instance().move_on_cur_map(Direction.Up)
            if self.__map_widget.move(Direction.Up):
                self.render()

        def move_right() -> None:
            if self.__map_widget.move(Direction.Right):
                self.render()

        def move_down() -> None:
            if self.__map_widget.move(Direction.Down):
                self.render()

        def move_left() -> None:
            if self.__map_widget.move(Direction.Left):
                self.render()

        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveUp), move_up)
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveRight), move_right)
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveDown), move_down)
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveLeft), move_left)

    def get_main_widget(self) -> WidgetWrapper:
        return self.__map_widget.widget

    def set_data(self, map_: Map) -> None:
        self.__map_widget.set_data(map_)

    def get_widget_list(self) -> List[Widget]:
        return [self.__map_widget]

    def update_story_progress(self, progress: int):
        super(NavigationWidgetSet, self).update_story_progress(progress)
        self.__map_widget.try_to_start_map()

    def reset(self) -> None:
        self.__map_widget.render_reset()


class ReachTargetWidgetSet(MyWidgetSet, ABC):
    __CHOICE_COLUMNS = 2
    __DETAILS_COLUMNS = 3
    _DETAILS_INFO_THEN_EDIT = 0
    _DETAILS_INFO_THEN_HELP = 1
    _DETAILS_INFO_THEN_CHOICES = 2
    _DETAILS_EDIT = 3
    _DETAILS_HELP = 4

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[], None], flee_choice: str = "Flee"):
        super().__init__(logger, root, render)
        self.__flee_choice = flee_choice
        self._continue_exploration_callback = continue_exploration_callback
        self._robot = None
        self._target = None
        self.__controls = None
        self.__num_of_qubits = -1   # needs to be an illegal value because we definitely want to reposition all
        # dependent widgets for the first usage of this WidgetSet
        self._details_content = None

        posy = 0
        posx = 0
        row_span = UIConfig.stv_height(2)   # doesn't matter since we reposition the dependent widgets anyway
        matrix_width = UIConfig.WINDOW_WIDTH - (UIConfig.INPUT_STV_WIDTH + UIConfig.OUTPUT_STV_WIDTH +
                                                UIConfig.TARGET_STV_WIDTH + 1 * 3)  # width of the three signs
        circuit_height = UIConfig.NON_HUD_HEIGHT - row_span - UIConfig.DIALOG_HEIGHT

        self.__hud = MyWidgetSet.create_hud_row(self)
        posy += UIConfig.HUD_HEIGHT

        matrix = self.add_block_label('Circuit Matrix', posy, posx, row_span, column_span=matrix_width,
                                      center=True)
        self.__circuit_matrix = CircuitMatrixWidget(matrix)
        posx += matrix_width

        multiplication = self.add_block_label('Mul sign', posy, posx, row_span, column_span=1, center=True)
        self.__mul_widget = SimpleWidget(multiplication)
        posx += 1

        stv = self.add_block_label('Input StV', posy, posx, row_span, UIConfig.INPUT_STV_WIDTH, center=True)
        self.__input_stv = InputStateVectorWidget(stv, "In")
        posx += UIConfig.INPUT_STV_WIDTH

        result = self.add_block_label('Eq sign', posy, posx, row_span, column_span=1, center=True)
        self.__result_widget = SimpleWidget(result)
        posx += 1

        stv = self.add_block_label('Output StV', posy, posx, row_span, UIConfig.OUTPUT_STV_WIDTH, center=True)
        self.__stv_robot = OutputStateVectorWidget(stv, "Out")
        posx += UIConfig.OUTPUT_STV_WIDTH

        equality = self.add_block_label('Eq sign', posy, posx, row_span, column_span=1, center=True)
        self.__eq_widget = SimpleWidget(equality)
        posx += 1

        stv = self.add_block_label('Target StV', posy, posx, row_span, UIConfig.TARGET_STV_WIDTH, center=True)
        self.__stv_target = TargetStateVectorWidget(stv, "Target")
        posx += UIConfig.TARGET_STV_WIDTH
        posy += row_span

        circuit = self.add_block_label('Circuit', posy, 0, row_span=circuit_height,
                                       column_span=UIConfig.WINDOW_WIDTH, center=True)
        ColorRules.apply_circuit_rules(circuit)
        self.__circuit = CircuitWidget(circuit, controls)
        posy += circuit_height

        choices = self.add_block_label('Choices', posy, 0, row_span=UIConfig.WINDOW_HEIGHT - posy,
                                       column_span=UIConfig.PUZZLE_CHOICES_WIDTH, center=True)
        choices.toggle_border()
        self._choices = SelectionWidget(choices, controls, columns=self.__CHOICE_COLUMNS)
        self.__init_choices()

        details = self.add_block_label('Details', posy, UIConfig.PUZZLE_CHOICES_WIDTH,
                                       row_span=UIConfig.WINDOW_HEIGHT - posy,
                                       column_span=UIConfig.WINDOW_WIDTH - UIConfig.PUZZLE_CHOICES_WIDTH, center=True)
        details.toggle_border()
        details.activate_individual_coloring()  # TODO: current reward highlight version is not satisfying
        self._details = SelectionWidget(details, controls, columns=self.__DETAILS_COLUMNS, is_second=True)

        # init action key commands
        def use_choices():
            if self._choices.use():
                Widget.move_focus(self._details, self)
                self._choices.render()
                self._details.render()
        self._choices.widget.add_key_command(controls.action, use_choices)

        def use_details():
            if self._details.use():
                if self._details_content == self._DETAILS_INFO_THEN_CHOICES or \
                        self._details.index == self._details.num_of_choices - 1 and \
                        self._details_content in [self._DETAILS_EDIT, self._DETAILS_HELP]:
                    # last selection possibility in edit is "Back"
                    self.__details_back()
                elif self._details_content == self._DETAILS_INFO_THEN_EDIT:
                    self._details_content = self._DETAILS_EDIT
                    self.__choices_adapt()
                    self.render()
                elif self._details_content == self._DETAILS_INFO_THEN_HELP:
                    self._details_content = self._DETAILS_HELP
                    self.__choices_help()
                    self.render()
                else:
                    # else we selected a gate and we initiate the placing process
                    Widget.move_focus(self.__circuit, self)
        self._details.widget.add_key_command(controls.get_keys(Keys.Cancel), self.__details_back)
        self._details.widget.add_key_command(controls.action, use_details)

        def use_circuit():
            success, gate = self.__circuit.place_gate()
            if success:
                if self._details.validate_index():
                    if gate:
                        self._details.update_text(gate.selection_str(), self._details.index)
                    else:
                        self.__choices_adapt()
                self.__choices_commit()
                Widget.move_focus(self._details, self)
                self.render()
        self.__circuit.widget.add_key_command(controls.action, use_circuit)

    def __init_choices(self):
        texts = ["Edit"]
        callbacks = [self.__choices_adapt]

        if Ach.check_unlocks(Unlocks.CircuitReset, self._progress):
            texts.append("Reset")
            callbacks.append(self.__choices_reset)

        texts.append("Gate Guide")
        callbacks.append(self.__choices_help)

        if Ach.check_unlocks(Unlocks.PuzzleFlee, self._progress):
            texts.append(self.__flee_choice)
            callbacks.append(self._choices_flee)

        self._choices.set_data(data=(texts, callbacks))

    def __details_back(self):
        Widget.move_focus(self._choices, self)
        self._choices.validate_index()
        self._details.render_reset()
        self.render()

    @property
    def _sign_offset(self) -> str:
        return "\n" * (1 + 2 ** (self._robot.num_of_qubits - 1))  # 1 (headline) + middle of actual Stv


    def _reposition_widgets(self, num_of_qubits: int):
        if num_of_qubits != self.__num_of_qubits:
            self.__num_of_qubits = num_of_qubits

            # adapt the height of the widgets
            row_span = UIConfig.stv_height(num_of_qubits)
            self.__input_stv.widget.reposition(row_span=row_span)
            self.__mul_widget.widget.reposition(row_span=row_span)
            self.__circuit_matrix.widget.reposition(row_span=row_span)
            self.__result_widget.widget.reposition(row_span=row_span)
            self.__stv_robot.widget.reposition(row_span=row_span)
            self.__eq_widget.widget.reposition(row_span=row_span)
            self.__stv_target.widget.reposition(row_span=row_span)

            # for smaller qubit numbers we shrink the matrix and place everything closer to the middle
            if num_of_qubits < 3:
                shrinkage = 2   # magic number that turned out to give a good visual result
                # window width minus width of all StVs and signs, afterwards adapted by the small-qubit-shrinkage
                matrix_width = UIConfig.WINDOW_WIDTH - (UIConfig.INPUT_STV_WIDTH + UIConfig.OUTPUT_STV_WIDTH +
                                                        UIConfig.TARGET_STV_WIDTH + 1 * 3) - 2 * shrinkage
                posx = shrinkage
                self.__circuit_matrix.widget.reposition(column=posx, column_span=matrix_width)
                posx += matrix_width
                self.__mul_widget.widget.reposition(column=posx)
                posx += 1
                self.__input_stv.widget.reposition(column=posx)
                posx += UIConfig.INPUT_STV_WIDTH
                self.__result_widget.widget.reposition(column=posx)
                posx += 1
                self.__stv_robot.widget.reposition(column=posx)
                posx += UIConfig.OUTPUT_STV_WIDTH
                self.__eq_widget.widget.reposition(column=posx)
                posx += 1
                self.__stv_target.widget.reposition(column=posx)

                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span + shrinkage)
            elif num_of_qubits == 4:

                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span)
                self._choices.widget.reposition(row=UIConfig.WINDOW_HEIGHT - 1, row_span=1)
                self._details.widget.reposition(row=UIConfig.WINDOW_HEIGHT - 1, row_span=1)
            else:
                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span)

    def get_main_widget(self) -> WidgetWrapper:
        return self._choices.widget

    def update_story_progress(self, progress: int):
        super(ReachTargetWidgetSet, self).update_story_progress(progress)
        self.__init_choices()

    def set_data(self, robot: Robot, target: Target) -> None:
        self._robot = robot
        self._target = target

        self._reposition_widgets(robot.num_of_qubits)

        # from a code readers perspective the reset would make more sense in switch_to_fight() etc. but then we would
        # have to add it to multiple locations and have the risk of forgetting to add it for new ReachTargetWidgetSets
        if GameplayConfig.auto_reset_circuit():
            robot.reset_circuit()

        self.__hud.set_data((robot, None))  # don't overwrite the current map name
        self.__circuit.set_data(robot)

        self.__input_stv.set_data(StateVector.create_zero_state_vector(robot.num_of_qubits))
        self.__mul_widget.set_data(self._sign_offset + "x")
        self.__result_widget.set_data(self._sign_offset + "=")
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
        self._choices.render_reset()
        self._details.render_reset()

    def __update_calculation(self, target_reached: bool):
        diff_stv = self._target.state_vector.get_diff(self._robot.state_vector)

        self.__circuit_matrix.set_data(self._robot.circuit_matrix)
        self.__stv_robot.set_data((self._robot.state_vector, diff_stv), target_reached=target_reached)

        if diff_stv.is_zero:
            self.__eq_widget.set_data(self._sign_offset + "===")
        else:
            self.__eq_widget.set_data(self._sign_offset + "=/=")

    def __choices_adapt(self) -> bool:
        options = [instruction.selection_str() for instruction in self._robot.backpack]
        self._details.set_data(data=(
            SelectionWidget.wrap_in_hotkey_str(options) + ["Remove", MyWidgetSet.BACK_STRING],
            [self.__choose_instruction]
        ))
        self._details_content = self._DETAILS_EDIT
        return True

    def __choose_instruction(self, index: int) -> bool:
        if 0 <= index < self._robot.backpack.used_capacity:
            cur_instruction = self._robot.get_instruction(index)
            if cur_instruction is not None:
                if cur_instruction.is_used():
                    # move the instruction
                    pos = cur_instruction.position
                    qubit = cur_instruction.get_qubit_at(0)
                    self._robot.remove_instruction(cur_instruction)
                    self.__circuit.start_gate_placement(cur_instruction, pos, qubit)
                    self.render()
                    return True
                else:
                    if self._robot.is_space_left:
                        self.__circuit.start_gate_placement(cur_instruction)
                        self.render()
                        return True
                    else:
                        CommonPopups.NoCircuitSpace.show()
                self.render()
            return False
        else:
            if index == self._details.num_of_choices - 1:   # "Back" is always last
                return True     # go back to choices
            else:   # "Remove" was chosen
                if self._robot.has_empty_circuit:
                    CommonPopups.NoGatePlaced.show()
                    return False
                else:
                    self.__circuit.start_gate_placement(None)
                    self.render()
                    return True

    def __choices_commit(self):
        if self._target is None:
            Logger.instance().error("Error! Target is not set!")
            return False
        self._robot.update_statevector()
        success, reward = self._target.is_reached(self._robot.state_vector)
        self.__update_calculation(success)
        self.render()
        if success:
            def give_reward_and_continue():
                self._robot.give_collectible(reward)
                self._continue_exploration_callback()
            self._details.set_data(data=(
                [f"Congratulations! Your reward: {ColorConfig.highlight_object(reward.to_string())}"],
                [give_reward_and_continue]
            ))
            self._details_content = self._DETAILS_INFO_THEN_CHOICES
        else:
            self._on_commit_fail()

    def __choices_reset(self) -> bool:
        if self._robot.has_empty_circuit:
            self._details.set_data(data=(
                ["Nothing to reset"],
                [self._empty_callback]
            ))
            self._details_content = self._DETAILS_INFO_THEN_CHOICES
            return True
        else:
            self._robot.reset_circuit()
            self.__update_calculation(False)
            self.render()
            return False

    def __choices_help(self) -> bool:
        def show_help_popup(index: int = 0) -> bool:
            if 0 <= index < self._robot.backpack.used_capacity:
                instruction = self._robot.backpack.get(index)
                Popup.generic_info(instruction.name(), instruction.description())
                return False
            return True
        options = [instruction.name() for instruction in self._robot.backpack]
        self._details.set_data(data=(
            SelectionWidget.wrap_in_hotkey_str(options) + [MyWidgetSet.BACK_STRING],
            [show_help_popup]
        ))
        self._details_content = self._DETAILS_HELP
        return True

    @abstractmethod
    def _on_commit_fail(self) -> bool:
        pass

    @abstractmethod
    def _choices_flee(self) -> bool:
        pass

    def _empty_callback(self) -> None:
        pass


class TrainingsWidgetSet(ReachTargetWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 back_to_spaceship_callback: Callable[[], None]):
        super().__init__(controls, render, logger, root, back_to_spaceship_callback, "Done")

    def _on_commit_fail(self) -> bool:
        self._details_content = ReachTargetWidgetSet._DETAILS_EDIT
        return True

    def _choices_flee(self) -> bool:
        self._details.set_data(data=(
            ["You return to the Spaceship!"],
            [self._continue_exploration_callback]
        ))
        return True


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
        if not self._robot.game_over_check():
            self._details.set_data(data=(
                [f"That's not yet the correct solution."],
                [self._empty_callback]
            ))
        self._details_content = ReachTargetWidgetSet._DETAILS_INFO_THEN_EDIT
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
                    ["Failed to flee. Your Robot has no more energy and lost the connection."],
                    [self.__game_over_callback]
                ))
            else:
                self._details.set_data(data=(
                    ["Failed to flee. Your Robot lost some Energy."],
                    [self._empty_callback]
                ))
            self._details_content = ReachTargetWidgetSet._DETAILS_INFO_THEN_EDIT
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
                 continue_exploration_callback: Callable[[], None]):
        super().__init__(logger, root, render)
        self.__continue_exploration = continue_exploration_callback
        self.__robot = None
        self.__items = None

        self.__hud = MyWidgetSet.create_hud_row(self)

        inv_width = UIConfig.SHOP_INVENTORY_WIDTH
        inventory = self.add_block_label("Inventory", UIConfig.HUD_HEIGHT, 0, row_span=UIConfig.NON_HUD_HEIGHT,
                                         column_span=inv_width)
        self.__inventory = SelectionWidget(inventory, controls, stay_selected=True)

        details = self.add_block_label("Details", UIConfig.HUD_HEIGHT, inv_width, row_span=UIConfig.SHOP_DETAILS_HEIGHT,
                                       column_span=UIConfig.WINDOW_WIDTH - inv_width)
        self.__details = SimpleWidget(details)
        buy = self.add_block_label("Buy", UIConfig.HUD_HEIGHT + UIConfig.SHOP_DETAILS_HEIGHT, inv_width, row_span=1,
                                   column_span=UIConfig.WINDOW_WIDTH - inv_width)
        self.__buy = SelectionWidget(buy, controls, is_second=True)

        # init action key commands
        def use_inventory():
            if self.__inventory.use():
                Widget.move_focus(self.__buy, self)
                self.render()
        self.__inventory.widget.add_key_command(controls.action, use_inventory)

        def use_buy():
            if self.__buy.use():
                Widget.move_focus(self.__inventory, self)
                self.__inventory.validate_index()
                self.__details.render_reset()
                self.__buy.render_reset()
                self.render()
        self.__buy.widget.add_key_command(controls.action, use_buy)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self.__inventory,
            self.__details,
            self.__buy,
        ]

    def get_main_widget(self) -> WidgetWrapper:
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
