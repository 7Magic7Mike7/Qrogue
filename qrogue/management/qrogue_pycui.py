import time
from enum import Enum
from threading import Thread
from typing import List, Callable, Optional, Any, Tuple, Union

from py_cui import PyCUI
from py_cui import popups
from py_cui.widget_set import WidgetSet

from qrogue.game.logic import collectibles
from qrogue.game.logic.actors import Boss, Controllable, Enemy, Riddle, Robot
from qrogue.game.logic.actors.controllables import BaseBot
from qrogue.game.logic.actors.puzzles import Challenge
from qrogue.game.logic.base import StateVector
from qrogue.game.logic.collectibles import Score
from qrogue.game.world.map import CallbackPack, WorldMap, Map
from qrogue.game.world.navigation import Direction
from qrogue.game.world.tiles import WalkTriggerTile, Message, Collectible
from qrogue.game.world.tiles.tiles import NpcTile
from qrogue.graphics import WidgetWrapper
from qrogue.graphics.popups import Popup, MultilinePopup, ConfirmationPopup
from qrogue.graphics.rendering import MultiColorRenderer
from qrogue.graphics.widgets import Renderable, BossFightWidgetSet, ExploreWidgetSet, \
    FightWidgetSet, MenuWidgetSet, MyWidgetSet, NavigationWidgetSet, PauseMenuWidgetSet, RiddleWidgetSet, \
    ChallengeWidgetSet, ShopWidgetSet, WorkbenchWidgetSet, TrainingsWidgetSet, Widget, TransitionWidgetSet, \
    ScreenCheckWidgetSet
from qrogue.util import achievements, common_messages, CheatConfig, Config, GameplayConfig, UIConfig, HelpText, \
    Logger, PathConfig, MapConfig, Controls, Keys, RandomManager, PyCuiConfig, PyCuiColors, Options, \
    TestConfig, CommonQuestions, ErrorConfig
from qrogue.util.achievements import Unlocks
from qrogue.util.config import FileTypes, PopupConfig
from qrogue.util.game_simulator import GameSimulator
from qrogue.util.key_logger import KeyLogger, OverWorldKeyLogger

from qrogue.management import MapManager, Pausing, SaveData, LevelInfo


class QrogueCUI(PyCUI):
    # how many seconds to wait after starting to mark initialization as complete (relevant for input handling)
    __INIT_DELAY = 0.1

    class _State(Enum):
        Menu = 0
        Pause = 1
        Explore = 2
        Fight = 3
        Shop = 4
        Riddle = 5
        BossFight = 6

        Spaceship = 7
        Workbench = 8
        Navigation = 9
        Training = 10

        Challenge = 11

        Transition = 12  # for atmospheric transitions and elements
        ScreenCheck = 13    # a menu to check dimensions and color of the screen/terminal the game is played

    class _StateMachine:
        def __init__(self, renderer: "QrogueCUI"):
            self.__renderer = renderer
            self.__cur_state: Optional["QrogueCUI._State"] = None
            self.__prev_state: Optional["QrogueCUI._State"] = None

        @property
        def cur_state(self) -> "QrogueCUI._State":
            return self.__cur_state

        @property
        def prev_state(self) -> "QrogueCUI._State":
            return self.__prev_state

        def change_state(self, state: "QrogueCUI._State", data) -> None:
            if self.__cur_state is not QrogueCUI._State.Transition:
                # don't overwrite previous prev_state if the new one would be Transition
                self.__prev_state = self.__cur_state
            self.__cur_state = state

            if self.__cur_state == QrogueCUI._State.Menu:
                self.__renderer._switch_to_menu(data)
            elif self.__cur_state == QrogueCUI._State.Explore:
                self.__renderer._switch_to_explore(data)
            elif self.__cur_state == QrogueCUI._State.Fight:
                self.__renderer._switch_to_fight(data)
            elif self.__cur_state == QrogueCUI._State.Riddle:
                self.__renderer._switch_to_riddle(data)
            elif self.__cur_state == QrogueCUI._State.Challenge:
                self.__renderer._switch_to_challenge(data)
            elif self.__cur_state == QrogueCUI._State.Shop:
                self.__renderer._switch_to_shop(data)
            elif self.__cur_state == QrogueCUI._State.BossFight:
                self.__renderer._switch_to_boss_fight(data)
            elif self.__cur_state == QrogueCUI._State.Pause:
                self.__renderer._switch_to_pause()

            elif self.__cur_state == QrogueCUI._State.Spaceship:
                ErrorConfig.raise_deletion_exception()
            elif self.__cur_state == QrogueCUI._State.Training:
                self.__renderer._switch_to_training(data)
            elif self.__cur_state == QrogueCUI._State.Workbench:
                self.__renderer._switch_to_workbench(data)
            elif self.__cur_state == QrogueCUI._State.Navigation:
                self.__renderer._switch_to_navigation(data)

            elif self.__cur_state == QrogueCUI._State.Transition:
                self.__renderer._switch_to_transition(data)
            elif self.__cur_state == QrogueCUI._State.ScreenCheck:
                self.__renderer._switch_to_screen_check(data)

    class _PopupHistory:
        def __init__(self, show_popup: Callable[[MultilinePopup], None]):
            self.__show_popup = show_popup
            self.__history: List[MultilinePopup] = []
            self.__index = -1
            self.__remove_on_close = False

        @property
        def is_empty(self) -> bool:
            return len(self) <= 0

        @property
        def present_index(self) -> int:
            return len(self.__history) - 1

        @property
        def is_in_present(self) -> bool:
            return self.__index == self.present_index

        def back(self, show_popup: bool = True):
            if self.is_empty or self.__index == 0:
                return  # we already show the oldest popup (or cannot show anything)
            elif self.__index < 0:
                self.__index = 0    # show oldest popup for invalid indices
            else:
                self.__index -= 1

            if show_popup: self.show()

        def forth(self, show_popup: bool = True):
            if self.is_empty or self.__index == self.present_index:
                return  # we already show the most recent popup (or cannot show anything)
            elif self.__index < 0:
                self.__index = self.present_index   # show most recent popup for invalid indices
            else:
                self.__index += 1

            if show_popup: self.show()

        def jump_to_present(self, show_popup: bool = True):
            if self.is_empty or self.__index == self.present_index:
                return  # we already show the most recent popup (or cannot show anything)
            self.__index = self.present_index

            if show_popup: self.show()

        def show(self):
            if 0 <= self.__index < len(self.__history):
                self.__show_popup(self.__history[self.__index])
            # else: can happen if a level doesn't start with a message, e.g. expeditions

        def add(self, new_popup: MultilinePopup, is_permanent: bool):
            """
            :param new_popup: the popup to add to the history
            :param is_permanent:  permanent popups stay in the history until it is reset, while non-permanent (i.e.,
                temporary) popups will be removed after the popup display closes
            """
            self.__history.append(new_popup)
            self.__index = self.present_index
            self.__remove_on_close = not is_permanent

        def resolve(self, force_remove: bool = False):
            if self.__remove_on_close or force_remove:
                self.__history.pop()
                self.__index = min(self.__index, self.present_index)    # adapt index if it pointed to the removed popup
                self.__remove_on_close = False
            elif 0 <= self.present_index < len(self.__history):     # if is needed to not crash on level loading error
                self.__history[self.present_index].freeze()

        def reset(self):
            self.__history = []
            self.__index = -1

        def __len__(self) -> int:
            return len(self.__history)

    @staticmethod
    def start_simulation(simulation_path: str) -> Optional[NewSaveData]:
        try:
            qrogue_cui = QrogueCUI()
            simulator = GameSimulator(simulation_path, in_keylog_folder=True,
                                      get_unlocks=lambda name: LevelInfo.get_level_completion_unlocks(name, qrogue_cui.__save_data.check_level, True))
            qrogue_cui._set_simulator(simulator)
            return qrogue_cui.start()

        except FileNotFoundError:
            Logger.instance().show_error(f"File \"{simulation_path}\" could not be found!")

    @staticmethod
    def start_simulation_test(simulation_path: str) -> bool:
        # first we have to reset all singletons
        Logger.reset()
        RandomManager.reset()
        OverWorldKeyLogger.reset()

        try:
            qrogue_cui = QrogueCUI(PathConfig.get_seed_from_key_log_file(simulation_path))
            simulator = GameSimulator(simulation_path, in_keylog_folder=True, get_unlocks=lambda name:
                        LevelInfo.get_level_completion_unlocks(name, qrogue_cui.__save_data.check_level, True))
            qrogue_cui._set_simulator(simulator, stop_when_finished=True)

            if TestConfig.is_automatic():
                qrogue_cui.set_refresh_timeout(TestConfig.automation_step_time())

            qrogue_cui.start()
            return True
        except FileNotFoundError:
            return False

    def __init__(self, width: int = UIConfig.WINDOW_WIDTH, height: int = UIConfig.WINDOW_HEIGHT,
                 save_data: Optional[NewSaveData] = None):
        self.__init_complete = False
        super().__init__(width, height)
        PyCuiConfig.set_get_dimensions_callback(self._get_absolute_grid_dimensions)
        self.set_title(f"Qrogue {Config.version()}")
        self.__controls = Controls(self._handle_key_presses)
        self.__seed = RandomManager.instance().seed
        OverWorldKeyLogger()    # todo: init this with other singletons?

        def move_focus(_widget: WidgetWrapper, _widget_set: WidgetSet):
            # this check is necessary for manual widget-set switches due to the call-order (the callback happens before
            # this move_focus here)
            if _widget_set is self.__cur_widget_set:
                self.move_focus(_widget, auto_press_buttons=False)
        self._auto_focus_buttons = False
        Widget.set_move_focus_callback(move_focus)

        # INIT MANAGEMENT
        Logger.instance().set_popup(self.show_message_popup, self.show_error_popup)
        CheatConfig.init(self.__show_message_popup, self.__show_input_popup, deactivate_cheats=not Config.debugging(),
                         allow_cheats=Config.debugging())
        Popup.update_popup_functions(self.__show_message_popup)
        ConfirmationPopup.update_popup_function(self.__show_confirmation_popup)

        Pausing(self.__pause_game)
        self.__cbp = CallbackPack(self.__start_level, self.__start_fight, self.__start_boss_fight, self.__open_riddle,
                                  self.__open_challenge, self.__visit_shop, self.__game_over)
        ########################################
        self.__save_data = NewSaveData()
        self.__map_manager = MapManager(self.__save_data, seed, self.__show_world, self.__start_level, self.__show_input_popup)
        ########################################

        if not Config.skip_learning():
            self.__map_manager.fill_expedition_queue(lambda: None, no_thread=True)

        Popup.update_check_achievement_function(SaveData.instance().check_achievement)
        common_messages.set_show_callback(Popup.generic_info)
        common_messages.set_ask_callback(ConfirmationPopup.ask)
        WalkTriggerTile.set_show_explanation_callback(Popup.from_message)
        Message.set_show_callback(Popup.from_message_trigger)
        Collectible.set_pickup_message_callback(Popup.generic_info)

        self.__key_logger = KeyLogger()
        self.__simulator: Optional[GameSimulator] = None
        self.__stop_with_simulation_end = False
        self.__last_input = time.time()
        self.__last_key: Optional[int] = None
        self.__focused_widget: Optional[Widget] = self.get_selected_widget()

        # INIT POPUP HISTORY
        def _show_popup_for_history(historic_popup: MultilinePopup):
            self.__focused_widget = self.get_selected_widget()
            self._popup = historic_popup
        self.__popup_history = self._PopupHistory(_show_popup_for_history)

        # INIT WIDGET SETS
        self.__menu = MenuWidgetSet(self.__controls, self.__render, Logger.instance(), self,
                                    MapManager.instance().load_first_uncleared_map,
                                    self.__start_playing, self.__start_expedition, self.stop, self.__choose_simulation,
                                    self.__show_screen_check)
        self.__screen_check = ScreenCheckWidgetSet(self.__controls, Logger.instance(), self, self.__render,
                                                   self._switch_to_menu)
        self.__transition = TransitionWidgetSet(self.__controls, Logger.instance(), self, self.__render,
                                                self.set_refresh_timeout)
        self.__pause = PauseMenuWidgetSet(self.__controls, self.__render, Logger.instance(), self,
                                          self.__general_continue, self.__save_data.save, self._switch_to_menu,
                                          self.__map_manager.reload, self.__save_data.to_achievements_string)
        self.__pause.set_data(None, "Qrogue", None)

        self.__training = TrainingsWidgetSet(self.__controls, self.__render, Logger.instance(), self,
                                             lambda b: None, self.__popup_history.show,
                                             self.__save_data.check_unlocks)   # todo: update signature
        self.__workbench = WorkbenchWidgetSet(self.__controls, Logger.instance(), self,
                                              self.__save_data.available_robots(), self.__render,
                                              lambda b: None)   # todo: update signature
        self.__navigation = NavigationWidgetSet(self.__controls, self.__render, Logger.instance(), self)

        self.__explore = ExploreWidgetSet(self.__controls, self.__render, Logger.instance(), self)
        self.__fight = FightWidgetSet(self.__controls, self.__render, Logger.instance(), self, self.__continue_explore,
                                      self.__popup_history.show, self.__save_data.check_unlocks)
        self.__boss_fight = BossFightWidgetSet(self.__controls, self.__render, Logger.instance(), self,
                                               self.__continue_explore, self.__popup_history.show,
                                               self.__save_data.check_unlocks)
        self.__riddle = RiddleWidgetSet(self.__controls, self.__render, Logger.instance(), self,
                                        self.__continue_explore, self.__popup_history.show,
                                        self.__save_data.check_unlocks)
        self.__challenge = ChallengeWidgetSet(self.__controls, self.__render, Logger.instance(), self,
                                              self.__continue_explore, self.__popup_history.show,
                                              self.__save_data.check_unlocks)
        self.__shop = ShopWidgetSet(self.__controls, self.__render, Logger.instance(), self, self.__continue_explore)

        widget_sets: List[MyWidgetSet] = [self.__training, self.__navigation, self.__explore,
                                          self.__fight, self.__boss_fight, self.__shop, self.__riddle, self.__challenge,
                                          self.__workbench]
        # INIT KEYS
        # add the general keys to everything except Transition, Menu and Pause
        for widget_set in widget_sets:
            widget_set.add_key_command(self.__controls.get_keys(Keys.Pause), Pausing.pause, add_to_widgets=True)
            widget_set.add_key_command(self.__controls.get_keys(Keys.PopupReopen), self.__popup_history.show,
                                       add_to_widgets=True, overwrite=False)

        # debugging keys
        for widget_set in (widget_sets + [self.__transition, self.__menu, self.__pause]):
            for widget in widget_set.get_widget_list():
                widget.widget.add_key_command(self.__controls.get_keys(Keys.PrintScreen), self._print_screen)
                widget.widget.add_key_command(self.__controls.get_keys(Keys.Render), lambda: self.__render(None))

        # special cheat keys
        self.__pause.get_main_widget().add_key_command(self.__controls.get_keys(Keys.CheatInput),
                                                       CheatConfig.cheat_input)
        self.__pause.get_main_widget().add_key_command(self.__controls.get_keys(Keys.CheatList), CheatConfig.cheat_list)

        # INIT STATE MACHINE
        self.__cur_widget_set: MyWidgetSet = self.__transition      # avoid None value
        self.__state_machine = QrogueCUI._StateMachine(self)
        self.__state_machine.change_state(QrogueCUI._State.Menu, self.__seed)

        # MISC
        if Config.debugging():
            self.set_on_draw_update_func(Config.inc_frame_count)

        if self.__save_data.is_fresh_save:
            def knowledge_question(index: int):
                if index == 0: GameplayConfig.set_newbie_mode()
                else: GameplayConfig.set_experienced_mode()
            ConfirmationPopup.ask("WELCOME TO QROGUE!", HelpText.Welcome.text, knowledge_question,
                                  ["Quantum Newbie", "Quantum Experienced"])

        Logger.print_to_console("Ready!")  # notify player that the game is fully loaded

    def _get_absolute_grid_dimensions(self):
        # wrapper because somehow the result is not updated if we pass grid.get_dimensions_absolute() as callback
        return self._grid.get_dimensions_absolute()

    def _refresh_height_width(self) -> None:
        try:
            super(QrogueCUI, self)._refresh_height_width()
            rows, cols = self._grid.get_dimensions_absolute()
            min_rows, min_cols = PyCuiConfig.get_min_dimensions()

            if rows < min_rows or cols < min_cols:
                raise PyCuiConfig.OutOfBoundsError()

        except PyCuiConfig.OutOfBoundsError:
            print("[Qrogue] ERROR!")
            rows, cols = self._grid.get_dimensions_absolute()
            print(f"Current dimensions are ({rows}, {cols}) but at least ({PyCuiConfig.get_min_dimensions()}) is "
                  f"needed. You can fix this by increasing the window size (e.g., maximize it) or adapting the font.")
            print("If you are running it in Windows Powershell you can also try to press ALT+ENTER to change to "
                  "fullscreen mode.")
            raise PyCuiConfig.OutOfBoundsError

    @property
    def is_simulating(self) -> bool:
        return self.__simulator is not None

    @property
    def seed(self) -> int:
        return self.__seed

    def set_refresh_timeout(self, timeout: int):
        """

        :param timeout: timeout in ms or -1 for no timeout
        :return: None
        """
        self._refresh_timeout = timeout
        if self._stdscr is not None:
            # handle the special case of stopping the draw-thread
            if self._refresh_timeout < 0:
                # we have to redraw manually since most likely the last update wasn't recognized by the draw-thread yet
                # calls are taken directly from super._draw() while ignoring input handling and logging
                self._stdscr.erase()
                # Draw status/title bar, and all widgets. Selected widget will be bolded.
                self._draw_status_bars(self._stdscr, self._height, self._width)
                self._draw_widgets()
                # draw the popup if required (although we most likely won't use popups during automated actions)
                if self._popup is not None:
                    self._popup._draw()
                self._stdscr.refresh()

            # since _draw is only called once, we have to set the timeout manually for the screen
            self._stdscr.timeout(self._refresh_timeout)

    def start(self, level_name: Optional[str] = None) -> NewSaveData:
        self.__render([self.__cur_widget_set])

        # We don't want to handle accidental input on startup of the game (e.g., during play-testing this once closed
        # the introduction popup before it was even visible to the player) so we set our init_complete-flag to True
        # after a short delay. Needs to be in an extra thread so _handle_key_presses() can try to handle the accidental
        # input. Otherwise, the input queue would not be cleared and the problem only delayed.
        def call_me():
            time.sleep(QrogueCUI.__INIT_DELAY)
            self.__init_complete = True
        Thread(target=call_me).start()

        if level_name is not None:
            self.__map_manager.load_map(level_name, None, None)

        super(QrogueCUI, self).start()
        return self.__save_data

    def __choose_simulation(self):
        title = f"Enter the path to the {FileTypes.KeyLog.value}-file to simulate:"
        self.__show_input_popup(title, PyCuiColors.WHITE_ON_CYAN, self.__start_simulation)

    def __start_simulation(self, path: str):
        try:
            simulator = GameSimulator(path, in_keylog_folder=True,
                                      get_unlocks=lambda name: LevelInfo.get_level_completion_unlocks(name, True))
            super(QrogueCUI, self)._handle_key_presses(self.__controls.get_key(Keys.SelectionUp))
            self._set_simulator(simulator)
        except FileNotFoundError:
            Logger.instance().show_error(f"File \"{path}\" could not be found!")

    def _set_simulator(self, simulator: GameSimulator, stop_when_finished: bool = False):
        self.__simulator = simulator
        self.__stop_with_simulation_end = stop_when_finished
        simulator.set_controls(self.__controls)

        if simulator.simulates_over_world:
            self.__menu.set_data(simulator.seed)
        else:
            self.__map_manager.load_map(simulator.map_name, None, simulator.seed)

        if simulator.version == Config.version():
            title, text = simulator.version_alright()
        else:
            title, text = simulator.version_warning()
        Popup.generic_info(title, text)

    def _ready_for_input(self, key_pressed: int, gameplay: bool = True) -> bool:
        if self.__last_key != key_pressed:
            self.__last_key = key_pressed
            return True

        if gameplay:
            pause = GameplayConfig.get_option_value(Options.gameplay_key_pause, convert=True)
        else:
            pause = GameplayConfig.get_option_value(Options.simulation_key_pause, convert=True)
        now_time = time.time()
        if now_time - self.__last_input >= pause:
            self.__last_input = now_time
            return True
        return False

    def _handle_key_presses(self, key_pressed):
        # ignore all input before we completed initialization
        if not self.__init_complete: return

        if key_pressed == 0:    # skips the "empty" key press during initialization
            return
        if key_pressed == PyCuiConfig.KEY_CTRL_Q:
            super(QrogueCUI, self)._handle_key_presses(PyCuiConfig.KEY_ESCAPE)
        if self.__simulator is None:
            if self._ready_for_input(key_pressed, gameplay=True):
                if key_pressed == PyCuiConfig.KEY_ESCAPE:
                    pass    # ignore ESC because this makes you leave the CUI
                else:
                    if GameplayConfig.log_keys() and not self.is_simulating:
                        if self.__map_manager.in_level:
                            self.__key_logger.log(self.__controls, key_pressed)
                        OverWorldKeyLogger.instance().log(self.__controls, key_pressed)
                    super(QrogueCUI, self)._handle_key_presses(key_pressed)
        elif key_pressed in self.__controls.get_keys(Keys.StopSimulator):
            Popup.message("Simulator", "stopped Simulator", reopen=False, overwrite=True)
            self.__simulator = None
        else:
            if self._ready_for_input(key_pressed, gameplay=False):
                key = self.__simulator.next()
                if key is None:
                    Popup.message("Simulator", "finished", reopen=False, overwrite=True)
                    self.__simulator = None
                    if self.__stop_with_simulation_end:
                        self.stop()
                else:
                    super(QrogueCUI, self)._handle_key_presses(key)

    def _cycle_widgets(self, reverse: bool = False) -> None:
        pass    # this is neither needed nor allowed in Qrogue

    def _initialize_widget_renderer(self):
        """Function that creates the renderer object that will draw each widget
        """
        if self._renderer is None:
            self._renderer = MultiColorRenderer(self, self._stdscr, self._logger)
        super(QrogueCUI, self)._initialize_widget_renderer()

    def move_focus(self, widget: WidgetWrapper, auto_press_buttons: bool = True) -> None:
        if widget is None:
            Logger.instance().throw(Exception("Widget to focus is None!"))
        if isinstance(widget, PyCuiConfig.PyCuiWidget):
            super(QrogueCUI, self).move_focus(widget, auto_press_buttons)
        else:
            Logger.instance().throw(Exception(
                f"Non-PyCUI widget used in renderer! CurWidgetSet = {self.__cur_widget_set}"))

    def _print_screen(self) -> None:
        text = ""
        for my_widget in self.__cur_widget_set.get_widget_list():
            text += str(my_widget) + "\n"
            text += my_widget.widget.get_title()
            text += "\n"
        PathConfig.new_screen_print(text)

    def apply_widget_set(self, new_widget_set: MyWidgetSet) -> None:
        new_widget_set.reset()
        super().apply_widget_set(new_widget_set)
        self.__cur_widget_set = new_widget_set
        self.move_focus(self.__cur_widget_set.get_main_widget(), auto_press_buttons=False)
        self.__cur_widget_set.update_story_progress(0)  # todo: only used to update HudConfig - change HudConfig directly since we don't alter it anyway?
        self.__cur_widget_set.render()

    def show_message_popup(self, title: str, text: str, color: int = PyCuiColors.WHITE_ON_BLACK) -> None:
        self.__focused_widget = self.get_selected_widget()
        super(QrogueCUI, self).show_message_popup(title, text, color)

    def show_error_popup(self, title: str, text: str) -> None:
        self.__focused_widget = self.get_selected_widget()
        super(QrogueCUI, self).show_error_popup(title, text)

    def __show_message_popup(self, title: str, text: str, position: int, color: int,
                             dimensions: Optional[Tuple[int, int]] = None, reopen: Optional[bool] = None,
                             padding_x: Optional[int] = None) -> None:
        if reopen is None:
            reopen = False
        self.__focused_widget = self.get_selected_widget()
        self._popup = MultilinePopup(self, title, text, color, self._renderer, self._logger, self.__controls,
                                     pos=position, dimensions=dimensions,
                                     situational_callback=(self.__popup_history.back, self.__popup_history.forth),
                                     padding_x=padding_x)
        self.__popup_history.add(self._popup, is_permanent=reopen)

        # immediately close the popup if we want to ignore messages (they are still added to the history if important)
        if CheatConfig.ignore_messages(): self.close_popup()

    def __show_confirmation_popup(self, title: str, text: str, color: int, callback: Callable[[int], None],
                                  answers: Optional[List[str]]):
        self.__focused_widget = self.get_selected_widget()
        self._popup = MultilinePopup(self, title, text, color, self._renderer, self._logger, self.__controls, callback,
                                     answers)

    def __show_input_popup(self, title: str, color: int, callback: Callable[[str], None]) -> None:
        self.__focused_widget = self.get_selected_widget()
        self._popup = popups.TextBoxPopup(self, title, color, callback, self._renderer, False, self._logger)

    def close_popup(self) -> None:
        self.__popup_history.resolve()
        super(QrogueCUI, self).close_popup()
        self.move_focus(self.__focused_widget)
        Popup.on_close()

    def __dummy(self) -> None:
        pass

    def __general_continue(self):
        self.__state_machine.change_state(self.__state_machine.prev_state, None)

    def _switch_to_menu(self, data=None) -> None:
        if self.__key_logger and self.__key_logger.is_initialized:
            self.__key_logger.flush_if_useful()
        if data:
            seed = data
        else:
            seed = RandomManager.instance().get_seed(msg="QroguePyCUI.switch_to_menu()")
        self.__menu.set_data(seed)
        self.apply_widget_set(self.__menu)

    def __show_screen_check(self):
        self.__state_machine.change_state(QrogueCUI._State.ScreenCheck, None)

    def _switch_to_screen_check(self, data=None) -> None:
        self.apply_widget_set(self.__screen_check)

    def __start_playing(self):
        if self.__save_data.check_unlocks(Unlocks.Spaceship):
            ErrorConfig.raise_deletion_exception()
        else:
            # load the newest level (exam phase) by
            self.__map_manager.load_first_uncleared_map()

    def __start_expedition(self):
        if self.__save_data.check_unlocks(Unlocks.Spaceship):
            self.__map_manager.load_expedition()
        else:
            def _callback(selection: int):
                if selection == 0:
                    self.__map_manager.load_expedition()
            CommonQuestions.SkipStoryTutorial.ask(_callback)

    def __start_training(self, direction: Direction):
        robot = BaseBot(CallbackPack.instance().game_over, num_of_qubits=2,
                        gates=[collectibles.XGate(), collectibles.XGate(), collectibles.HGate(), collectibles.CXGate()])
        enemy = Enemy(0, eid=0, target=StateVector([0] * (2**robot.num_of_qubits), num_of_used_gates=0), reward=Score())
        self.__state_machine.change_state(QrogueCUI._State.Training, (robot, enemy))

    def _switch_to_training(self, data=None):
        if data:
            robot, enemy = data
            self.__training.set_data(robot, enemy, False, False)
        self.apply_widget_set(self.__training)

    def __use_workbench(self, direction: Direction, controllable: Controllable):
        self.__state_machine.change_state(QrogueCUI._State.Workbench, self.__save_data)

    def _switch_to_workbench(self, _=None):
        # no data parameter needed
        self.apply_widget_set(self.__workbench)

    def __show_world(self, world: WorldMap = None) -> None:
        ErrorConfig.raise_deletion_exception()

    def _switch_to_navigation(self, data) -> None:
        ErrorConfig.raise_deletion_exception()

    def __start_level(self, seed: int, level: Map) -> None:
        Logger.instance().info(f"Starting level {level.internal_name} with seed={seed}.", from_pycui=False)
        # reset in-level stuff
        self.__save_data.reset_level_events()
        self.__popup_history.reset()

        robot = level.controllable_tile.controllable
        if isinstance(robot, Robot):
            self.__key_logger.reinit(level.seed, level.internal_name)  # the seed used to build the Map
            OverWorldKeyLogger.instance().level_start(level.internal_name)
            robot.reset_score()     # reset the score at the start of each level
            self.__save_data.restart_level_timer()

            self.__pause.set_data(robot, level.name, None)
            self.__state_machine.change_state(QrogueCUI._State.Explore, level)
        else:
            Logger.instance().throw(ValueError(f"Tried to start a level with a non-Robot: {robot}"))

    def __game_over(self) -> None:
        def callback(confirmed: int):
            if confirmed == 0:
                self.__map_manager.reload()
            elif confirmed == 1:
                if self.__save_data.check_unlocks(Unlocks.Spaceship):
                    self.__state_machine.change_state(QrogueCUI._State.Spaceship, None)
                else:
                    self.__state_machine.change_state(QrogueCUI._State.Menu, None)
        if self.__map_manager.in_tutorial_world:
            ConfirmationPopup.ask(Config.system_name(), f"Your Robot is out of energy.\n"
                                                        f"How do you want to continue?", callback,
                                                        ["Restart lesson", "Back to menu"])
        else:
            ConfirmationPopup.ask(Config.system_name(), f"Your Robot is out of energy. Emergency departure initiated.\n"
                                                        "Do you want to retry the expedition?",
                                                        callback, ["Yes", "No"])

    def __start_fight(self, robot: Robot, enemy: Enemy, direction: Direction) -> None:
        self.__state_machine.change_state(QrogueCUI._State.Fight, (robot, enemy))

    def __start_boss_fight(self, robot: Robot, boss: Boss, direction: Direction):
        self.__state_machine.change_state(QrogueCUI._State.BossFight, (robot, boss))

    def _switch_to_pause(self, data=None) -> None:
        self.apply_widget_set(self.__pause)

    def __pause_game(self) -> None:
        self.__state_machine.change_state(QrogueCUI._State.Pause, None)

    def _switch_to_explore(self, data: Optional[Union[Map, Tuple[Optional[Map], Optional[bool]]]]) -> None:
        if data is not None:
            if isinstance(data, Map):
                self.__explore.set_data(data)
            else:
                map_, undo_last_move = data
                if map_ is not None:
                    self.__explore.set_data(map_)
                if undo_last_move:
                    self.__explore.undo_last_move()
        self.apply_widget_set(self.__explore)

    def __continue_explore(self, undo_last_move: bool = False) -> None:
        self.__state_machine.change_state(QrogueCUI._State.Explore, (None, undo_last_move))

    def _switch_to_fight(self, data) -> None:
        if data is not None:
            robot = data[0]
            enemy = data[1]
            self.__fight.set_data(robot, enemy, self.__map_manager.in_expedition,
                                  self.__map_manager.show_individual_qubits)
        self.apply_widget_set(self.__fight)

    def _switch_to_boss_fight(self, data) -> None:
        if data is not None:
            player = data[0]
            boss = data[1]
            self.__boss_fight.set_data(player, boss, self.__map_manager.in_expedition,
                                       self.__map_manager.show_individual_qubits)
        self.apply_widget_set(self.__boss_fight)

    def __open_riddle(self, robot: Robot, riddle: Riddle):
        self.__state_machine.change_state(QrogueCUI._State.Riddle, (robot, riddle))

    def _switch_to_riddle(self, data) -> None:
        if data is not None:
            player = data[0]
            riddle = data[1]
            self.__riddle.set_data(player, riddle, self.__map_manager.in_expedition,
                                   self.__map_manager.show_individual_qubits)
        self.apply_widget_set(self.__riddle)

    def __open_challenge(self, robot: Robot, challenge: Challenge):
        self.__state_machine.change_state(QrogueCUI._State.Challenge, (robot, challenge))

    def _switch_to_challenge(self, data) -> None:
        if data is not None:
            robot = data[0]
            challenge = data[1]
            self.__challenge.set_data(robot, challenge, self.__map_manager.in_expedition,
                                      self.__map_manager.show_individual_qubits)
        self.apply_widget_set(self.__challenge)

    def __visit_shop(self, robot: Robot, items: "list of ShopItems"):
        self.__state_machine.change_state(QrogueCUI._State.Shop, (robot, items))

    def _switch_to_shop(self, data) -> None:
        if data is not None:
            player = data[0]
            items = data[1]
            self.__shop.set_data(player, items)
        self.apply_widget_set(self.__shop)

    def _execute_transition(self, text_scrolls: List[TransitionWidgetSet.TextScroll], next_state: "QrogueCUI._State",
                            next_data: Any, additional_callback: Optional[Callable] = None):
        def callback():
            self.__state_machine.change_state(next_state, next_data)
            if additional_callback is not None:
                additional_callback()
        self.__state_machine.change_state(QrogueCUI._State.Transition, (text_scrolls, callback))

    def _switch_to_transition(self, data) -> None:
        texts, continue_ = data
        self.__transition.set_data(texts, continue_)
        self.apply_widget_set(self.__transition)

    def __render(self, renderables: Optional[List[Renderable]]):
        if renderables is None:
            renderables = self.__cur_widget_set.get_widget_list()
        for r in renderables:
            r.render()
