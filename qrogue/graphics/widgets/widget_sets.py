import threading
from abc import abstractmethod, ABC
from threading import Timer
from typing import List, Callable, Optional, Tuple, Any, Union

import py_cui
from py_cui.widget_set import WidgetSet

from qrogue.game.logic.actors import Enemy, Riddle, Challenge, Boss, Robot, BaseBot
from qrogue.game.logic.actors.puzzles import Target
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Collectible, instruction as gates, Instruction, InstructionManager, \
    CollectibleType
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.graphics.popups import Popup
from qrogue.graphics.rendering import ColorRules
from qrogue.graphics.widget_base import WidgetWrapper
from qrogue.graphics.widgets import Renderable, Widget, MyBaseWidget
from qrogue.graphics.widgets.my_widgets import SelectionWidget, CircuitWidget, MapWidget, SimpleWidget, HudWidget, \
    OutputStateVectorWidget, CircuitMatrixWidget, TargetStateVectorWidget, InputStateVectorWidget, MyMultiWidget, \
    HistoricWrapperWidget
from qrogue.util import CommonPopups, Config, Controls, GameplayConfig, HelpText, Logger, PathConfig, \
    Keys, UIConfig, ColorConfig, Options, PuzzleConfig, ScoreConfig, \
    get_filtered_help_texts, CommonQuestions, MapConfig, PyCuiConfig, ColorCode, split_text, MyRandom, \
    LevelInfo, CommonInfos, LevelData, StvDifficulty, GateType, RandomManager
from qrogue.util.achievements import Unlocks
from qrogue.util.util_functions import enum_string, cur_datetime, time_diff, open_folder


class MyWidgetSet(WidgetSet, Renderable, ABC):
    """
    Class that handles different sets of widgets, so we can easily switch between different screens.
    """

    class _SelectedGate:
        """
        Wrapper-class to easily handle selection of gates in widget sets.
        """

        def __init__(self, gate_type: GateType, is_selected: bool = False):
            self.__gate_type = gate_type
            self.__is_selected = is_selected
            self.__temp_is_selected = is_selected

        @property
        def is_selected(self) -> bool:
            return self.__is_selected

        @property
        def gate_type(self) -> GateType:
            return self.__gate_type

        @property
        def name(self) -> str:
            return self.__gate_type.name

        def invert_selection(self):
            self.__temp_is_selected = not self.__temp_is_selected

        def select(self, auto_commit: bool = False) -> bool:
            """
            Returns whether this call changed the internal state or not.

            :param auto_commit: whether
            :return: True if __is_selected was changed, False otherwise
            """
            # ret_val is False if temp_is_selected is already selected, and hence, nothing changed
            ret_val = not self.__temp_is_selected
            self.__temp_is_selected = True  # set value to True (might have been True before)
            if auto_commit:
                self.commit()
            # we don't care if is_selected changed (just if temp_is_selected did) so ignore return value of commit()
            return ret_val

        def commit(self) -> bool:
            """
            Returns whether this call changed the internal state or not.

            :return: True if __is_selected was changed, False otherwise
            """
            if self.__is_selected == self.__temp_is_selected:
                return False
            self.__is_selected = self.__temp_is_selected
            return True

        def discard(self) -> bool:
            """
            Returns whether this call changed the internal state or not.

            :return: True if temp_is_selected was changed, False otherwise
            """
            if self.__temp_is_selected == self.__is_selected:
                return False
            self.__temp_is_selected = self.__is_selected
            return True

        def reset(self):
            self.__is_selected = False
            self.__temp_is_selected = False

        def to_gate(self) -> Instruction:
            return InstructionManager.from_type(self.gate_type)

        def __str__(self) -> str:
            return f"[{'x' if self.__temp_is_selected else ' '}] {self.name}"

    @staticmethod
    def create_hud_row(widget_set: "MyWidgetSet") -> HudWidget:
        hud = widget_set.add_block_label('HUD', 0, 0, row_span=UIConfig.HUD_HEIGHT, column_span=UIConfig.HUD_WIDTH,
                                         center=False)
        hud.toggle_border()
        widgets = [hud]
        width = UIConfig.WINDOW_WIDTH - UIConfig.HUD_WIDTH

        if Config.debugging():
            width -= 1  # we need space for frame count

        situational_hud = widget_set.add_block_label('Situational', 0, UIConfig.HUD_WIDTH, row_span=UIConfig.HUD_HEIGHT,
                                                     column_span=width, center=False)
        situational_hud.toggle_border()
        widgets.append(situational_hud)

        if Config.debugging():
            frame_count = widget_set.add_block_label('Frame count', 0, UIConfig.WINDOW_WIDTH - 1,
                                                     row_span=UIConfig.HUD_HEIGHT, column_span=1, center=False)
            widgets.append(frame_count)

        return HudWidget(MyMultiWidget(widgets))

    BACK_STRING = "-Back-"

    def __init__(self, logger, root: py_cui.PyCUI, base_render_callback: Callable[[List[Renderable]], None]):
        super().__init__(UIConfig.WINDOW_HEIGHT, UIConfig.WINDOW_WIDTH, logger, root)
        self.__base_render = base_render_callback

    def add_block_label(self, title, row, column, row_span=1, column_span=1, padx=1, pady=0, center=True) \
            -> MyBaseWidget:
        """Function that adds a new block label to the CUI grid

        Parameters
        ----------
        title : str
            The title of the block label
        row : int
            The row value, from the top-down
        column : int
            The column value from the top-down
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

    def add_block_label_by_dimension(self, title: str, dimensions: UIConfig.Dimensions, center: bool = True) \
            -> MyBaseWidget:
        return self.add_block_label(title, center=center,
                                    row=dimensions.margin_top, column=dimensions.margin_left,
                                    row_span=dimensions.height, column_span=dimensions.width,
                                    padx=dimensions.pad_x, pady=dimensions.pad_y)

    def add_key_command(self, keys: List[int], command: Callable[[], Any], add_to_widgets: bool = False,
                        overwrite: bool = True, overwrite_widgets: Optional[bool] = None) -> Any:
        if overwrite_widgets is None:
            overwrite_widgets = overwrite
        for key in keys:
            if overwrite or key not in self._keybindings:
                super(MyWidgetSet, self).add_key_command(key, command)
        if add_to_widgets:
            for widget in self.get_widget_list():
                widget.widget.add_key_command(keys, command, overwrite_widgets)

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


class MenuWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 quick_start_callback: Callable[[], None], start_playing_callback: Callable[[], None],
                 start_expedition_callback: Callable[[], None], stop_callback: Callable[[], None],
                 show_screen_check_callback: Callable[[], None], show_level_select_callback: Callable[[], None],
                 show_workbench_callback: Callable[[], None],
                 check_unlocks_callback: Callable[[Union[str, Unlocks]], bool],
                 save_callback: Callable[[], Tuple[bool, CommonInfos]]):
        self.__seed = 0
        self.__quick_start_callback = quick_start_callback
        self.__start_playing_callback = start_playing_callback
        self.__start_expedition_callback = start_expedition_callback
        self.__stop_callback = stop_callback
        self.__show_screen_check_callback = show_screen_check_callback
        self.__show_level_select_callback = show_level_select_callback
        self.__show_workbench_callback = show_workbench_callback
        self.__check_unlocks = check_unlocks_callback
        self.__save_game = save_callback
        super().__init__(logger, root, render)

        width = UIConfig.WINDOW_WIDTH - UIConfig.ASCII_ART_WIDTH
        selection = self.add_block_label("", UIConfig.MAIN_MENU_ROW, 0, row_span=UIConfig.MAIN_MENU_HEIGHT,
                                         column_span=width, center=True)
        self.__selection = SelectionWidget(selection, controls)
        self.__update_selection()

        show_controls = self.add_block_label("Show Controls", UIConfig.WINDOW_HEIGHT - 2, 0, row_span=2,
                                             column_span=width, center=False)
        self.__show_controls = SimpleWidget(show_controls)
        self.__show_controls.set_data("Select with WASD\nConfirm selection with Space or Enter")

        title = self.add_block_label("Ascii Art", 0, width, row_span=UIConfig.WINDOW_HEIGHT - 1,
                                     column_span=UIConfig.ASCII_ART_WIDTH, center=True)
        self.__title = SimpleWidget(title)
        self.__title.set_data(Config.ascii_art())

        seed = self.add_block_label("Seed", UIConfig.WINDOW_HEIGHT - 1, width, row_span=1,
                                    column_span=UIConfig.ASCII_ART_WIDTH, center=True)
        self.__seed_widget = SimpleWidget(seed)

        self.__selection.widget.add_key_command(controls.action, self.__selection.use)

        self.__selection.widget.add_key_command(controls.get_keys(Keys.Pause), self.__qrogue_console)

    @property
    def seed(self) -> int:
        return self.__seed  # used to test whether the simulation needs to set the MenuWidgetSet's seed

    def __save(self) -> bool:
        _, common_info = self.__save_game()
        common_info.show()
        return False

    def __qrogue_console(self):
        def open_user_data(answer: int):
            if answer == 0:
                try:
                    open_folder(PathConfig.user_data_path())
                except Exception as ex:
                    Popup.error(f"Failed to open folder at {PathConfig.user_data_path()}: {ex}")

        CommonQuestions.OpenUserDataFolder.ask(open_user_data)

    def __update_selection(self):
        choices = []
        callbacks = []
        if self.__check_unlocks(Unlocks.MainMenuContinue):
            choices.append("CONTINUE JOURNEY\n")
            callbacks.append(self.__quick_start_callback)

        else:
            choices.append("START YOUR JOURNEY\n")
            callbacks.append(self.__start_playing_callback)

        if self.__check_unlocks(Unlocks.LevelSelection):
            choices.append("SELECT LEVEL\n")
            callbacks.append(self.__show_level_select_callback)

        if True or self.__check_unlocks(Unlocks.Workbench):
            choices.append("WORKBENCH\n")
            callbacks.append(self.__show_workbench_callback)

        # choices.append("START AN EXPEDITION\n")
        # callbacks.append(self.__start_expedition)

        choices.append("SCREEN CHECK\n")
        callbacks.append(self.__show_screen_check_callback)

        choices.append("SAVE\n")
        callbacks.append(self.__save)

        # choices.append("OPTIONS\n")  # for more space between the rows we add "\n"
        # callbacks.append(self.__options)
        choices.append("EXIT\n")
        callbacks.append(self.__stop_callback)
        self.__selection.set_data(data=(choices, callbacks))

    def set_data(self, new_seed: int):
        self.__update_selection()
        self.__seed = new_seed
        self.__seed_widget.set_data(f"Seed: {self.__seed}")
        # self.__seed_widget.render()

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


class LevelSelectWidgetSet(MyWidgetSet):
    __SEED_HEADER = "Seed: "
    __LEVEL_HEADER = "Level: "
    __CUSTOM_MAP_CODE = "custom"
    __GATE_CONFIRM = "confirm"
    __GATE_CANCEL = "cancel"

    def __init__(self, controls: Controls, logger: Logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None], rm: MyRandom,
                 show_input_popup_callback: Callable[[str, int, Callable[[str], None]], None],
                 get_available_levels_callback: Callable[[], List[LevelData]],
                 switch_to_menu_callback: Callable[[], None],
                 start_level_callback: Callable[[str, Optional[int], Optional[List[Instruction]]], None],
                 get_expedition_progress_callback: Callable[[], int],
                 get_available_gates_callback: Callable[[], List[GateType]]):
        """
        :param get_available_levels_callback: a Callable that returns a List of LevelData of all levels that can be
            played (i.e., were completed before)
        """
        super().__init__(logger, root, base_render_callback)
        # select seed
        # select level (or choose Expedition)
        # select starting gates
        # start
        # back to menu
        self.__rm = RandomManager.create_new(rm.get_seed("initial seed for LevelSelectWidgetSet.__rm"))
        self.__show_input_popup = show_input_popup_callback
        self.__get_available_levels = get_available_levels_callback
        self.__start_level = start_level_callback
        self.__get_expedition_progress = get_expedition_progress_callback
        self.__get_available_gates = get_available_gates_callback

        self.__seed = None
        self.__level: Optional[str] = None
        self.__selected_gates: List[LevelSelectWidgetSet._SelectedGate] = []
        self.__has_custom_gates = False
        self.reinit()

        row, col = 1, 4
        col_span = 2
        summary_seed = self.add_block_label('Seed', row, col, column_span=col_span, center=False)
        ColorRules.apply_level_selection_seed_rules(summary_seed)
        self.__summary_seed = SimpleWidget(summary_seed, f"{LevelSelectWidgetSet.__SEED_HEADER}???")
        col += col_span
        summary_level = self.add_block_label('Level', row, col, column_span=UIConfig.WINDOW_WIDTH - col, center=False)
        ColorRules.apply_level_selection_level_rules(summary_level)
        self.__summary_level = SimpleWidget(summary_level, f"{LevelSelectWidgetSet.__LEVEL_HEADER}???")
        self.__summary_level.render()

        row, col = UIConfig.LEVEL_SELECT_MAIN_Y, UIConfig.LEVEL_SELECT_MAIN_X
        row_span, col_span = UIConfig.LEVEL_SELECT_MAIN_HEIGHT, UIConfig.LEVEL_SELECT_CHOICES_WIDTH

        select = self.add_block_label('Select', row, col, row_span=row_span, column_span=col_span, center=False)
        self.__choices = SelectionWidget(select, controls, stay_selected=True)
        self.__choices.set_data([
            ("Select Level", self.__select_level),
            ("Change Gates", self.__choose_gates),
            ("Set Seed", self.__set_seed),
            ("Start Playing", self.__play_level),
            ("Back to Menu", switch_to_menu_callback),
            # todo: add "Set Difficulty" for more fine-grained difficulty settings and open popup if player tries to open it for a level
        ])
        col += col_span

        col_span = UIConfig.LEVEL_SELECT_DETAILS_WIDTH
        details = self.add_block_label('Details', row, col, row_span=row_span, column_span=col_span, center=False)
        self.__details = SelectionWidget(details, controls, is_second=True)
        col += col_span

        highscores = self.add_block_label('Highscores', row, col, row_span=row_span, column_span=1, center=False)
        self.__highscores = SimpleWidget(highscores)
        col += 1
        durations = self.add_block_label('Durations', row, col, row_span=row_span, column_span=1, center=False)
        self.__durations = SimpleWidget(durations)
        col += 1

        def use_choices():
            if self.__choices.use():
                Widget.move_focus(self.__details, self)
                self.render()
        self.__choices.widget.add_key_command(controls.action, use_choices)

        def use_details():
            if self.__details.use():
                Widget.move_focus(self.__choices, self)
                self.__details.render_reset()
                self.__highscores.render_reset()
                self.__durations.render_reset()
                self.render()
        self.__details.widget.add_key_command(controls.action, use_details)

        self.__summary_seed.set_data(f"Seed: {'???' if self.__seed is None else str(self.__seed)}")

    def reinit(self):
        self.__seed = None
        self.__level = None
        self.__selected_gates = [LevelSelectWidgetSet._SelectedGate(gate) for gate in self.__get_available_gates()]
        self.__has_custom_gates = False

    def __set_seed(self) -> bool:
        def set_seed(text: str):
            try:
                seed = int(text)
                self.__seed = seed
                self.__summary_seed.set_data(f"{LevelSelectWidgetSet.__SEED_HEADER}{seed}")
                self.render()

            except ValueError:
                Popup.error(f"\"{text}\" is not a valid seed. \nPlease input a positive integer!", log_error=False)

        self.__show_input_popup("Input Seed", ColorConfig.SEED_INPUT_POPUP_COLOR, set_seed)
        return False

    def __is_level_completed(self, level_name: str) -> bool:
        Config.check_reachability("LevelSelectWidgetSet.__is_level_completed()")
        for level in self.__get_available_levels():
            if level.name == self.__level:
                return False
            if level.name == level_name:
                return True
        return False

    def __set_standard_gates(self, internal_level_name: Optional[str] = None):
        if internal_level_name is None:
            internal_level_name = self.__level

        self.__has_custom_gates = False
        gate_type_list = LevelInfo.get_level_start_gates(internal_level_name)
        for sg in self.__selected_gates:
            if sg.gate_type in gate_type_list:
                # remove from list to handle multiple gates of the same type correctly
                gate_type_list.remove(sg.gate_type)
                # set the gate as selected (commit, so it's not just temporarily)
                sg.select(auto_commit=True)
            else:
                sg.reset()  # deselects sg

    def __select_level(self) -> bool:
        # retrieve data of all available levels for displaying and loading
        levels_data = self.__get_available_levels()
        internal_names, display_names = [], []
        highscores, durations = [], []
        for level_data in levels_data:
            if not level_data.is_level: continue    # skip expeditions (they are added separately) and other non-levels

            internal_names.append(level_data.name)
            display_name = LevelInfo.convert_to_display_name(level_data.name, True)
            if display_name is None:
                Logger.instance().warn(f"No display name found for \"{level_data.name}\".", from_pycui=False)
                display_names.append(f"\"{level_data.name}\"")
            else:
                display_names.append(display_name)
            highscores.append(f"#{level_data.total_score}")
            durations.append(f"{level_data.duration}s")

        # add expeditions
        # the next difficulty is also unlocked from the get go, so you can always challenge yourself to harder puzzles
        max_expedition_level = min(LevelInfo.get_expedition_difficulty(self.__get_expedition_progress()) + 1,
                                   StvDifficulty.max_difficulty_level())
        for i in range(max_expedition_level + 1):   # +1 because max_expedition_level should be included
            diff_code = str(i + StvDifficulty.min_difficulty_level())
            display_names.append(f"Expedition {diff_code}")
            internal_names.append(f"{MapConfig.expedition_map_prefix()}{diff_code}")

        if Config.debugging():
            # add custom option so the player can use custom difficulty or load levels otherwise
            display_names.append("+Select via Map Code+")
            internal_names.append(LevelSelectWidgetSet.__CUSTOM_MAP_CODE)

        # add cancel to stop selecting a level
        display_names.append("-Cancel-")
        internal_names.append(None)  # the selection-object to easily identify cancel

        def overwrite(index: int):
            if index == 0:  # Yes, reset custom gate selection to level specific selection
                self.__set_standard_gates()
            # else:         # No, keep custom selection (i.e., do nothing)
            Widget.move_focus(self.__choices, self)    # move focus manually since this is called from a (focused) popup

        def set_level(index: int) -> bool:
            if self.__details.selected_object is None:
                return True  # "Cancel" was selected

            self.__level = self.__details.selected_object
            if self.__details.selected_object == LevelSelectWidgetSet.__CUSTOM_MAP_CODE:
                def callback(map_code: str):
                    self.__summary_level.set_data(f"Map Code: {map_code}")
                    self.__level = map_code
                    self.render()
                    Widget.move_focus(self.__choices, self)
                self.__show_input_popup("Enter map code", ColorConfig.LEVEL_SELECTION_INPUT_MAP_CODE, callback)
            elif self.__details.selected_object.startswith(MapConfig.expedition_map_prefix()):
                self.__summary_level.set_data(f"{LevelSelectWidgetSet.__LEVEL_HEADER}{display_names[index]} ")
                if not self.__has_custom_gates:
                    # reset selection so a random subset is chosen instead of simply the ones from the previously
                    # selected level
                    for sg in self.__selected_gates: sg.reset()
            else:
                self.__summary_level.set_data(f"{LevelSelectWidgetSet.__LEVEL_HEADER}{display_names[index]} "
                                              f"({highscores[index]}, {durations[index]})")
                if self.__has_custom_gates:
                    CommonQuestions.OverwriteCustomGates.ask(overwrite)
                else:
                    self.__set_standard_gates()
            return True

        self.__details.set_data(((display_names, internal_names), set_level))
        self.__highscores.set_data("\n".join(highscores))
        self.__durations.set_data("\n".join(durations))
        return True

    def __choose_gates(self) -> bool:
        def add_gate(index: int) -> bool:
            if self.__details.selected_object is LevelSelectWidgetSet.__GATE_CANCEL:
                for gate in self.__selected_gates: gate.discard()
                return True     # "Cancel" was selected
            if self.__details.selected_object is LevelSelectWidgetSet.__GATE_CONFIRM:
                ret_val = [gate.commit() for gate in self.__selected_gates]
                if sum(ret_val) > 0:    # at least one confirm() changed the state (i.e., returned True)
                    self.__has_custom_gates = True
                return True

            sel_gate: LevelSelectWidgetSet._SelectedGate = self.__details.selected_object
            sel_gate.invert_selection()

            self.__details.update_text(str(self.__details.selected_object), index)
            self.__details.render()
            return False

        # add all available gates plus meta options Confirm and Cancel
        names: List[str] = [str(gate) for gate in self.__selected_gates] + ["-Confirm-", "-Cancel-"]
        gate_objects: List[Union[LevelSelectWidgetSet._SelectedGate, str]] = \
            self.__selected_gates + [LevelSelectWidgetSet.__GATE_CONFIRM, LevelSelectWidgetSet.__GATE_CANCEL]
        self.__details.set_data(((names, gate_objects), add_gate))
        return True

    def __play_level(self) -> bool:
        if self.__level is None:
            Popup.error("No Level selected!", log_error=False)
            return False

        # filter and convert all selected gates
        available_gates = [sg.to_gate() for sg in self.__selected_gates if sg.is_selected]
        seed = self.__seed if self.__seed is not None else self.__rm.get_seed("LevelSelect play unspecified")
        self.__start_level(self.__level, seed, available_gates)
        return True

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__summary_seed,
            self.__summary_level,
            self.__choices,
            self.__details,
            self.__highscores,
            self.__durations,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__choices.widget

    def reset(self) -> None:
        self.__choices.render_reset()
        self.__details.render_reset()

        self.__level = None
        self.__summary_level.set_data(f"{LevelSelectWidgetSet.__LEVEL_HEADER}???")

        self.__seed = None
        self.__summary_seed.set_data(f"{LevelSelectWidgetSet.__SEED_HEADER}???")


class ScreenCheckWidgetSet(MyWidgetSet):
    __LEVEL = 0
    __PUZZLE = 1
    __POPUP = 2

    # content of the different modes
    # Note that Puzzle-mode cannot be statically created like the other modes because it's created by various widgets
    # just like the real UI for puzzle solving (@ReachTargetWidgetSet).

    @staticmethod
    def level_content() -> str:
        # prepare text to showcase an example level
        pseudo_level: List[List[str]] = [
            ["#" * MapConfig.room_width()] * MapConfig.map_width(),
            ["#" + " " * (MapConfig.room_width() - 2) + "#"] * MapConfig.map_width(),
            ["#" + " " * (MapConfig.room_width() - 2) + "#"] * MapConfig.map_width(),
            ["#" + " " * (MapConfig.room_width() - 2) + "#"] * MapConfig.map_width(),
            ["#" + " " * (MapConfig.room_width() - 2) + "#"] * MapConfig.map_width(),
            ["#" + " " * (MapConfig.room_width() - 2) + "#"] * MapConfig.map_width(),
            ["#" * MapConfig.room_width()] * MapConfig.map_width(),
        ]
        # room1: more or less random ensemble of all possible tiles
        # room2: tiles in contrast to obstacles and enemies
        # room3: relative empty, but realistic room
        # room4: ?
        # room5: all tile colors next to Qubot for reference
        # room6: relative full, but realistic room
        # room7: rows of all (frequently used) tile colors
        pseudo_level[1] = ["#9o87c#", "# sB  #", "#c   9#", "#     #", "# GQ. #", "#66 33#", "#12345#"]
        pseudo_level[2] = ["#oo6cc#", "# .o? #", "#  3  #", "#     #", "#  c  #", "# ooo #", "#QQQQQ#"]
        pseudo_level[3] = ["#12345#", "# o0o #", "#2    #", "#     #", "#   1 #", "#Qooo #", "#ckgkc#"]
        pseudo_level[4] = ["#0B?#!#", "#1coQ #", "# .  1#", "#     #", "#  BQ #", "#2ooo7#", "#ooooo#"]
        pseudo_level[5] = ["#s.Q G#", "#k1 7k#", "#ooooo#", "#     #", "#   o #", "#2 . 7#", "#.....#"]

        return "\n".join([" ".join(row) for row in pseudo_level])

    @staticmethod
    def popup_content() -> str:
        return f"Let's have a look at the different colors in popups like this to make sure they are " \
               f"distinguishable:\n" \
               f"- {ColorConfig.highlight_tile('tile')}: this refers to tiles in the game world\n" \
               f"             \"the green {ColorConfig.highlight_tile('G')} represents the goal\"\n" \
               f"- {ColorConfig.highlight_action('action')}: this is used to highlight certain actions you " \
               f"can perform\n" \
               f"             \"{ColorConfig.highlight_action('move')} to the next room\"\n" \
               f"- {ColorConfig.highlight_object('object')}: this shows important objects and concepts " \
               f"within the game\n" \
               f"             \"you found an {ColorConfig.highlight_object('XGate')}\"\n" \
               f"- {ColorConfig.highlight_word('word')}: this highlights various noteworthy words " \
               f"without a specific category\n" \
               f"             \"you need a {ColorConfig.highlight_word('new')} item to proceed\"\n" \
               f"- {ColorConfig.highlight_key('key')}: this informs you about the controls of the game\n" \
               f"             \"use {ColorConfig.highlight_key('Space')} to close a popup\""

    @staticmethod
    def _initial_description() -> str:
        return f"Select a topic on the left and confirm to see a corresponding " \
               f"{ColorConfig.highlight_word('description', invert=True)} here."

    @staticmethod
    def level_description() -> str:
        return f"You should see seven rooms next to each other. While the specific colors don't matter, it is " \
               f"important to be able to distinguish different elements of the game world (although they also differ " \
               f"in their character representation).\n" \
               f"- {ColorConfig.highlight_object('Pickups', True)} are designed to be " \
               f"{ColorConfig.highlight_word('blue', True)} lower-case characters like " \
               f"{ColorConfig.highlight_tile('s', True)}, {ColorConfig.highlight_tile('k', True)}, " \
               f"{ColorConfig.highlight_tile('c', True)} or {ColorConfig.highlight_tile('g', True)}.\n" \
               f"- Tiles containing {ColorConfig.highlight_object('Puzzles', True)} are meant to be " \
               f"{ColorConfig.highlight_word('red', True)} and are {ColorConfig.highlight_tile('digits', True)}, " \
               f"{ColorConfig.highlight_tile('!', True)}, {ColorConfig.highlight_tile('?', True)} and inverted " \
               f"{ColorConfig.highlight_tile('B', True)} for bosses.\n" \
               f"- The {ColorConfig.highlight_object('Goal', True)} " \
               f"{ColorConfig.highlight_tile('G', True)} of a level and the " \
               f"{ColorConfig.highlight_object('Player Character', True)} {ColorConfig.highlight_tile('Q', True)} " \
               f"are usually {ColorConfig.highlight_word('green', True)}.\n" \
               f"- Level-shaping tiles like {ColorConfig.highlight_tile('#', True)} and {ColorConfig.highlight_tile('o', True)} " \
               f"are {ColorConfig.highlight_word('white', True)} inverted\n" \
               f"- Lastly, simple {ColorConfig.highlight_word('white', True)} dots " \
               f"{ColorConfig.highlight_tile('.', True)} are messages that open Popups\n" \
               f"\n" \
               f"The last two elements are neutral to the player and, hence, not specifically highlighted (in fact, " \
               f"they share their color with normal text and UI elements), while the other three are important for " \
               f"gameplay and should therefore be highlighted."

    @staticmethod
    def puzzle_description(controls: Optional[Controls] = None) -> str:
        if controls is None:
            matrix_key = "M"
        else:
            matrix_key = controls.to_keyboard_string(Keys.MatrixPopup)
        return f"Here you can see an example of an advanced 3-qubit puzzle. Specifically, there is one matrix " \
               f"followed by three vertical vectors.\n" \
               f"Overall they should contain five different colors:\n" \
               f"- {ColorConfig.colorize(ColorCode.PUZZLE_HEADLINES, 'headlines')} of matrix and vectors " \
               f"(~Circuit Matrix~, ~In~, ~Out~, ~Target~)\n" \
               f"- {ColorConfig.colorize(ColorCode.PUZZLE_KET, '|000>')} to " \
               f"{ColorConfig.colorize(ColorCode.PUZZLE_KET, '|111>')} (called ket-notation) labeling columns and " \
               f"rows\n" \
               f"- first two entries of ~Out~, indicating " \
               f"{ColorConfig.colorize(ColorCode.PUZZLE_WRONG_AMPLITUDE, 'incorrect values')}\n" \
               f"- last six entries of ~Out~, indicating " \
               f"{ColorConfig.colorize(ColorCode.PUZZLE_CORRECT_AMPLITUDE, 'correct values')}\n" \
               f"- other matrix/vector entries are in default color (i.e., the same as non-highlighted UI " \
               f"elements)\n" \
               f"\n" \
               f"If you cannot see all eight rows or columns of the matrix, press " \
               f"{ColorConfig.highlight_key(matrix_key, invert=True)} to open a popup for suggested solutions."

    @staticmethod
    def popup_description() -> str:
        return f"In the middle of the screen an inverted (i.e., background is the normal text color and text has the " \
               f"color of normal background) rectangle should have popped up. It has a differently colored headline " \
               f"followed by text that describes the usage of different colors used inside such Popups. Furthermore, " \
               f"the bottom left should state \"scroll down\", while the bottom right indicates the number of rows " \
               f"you can scroll down until the end of the Popup's text is reached. These two bottom elements should " \
               f"also be highlighted (i.e., different from the colors used inside the Popup)."

    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None], switch_to_menu: Callable[[], None]):
        super().__init__(logger, root, base_render_callback)
        self.__mode = -1

        details_height = 4
        details_y = UIConfig.WINDOW_HEIGHT - details_height
        select_width = 3
        select_widget = self.add_block_label('Select', details_y, 0, row_span=details_height, column_span=select_width,
                                             center=True)
        self.__select_widget = SelectionWidget(select_widget, controls, stay_selected=True)
        self.__select_widget.set_data([
            ("Level", self.__show_level),
            ("Popup", self.__show_popup),
            ("Puzzle", self.__show_puzzle),
            ("Back", switch_to_menu),
        ])

        self.__setup_widgets()

        def use_select():
            if self.__select_widget.use():
                cur_dimensions = PyCuiConfig.get_dimensions()
                min_dimensions = PyCuiConfig.get_min_dimensions()
                if cur_dimensions < min_dimensions:
                    self.__hud.update_situational(f"Your window is TOO SMALL:    {cur_dimensions}\n"
                                                  f"Minimum required dimensions: {min_dimensions}")
                else:
                    self.__hud.update_situational(f"Your window's dimensions:    {cur_dimensions}\n"
                                                  f"Minimum required dimensions: {min_dimensions}")
                self.render()

        self.__select_widget.widget.add_key_command(controls.action, use_select)

        desc_widget = self.add_block_label('Desc', details_y, select_width, row_span=details_height,
                                           column_span=UIConfig.WINDOW_WIDTH - select_width - 1, center=False)
        desc_widget.activate_individual_coloring()
        self.__desc_widget = SimpleWidget(desc_widget, self._initial_description())

        def width_check():
            if self.__mode != ScreenCheckWidgetSet.__PUZZLE: return

            content_width = max([len(row) for row in self.__content_mat.widget.get_title().split("\n")])
            # the matrix needs approximately 42% of the width, which is the second element of dimensions
            providable_width = int(PyCuiConfig.get_dimensions()[1] * 0.42)
            if providable_width <= 0:
                Popup.generic_info("Dimension Unknown", "Failed to measure width of the window. Please check yourself "
                                                        "if the matrix is displayed as a whole or if some parts are "
                                                        "missing.")
            elif content_width > providable_width:
                Popup.generic_info("Dimension Error",
                                   f"Only {providable_width} characters available but {content_width} needed to "
                                   f"correctly display the matrix of a 3-qubit circuit!\n"
                                   f"You can either increase the size of your window, adapt font or press "
                                   f"{controls.to_keyboard_string(Keys.MatrixPopup)} to view the whole matrix in a "
                                   f"Popup.")
            else:
                Popup.generic_info("Dimension Fine", f"{providable_width} characters available and only {content_width}"
                                                     f" needed to display the matrix of a 3-qubit circuit")

        def matrix_popup():
            if self.__mode != ScreenCheckWidgetSet.__PUZZLE: return
            popup_text = \
                f"If you cannot see the matrix as a whole, you can try {ColorConfig.highlight_word('resizing')} or " \
                f"{ColorConfig.highlight_word('maximizing')} the window, as well as " \
                f"{ColorConfig.highlight_word('adapting')} the used {ColorConfig.highlight_word('font')} or font " \
                f"size (check your terminal's settings for that).\n" \
                f"In case this does not work or gives otherwise undesirable results, QRogue provides an " \
                f"{ColorConfig.highlight_word('explicit workaround')} by {ColorConfig.highlight_action('pressing')} " \
                f"{ColorConfig.highlight_key(controls.to_keyboard_string(Keys.MatrixPopup))} while solving a Puzzle " \
                f"to open a {ColorConfig.highlight_word('Popup')} that shows the whole matrix. An example of the " \
                f"3-qubit matrix shown behind this Popup is provided below (just scroll down).\n" \
                f"Furthermore, for fine-tuning, you can {ColorConfig.highlight_action('press')} " \
                f"{ColorConfig.highlight_key(controls.to_keyboard_string(Keys.Help))} after closing this " \
                f"Popup to open another one that tells you how much space is available to the matrix (based on your " \
                f"current settings) versus how much it actually needs.\n\n"
            Popup.show_matrix("Matrix Popup", self.__content_mat.widget.get_title(), prefix=popup_text)

        self.__select_widget.widget.add_key_command(controls.get_keys(Keys.Help), width_check)
        self.__select_widget.widget.add_key_command(controls.get_keys(Keys.MatrixPopup), matrix_popup)

    def __setup_widgets(self):
        # todo: show both 3-qubit and 2-qubit puzzles?
        # prepare puzzle
        # robot doesn't need a real game_over callback for screen checks, hence we can use an empty lambda
        robot = BaseBot(game_over_callback=lambda: None, num_of_qubits=3, gates=[])
        input_stv = gates.Instruction.compute_stv([gates.RZGate(1).setup([2])], 3)
        target_stv = gates.Instruction.compute_stv([gates.XGate().setup([0]), gates.RZGate(1.6).setup([0])], 3)
        enemy = Enemy(0, eid=0, target=target_stv, reward=None, input_=input_stv)

        robot.use_instruction(gates.RZGate(2.5).setup([0]), 0)
        robot.update_statevector(enemy.input_stv, use_energy=False, check_for_game_over=False)

        # below widget setup is mostly copied from ReachTargetWidgetSet since we want to mimic its layout
        posy = 0
        posx = 0
        row_span = UIConfig.stv_height(3)
        matrix_width = UIConfig.WINDOW_WIDTH - (UIConfig.INPUT_STV_WIDTH + UIConfig.OUTPUT_STV_WIDTH +
                                                UIConfig.TARGET_STV_WIDTH + 1 * 3)  # + width of the three signs

        # HUD
        self.__hud = MyWidgetSet.create_hud_row(self)
        self.__hud.set_data((robot, "HUD", "Situational HUD"))
        self.__hud.render()
        posy += UIConfig.HUD_HEIGHT

        # CIRCUIT MATRIX
        widget = self.add_block_label('Circuit Matrix', posy, posx, row_span, column_span=matrix_width, center=True)
        mat_circ = CircuitMatrixWidget(widget)
        mat_circ.set_data(robot.circuit_matrix)
        mat_circ.render()
        self.__text_mat = mat_circ.widget.get_title()
        posx += matrix_width

        # MULTIPLICATION
        widget = self.add_block_label('Mul sign', posy, posx, row_span, column_span=1, center=True)
        self.__w_mul = SimpleWidget(widget, "*")
        self.__w_mul.render()
        posx += 1

        # INPUT STV
        widget = self.add_block_label('Input StV', posy, posx, row_span, UIConfig.INPUT_STV_WIDTH, center=True)
        stv_in = InputStateVectorWidget(widget, "In")
        stv_in.set_data(enemy.input_stv)
        stv_in.render()
        self.__text_in = stv_in.widget.get_title()
        posx += UIConfig.INPUT_STV_WIDTH

        # EQUALITY
        widget = self.add_block_label('Eq sign', posy, posx, row_span, column_span=1, center=True)
        self.__w_res = SimpleWidget(widget, "=")
        self.__w_res.render()
        posx += 1

        # OUTPUT STV
        widget = self.add_block_label('Output StV', posy, posx, row_span, UIConfig.OUTPUT_STV_WIDTH, center=True)
        stv_out = OutputStateVectorWidget(widget, "Out")
        stv_out.set_data((robot.state_vector, enemy.state_vector.get_diff(robot.state_vector)))
        stv_out.render()
        self.__text_out = stv_out.widget.get_title()
        posx += UIConfig.OUTPUT_STV_WIDTH

        # EQUALITY CHECK
        widget = self.add_block_label('Eq sign', posy, posx, row_span, column_span=1, center=True)
        self.__w_eq = SimpleWidget(widget, "=/=")
        self.__w_eq.render()
        posx += 1

        # TARGET STV
        widget = self.add_block_label('Target StV', posy, posx, row_span, UIConfig.TARGET_STV_WIDTH, center=True)
        stv_target = TargetStateVectorWidget(widget, "Target")
        stv_target.set_data(enemy.state_vector)
        stv_target.render()
        self.__text_target = stv_target.widget.get_title()
        posx += UIConfig.TARGET_STV_WIDTH
        posy += row_span

        # ACTUAL WIDGETS
        self.__content_hud = self.__hud
        self.__content_mat = SimpleWidget(mat_circ.widget, "C1")
        self.__content_in = SimpleWidget(stv_in.widget, "C2")
        self.__content_out = SimpleWidget(stv_out.widget, "C3")
        self.__content_target = SimpleWidget(stv_target.widget, "C4")

    def __fit_description(self, description: str, padding: int = 0) -> str:
        width, _ = self.__desc_widget.widget.get_abs_size()
        # use width-2 because it seems as if PyCUI forces a one-character border on both sides
        # an experiment showed that a width of 104 can only display 102 characters
        content = split_text(description, width - 2, padding,
                             handle_error=lambda err: Logger.instance().error(err, show=False, from_pycui=False))
        return "\n".join(content)

    def __show_level(self):
        self.__mode = ScreenCheckWidgetSet.__LEVEL
        self.__content_mat.widget.reset_text_color_rules()
        ColorRules.apply_map_rules(self.__content_mat.widget)

        self.__desc_widget.set_data(self.__fit_description(self.level_description()))
        self.__content_mat.set_data(self.level_content())
        self.__content_in.set_data("")
        self.__content_out.set_data("")
        self.__content_target.set_data("")

    def __show_puzzle(self):
        self.__mode = ScreenCheckWidgetSet.__PUZZLE
        self.__content_mat.widget.reset_text_color_rules()
        ColorRules.apply_heading_rules(self.__content_mat.widget)
        ColorRules.apply_qubit_config_rules(self.__content_mat.widget)

        self.__desc_widget.set_data(self.__fit_description(self.puzzle_description()))
        self.__content_mat.set_data(self.__text_mat)
        self.__content_in.set_data(self.__text_in)
        self.__content_out.set_data(self.__text_out)
        self.__content_target.set_data(self.__text_target)

    def __show_popup(self):
        self.__mode = ScreenCheckWidgetSet.__POPUP
        self.__content_mat.widget.reset_text_color_rules()

        # clear all other texts
        self.__content_mat.set_data("")
        self.__content_in.set_data("")
        self.__content_out.set_data("")
        self.__content_target.set_data("")

        self.__desc_widget.set_data(self.__fit_description(self.popup_description()))
        Popup.generic_info("This headline usually indicates the Speaker", self.popup_content(), pos=Popup.Pos.Top)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__content_hud,
            self.__content_mat, self.__w_mul, self.__content_in, self.__w_res, self.__content_out, self.__w_eq,
            self.__content_target,

            self.__select_widget,
            self.__desc_widget,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__select_widget.widget

    def reset(self) -> None:
        self.__select_widget.render_reset()

        for widget in [self.__content_mat, self.__w_mul, self.__content_in, self.__w_res, self.__content_out,
                       self.__w_eq, self.__content_target, self.__desc_widget]:
            widget.render_reset()
        self.__desc_widget.set_data(self._initial_description())


class TransitionWidgetSet(MyWidgetSet):
    class TextScroll:
        __DEFAULT_TEXT_DELAY = 0.01  # 0 can lead to messed up render order, so we just use a very small number
        _SLOW = 1.0
        _RELAXED = 0.65
        _MEDIUM = 0.15
        _FAST = 0.05
        _HASTY = 0.01

        @staticmethod
        def slow(text: str, text_delay: float = 0, clear_previous: bool = False) -> "TransitionWidgetSet.TextScroll":
            char_pause = TransitionWidgetSet.TextScroll._SLOW
            return TransitionWidgetSet.TextScroll(text, char_pause, text_delay, clear_previous)

        @staticmethod
        def relaxed(text: str, text_delay: float = 0, clear_previous: bool = False) -> "TransitionWidgetSet.TextScroll":
            char_pause = TransitionWidgetSet.TextScroll._RELAXED
            return TransitionWidgetSet.TextScroll(text, char_pause, text_delay, clear_previous)

        @staticmethod
        def medium(text: str, text_delay: float = 0, clear_previous: bool = False) -> "TransitionWidgetSet.TextScroll":
            char_pause = TransitionWidgetSet.TextScroll._MEDIUM
            return TransitionWidgetSet.TextScroll(text, char_pause, text_delay, clear_previous)

        @staticmethod
        def fast(text: str, text_delay: float = 0, clear_previous: bool = False) -> "TransitionWidgetSet.TextScroll":
            char_pause = TransitionWidgetSet.TextScroll._FAST
            return TransitionWidgetSet.TextScroll(text, char_pause, text_delay, clear_previous)

        @staticmethod
        def hasty(text: str, text_delay: float = 0, clear_previous: bool = False) -> "TransitionWidgetSet.TextScroll":
            char_pause = TransitionWidgetSet.TextScroll._HASTY
            return TransitionWidgetSet.TextScroll(text, char_pause, text_delay, clear_previous)

        @staticmethod
        def instant(text: str, text_delay: float = 0, clear_previous: bool = False) -> "TransitionWidgetSet.TextScroll":
            return TransitionWidgetSet.TextScroll(text, 0, text_delay, clear_previous)

        def __init__(self, text: str, char_pause: float, text_delay: float = __DEFAULT_TEXT_DELAY,
                     clear_previous: bool = False):
            """

            :param text:
            :param char_pause: pause between rendering each character in seconds
            :param text_delay: delay for rendering different TextScrolls in seconds
            :param clear_previous:
            """
            assert len(text) > 0, "Avoid empty texts by defining a text_delay instead!"
            assert char_pause >= 0, "Negative char_pauses are not allowed!"
            assert text_delay >= 0, "Negative text_delays are not allowed!"

            self.__text = text
            self.__char_pause = char_pause
            self.__text_delay = text_delay
            self.__clear_prev = clear_previous
            self.__pos = 0

        @property
        def text_delay(self) -> float:
            if GameplayConfig.get_option_value(Options.auto_skip_text_animation):
                return self.__DEFAULT_TEXT_DELAY
            return self.__text_delay

        @property
        def char_pause(self) -> float:
            return self.__char_pause

        @property
        def clear_previous(self) -> bool:
            return self.__clear_prev

        @property
        def is_done(self) -> bool:
            return self.__pos >= len(self.__text)

        def next(self) -> Optional[str]:
            if self.is_done:
                return None
            elif self.__char_pause == 0:
                self.__pos = len(self.__text)
                return self.__text
            else:
                char = self.__text[self.__pos]
                self.__pos += 1
                return char

        def skip_to_end(self) -> str:
            if self.is_done:
                return ""
            else:
                text = self.__text[self.__pos:]
                self.__pos = len(self.__text)
                return text

        def __len__(self) -> int:
            return len(self.__text)

        def __str__(self) -> str:
            return self.__text

    def __init__(self, controls: Controls, logger, root: py_cui.PyCUI,
                 base_render_callback: Callable[[List[Renderable]], None],
                 set_refresh_timeout_callback: Callable[[int], None]):
        super().__init__(logger, root, base_render_callback)
        self.__set_refresh_timeout = lambda: set_refresh_timeout_callback(int(self._cur_text_scroll.char_pause * 1000))
        self.__reset_refresh_timeout = lambda: set_refresh_timeout_callback(-1)

        self.__display_lock = threading.Lock()
        self.__index_lock = threading.Lock()
        self.__timer_lock = threading.Lock()

        self.__continue: Optional[Callable[[], None]] = None
        self.__text_scrolls: List[TransitionWidgetSet.TextScroll] = []
        self.__index = 0

        self.__display_text = ""
        self.__timer: Optional[Timer] = None
        self.__wait_for_confirmation = False
        self.__auto_scroll = False

        widget = self.add_block_label("Text", UIConfig.TRANSITION_SCREEN_ROW, UIConfig.TRANSITION_SCREEN_COL,
                                      row_span=UIConfig.TRANSITION_SCREEN_HEIGHT,
                                      column_span=UIConfig.TRANSITION_SCREEN_WIDTH, center=False)
        widget.add_key_command(controls.get_keys(Keys.Cancel), self.__next_text)
        widget.add_key_command(controls.action, self.__next_section)
        widget.toggle_border()
        self.__text = SimpleWidget(widget)
        self.__line_width = self.__text.widget.get_abs_size()[0] - 6  # -6 comes from some PyCUI internal border padding

        widget = self.add_block_label("Confirm", UIConfig.TRANSITION_SCREEN_ROW + UIConfig.TRANSITION_SCREEN_HEIGHT + 1,
                                      UIConfig.TRANSITION_SCREEN_COL, row_span=1,
                                      column_span=UIConfig.TRANSITION_SCREEN_WIDTH, center=True)
        self.__confirm = SimpleWidget(widget)

        if Config.debugging():
            widget = self.add_block_label("Frame count", 0, UIConfig.WINDOW_WIDTH - 1)
            self.__frame_count = SimpleWidget(widget)

    @property
    def at_transition_end(self) -> bool:
        self._lock(self.__index_lock)
        value = self.__index >= len(self.__text_scrolls)
        self._unlock(self.__index_lock)
        return value

    @property
    def _cur_text_scroll(self) -> TextScroll:
        assert not self.at_transition_end
        self._lock(self.__index_lock)
        value = self.__text_scrolls[self.__index]
        self._unlock(self.__index_lock)
        return value

    def _lock(self, lock: threading.Lock, blocking: bool = True, timeout: Optional[float] = None):
        if timeout is None:
            timeout = 1000  # todo use twice refresh timeout instead?
        lock.acquire(blocking=blocking, timeout=timeout)

    def _unlock(self, lock: threading.Lock):
        lock.release()

    def _stop_timer(self):
        self._lock(self.__timer_lock)
        if self.__timer is not None:
            self.__timer.cancel()  # todo what if we cancel the thread before it started?
            self.__timer = None  # todo is it actually good to set it to None?
        self._unlock(self.__timer_lock)

    def __update_screen(self, new_text: str):
        self._lock(self.__display_lock)
        if len(self.__display_text) == 0:
            remaining_chars = self.__line_width
        else:
            # compute difference between len(text) and the next bigger multiple of line_width
            remaining_chars = -len(self.__display_text) % self.__line_width
        while len(new_text) >= remaining_chars:
            self.__display_text += new_text[:remaining_chars]
            self.__display_text += "\n"
            new_text = new_text[remaining_chars:]
            remaining_chars = self.__line_width
        self.__display_text += new_text  # append the remaining text

        self.__text.set_data(self.__display_text)
        self.__text.render()
        self._unlock(self.__display_lock)

        if Config.debugging():
            self.__frame_count.set_data(str(Config.frame_count()))
            self.__frame_count.render()

    def __update_confirm_text(self, confirm: bool, transition_end: bool = False):
        if self.__auto_scroll:
            self.__confirm.set_data("Continuing automatically as soon as text is rendered completely")
        else:
            if confirm:
                self._stop_timer()
                if transition_end:
                    self.__confirm.set_data("Press [Confirm] to continue playing.")
                else:
                    self.__confirm.set_data("Press [Confirm] to start next text section.")
            else:
                self.__confirm.set_data("Press [Cancel] to skip to next text.")
            self.__wait_for_confirmation = confirm
            self.__confirm.render()

            if confirm:
                self.__reset_refresh_timeout()
            else:
                self.__set_refresh_timeout()

    def __next_section(self):
        if self.__wait_for_confirmation:
            if not self.at_transition_end:
                if self._cur_text_scroll.clear_previous:
                    self._lock(self.__display_lock)
                    self.__display_text = ""
                    self._unlock(self.__display_lock)
                self.__update_confirm_text(confirm=False)
                self.__render_text_scroll()

            elif self.__continue is not None:
                self.__continue()

    def __next_text(self):
        if self.__wait_for_confirmation:
            # do nothing until confirmation
            return

        self._stop_timer()
        # at this point there is only one active thread (the other one was stopped if it existed)

        if not self.at_transition_end:
            # immediately show the whole content of the current text scroll in case the user manually proceeded
            self.__update_screen(self._cur_text_scroll.skip_to_end())

            self._lock(self.__index_lock)
            self.__index += 1
            self._unlock(self.__index_lock)
            if not self.at_transition_end:
                if self._cur_text_scroll.clear_previous:
                    self.__update_confirm_text(confirm=True, transition_end=False)
                else:
                    # start rendering the new one
                    # don't wait for text delay since the player also didn't want to wait for the characters
                    self.__render_text_scroll()
                    self.__update_confirm_text(confirm=False)
            else:
                self.__update_confirm_text(confirm=True, transition_end=True)

        elif self.__continue is not None:
            self.__continue()

    def __render_text_scroll(self):
        # check is necessary due to multiple threads working with __index
        if self.at_transition_end:
            return

        if GameplayConfig.get_option_value(Options.auto_skip_text_animation):
            self.__update_screen(self._cur_text_scroll.skip_to_end())

        next_char = self._cur_text_scroll.next()
        if next_char is None:
            self._lock(self.__index_lock)
            self.__index += 1
            self._unlock(self.__index_lock)

            if not self.at_transition_end:
                # continue with the next text scroll
                if self._cur_text_scroll.clear_previous:
                    self._stop_timer()
                    self.__update_confirm_text(confirm=True, transition_end=False)
                else:
                    self.__set_refresh_timeout()  # update timeout
                    self._lock(self.__timer_lock)
                    self.__timer = Timer(self._cur_text_scroll.text_delay, self.__render_text_scroll)
                    self.__timer.start()
                    self._unlock(self.__timer_lock)
            else:
                # inform the player that we finished
                self.__update_confirm_text(confirm=True, transition_end=True)
        else:
            self._lock(self.__timer_lock)
            self.__timer = Timer(self._cur_text_scroll.char_pause, self.__render_text_scroll)
            self.__timer.start()
            self._unlock(self.__timer_lock)
            self.__update_screen(next_char)

    def set_data(self, text_scrolls: List[TextScroll], continue_callback: Callable[[], None],
                 auto_scroll: bool = False):
        assert len(text_scrolls) > 0, "Empty list of texts provided!"

        self.__text_scrolls = text_scrolls
        self.__continue = continue_callback
        self.__auto_scroll = auto_scroll

        # no locks required since there are no additional threads at this point
        self.__display_text = ""
        self.__index = 0

        self.__update_confirm_text(confirm=False)
        self.__timer = Timer(self._cur_text_scroll.text_delay, self.__render_text_scroll)
        self.__timer.start()

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__text,
            self.__confirm,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__text.widget

    def reset(self) -> None:
        pass
        # self.__confirm.set_data("Press [Confirm] for next text.")  # todo how to handle thread states?


class PauseMenuWidgetSet(MyWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_callback: Callable[[], None], save_callback: Callable[[], Tuple[bool, CommonInfos]],
                 exit_run_callback: Callable[[], None], restart_callback: Callable[[], None],
                 achievements_to_string_callback: Callable[[], str]):
        super().__init__(logger, root, render)
        self.__continue_callback = continue_callback
        self.__save_game = save_callback
        self.__exit_run = exit_run_callback
        self.__restart_callback = restart_callback
        self.__achievements_to_string = achievements_to_string_callback

        self.__hud = MyWidgetSet.create_hud_row(self)

        choices = self.add_block_label('Choices', UIConfig.HUD_HEIGHT, 0, row_span=UIConfig.NON_HUD_HEIGHT,
                                       column_span=UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__choices = SelectionWidget(choices, controls, stay_selected=True)

        self.__choices.set_data([
            ("Continue", self.__continue),
            ("Restart", self.__restart),
            ("Save", self.__save),
            ("Manual", self.__help),
            # ("Achievements", self.__achievements),
            ("Options", self.__options),
            ("Exit", self.__exit),
        ])

        details = self.add_block_label('Details', UIConfig.HUD_HEIGHT, UIConfig.PAUSE_CHOICES_WIDTH,
                                       row_span=UIConfig.WINDOW_HEIGHT - UIConfig.HUD_HEIGHT,
                                       column_span=UIConfig.WINDOW_WIDTH - UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__details = SelectionWidget(details, controls, is_second=True)

        description = self.add_block_label('Description', UIConfig.WINDOW_HEIGHT - UIConfig.PAUSE_DESCRIPTION_HEIGHT,
                                           UIConfig.PAUSE_CHOICES_WIDTH, row_span=UIConfig.PAUSE_DESCRIPTION_HEIGHT,
                                           column_span=UIConfig.WINDOW_WIDTH - UIConfig.PAUSE_CHOICES_WIDTH,
                                           center=False)
        self.__description = SimpleWidget(description)
        description.activate_individual_coloring()

        # add action key commands
        def use_choices():
            if self.__choices.use():
                Widget.move_focus(self.__details, self)
                self.__choices.render()
                self.__details.render()

        self.__choices.widget.add_key_command(controls.action, use_choices)

        def use_details():
            if self.__details.use():
                self.__focus_choices()

        self.__details.widget.add_key_command(controls.action, use_details)

    def __focus_choices(self):
        Widget.move_focus(self.__choices, self)
        self.__details.render_reset()
        self.render()

    def __continue(self) -> bool:
        self.__continue_callback()
        return False

    def __restart(self) -> bool:
        self.__restart_callback()
        return False

    def __save(self) -> bool:
        _, common_info = self.__save_game()
        common_info.show()
        return False

    def __help(self) -> bool:
        texts = [enum_string(val, skip_type_prefix=True) for val in get_filtered_help_texts()] + [MyWidgetSet.BACK_STRING]

        def func(val: HelpText) -> Callable[[], bool]:
            # the check for "is not None" leads to a return value of False (because we don't want to switch widgets)
            return lambda: Popup.generic_info(enum_string(val, skip_type_prefix=True), val.text) is not None

        callbacks = [func(val) for val in get_filtered_help_texts()]
        callbacks.append(lambda: True)  # simple callback for "back"

        self.__details.set_data(data=(texts, callbacks))
        return True

    def __achievements(self) -> bool:
        Popup.generic_info("Current Achievement status", self.__achievements_to_string())
        return False

    def __options(self) -> bool:
        # hide most options for tutorial's sake
        options = GameplayConfig.get_options()  # [Options.allow_implicit_removal, Options.allow_multi_move])
        texts = []
        for op_tup in options:
            op, _ = op_tup
            texts.append(f"{op.name}: {GameplayConfig.get_option_value(op, convert=False)}")

        def callback(index: int) -> bool:
            if 0 <= index < len(options):
                option, next_ = options[index]
                new_title = f"{option.name}: {next_(option)}"
                self.__details.update_text(new_title, index)
                self.__details.render()
                self.__description.set_data(option.description)
                self.__description.render()
                return False  # don't change widget focus

            if index == len(options):
                # save was selected
                if Config.save_gameplay_config():
                    # we cannot go back directly since we want to inform the user that saving was successful
                    # therefore we go back after closing the Popup
                    Popup.message(CommonInfos.OptionsSaved.title, CommonInfos.OptionsSaved.text, reopen=False,
                                  on_close_callback=self.__focus_choices)
                else:
                    CommonInfos.OptionsNotSaved.show()
                return False
            else:
                # reset changes
                try:
                    Config.load_gameplay_config()  # todo error message or is the file exception good enough?
                except FileNotFoundError as error:
                    Logger.instance().throw(error)
                return True  # index out of range and no special case -> go back

        self.__details.set_data(data=(
            texts + ["-Save-", MyWidgetSet.BACK_STRING],
            [callback]
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
            self.__description,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__choices.widget

    def set_data(self, robot: Optional[Robot], map_name: str,
                 achievement_manager: Optional["AchievementManager"]):  # todo: remove achievement_manager parameter?
        # todo maybe needs some overhaul?
        self.__hud.set_data((robot, map_name, None))
        self.__description.set_data(HelpText.Pause.text)

    def reset(self) -> None:
        self.__choices.render_reset()
        self.__details.render_reset()
        self.__description.render_reset(reset_text=False)


class WorkbenchWidgetSet(MyWidgetSet):
    def __init__(self, logger, root: py_cui.PyCUI, base_render_callback: Callable[[List[Renderable]], None],
                 controls: Controls, open_fusion_circuit_callback: Callable[[], None]):
        super().__init__(logger, root, base_render_callback)

        resource_info = self.add_block_label_by_dimension('Resources', UIConfig.WB_RESOURCES_DIMS)
        resource_info.toggle_border()
        self.__resources = SimpleWidget(resource_info)

        action_selection = self.add_block_label_by_dimension('Actions', UIConfig.WB_ACTIONS_DIMS)
        action_selection.toggle_border()
        self.__choices = SelectionWidget(action_selection, controls, stay_selected=True)

        gate_selection = self.add_block_label_by_dimension('Gates', UIConfig.WB_GATES_DIMS)
        gate_selection.toggle_border()
        self.__details = SelectionWidget(gate_selection, controls, columns=3, is_second=True)

        info_widget = self.add_block_label_by_dimension('Infos', UIConfig.WB_INFOS_DIMS, center=True)
        info_widget.toggle_border()
        self.__info = SimpleWidget(info_widget)

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__choices,
            self.__details,
            self.__info,
        ]

    def get_main_widget(self) -> WidgetWrapper:
        return self.__choices.widget

    def reset(self) -> None:
        self.__choices.render_reset()
        self.__details.render_reset()
        self.__info.render_reset()


class MapWidgetSet(MyWidgetSet, ABC):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI):
        super().__init__(logger, root, render)

        map_widget = self.add_block_label('MAP', UIConfig.HUD_HEIGHT, 0, row_span=UIConfig.NON_HUD_HEIGHT,
                                          column_span=UIConfig.WINDOW_WIDTH, center=True)
        self.__map_widget = MapWidget(map_widget)

        # init movement keys
        def move(direction: Direction) -> Callable[[], None]:
            def _move() -> None:
                if GameplayConfig.get_option_value(Options.allow_multi_move, convert=True):
                    while self.__move_counter > 1:
                        if not self.__map_widget.move(direction):
                            self.render()
                            # reset because otherwise the next direction would use remaining counter value
                            self.__move_counter = 0
                            return  # abort if we cannot move in this direction
                        self.__move_counter -= 1
                if self.__map_widget.move(direction):
                    self.render()

            return _move

        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveUp), move(Direction.Up))
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveRight), move(Direction.Right))
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveDown), move(Direction.Down))
        self.__map_widget.widget.add_key_command(controls.get_keys(Keys.MoveLeft), move(Direction.Left))

        self.__move_counter = 0

        def setup_hotkey(number: int):
            def set_move_counter():
                self.__move_counter = number

            self.__map_widget.widget.add_key_command(controls.get_hotkey(number), set_move_counter)

        if Config.debugging():
            [setup_hotkey(i) for i in range(10)]

    @property
    def _map_widget(self) -> MapWidget:
        return self.__map_widget

    def try_to_start_map(self):
        """
        Starts the map (e.g., shows description) if it wasn't started already.
        """
        self.__map_widget.try_to_start_map()

    def get_main_widget(self) -> WidgetWrapper:
        return self.__map_widget.widget

    def reset(self) -> None:
        self.__map_widget.render_reset()


class ExploreWidgetSet(MapWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI):
        super().__init__(controls, render, logger, root)
        self.__hud = MyWidgetSet.create_hud_row(self)
        ColorRules.apply_map_rules(self._map_widget.widget)

    def undo_last_move(self) -> bool:
        return self._map_widget.undo_last_move()

    def set_data(self, map_: Map) -> None:
        self.__hud.set_data((map_.robot, map_.name, ""))  # todo fix/remove
        self._map_widget.set_data(map_)
        # map_.start()  # we cannot start the map here because the widget_set has not been applied yet

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self._map_widget
        ]

    def render(self) -> None:
        start = cur_datetime()
        super(ExploreWidgetSet, self).render()
        duration = cur_datetime() - start
        self.__hud.update_render_duration(duration.microseconds / 1000.0)


class NavigationWidgetSet(MapWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI):
        super().__init__(controls, render, logger, root)
        ColorRules.apply_navigation_rules(self._map_widget.widget)

    def set_data(self, map_: Map) -> None:
        self._map_widget.set_data(map_)

    def get_widget_list(self) -> List[Widget]:
        return [self._map_widget]


class ReachTargetWidgetSet(MyWidgetSet, ABC):
    __DETAILS_COLUMNS = 4
    __CHOICES_REMOVE_OBJECT = "remove"
    __CHOICES_RESET_OBJECT = "reset"
    __CHOICES_FLEE_OBJECT = "flee"

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[bool], None], reopen_popup: Callable[[], None],
                 check_unlocks_callback: Callable[[Union[str, Unlocks]], bool],
                 flee_choice: str = "Flee", dynamic_input: bool = True, dynamic_target: bool = True,
                 enable_reset: bool = False):
        """
        :param controls: controls used by the CUI to add keys
        :param render: callback to render the CUI
        :param logger: logger for the CUI
        :param continue_exploration_callback: callback to exit this WidgetSet and continue exploration
        :param reopen_popup: callback to reopen popup history
        :param check_unlocks_callback: callback to check if certain locked features were already unlocked
        :param flee_choice: the text used to prompt the player with aborting this widget set's puzzle
        :param dynamic_input:
        :param dynamic_target:
        :param enable_reset: whether we want to add a Reset-command or not
        """
        super().__init__(logger, root, render)
        self.__flee_choice = flee_choice
        self.__dynamic_input = dynamic_input
        self.__dynamic_target = dynamic_target
        self.__enable_reset = enable_reset
        self._continue_exploration = lambda: continue_exploration_callback(False)
        self._continue_and_undo_callback = lambda: continue_exploration_callback(True)
        self._check_unlocks = check_unlocks_callback
        self._robot: Optional[Robot] = None
        self.__target: Optional[Target] = None
        self.__num_of_qubits = -1  # needs to be an illegal value because we definitely want to reposition all
        # dependent widgets for the first usage of this WidgetSet
        self._choices_content = None
        self._in_reward_message = False  # _choices currently displays the reward message
        self.__in_expedition = False
        self.__puzzle_timer = cur_datetime()

        if not (self.__dynamic_target and self.__dynamic_input):
            Config.check_reachability("ReachTargetWidgetSet() - dynamic target and input?", raise_exception=True)

        posy = 0
        posx = 0
        row_span = UIConfig.stv_height(2)  # doesn't matter since we reposition the dependent widgets anyway
        matrix_width = UIConfig.WINDOW_WIDTH - (UIConfig.INPUT_STV_WIDTH + UIConfig.OUTPUT_STV_WIDTH +
                                                UIConfig.TARGET_STV_WIDTH + 1 * 3)  # + width of the three signs
        circuit_height = UIConfig.NON_HUD_HEIGHT - row_span - UIConfig.DIALOG_HEIGHT

        self._hud = MyWidgetSet.create_hud_row(self)
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
        self.__circuit = CircuitWidget(circuit, controls)
        posy += circuit_height

        # wrap the widget that tell us about the puzzle state
        historic_widgets = [self.__circuit, self.__circuit_matrix, self.__stv_robot]
        if self.__dynamic_target: historic_widgets.append(self.__stv_target)
        if self.__dynamic_input: historic_widgets.append(self.__input_stv)
        self.__history_widget = HistoricWrapperWidget(historic_widgets, render_widgets=True, save_initial_state=False)

        def jump_to_present(key: Keys):
            # key doesn't matter since we want to jump back to the present on every key press
            if GameplayConfig.get_option_value(Options.auto_reset_history, convert=True):
                self.__history_widget.jump_to_present(render=True)

        # the remaining widgets are the user interface
        choices = self.add_block_label('Choices', posy, 0, row_span=UIConfig.WINDOW_HEIGHT - posy,
                                       column_span=UIConfig.WINDOW_WIDTH, center=True)
        choices.toggle_border()
        choices.activate_individual_coloring()  # TODO: current reward highlight version is not satisfying
        self._choices = SelectionWidget(choices, controls, columns=self.__DETAILS_COLUMNS, is_second=False,
                                        on_key_press=jump_to_present)

        def use_choices():
            if self._choices.use():
                # only other widget to focus (use() == True means we should move focus) is circuit
                Widget.move_focus(self.__circuit, self)

        self._choices.widget.add_key_command(controls.action, use_choices)

        def gate_guide():
            # check if a gate or a meta choice (e.g., cancel) is selected
            if isinstance(self._choices.selected_object, Instruction):
                gate = self._choices.selected_object
                if gate.gate_type.has_other_names:
                    other_names = "\nAlso known as: " + gate.gate_type.get_other_names(" Gate, ") + " Gate"
                else:
                    other_names = ""
                Popup.generic_info(gate.gate_type.full_name, f"Short name: {gate.gate_type.short_name} Gate\n" +
                                   gate.description(self._check_unlocks) + other_names)
            else:
                reopen_popup()  # open popup history

        self._choices.widget.add_key_command(controls.get_keys(Keys.Help), gate_guide)

        def use_circuit():
            success, gate = self.__circuit.place_gate()
            if success:
                if self._choices.validate_index():
                    if gate is None:
                        self.__init_choices()
                    else:
                        self._choices.update_text(gate.selection_str(), self._choices.index)
                self.__choices_commit()
                Widget.move_focus(self._choices, self)
                self.render()

        self.__circuit.widget.add_key_command(controls.action, use_circuit)
        # disable pausing mid gate-placement
        self.__circuit.widget.add_key_command(controls.get_keys(Keys.Pause), lambda: None, overwrite=True)

        def cancel_circuit():
            self.__circuit.abort_placement()
            Widget.move_focus(self._choices, self)
            self.render()

        self.__circuit.widget.add_key_command(controls.get_keys(Keys.Cancel), cancel_circuit)

        # situational keys for travelling through history need to be set last because everything needs to be
        # initialized first for the hidden render()-call to succeed
        def travel_history(forth: bool) -> Callable[[], None]:
            def func():
                if GameplayConfig.get_option_value(Options.enable_puzzle_history, convert=True):
                    # block functionality if we are displaying the reward message or are not focused on _choices
                    # (e.g., are manipulating the circuit)
                    if self._choices.widget.is_selected() and not self._in_reward_message:
                        self.__history_widget.travel(forth, render=True)

            return func

        self.add_key_command(controls.get_keys(Keys.Situational1), travel_history(False), add_to_widgets=True)
        self.add_key_command(controls.get_keys(Keys.Situational2), travel_history(True), add_to_widgets=True)

        # special key to open matrix in extra popup (e.g., if CircuitMatrixWidget is too narrow to display a 8x8 matrix)
        def show_matrix_popup():
            if not self._check_unlocks(Unlocks.ShowEquation): return
            text_mat = self.__circuit_matrix.widget.get_title()
            if "\n" in text_mat:
                headline = text_mat[:text_mat.index("\n")]
                Popup.show_matrix(headline, text_mat[len(headline) + 1:])
            else:
                Logger.error(f"No \"\\n\" found in matrix: {text_mat}.", show=False, from_pycui=False)

        self.add_key_command(controls.get_keys(Keys.MatrixPopup), show_matrix_popup, add_to_widgets=True)

        # clear some widgets if the player hasn't unlocked the equations yet
        if not self._check_unlocks(Unlocks.ShowEquation):
            self.__input_stv.render_reset()
            self.__mul_widget.render_reset()
            self.__circuit_matrix.render_reset()
            self.__result_widget.render_reset()
            self.__stv_robot.render_reset()
            self.__eq_widget.render_reset()
            self.__stv_target.render_reset()

    @property
    def _target(self) -> Target:
        return self.__target

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
                # window width minus width of all StVs and signs, afterwards adapted by the small-qubit-shrinkage
                matrix_width = UIConfig.WINDOW_WIDTH - (UIConfig.INPUT_STV_WIDTH + UIConfig.OUTPUT_STV_WIDTH +
                                                        UIConfig.TARGET_STV_WIDTH + 1 * 3)
                posx = 0
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

                # "+2" is a magic number that gave good visual results
                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span + 2)

            elif num_of_qubits == 4:
                # todo problem with 4 qubits: out has not enough space, hence, its coloring doesn't work
                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span)
                self._choices.widget.reposition(row=UIConfig.WINDOW_HEIGHT - 1, row_span=1)
            else:
                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span + 1)  # + 1 for visuals

    def get_main_widget(self) -> WidgetWrapper:
        return self._choices.widget

    def set_data(self, robot: Robot, target: Target, tutorial_data: Any) -> None:
        """
        :param robot: the Robot that tries to solve the puzzle
        :param target: the Target of which the Robot should reach the StateVector
        :param tutorial_data: additional data we might need for tutorial purposes
        """
        self._robot = robot
        self.__target = target

        self._reposition_widgets(robot.num_of_qubits)

        # from a code readers perspective the reset would make more sense in switch_to_fight() etc. but then we would
        # have to add it to multiple locations and have the risk of forgetting to add it for new ReachTargetWidgetSets
        if GameplayConfig.auto_reset_circuit():
            robot.reset_circuit()

        self._hud.set_data((robot, None, None))  # don't overwrite the current map name
        if tutorial_data:
            vectors = target.input_stv, target.state_vector
        else:
            vectors = None
        self.__circuit.set_data((robot, vectors))

        if self._check_unlocks(Unlocks.ShowEquation):
            self.__input_stv.set_data(target.input_stv)
            self.__mul_widget.set_data(self._sign_offset + "x")
            self.__result_widget.set_data(self._sign_offset + "=")
            self.__stv_target.set_data(target.state_vector)

        self.__history_widget.clear_history()  # clean/reset history
        self._robot.update_statevector(input_stv=target.input_stv, use_energy=False, check_for_game_over=False)
        self.__update_calculation(False)    # stores the puzzle's beginning state in history_widget

        self.__init_choices()

        self.__puzzle_timer = cur_datetime()
        # log info about the puzzle
        info_msg = f"[target id={target.id}] Starting puzzle...\n" \
                   f"input={target.input_stv}\n" \
                   f"target={target.state_vector}"
        Logger.instance().info(info_msg, from_pycui=False)

    def get_widget_list(self) -> List[Widget]:
        return [
            self._hud,
            self.__input_stv,
            self.__mul_widget,
            self.__circuit_matrix,
            self.__result_widget,
            self.__stv_robot,
            self.__eq_widget,
            self.__stv_target,
            self.__circuit,
            self._choices
        ]

    def reset(self) -> None:
        self._choices.render_reset()

    def _save_puzzle_to_history(self, input_stv: StateVector, target_stv: StateVector):
        if self._check_unlocks(Unlocks.PuzzleHistory):
            self.__input_stv.set_data(input_stv)
            self.__stv_target.set_data(target_stv)
            # we don't know equality, and we don't care for this preview
            self.__eq_widget.set_data(self._sign_offset + "=?=")
            self.__history_widget.save_state(rerender=True, force=False)

    def __update_calculation(self, target_reached: bool):
        if self._check_unlocks(Unlocks.ShowEquation):
            diff_stv = self._target.state_vector.get_diff(self._robot.state_vector)

            self.__circuit_matrix.set_data(self._robot.circuit_matrix)
            self.__stv_robot.set_data((self._robot.state_vector, diff_stv), target_reached=target_reached)

            if self.__dynamic_input: self.__input_stv.set_data(self._target.input_stv)
            if self.__dynamic_target: self.__stv_target.set_data(self._target.state_vector)

            if diff_stv.is_zero:
                self.__eq_widget.set_data(self._sign_offset + "===")
            else:
                self.__eq_widget.set_data(self._sign_offset + "=/=")

        if self._check_unlocks(Unlocks.PuzzleHistory):
            self.__history_widget.save_state(rerender=True, force=False)

    def __init_choices(self):
        choices, objects = [], []  # Tuple[List[str], List[object]]
        callbacks: List[Callable[[], bool]] = []
        for instruction in self._robot.instructions:
            choices.append(instruction.selection_str())
            objects.append(instruction)
            callbacks.append(self.__choose_instruction)
        choices = SelectionWidget.wrap_in_hotkey_str(choices)

        # add commands
        if self._check_unlocks(Unlocks.GateRemove):
            choices.append("Remove")
            objects.append(ReachTargetWidgetSet.__CHOICES_REMOVE_OBJECT)
            callbacks.append(self.__remove)
        if self.__enable_reset:
            choices.append("Reset")
            objects.append(ReachTargetWidgetSet.__CHOICES_RESET_OBJECT)
            callbacks.append(self.__reset_circuit)
        if self._check_unlocks(Unlocks.PuzzleFlee):
            choices.append(self.__flee_choice)
            objects.append(ReachTargetWidgetSet.__CHOICES_FLEE_OBJECT)
            callbacks.append(self.__flee)  # just return True to change back to previous screen

        self._choices.set_data(data=((choices, objects), callbacks))

    def __choose_instruction(self) -> bool:
        cur_instruction = self._choices.selected_object
        if cur_instruction is not None:
            if cur_instruction.is_used():
                # move the instruction
                pos = cur_instruction.position
                qubit = cur_instruction.get_qubit_at(0)
                self._robot.remove_instruction(cur_instruction)
                self.__circuit.start_gate_placement(cur_instruction, pos, qubit)
                self.__circuit.render()
                return True
            else:
                if self._robot.is_space_left or GameplayConfig.get_option_value(Options.allow_implicit_removal):
                    self.__circuit.start_gate_placement(cur_instruction)
                    self.__circuit.render()
                    return True
                else:
                    CommonPopups.NoCircuitSpace.show()
            self.render()
        return False

    def __remove(self) -> bool:
        if self._robot.has_empty_circuit:
            CommonPopups.NoGatePlaced.show()
            return False  # stay in choices
        else:
            self.__circuit.start_gate_placement(None)
            self.render()
            return True  # focus circuit

    def __reset_circuit(self) -> bool:
        # todo: currently this does not decrease edits (for riddles), but maybe it should?
        for pos in range(self._robot.circuit_space):
            self.__circuit.start_gate_placement(None, pos)
            self.__circuit.place_gate()     # placing "None" removes the gate placed at pos
        self.__circuit.abort_placement()    # needed to remove the "eraser" before rendering

        self._robot.update_statevector(input_stv=self._target.input_stv, use_energy=False, check_for_game_over=False)
        self.__update_calculation(False)
        self.render()
        return False    # don't change focus

    def __flee(self) -> bool:
        # last selection possibility in edit is for fleeing
        self._choices_flee()
        self._choices.render()

        duration, _ = time_diff(self.__puzzle_timer, cur_datetime())
        Logger.instance().info(f"[target id={self._target.id}]\n"
                               f"Fled from puzzle after {duration}s "
                               f"and {self._target.checks} steps.", from_pycui=False)
        return False  # stay in choices

    def __choices_commit(self):
        if self._target is None:
            Popup.error("No target was set! You automatically win.", add_report_note=True)
            self._on_success()
            return
        self._robot.update_statevector(input_stv=self._target.input_stv)
        success, reward = self._target.is_reached(self._robot.state_vector, self._robot.circuit_matrix)
        self.__update_calculation(success)
        self.render()
        if success:
            self._robot.increase_score(ScoreConfig.get_puzzle_score(self._target.checks,
                                                                    self._robot.state_vector.num_of_used_gates,
                                                                    self._target.state_vector.num_of_used_gates))
            self._in_reward_message = True
            self._prepare_reward_message(reward)
            self._on_success()
        else:
            self._on_commit_fail()

    def _prepare_reward_message(self, reward: Collectible):
        def give_reward_and_continue() -> bool:
            if reward is not None: self._robot.give_collectible(reward)
            self._in_reward_message = False  # undo the blocking since the success notification is over
            self._continue_exploration()
            return False  # stay in choices

        if reward is None:
            self._choices.set_data(data=(
                [f"Congratulations, you solved the {ColorConfig.highlight_object('Puzzle', invert=True)}!"],
                [give_reward_and_continue]
            ))
        else:
            Logger.instance().assertion(isinstance(reward, Collectible), f"Reward is no Collectible: {reward}")
            self._choices.set_data(data=(
                [f"Congratulations! Your reward: {ColorConfig.highlight_object(reward.to_string())}"],
                [give_reward_and_continue]
            ))

    def _fleeing_failed_callback(self) -> bool:
        self.__init_choices()
        self._choices.render()
        return False  # stay in choices

    def _on_success(self):
        duration, _ = time_diff(self.__puzzle_timer, cur_datetime())
        instructions_str = ""
        for pos in range(self._robot.circuit_space):
            inst = self._robot.gate_used_at(pos)
            if inst is not None:
                instructions_str += f"{inst}, "
        instructions_str = instructions_str[:-2]  # remove trailing ", "
        info_msg = f"[target id={self._target.id}]\n" \
                   f"Solved puzzle after {duration}s in {self._target.checks} steps. \n" \
                   f"Used: {instructions_str}"
        Logger.instance().info(info_msg, from_pycui=False)

    @abstractmethod
    def _on_commit_fail(self) -> bool:
        pass

    @abstractmethod
    def _choices_flee(self) -> bool:
        pass


class TrainingsWidgetSet(ReachTargetWidgetSet):  # todo: remove or overhaul
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 back_to_menu_callback: Callable[[], None], reopen_popup_callback: Callable[[], None],
                 check_unlocks_callback: Callable[[str], bool]):
        super().__init__(controls, render, logger, root, back_to_menu_callback, reopen_popup_callback,
                         check_unlocks_callback, "Done")

    def _on_commit_fail(self) -> bool:
        return True

    def _choices_flee(self) -> bool:
        from qrogue.util import ErrorConfig
        ErrorConfig.raise_deletion_exception()
        return True


class FightWidgetSet(ReachTargetWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[bool], None], reopen_popup_callback: Callable[[], None],
                 check_unlocks_callback: Callable[[str], bool]):
        super(FightWidgetSet, self).__init__(controls, render, logger, root, continue_exploration_callback,
                                             reopen_popup_callback, check_unlocks_callback)
        self.__flee_check = None

    def set_data(self, robot: Robot, target: Enemy, tutorial_data):
        super(FightWidgetSet, self).set_data(robot, target, tutorial_data)
        self.__flee_check = target.flee_check

    def _on_commit_fail(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            self._robot.game_over_check()
        return True

    def _choices_flee(self) -> bool:
        extra_text = ""
        if GameplayConfig.get_option_value(Options.energy_mode):
            if self._robot.cur_energy > self._target.flee_energy:
                damage_taken, _ = self._robot.decrease_energy(amount=self._target.flee_energy)
                extra_text = f"Your Qubot lost {damage_taken} energy."
            else:
                CommonPopups.NotEnoughEnergyToFlee.show()
                return False  # don't switch to choices widget

        if self.__flee_check():
            self._choices.set_data(data=(
                [f"Fled successfully. {extra_text}"],
                [self._continue_and_undo_callback]
            ))
        else:
            self._choices.set_data(data=(
                [f"Failed to flee. {extra_text}"],
                [self._fleeing_failed_callback]
            ))
        return True


class RiddleWidgetSet(ReachTargetWidgetSet):
    _TRY_PHRASING = "edits"

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[bool], None], reopen_popup_callback: Callable[[], None],
                 check_unlocks_callback: Callable[[str], bool], enable_reset: bool = False):
        super().__init__(controls, render, logger, root, continue_exploration_callback, reopen_popup_callback,
                         check_unlocks_callback, "Give Up", enable_reset=enable_reset)

    @property
    def _target(self) -> Riddle:
        # override this property to return the correct, specialised subtype of Target
        return super()._target

    def set_data(self, robot: Robot, target: Riddle, tutorial_data) -> None:
        super(RiddleWidgetSet, self).set_data(robot, target, tutorial_data)
        self._hud.set_data((robot, None, f"Remaining {RiddleWidgetSet._TRY_PHRASING}: {target.edits}"))

    def _on_commit_fail(self) -> bool:
        if not self._target.can_attempt:
            self._choices.set_data(data=(
                [f"You couldn't solve the riddle within the given number of {RiddleWidgetSet._TRY_PHRASING}. "
                 f"It vanished together with its reward."],
                [self._continue_exploration]
            ))
        self._hud.update_situational(f"Remaining {RiddleWidgetSet._TRY_PHRASING}: {self._target.edits}")
        return True

    def _choices_flee(self) -> bool:
        self._choices.set_data(data=(
            [f"Abort - you can still try again later", "Continue"],
            [self._continue_and_undo_callback, self._fleeing_failed_callback]
        ))
        return True


class ChallengeWidgetSet(ReachTargetWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[bool], None], reopen_popup_callback: Callable[[], None],
                 check_unlocks_callback: Callable[[str], bool]):
        super().__init__(controls, render, logger, root, continue_exploration_callback, reopen_popup_callback,
                         check_unlocks_callback)

    def set_data(self, robot: Robot, target: Challenge, tutorial_data) -> None:
        super(ChallengeWidgetSet, self).set_data(robot, target, tutorial_data)
        if target.min_gates == target.max_gates:
            constraints = f"Constraints: Use exactly {target.min_gates} gates."
        else:
            constraints = f"Constraints: Use between {target.min_gates} and {target.max_gates} gates."
        self._hud.update_situational(constraints)

    def _on_commit_fail(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            self._robot.game_over_check()
        return True

    def _choices_flee(self) -> bool:
        CommonPopups.CannotFlee.show()
        return False


class BossFightWidgetSet(RiddleWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[bool], None], reopen_popup_callback: Callable[[], None],
                 check_unlocks_callback: Callable[[str], bool], exit_level_callback: Callable[[], None],
                 proceed_to_next_level_callback: Callable[[], None]):
        super().__init__(controls, render, logger, root, continue_exploration_callback, reopen_popup_callback,
                         check_unlocks_callback, enable_reset=True)
        self._exit_level = exit_level_callback
        self._proceed_to_next_level = proceed_to_next_level_callback

    def _choices_flee(self) -> bool:
        self._choices.set_data(data=(
            ["You fled to try again later."],
            [self._continue_and_undo_callback]
        ))
        return True

    def set_data(self, robot: Robot, target: Boss, tutorial_data):
        # override to make sure a Boss is passed
        super(BossFightWidgetSet, self).set_data(robot, target, tutorial_data)

    def _prepare_reward_message(self, reward: Collectible):
        if reward is None:
            Logger.instance().warn("No reward specified for Boss!", from_pycui=False)
            reward_text = ""
        else:
            reward_text = f"Your reward: {ColorConfig.highlight_object(reward.to_string())}."
            if reward.type is CollectibleType.QuantumFuser:
                # todo: currently the number of QuantumFusers is increased in NewSaveData.complete_expedition()
                pass
            else:
                Config.check_reachability("BossFightWidgetSet._prepare_reward_message()")
                self._robot.give_collectible(reward)

        def callback() -> bool:
            self._continue_exploration()    # leave the fight screen
            self._proceed_to_next_level()   # and then proceed
            return False

        self._choices.set_data(data=(
            [f"Congratulations, you solved the {ColorConfig.highlight_object('Boss Puzzle')}!\n" + reward_text],
            [callback]
        ))

    def _on_commit_fail(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            if self._robot.decrease_energy(PuzzleConfig.BOSS_FAIL_DAMAGE)[1]:
                pass    # todo: show message and call game_over()

        if not self._target.can_attempt:
            self._choices.set_data(data=(
                [f"You {ColorConfig.highlight_word('could not solve')} the Boss puzzle within the given number of "
                 f"{RiddleWidgetSet._TRY_PHRASING}.\n"
                 f"You {ColorConfig.highlight_word('exit the level')} with your emergency kit."],
                [self._exit_level]
            ))
        self._hud.update_situational(f"Remaining {RiddleWidgetSet._TRY_PHRASING}: {self._target.edits}")
        return True
