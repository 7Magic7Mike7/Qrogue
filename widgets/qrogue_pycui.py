
import py_cui

import game.controls
from util.logger import Logger
from widgets.map_widget import MapWidget
from game.map.map import Map
from game.controls import Controls

class QroguePyCUI(py_cui.PyCUI):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9
    __MAP_WIDTH = 10
    __MAP_HEIGHT = 5
    __MAP_SEED = 7

    def __init__(self, seed: int = __MAP_SEED):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS)
        self.__seed = seed

        self.__init_keys()

        firstRow = self.add_block_label('first line (metadata like playtime, floor, ...?)', 0, 0, column_span=self.__NUM_OF_COLS)
        firstRow.toggle_border()
        lastRow = self.add_block_label('last line', 8, 0, column_span=self.__NUM_OF_COLS)
        lastRow.toggle_border()

        self.__logger = Logger(lastRow)
        self.__init_widgets()

        self.__map = Map(seed, self.__MAP_WIDTH, self.__MAP_HEIGHT)
        self.__map_widget.set_map(self.__map)

        # manually set and loose focus because key strokes only work after a focus was set at least once?
        self.move_focus(firstRow)
        self.lose_focus()

    def __init_keys(self):
        self.__controls = Controls()
        # Add the key binding to the PyCUI object itself for overview mode.
        self.add_key_command(self.__controls.move_up(), self.__move_up)
        self.add_key_command(self.__controls.render(), self.__render)

    def __init_widgets(self):
        map_widget = self.add_block_label('MAP', 1, 2, row_span=5, column_span=5, center=True)
        map_widget.toggle_border()
        self.__map_widget = MapWidget(map_widget, self.__logger)

        self.__player_info_widget = self.add_block_label('Player', 1, 0, row_span=5, column_span=2, center=True)
        self.__player_info_widget.toggle_border()

        self.__qubits_widget = self.add_block_label('Qubits life & state', 6, 0, row_span=2, column_span=2, center=True)
        self.__qubits_widget.toggle_border()

        self.__circuit_widget = self.add_block_label('Circuit', 6, 2, row_span=2, column_span=5, center=True)
        self.__circuit_widget.toggle_border()

        self.__event_info_widget = self.add_block_label('Enemy/Event', 1, 7, row_span=5, column_span=2, center=True)
        self.__event_info_widget.toggle_border()

        self.__event_targets_widget = self.add_block_label('Event targets', 6, 7, row_span=2, column_span=2, center=True)
        self.__event_targets_widget.toggle_border()

    def __render(self):
        self.__map_widget.render()
        print("rend rend")
        self.__logger.clear()
        self.__logger.println("rendering")

    def __move_up(self):
        self.__logger.println("moving")
        self.__map_widget.move('up')

"""
    def add_circuit_widget(self, title, row, column, row_span = 1, column_span = 1, padx = 0, pady = 0):
        id = 'Widget{}'.format(len(self._widgets.keys()))
        circuit_widget = CircuitWidget(id,
                                         title,
                                         self._grid,
                                         row,
                                         column,
                                         row_span,
                                         column_span,
                                         padx,
                                         pady,
                                         self._logger)
        print(f"Renderer inside: {self._renderer}, type = {type(self._renderer)}")
        circuit_widget._assign_renderer(self._renderer)
        self._widgets[id]  = circuit_widget
        self._logger.info('Adding widget {} w/ ID {} of type {}'.format(title, id, str(type(circuit_widget))))
        return circuit_widget

    def add_my_label(self, title, row, column, row_span = 1, column_span = 1, padx = 1, pady = 0, center=True) -> py_cui.widgets.BlockLabel:
        id = 'Widget{}'.format(len(self._widgets.keys()))
        new_label = MyLabel(id,
                                              title,
                                              self._grid,
                                              row,
                                              column,
                                              row_span,
                                              column_span,
                                              padx,
                                              pady,
                                              self._logger)
        new_label._assign_renderer(self._renderer)
        self._widgets[id]  = new_label
        self._logger.info('Adding widget {} w/ ID {} of type {}'.format(title, id, str(type(new_label))))
        return new_label
"""