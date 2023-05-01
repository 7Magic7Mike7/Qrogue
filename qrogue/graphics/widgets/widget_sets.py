import threading
from threading import Timer
import time
from abc import abstractmethod, ABC
from typing import List, Callable, Optional, Tuple, Any

import py_cui
from py_cui.widget_set import WidgetSet

from qrogue.game.logic import StateVector
from qrogue.game.logic.actors import Boss, Enemy, Riddle, Robot
from qrogue.game.logic.actors.puzzles import Target, Challenge
from qrogue.game.logic.collectibles import ShopItem, Collectible, Instruction, GateType
from qrogue.game.world.map import Map
from qrogue.game.world.navigation import Direction
from qrogue.graphics.popups import Popup
from qrogue.graphics.rendering import ColorRules
from qrogue.graphics.widget_base import WidgetWrapper
from qrogue.util import CommonPopups, Config, Controls, GameplayConfig, HelpText, HelpTextType, Logger, PathConfig, \
    RandomManager, AchievementManager, Keys, UIConfig, HudConfig, ColorConfig, Options, PuzzleConfig
from qrogue.util.achievements import Ach, Unlocks

from qrogue.graphics.widgets import Renderable, Widget, MyBaseWidget
from qrogue.graphics.widgets.my_widgets import SelectionWidget, CircuitWidget, MapWidget, SimpleWidget, HudWidget, \
    OutputStateVectorWidget, CircuitMatrixWidget, TargetStateVectorWidget, InputStateVectorWidget, MyMultiWidget, \
    HistoricWrapperWidget


class MyWidgetSet(WidgetSet, Renderable, ABC):
    """
    Class that handles different sets of widgets so we can easily switch between different screens.
    """

    @staticmethod
    def create_hud_row(widget_set: "MyWidgetSet") -> HudWidget:
        hud = widget_set.add_block_label('HUD', 0, 0, row_span=UIConfig.HUD_HEIGHT, column_span=UIConfig.HUD_WIDTH,
                                         center=False)
        hud.toggle_border()
        widgets = [hud]
        width = UIConfig.WINDOW_WIDTH-UIConfig.HUD_WIDTH

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

    def add_key_command(self, keys: List[int], command: Callable[[], Any], add_to_widgets: bool = False,
                        overwrite: bool = True) -> Any:
        for key in keys:
            if overwrite or key not in self._keybindings:
                super(MyWidgetSet, self).add_key_command(key, command)
        if add_to_widgets:
            for widget in self.get_widget_list():
                widget.widget.add_key_command(keys, command, overwrite)

    def update_story_progress(self, progress: int):
        self.__progress = progress
        # globally update HUD based on the progress
        HudConfig.ShowMapName = True
        HudConfig.ShowKeys = True
        HudConfig.ShowEnergy = False    # Ach.check_unlocks(Unlocks.ShowEnergy, progress)

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
                 start_expedition_callback: Callable[[], None], stop_callback: Callable[[], None],
                 choose_simulation_callback: Callable[[], None]):
        self.__seed = 0
        self.__quick_start = quick_start_callback
        self.__start_playing = start_playing_callback
        self.__start_expedition = start_expedition_callback
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
            choices.append("CONTINUE JOURNEY\n")
            callbacks.append(self.__quick_start)

        else:
            choices.append("START YOUR JOURNEY\n")
            callbacks.append(self.__start_playing)

        #choices.append("START AN EXPEDITION\n")
        #callbacks.append(self.__start_expedition)

        # choices.append("OPTIONS\n")  # for more space between the rows we add "\n"
        # callbacks.append(self.__options)
        choices.append("EXIT\n")
        callbacks.append(self.__stop)
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


class TransitionWidgetSet(MyWidgetSet):
    class TextScroll:
        __DEFAULT_TEXT_DELAY = 0.01     # 0 can lead to messed up render order so we just use a very small number
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
            widget = self.add_block_label("Frame count", 0, UIConfig.WINDOW_WIDTH-1)
            self.__frame_count = SimpleWidget(widget)

        # todo autoscroll?

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
        self.__display_text += new_text     # append the remaining text

        self.__text.set_data(self.__display_text)
        self.__text.render()
        self._unlock(self.__display_lock)

        if Config.debugging():
            self.__frame_count.set_data(Config.frame_count())
            self.__frame_count.render()

    def __update_confirm_text(self, confirm: bool, transition_end: bool = False):
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

    def set_data(self, text_scrolls: List[TextScroll], continue_callback: Callable[[], None]):
        assert len(text_scrolls) > 0, "Empty list of texts provided!"

        self.__text_scrolls = text_scrolls
        self.__continue = continue_callback

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
        #self.__confirm.set_data("Press [Confirm] for next text.")  # todo how to handle thread states?


class PauseMenuWidgetSet(MyWidgetSet):
    __HELP_TEXTS = (
        [
            "Game",
            "Controls", "Fight",
            "Riddle",
            "Pause",
        ],
        [
            HelpText.get(HelpTextType.Game),
            HelpText.get(HelpTextType.Controls), HelpText.get(HelpTextType.Fight),
            HelpText.get(HelpTextType.Riddle),
            HelpText.get(HelpTextType.Pause),
         ]
    )

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_callback: Callable[[], None], save_callback: Callable[[], Tuple[bool, CommonPopups]],
                 exit_run_callback: Callable[[], None], restart_callback: Callable[[], None]):
        super().__init__(logger, root, render)
        self.__continue_callback = continue_callback
        self.__save_callback = save_callback
        self.__exit_run = exit_run_callback
        self.__restart_callback = restart_callback
        self.__achievement_manager = None

        self.__hud = MyWidgetSet.create_hud_row(self)

        choices = self.add_block_label('Choices', UIConfig.HUD_HEIGHT, 0, row_span=UIConfig.NON_HUD_HEIGHT,
                                       column_span=UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__choices = SelectionWidget(choices, controls, stay_selected=True)
        self.__choices.set_data(data=(
            ["Continue", "Restart", "Save", "Manual", "Options", "Exit"],
            [self.__continue, self.__restart, self.__save, self.__help, self.__options,
             self.__exit]
        ))  # todo add back achievements

        details = self.add_block_label('Details', UIConfig.HUD_HEIGHT, UIConfig.PAUSE_CHOICES_WIDTH,
                                       row_span=UIConfig.WINDOW_HEIGHT-UIConfig.HUD_HEIGHT,
                                       column_span=UIConfig.WINDOW_WIDTH-UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__details = SelectionWidget(details, controls, is_second=True)

        description = self.add_block_label('Description', UIConfig.WINDOW_HEIGHT-UIConfig.PAUSE_DESCRIPTION_HEIGHT,
                                           UIConfig.PAUSE_CHOICES_WIDTH, row_span=UIConfig.PAUSE_DESCRIPTION_HEIGHT,
                                           column_span=UIConfig.WINDOW_WIDTH-UIConfig.PAUSE_CHOICES_WIDTH, center=True)
        self.__description = SimpleWidget(description)

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
        # hide most options for tutorial's sake
        options = GameplayConfig.get_options() #[Options.allow_implicit_removal, Options.allow_multi_move])
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
                    Popup.message(CommonPopups.OptionsSaved.title, CommonPopups.OptionsSaved.text, reopen=False,
                                  on_close_callback=self.__focus_choices)
                else:
                    CommonPopups.OptionsNotSaved.show()
                return False
            else:
                # reset changes
                try:
                    Config.load_gameplay_config()   # todo error message or is the file exception good enough?
                except FileNotFoundError as error:
                    Logger.instance().throw(error)
                return True     # index out of range and no special case -> go back

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

    def set_data(self, robot: Optional[Robot], map_name: str, achievement_manager: AchievementManager):
        # todo maybe needs some overhaul?
        self.__hud.set_data((robot, map_name, None))
        self.__achievement_manager = achievement_manager

    def reset(self) -> None:
        self.__choices.render_reset()
        self.__details.render_reset()
        self.__description.render_reset()


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

        [setup_hotkey(i) for i in range(10)]

    @property
    def _map_widget(self) -> MapWidget:
        return self.__map_widget

    def get_main_widget(self) -> WidgetWrapper:
        return self.__map_widget.widget

    def update_story_progress(self, progress: int):
        super(MapWidgetSet, self).update_story_progress(progress)
        self.__map_widget.try_to_start_map()

    def reset(self) -> None:
        self.__map_widget.render_reset()


class ExploreWidgetSet(MapWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI):
        super().__init__(controls, render, logger, root)
        self.__hud = MyWidgetSet.create_hud_row(self)
        ColorRules.apply_map_rules(self._map_widget.widget)

    def set_data(self, map_: Map) -> None:
        controllable = map_.controllable_tile.controllable
        if isinstance(controllable, Robot):
            self.__hud.set_data((controllable, map_.name, ""))  # todo fix/remove
        else:
            self.__hud.reset_data()
        self._map_widget.set_data(map_)
        # map_.start()  # we cannot start the map here because the widget_set has not been applied yet

    def get_widget_list(self) -> List[Widget]:
        return [
            self.__hud,
            self._map_widget
        ]

    def render(self) -> None:
        start = time.time()
        super(ExploreWidgetSet, self).render()
        duration = time.time() - start
        self.__hud.update_render_duration(duration)
        self.__hud.render()


class NavigationWidgetSet(MapWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI):
        super().__init__(controls, render, logger, root)
        ColorRules.apply_navigation_rules(self._map_widget.widget)

    def set_data(self, map_: Map) -> None:
        self._map_widget.set_data(map_)

    def get_widget_list(self) -> List[Widget]:
        return [self._map_widget]


class ReachTargetWidgetSet(MyWidgetSet, ABC):
    __CHOICE_COLUMNS = 2
    __DETAILS_COLUMNS = 3
    _DETAILS_INFO_THEN_EDIT = 0
    _DETAILS_INFO_THEN_CHOICES = 2
    _DETAILS_EDIT = 3
    _DEFAULT_FAIL_MESSAGE = "That's not yet the correct solution."

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[], None], flee_choice: str = "Flee"):
        super().__init__(logger, root, render)
        self.__flee_choice = flee_choice
        self._continue_exploration_callback = continue_exploration_callback
        self._robot: Optional[Robot] = None
        self._target: Optional[Target] = None
        self.__num_of_qubits = -1   # needs to be an illegal value because we definitely want to reposition all
        # dependent widgets for the first usage of this WidgetSet
        self._details_content = None
        self.__in_expedition = False

        posy = 0
        posx = 0
        row_span = UIConfig.stv_height(2)   # doesn't matter since we reposition the dependent widgets anyway
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
        ColorRules.apply_circuit_rules(circuit)
        self.__circuit = CircuitWidget(circuit, controls)
        posy += circuit_height

        # wrap the widget that tell us about the puzzle state
        self.__history_widget = HistoricWrapperWidget((self.__circuit, self.__circuit_matrix, self.__stv_robot),
                                                      render_widgets=True)

        def jump_to_present(key: Keys):
            if GameplayConfig.get_option_value(Options.auto_reset_history, convert=True):
                self.__history_widget.jump_to_present(render=True)

        # the remaining widgets are the user interface
        choices = self.add_block_label('Choices', posy, 0, row_span=UIConfig.WINDOW_HEIGHT - posy,
                                       column_span=UIConfig.PUZZLE_CHOICES_WIDTH, center=True)
        choices.toggle_border()
        self._choices = SelectionWidget(choices, controls, columns=self.__CHOICE_COLUMNS, on_key_press=jump_to_present)
        self.__init_choices()

        details = self.add_block_label('Details', posy, UIConfig.PUZZLE_CHOICES_WIDTH,
                                       row_span=UIConfig.WINDOW_HEIGHT - posy,
                                       column_span=UIConfig.WINDOW_WIDTH - UIConfig.PUZZLE_CHOICES_WIDTH, center=True)
        details.toggle_border()
        details.activate_individual_coloring()  # TODO: current reward highlight version is not satisfying
        self._details = SelectionWidget(details, controls, columns=self.__DETAILS_COLUMNS, is_second=True,
                                        on_key_press=jump_to_present)

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
                        self._details_content == self._DETAILS_EDIT:
                    # last selection possibility in edit is "Back"
                    self.__details_back()
                elif self._details_content == self._DETAILS_INFO_THEN_EDIT:
                    self._details_content = self._DETAILS_EDIT
                    self.__choices_edit()
                    self.render()
                else:
                    # else we selected a gate, and we initiate the placing process
                    Widget.move_focus(self.__circuit, self)
        self._details.widget.add_key_command(controls.get_keys(Keys.Cancel), self.__details_back)
        self._details.widget.add_key_command(controls.action, use_details)

        def gate_guide():
            gates = self._robot.get_available_instructions()
            if 0 <= self._details.index < len(gates):
                gate = gates[self._details.index].gate_type
                Popup.generic_info(gate.short_name, Instruction.get_description(gate))
        self._details.widget.add_key_command(controls.get_keys(Keys.Help), gate_guide)

        def use_circuit():
            success, gate = self.__circuit.perform_action()     # todo gate variable seems useless or at least misused
            if success:
                if self._details.validate_index():
                    if gate is None:
                        self.__choices_edit()
                    else:
                        self._details.update_text(gate.selection_str(), self._details.index)
                self.__choices_commit()
                Widget.move_focus(self._details, self)
                self.render()
        self.__circuit.widget.add_key_command(controls.action, use_circuit)

        def cancel_circuit():
            self.__circuit.abort_action()
            Widget.move_focus(self._details, self)
            self.render()
        self.__circuit.widget.add_key_command(controls.get_keys(Keys.Cancel), cancel_circuit)

        # situational keys for travelling through history need to be set last because everything needs to be
        # initialized first for the hidden render()-call to succeed
        def history_back():
            if GameplayConfig.get_option_value(Options.enable_puzzle_history, convert=True):
                self.__history_widget.back(render=True)

        def history_forth():
            if GameplayConfig.get_option_value(Options.enable_puzzle_history, convert=True):
                self.__history_widget.forth(render=True)
        self.add_key_command(controls.get_keys(Keys.Situational1), history_back, add_to_widgets=True)
        self.add_key_command(controls.get_keys(Keys.Situational2), history_forth, add_to_widgets=True)

    def __init_choices(self):
        texts = ["Edit"]
        callbacks = [self.__choices_edit]

        if self.__in_expedition or Ach.check_unlocks(Unlocks.CircuitReset, self._progress):
            texts.append("Reset")
            callbacks.append(self.__choices_reset)

        if self.__in_expedition or Ach.check_unlocks(Unlocks.PuzzleFlee, self._progress):
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

    @property
    def _is_expedition(self) -> bool:
        return self.__in_expedition

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
                shrinkage = 1   # magic number that turned out to give a good visual result
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

                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span + 2 * shrinkage)
            elif num_of_qubits == 4:
                # todo problem with 4 qubits: out has not enough space, hence, its coloring doesn't work
                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span)
                self._choices.widget.reposition(row=UIConfig.WINDOW_HEIGHT - 1, row_span=1)
                self._details.widget.reposition(row=UIConfig.WINDOW_HEIGHT - 1, row_span=1)
            else:
                self.__circuit.widget.reposition(row=UIConfig.HUD_HEIGHT + row_span + 1)    # + 1 for visuals

    def get_main_widget(self) -> WidgetWrapper:
        return self._choices.widget

    def update_story_progress(self, progress: int):
        super(ReachTargetWidgetSet, self).update_story_progress(progress)
        self.__init_choices()

    def set_data(self, robot: Robot, target: Target, in_expedition: bool) -> None:
        self._robot = robot
        self._target = target
        self.__in_expedition = in_expedition

        self._reposition_widgets(robot.num_of_qubits)

        # from a code readers perspective the reset would make more sense in switch_to_fight() etc. but then we would
        # have to add it to multiple locations and have the risk of forgetting to add it for new ReachTargetWidgetSets
        if GameplayConfig.auto_reset_circuit():
            robot.reset_circuit()

        self._hud.set_data((robot, None, None))  # don't overwrite the current map name
        self.__circuit.set_data(robot.grid)

        self.__input_stv.set_data(StateVector.create_zero_state_vector(robot.num_of_qubits))
        self.__mul_widget.set_data(self._sign_offset + "x")
        self.__result_widget.set_data(self._sign_offset + "=")
        self.__update_calculation(False)
        self.__stv_target.set_data(target.state_vector)

        self.__init_choices()

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
            self._choices,
            self._details
        ]

    def reset(self) -> None:
        self._choices.render_reset()
        self._details.render_reset()
        self.__history_widget.clean_history()       # todo Note: this also cleans history when going to the pause menu!

    def __update_calculation(self, target_reached: bool):
        diff_stv = self._target.state_vector.get_diff(self._robot.state_vector)

        self.__circuit_matrix.set_data(self._robot.circuit_matrix)
        self.__stv_robot.set_data((self._robot.state_vector, diff_stv), target_reached=target_reached)
        self.__history_widget.save_state(rerender=True, force=False)

        if diff_stv.is_zero:
            self.__eq_widget.set_data(self._sign_offset + "===")
        else:
            self.__eq_widget.set_data(self._sign_offset + "=/=")

    def __choices_edit(self) -> bool:
        choices, objects = [], []
        for instruction in self._robot.backpack:
            choices.append(instruction.selection_str())
            objects.append(instruction)
        choices = SelectionWidget.wrap_in_hotkey_str(choices)

        # add commands
        if Ach.check_unlocks(Unlocks.GateRemove, self._progress):
            choices.append("Remove")
        choices.append(MyWidgetSet.BACK_STRING)

        self._details.set_data(data=((choices, objects), [self.__choose_instruction]))
        self._details_content = self._DETAILS_EDIT
        return True

    def __choose_instruction(self, index: int) -> bool:
        if 0 <= index < self._robot.backpack.used_capacity:
            cur_instruction = self._details.selected_object
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
        else:
            if index == self._details.num_of_choices - 1:   # "Back" is always last
                return True     # go back to choices
            else:   # "Remove" was chosen
                if self._robot.has_empty_circuit:
                    CommonPopups.NoGatePlaced.show()
                    return False
                else:
                    #self.__circuit.start_gate_placement(None)
                    self.__circuit.start_gate_removal()
                    self.render()
                    return True

    def __choices_commit(self):
        if self._target is None:
            Logger.instance().error("Error! Target is not set!", from_pycui=False)
            return False
        self._robot.update_statevector()
        success, reward = self._target.is_reached(self._robot.state_vector)
        self.__update_calculation(success)
        self.render()
        if success:
            if reward is None:
                self._details.set_data(data=(
                    [f"Congratulations, you solved the "
                     f"{ColorConfig.highlight_object('Puzzle')}!"],
                    [self._continue_exploration_callback]
                ))
            else:
                Logger.instance().assertion(isinstance(reward, Collectible),
                                            f"Error! Reward is not a Collectible: {reward}")

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
                 continue_exploration_callback: Callable[[], None]):
        super(FightWidgetSet, self).__init__(controls, render, logger, root, continue_exploration_callback)
        self.__flee_check = None

    def set_data(self, robot: Robot, target: Enemy, in_expedition: bool):
        super(FightWidgetSet, self).set_data(robot, target, in_expedition)
        self.__flee_check = target.flee_check

    def _on_commit_fail(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            self._robot.game_over_check()
        self._details_content = ReachTargetWidgetSet._DETAILS_EDIT
        return True

    def _choices_flee(self) -> bool:
        extra_text = ""
        if GameplayConfig.get_option_value(Options.energy_mode):
            if self._robot.cur_energy > self._target.flee_energy:
                damage_taken, _ = self._robot.decrease_energy(amount=self._target.flee_energy)
                extra_text = f"Your Qubot lost {damage_taken} energy."
            else:
                CommonPopups.NotEnoughEnergyToFlee.show()
                return False    # don't switch to details widget

        if self.__flee_check():
            self._details.set_data(data=(
                [f"Fled successfully. {extra_text}"],
                [self._continue_exploration_callback]
            ))
        else:
            self._details.set_data(data=(
                [f"Failed to flee. {extra_text}"],
                [self._empty_callback]
            ))
            self._details_content = ReachTargetWidgetSet._DETAILS_INFO_THEN_EDIT
        return True


class BossFightWidgetSet(FightWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[], None]):
        super().__init__(controls, render, logger, root, continue_exploration_callback)

    def set_data(self, robot: Robot, target: Boss, in_expedition: bool):
        super(BossFightWidgetSet, self).set_data(robot, target, in_expedition)

    def _on_commit_fail(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            self._robot.decrease_energy(PuzzleConfig.BOSS_FAIL_DAMAGE)
        return super(BossFightWidgetSet, self)._on_commit_fail()


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
        self.__hud.set_data((robot, None, None))    # don't overwrite the current map name
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
        if self.__robot.backpack.spend_coins(self.__cur_item.price):
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
    __TRY_PHRASING = "edits"

    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[None], None]):
        super().__init__(controls, render, logger, root, continue_exploration_callback, "Give Up")

    def set_data(self, robot: Robot, target: Riddle, in_expedition: bool) -> None:
        super(RiddleWidgetSet, self).set_data(robot, target, in_expedition)
        self._hud.set_data((robot, None, f"Remaining {RiddleWidgetSet.__TRY_PHRASING}: {target.attempts}"))

    def _on_commit_fail(self) -> bool:
        if not self._target.can_attempt:
            self._details.set_data(data=(
                [f"You couldn't solve the riddle within the given number of {RiddleWidgetSet.__TRY_PHRASING}. "
                 f"It vanished together with its reward."],
                [self._continue_exploration_callback]
            ))
        self._hud.update_situational(f"Remaining {RiddleWidgetSet.__TRY_PHRASING}: {self._target.attempts}")
        self._details_content = ReachTargetWidgetSet._DETAILS_EDIT
        return True

    def _choices_flee(self) -> bool:
        if self._target.can_attempt:
            self._details.set_data(data=(
                [f"Abort - you can still try again later", "Continue"],
                [self._continue_exploration_callback, self._empty_callback]
            ))
            self._details_content = ReachTargetWidgetSet._DETAILS_INFO_THEN_EDIT
        else:
            self._details.set_data(data=(
                [f"Abort - but you don't have any {RiddleWidgetSet.__TRY_PHRASING} left to try again later!",
                 "Continue"],
                [self._continue_exploration_callback, self._empty_callback]
            ))
        return True


class ChallengeWidgetSet(ReachTargetWidgetSet):
    def __init__(self, controls: Controls, render: Callable[[List[Renderable]], None], logger, root: py_cui.PyCUI,
                 continue_exploration_callback: Callable[[], None]):
        super().__init__(controls, render, logger, root, continue_exploration_callback)

    def set_data(self, robot: Robot, target: Challenge, in_expedition: bool) -> None:
        super(ChallengeWidgetSet, self).set_data(robot, target, in_expedition)
        if target.min_gates == target.max_gates:
            constraints = f"Constraints: Use exactly {target.min_gates} gates."
        else:
            constraints = f"Constraints: Use between {target.min_gates} and {target.max_gates} gates."
        self._hud.update_situational(constraints)

    def _on_commit_fail(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            self._robot.game_over_check()
        self._details_content = ReachTargetWidgetSet._DETAILS_EDIT
        return True

    def _choices_flee(self) -> bool:
        if GameplayConfig.get_option_value(Options.energy_mode):
            if self._robot.cur_energy > self._target.flee_energy:
                _, _ = self._robot.decrease_energy(amount=self._target.flee_energy)
            else:
                CommonPopups.NotEnoughEnergyToFlee.show()
                return False  # don't switch to details widget

        self._details.set_data(data=(
            ["You successfully fled!"],
            [self._continue_exploration_callback]
        ))
        return True
