
import py_cui
from util.logger import Logger
from widgets.circuit_widget import *
from widgets.map_widget import Map

"""
def add_circ_widg(root, title, row, column, row_span = 1, column_span = 1, padx = 0, pady = 0):
    id = 'Widget{}'.format(len(root._widgets.keys()))
    circuit_widget = MyLabel(id,
                                        title,
                                        root._grid,
                                        row,
                                        column,
                                        row_span,
                                        column_span,
                                        padx,
                                        pady,
                                        root._logger)
    print(f"Renderer inside: {root._renderer}, type = {type(root._renderer)}")
    circuit_widget._assign_renderer(root._renderer)
    root._widgets[id]  = circuit_widget
    root._logger.info('Adding widget {} w/ ID {} of type {}'.format(title, id, str(type(circuit_widget))))
    return circuit_widget
"""


class QroguePyCUI(py_cui.PyCUI):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9

    def __init__(self):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS)

        # Add the key binding to the PyCUI object itself for overview mode.
        self.add_key_command(py_cui.keys.KEY_T_LOWER, self.__move_up)

        firstRow = self.add_block_label('first line (metadata like playtime, floor, ...?)', 0, 0, column_span=self.__NUM_OF_COLS)
        firstRow.toggle_border()
        lastRow = self.add_block_label('last line', 8, 0, column_span=self.__NUM_OF_COLS)
        lastRow.toggle_border()

        self.__logger = Logger(lastRow)

        map = self.add_block_label('MAP', 1, 2, row_span=5, column_span=5, center=True)
        map.toggle_border()
        self.__map = Map(map, self.__logger)

        self.__player_info = self.add_block_label('Player', 1, 0, row_span=5, column_span=2, center=True)
        self.__player_info.toggle_border()

        self.__qubits = self.add_block_label('Qubits life & state', 6, 0, row_span=2, column_span=2, center=True)
        self.__qubits.toggle_border()

        self.__circuit = self.add_block_label('Circuit', 6, 2, row_span=2, column_span=5, center=True)
        self.__circuit.toggle_border()

        self.__event_info = self.add_block_label('Enemy/Event', 1, 7, row_span=5, column_span=2, center=True)
        self.__event_info.toggle_border()

        self.__event_targets = self.add_block_label('Event targets', 6, 7, row_span=2, column_span=2, center=True)
        self.__event_targets.toggle_border()

        # manually set and loose focus because key strokes only work after a focus was set at least once?
        self.move_focus(map)
        self.lose_focus()

    def __move_up(self):
        self.__logger.println("moving")
        self.__map.move('up')

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