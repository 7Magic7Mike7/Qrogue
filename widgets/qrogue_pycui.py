import curses
import time
from enum import Enum
from typing import List

import py_cui

from game.actors.boss import Boss
from game.actors.enemy import Enemy
from game.actors.riddle import Riddle
from game.actors.robot import Robot, TestBot
from game.callbacks import CallbackPack
from game.controls import Controls, Pausing, Keys
from game.map import tiles
from game.map.map import Map
from game.map.navigation import Direction
from game.map.tutorial import Tutorial
from game.save_data import SaveData
from util.config import PathConfig, ColorConfig, CheatConfig, GameplayConfig, Config
from util.game_simulator import GameSimulator
from util.key_logger import KeyLogger
from util.logger import Logger
from widgets.color_rules import MultiColorRenderer
from widgets.my_popups import Popup, MultilinePopup
from widgets.renderable import Renderable
from widgets.spaceship import SpaceshipWidgetSet
from widgets.widget_sets import ExploreWidgetSet, FightWidgetSet, MyWidgetSet, ShopWidgetSet, \
    RiddleWidgetSet, BossFightWidgetSet, PauseMenuWidgetSet, MenuWidgetSet, WorkbenchWidgetSet


class QrogueCUI(py_cui.PyCUI):
    def __init__(self, seed: int, controls: Controls, width: int = 8, height: int = 9):
        super().__init__(width, height)
        self.set_title(f"Qrogue {Config.version()}")
        Logger.instance().set_popup(self.show_message_popup, self.show_error_popup)
        Popup.update_popup_functions(self.__show_popup)
        CheatConfig.init(self.__show_popup, self.__show_input_popup)

        self.__key_logger = None  #KeyLogger(seed)
        self.__simulator = None
        self.__state_machine = StateMachine(self)
        self.__seed = seed
        self.__controls = controls
        self.__last_input = time.time()
        self.__last_key = None
        self.__focused_widget = None

        self.__save_data = SaveData() # todo load data

        cbp = CallbackPack(self.__start_expedition, self.__start_fight, self.__start_boss_fight, self.__open_riddle,
                           self.__visit_shop)
        self.__menu = MenuWidgetSet(controls, self.__render, Logger.instance(), self, self.__start_playing, self.stop,
                                    self.__choose_simulation)
        self.__pause = PauseMenuWidgetSet(controls, self.__render, Logger.instance(), self, self.__general_continue,
                                          self.switch_to_menu)

        self.__spaceship = SpaceshipWidgetSet(controls, Logger.instance(), self, self.__render, cbp, self.__seed,
                                              self.__save_data)
        self.__workbench = WorkbenchWidgetSet(controls, Logger.instance(), self, self.__render,
                                              self.__continue_spaceship)

        self.__explore = ExploreWidgetSet(controls, self.__render, Logger.instance(), self)
        self.__fight = FightWidgetSet(controls, self.__render, Logger.instance(), self, self.__continue_explore,
                                      self.__end_of_gameplay)
        self.__boss_fight = BossFightWidgetSet(controls, self.__render, Logger.instance(), self,
                                               self.__continue_explore, self.__end_of_gameplay, self.__won_tutorial)
        self.__riddle = RiddleWidgetSet(controls, self.__render, Logger.instance(), self, self.__continue_explore)
        self.__shop = ShopWidgetSet(controls, self.__render, Logger.instance(), self, self.__continue_explore)

        self.__cur_widget_set = None
        self.__init_keys()

        self.__state_machine.change_state(State.Menu, None)
        self.__game_started = False

    @property
    def simulating(self) -> bool:
        return self.__simulator is not None

    def start(self):
        self.render()
        super(QrogueCUI, self).start()

    def __choose_simulation(self):
        title = "Enter the path to the .qrkl-file to simulate:"
        self.__show_input_popup(title, py_cui.WHITE_ON_CYAN, self.__start_simulation)

    def __start_simulation(self, path: str):
        if not path.endswith(".qrkl"):
            path += ".qrkl"
        try:
            self.__simulator = GameSimulator(self.__controls, path, in_keylog_folder=True)
            self.__menu.simulate_with_seed(self.__simulator.seed)
            # go back to the original position of the cursor and start the game
            super(QrogueCUI, self)._handle_key_presses(self.__controls.get_key(Keys.SelectionUp))
            super(QrogueCUI, self)._handle_key_presses(self.__controls.get_key(Keys.SelectionUp))
            super(QrogueCUI, self)._handle_key_presses(self.__controls.get_key(Keys.Action))
            if self.__simulator.version == Config.version():
                __space = "Space"
                Popup.message("Starting Simulation", f"You started a run with \nseed = {self.__simulator.seed}\n"
                                                     f"recorded at {self.__simulator.time}.\n"
                                                     f"Press {ColorConfig.highlight_key(__space)} to execute the "
                                                     "simulation step by step. Alternatively, if you keep it pressed "
                                                     "the simulation will be executed automatically with short delays "
                                                     "after each step until you let go of Space again.")
            else:
                Popup.message("Simulating other version", "You try to simulate the run of a different game version.\n"
                                                          f"Your version: {Config.version()}\n"
                                                          f"Version you try to simulate: {self.__simulator.version}\n"
                                                          "This is not supported and can cause problems. Only "
                                                          "continue if you know what you do! Else close this popup "
                                                          "and press ESC to abort the simulation.")
        except FileNotFoundError:
            Logger.instance().show_error(f"File \"{path}\" could not be found!")

    def _ready_for_input(self, key_pressed: int, gameplay: bool = True) -> bool:
        if self.__last_key != key_pressed:
            self.__last_key = key_pressed
            return True

        if gameplay:
            pause = GameplayConfig.gameplay_key_pause()
        else:
            pause = GameplayConfig.simulation_key_pause()
        now_time = time.time()
        if now_time - self.__last_input >= pause:
            self.__last_input = now_time
            return True
        return False

    def _handle_key_presses(self, key_pressed):
        if key_pressed == py_cui.keys.KEY_CTRL_Q:
            super(QrogueCUI, self)._handle_key_presses(py_cui.keys.KEY_ESCAPE)
        if self.__simulator is None:
            if self._ready_for_input(key_pressed, gameplay=True):
                if key_pressed == py_cui.keys.KEY_ESCAPE:
                    pass    # ignore ESC because this makes you leave the CUI
                else:
                    if GameplayConfig.log_keys() and self.__game_started and not self.simulating:
                        self.__key_logger.log(self.__controls, key_pressed)
                    super(QrogueCUI, self)._handle_key_presses(key_pressed)
        elif key_pressed in self.__controls.get_keys(Keys.StopSimulator):
            Popup.message("Simulator", "stopped Simulator")
            self.__simulator = None
        else:
            if self._ready_for_input(key_pressed, gameplay=False):
                key = self.__simulator.next()
                if key:
                    super(QrogueCUI, self)._handle_key_presses(key)
                else:
                    Popup.message("Simulator", "finished")
                    self.__simulator = None

    def _draw(self, stdscr) -> None:    # overridden because we want to ignore mouse events
        """Main CUI draw loop called by start()

        Parameters
        --------
        stdscr : curses Standard screen
            The screen buffer used for drawing CUI elements
        """

        self._stdscr = stdscr
        key_pressed = 0

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()
        #curses.mousemask(curses.ALL_MOUSE_EVENTS)   # ignore mouse events for our CUI
        # stdscr.nodelay(False)
        #stdscr.keypad(True)

        # Initialization functions. Generates colors and renderer
        self._initialize_colors()
        self._initialize_widget_renderer()

        # If user specified a refresh timeout, apply it here
        if self._refresh_timeout > 0:
            self._stdscr.timeout(self._refresh_timeout)

        # If user sets non-default border characters, update them here
        if self._border_characters is not None and self._renderer is not None:
            self._renderer._set_border_renderer_chars(self._border_characters)

        # Loop where key_pressed is the last character pressed. Wait for exit key while no popup or focus mode
        while key_pressed != self._exit_key or self._in_focused_mode or self._popup is not None:

            try:
                # If we call stop, we want to break out of the main draw loop
                if self._stopped:
                    break

                # Initialization and size adjustment
                stdscr.erase()

                # If the user defined an update function to fire on each draw call,
                # Run it here. This can of course be also handled user-side
                # through a separate thread.
                if self._on_draw_update_func is not None:
                    self._on_draw_update_func()

                # This is what allows the CUI to be responsive. Adjust grid size based on current terminal size
                # Resize the grid and the widgets if there was a resize operation
                if key_pressed == curses.KEY_RESIZE:
                    try:
                        self._refresh_height_width()
                    except py_cui.errors.PyCUIOutOfBoundsError as e:
                        self._logger.info('Resized terminal too small')
                        self._display_window_warning(stdscr, str(e))

                # Here we handle mouse click events globally, or pass them to the UI element to handle
                elif key_pressed == curses.KEY_MOUSE:
                    self._logger.info('Detected mouse click')

                    valid_mouse_event = True
                    try:
                        id, x, y, _, mouse_event = curses.getmouse()
                    except curses.error as e:
                        valid_mouse_event = False
                        self._logger.error(f'Failed to handle mouse event: {str(e)}')

                    if valid_mouse_event:
                        in_element = self.get_element_at_position(x, y)

                        # In first case, we click inside already selected widget, pass click for processing
                        if in_element is not None:
                            self._logger.info(f'handling mouse press for elem: {in_element.get_title()}')
                            in_element._handle_mouse_press(x, y, mouse_event)

                        # Otherwise, if not a popup, select the clicked on widget
                        elif in_element is not None and not isinstance(in_element, py_cui.popups.Popup):
                            self.move_focus(in_element)
                            in_element._handle_mouse_press(x, y, mouse_event)

                # If we have a post_loading_callback, fire it here
                if self._post_loading_callback is not None and not self._loading:
                    self._logger.debug(f'Firing post-loading callback function {self._post_loading_callback.__name__}')
                    self._post_loading_callback()
                    self._post_loading_callback = None

                # Handle widget cycling
                if key_pressed == self._forward_cycle_key:
                    self._cycle_widgets()
                elif key_pressed == self._reverse_cycle_key:
                    self._cycle_widgets(reverse=True)

                # Handle keypresses
                self._handle_key_presses(key_pressed)

                try:
                    # Draw status/title bar, and all widgets. Selected widget will be bolded.
                    self._draw_status_bars(stdscr, self._height, self._width)
                    self._draw_widgets()
                    # draw the popup if required
                    if self._popup is not None:
                        self._popup._draw()

                    # If we are in live debug mode, we draw our debug messages
                    if self._logger.is_live_debug_enabled():
                        self._logger.draw_live_debug()

                except curses.error as e:
                    self._logger.error('Curses error while drawing TUI')
                    self._display_window_warning(stdscr, str(e))
                except py_cui.errors.PyCUIOutOfBoundsError as e:
                    self._logger.error('Resized terminal too small')
                    self._display_window_warning(stdscr, str(e))

                # Refresh the screen
                stdscr.refresh()

                # Wait for next input
                if self._loading or self._post_loading_callback is not None:
                    # When loading, refresh screen every quarter second
                    time.sleep(0.25)
                    # Need to reset key_pressed, because otherwise the previously pressed key will be used.
                    key_pressed = 0
                elif self._stopped:
                    key_pressed = self._exit_key
                else:
                    self._logger.info('Waiting for next keypress')
                    key_pressed = stdscr.getch()

            except KeyboardInterrupt:
                self._logger.info('Detect Keyboard Interrupt, Exiting...')
                self._stopped = True


        stdscr.erase()
        stdscr.refresh()
        curses.endwin()
        if self._on_stop is not None:
            self._logger.debug(f'Firing onstop function {self._on_stop.__name__}')
            self._on_stop()

    def _initialize_widget_renderer(self):
        """Function that creates the renderer object that will draw each widget
        """
        if self._renderer is None:
            self._renderer = MultiColorRenderer(self, self._stdscr, self._logger)
        super(QrogueCUI, self)._initialize_widget_renderer()

    def __init_keys(self) -> None:
        # debugging stuff
        self.add_key_command(self.__controls.get_key(Keys.PrintScreen), self.print_screen)
        self.__menu.get_main_widget().add_key_command(self.__controls.get_keys(Keys.PrintScreen), self.print_screen)
        self.__explore.get_main_widget().add_key_command(self.__controls.get_keys(Keys.PrintScreen), self.print_screen)
        self.__fight.get_main_widget().add_key_command(self.__controls.get_keys(Keys.PrintScreen), self.print_screen)
        self.__boss_fight.get_main_widget().add_key_command(self.__controls.get_keys(Keys.PrintScreen),
                                                            self.print_screen)

        self.__pause.get_main_widget().add_key_command(self.__controls.get_keys(Keys.CheatInput),
                                                       CheatConfig.cheat_input)
        self.__pause.get_main_widget().add_key_command(self.__controls.get_keys(Keys.CheatList), CheatConfig.cheat_list)
        # don't add the pause key to Menu and Pause itself!
        for widget_set in [self.__spaceship, self.__explore, self.__fight, self.__boss_fight, self.__shop,
                           self.__riddle]:
            for widget in widget_set.get_widget_list():
                widget.widget.add_key_command(self.__controls.get_keys(Keys.Pause), Pausing.pause)

        # all selections
        selection_widgets = [
            self.__menu.selection,
            self.__workbench.selection, self.__workbench.upgrades,
            self.__fight.choices, self.__fight.details,
            self.__boss_fight.choices, self.__boss_fight.details,
            self.__shop.inventory, self.__shop.buy,
            self.__riddle.choices, self.__riddle.details,
            self.__pause.choices, self.__pause.details,
        ]
        for my_widget in selection_widgets:
            widget = my_widget.widget
            widget.add_key_command(self.__controls.get_keys(Keys.SelectionUp), my_widget.up)
            widget.add_key_command(self.__controls.get_keys(Keys.SelectionRight), my_widget.right)
            widget.add_key_command(self.__controls.get_keys(Keys.SelectionDown), my_widget.down)
            widget.add_key_command(self.__controls.get_keys(Keys.SelectionLeft), my_widget.left)

        # menu
        self.__menu.selection.widget.add_key_command(self.__controls.action, self.__use_menu_selection)

        # spaceship
        w = self.__spaceship.get_main_widget()
        w.add_key_command(self.__controls.get_keys(Keys.MoveUp), self.__spaceship.move_up)
        w.add_key_command(self.__controls.get_keys(Keys.MoveRight), self.__spaceship.move_right)
        w.add_key_command(self.__controls.get_keys(Keys.MoveDown), self.__spaceship.move_down)
        w.add_key_command(self.__controls.get_keys(Keys.MoveLeft), self.__spaceship.move_left)

        # workbench
        self.__workbench.selection.widget.add_key_command(self.__controls.action, self.__workbench_selection)
        self.__workbench.upgrades.widget.add_key_command(self.__controls.action, self.__workbench_upgrades)

        # pause
        self.__pause.choices.widget.add_key_command(self.__controls.action, self.__pause_choices)
        self.__pause.details.widget.add_key_command(self.__controls.action, self.__pause_details)

        # explore
        w = self.__explore.get_main_widget()
        w.add_key_command(self.__controls.get_keys(Keys.MoveUp), self.__explore.move_up)
        w.add_key_command(self.__controls.get_keys(Keys.MoveRight), self.__explore.move_right)
        w.add_key_command(self.__controls.get_keys(Keys.MoveDown), self.__explore.move_down)
        w.add_key_command(self.__controls.get_keys(Keys.MoveLeft), self.__explore.move_left)

        # fight
        self.__fight.choices.widget.add_key_command(self.__controls.action, self.__fight_choices)
        self.__fight.details.widget.add_key_command(self.__controls.action, self.__fight_details)
        self.__fight.details.widget.add_key_command(self.__controls.get_keys(Keys.Cancel), self.__fight_details_back)
        self.__boss_fight.choices.widget.add_key_command(self.__controls.action, self.__boss_fight_choices)
        self.__boss_fight.details.widget.add_key_command(self.__controls.action, self.__boss_fight_details)
        self.__boss_fight.details.widget.add_key_command(self.__controls.get_keys(Keys.Cancel),
                                                         self.__boss_fight_details_back)

        # shop
        self.__shop.inventory.widget.add_key_command(self.__controls.action, self.__shop_inventory)
        self.__shop.buy.widget.add_key_command(self.__controls.action, self.__shop_buy)

        # riddle
        self.__riddle.choices.widget.add_key_command(self.__controls.action, self.__riddle_choices)
        self.__riddle.details.widget.add_key_command(self.__controls.action, self.__riddle_details)
        self.__riddle.details.widget.add_key_command(self.__controls.get_keys(Keys.Cancel), self.__riddle_details_back)

    def print_screen(self) -> None:
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
        self.__cur_widget_set.render()

    def __show_popup(self, title: str, text: str, color: int) -> None:
        self.__focused_widget = self.get_selected_widget()
        self._popup = MultilinePopup(self, title, text, color, self._renderer, self._logger, self.__controls)

    def __show_input_popup(self, title: str, color: int, callback: "(str,)") -> None:
        self.__focused_widget = self.get_selected_widget()
        self._popup = py_cui.popups.TextBoxPopup(self, title, color, callback, self._renderer, False, self._logger)

    def close_popup(self) -> None:
        super(QrogueCUI, self).close_popup()
        self.move_focus(self.__focused_widget)

    def __dummy(self) -> None:
        pass

    def __general_continue(self):
        self.__state_machine.change_state(self.__state_machine.prev_state, None)

    def __start_playing(self):
        Pausing(self.__pause_game)
        self.__state_machine.change_state(State.Spaceship, self.__save_data)

    def switch_to_spaceship(self, data=None):
        # todo maybe data is the save data?
        self.apply_widget_set(self.__spaceship)
        if data:
            player_tile = tiles.RobotTile(TestBot(0))  # todo take real values
            self.__spaceship.set_data((player_tile, self.__use_workbench))

    def __continue_spaceship(self) -> None:
        self.__state_machine.change_state(State.Spaceship, None)
        print("continue spaceship")

    def __use_workbench(self, save_data: SaveData):
        self.__state_machine.change_state(State.Workbench, save_data)

    def switch_to_workbench(self, data=None):
        self.__workbench.set_data(self.__save_data)
        self.apply_widget_set(self.__workbench)

    def switch_to_menu(self, data=None) -> None:
        self.__menu.new_seed()
        self.apply_widget_set(self.__menu)

    def __start_expedition(self, seed: int, robot: Robot, map: Map) -> None:
        self.__pause.set_data(robot)   # needed for the HUD
        self.__state_machine.change_state(State.Explore, map)

        self.__key_logger = KeyLogger(seed)     # the seed used to build the Map
        self.__game_started = True

    def __end_of_gameplay(self) -> None:
        self.switch_to_menu(None)

    def __won_tutorial(self) -> None:
        self.switch_to_menu(None)
        bell = ColorConfig.highlight_word("Bell")
        Popup.message("You won!", f"Congratulations, you defeated {bell} and successfully played the Tutorial!")

    def __start_fight(self, robot: Robot, enemy: Enemy, direction: Direction) -> None:
        self.__state_machine.change_state(State.Fight, (enemy, robot))

    def __start_boss_fight(self, robot: Robot, boss: Boss, direction: Direction):
        self.__state_machine.change_state(State.BossFight, (robot, boss))

    def switch_to_pause(self, data=None) -> None:
        self.apply_widget_set(self.__pause)

    def __pause_game(self) -> None:
        self.__state_machine.change_state(State.Pause, None)
        Tutorial.show_pause_tutorial()

    def switch_to_explore(self, data) -> None:
        if data is not None:
            map = data
            self.__explore.set_data(map, map.robot_tile)
        self.apply_widget_set(self.__explore)

    def __continue_explore(self) -> None:
        self.__state_machine.change_state(State.Explore, None)

    def switch_to_fight(self, data) -> None:
        if data is not None:
            enemy = data[0]
            player = data[1]
            self.__fight.set_data(player, enemy)
        self.apply_widget_set(self.__fight)

    def switch_to_boss_fight(self, data) -> None:
        if data is not None:
            player = data[0]
            boss = data[1]
            self.__boss_fight.set_data(player, boss)
        self.apply_widget_set(self.__boss_fight)

    def __open_riddle(self, robot: Robot, riddle: Riddle):
        self.__state_machine.change_state(State.Riddle, (robot, riddle))

    def switch_to_riddle(self, data) -> None:
        if data is not None:
            player = data[0]
            riddle = data[1]
            self.__riddle.set_data(player, riddle)
        self.apply_widget_set(self.__riddle)

    def __visit_shop(self, robot: Robot, items: "list of ShopItems"):
        self.__state_machine.change_state(State.Shop, (robot, items))

    def switch_to_shop(self, data) -> None:
        if data is not None:
            player = data[0]
            items = data[1]
            self.__shop.set_data(player, items)
        self.apply_widget_set(self.__shop)

    def render(self) -> None:
        self.__render([self.__cur_widget_set])

    def __render(self, renderables: List[Renderable]):
        for r in renderables:
            r.render()

    def __use_menu_selection(self) -> None:
        if self.__menu.selection.use() and self.__cur_widget_set is self.__menu:
            self.render()

    def __workbench_selection(self) -> None:
        if self.__workbench.selection.use() and self.__cur_widget_set is self.__workbench:
            self.move_focus(self.__workbench.upgrades.widget, auto_press_buttons=False)
            self.render()

    def __workbench_upgrades(self) -> None:
        if self.__workbench.upgrades.use() and self.__cur_widget_set is self.__workbench:
            self.move_focus(self.__workbench.selection.widget, auto_press_buttons=False)
            self.render()

    def __pause_choices(self) -> None:
        if self.__pause.choices.use() and self.__cur_widget_set is self.__pause:
            self.move_focus(self.__pause.details.widget, auto_press_buttons=False)
            self.__render([self.__pause.choices, self.__pause.details])

    def __pause_details(self) -> None:
        if self.__pause.details.use() and self.__cur_widget_set is self.__pause:
            self.move_focus(self.__pause.choices.widget, auto_press_buttons=False)
            self.__pause.details.render_reset()
            self.render()

    def __fight_choices(self) -> None:
        if self.__fight.choices.use() and self.__cur_widget_set is self.__fight:
            self.move_focus(self.__fight.details.widget, auto_press_buttons=False)
            self.__render([self.__fight.choices, self.__fight.details])

    def __fight_details(self) -> None:
        if self.__fight.details.use():
            self.__fight_details_back()

    def __fight_details_back(self) -> None:
        if self.__cur_widget_set is self.__fight:
            self.move_focus(self.__fight.choices.widget, auto_press_buttons=False)
            self.__fight.choices.validate_index()   # somehow it can happen that the index is out of bounds after
                                                    # coming back from details which is why we validate it now
            self.__fight.details.render_reset()
            self.render()   # render the whole widget_set for updating the StateVectors and the circuit

    def __boss_fight_choices(self) -> None:
        if self.__boss_fight.choices.use() and self.__cur_widget_set is self.__boss_fight:
            self.move_focus(self.__boss_fight.details.widget, auto_press_buttons=False)
            self.__render([self.__boss_fight.choices, self.__boss_fight.details])

    def __boss_fight_details_back(self) -> None:
        if self.__cur_widget_set is self.__boss_fight:
            self.move_focus(self.__boss_fight.choices.widget, auto_press_buttons=False)
            self.__boss_fight.choices.validate_index()  # somehow it can happen that the index is out of bounds after
            # coming back from details which is why we validate it now
            self.__boss_fight.details.render_reset()
            self.render()  # render the whole widget_set for updating the StateVectors and the circuit

    def __boss_fight_details(self) -> None:
        if self.__boss_fight.details.use():
            self.__boss_fight_details_back()

    def __riddle_choices(self):
        if self.__riddle.choices.use() and self.__cur_widget_set is self.__riddle:
            self.move_focus(self.__riddle.details.widget, auto_press_buttons=False)
            self.__render([self.__riddle.choices, self.__riddle.details])

    def __riddle_details_back(self) -> None:
        if self.__cur_widget_set is self.__riddle:
            self.move_focus(self.__riddle.choices.widget, auto_press_buttons=False)
            self.__riddle.choices.validate_index()   # somehow it can happen that the index is out of bounds after
                                                    # coming back from details which is why we validate it now
            self.__riddle.details.render_reset()
            self.render()   # render the whole widget_set for updating the StateVectors and the circuit

    def __riddle_details(self) -> None:
        if self.__riddle.details.use():
            self.__riddle_details_back()

    def __shop_inventory(self) -> None:
        if self.__shop.inventory.use() and self.__cur_widget_set is self.__shop:
            self.move_focus(self.__shop.buy.widget, auto_press_buttons=False)
            self.render()

    def __shop_buy(self) -> None:
        if self.__shop.buy.use() and self.__cur_widget_set is self.__shop:
            self.move_focus(self.__shop.inventory.widget, auto_press_buttons=False)
            self.__shop.inventory.validate_index()   # somehow it can happen that the index is out of bounds after
                                                     # coming back from details which is why we validate it now
            self.__shop.details.render_reset()
            self.__shop.buy.render_reset()
            #self.__shop.buy.clear_text() # not needed since render_reset does this for second SelectionWidgets
            self.render()


class State(Enum):
    Menu = 0
    Pause = 1
    Explore = 2
    Fight = 3
    Shop = 4
    Riddle = 5
    BossFight = 6

    Spaceship = 7
    Workbench = 8


class StateMachine:
    def __init__(self, renderer: QrogueCUI):
        self.__renderer = renderer
        self.__cur_state = None
        self.__prev_state = None

    @property
    def cur_state(self) -> State:
        return self.__cur_state

    @property
    def prev_state(self) -> State:
        return self.__prev_state

    def change_state(self, state: State, data) -> None:
        self.__prev_state = self.__cur_state
        self.__cur_state = state

        if self.__cur_state == State.Menu:
            self.__renderer.switch_to_menu(data)
        elif self.__cur_state == State.Explore:
            self.__renderer.switch_to_explore(data)
        elif self.__cur_state == State.Fight:
            self.__renderer.switch_to_fight(data)
        elif self.__cur_state == State.Riddle:
            self.__renderer.switch_to_riddle(data)
        elif self.__cur_state == State.Shop:
            self.__renderer.switch_to_shop(data)
        elif self.__cur_state == State.BossFight:
            self.__renderer.switch_to_boss_fight(data)
        elif self.__cur_state == State.Pause:
            self.__renderer.switch_to_pause()

        elif self.__cur_state == State.Spaceship:
            self.__renderer.switch_to_spaceship(data)
        elif self.__cur_state == State.Workbench:
            self.__renderer.switch_to_workbench(data)
            Logger.instance().debug("changing to Workbench")
