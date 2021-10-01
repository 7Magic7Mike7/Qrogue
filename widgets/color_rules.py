import py_cui.colors

from game.map import tiles
from widgets.my_widgets import MapWidget, StateVectorWidget, SelectionWidget, CircuitWidget


class ColorRules:
    @staticmethod
    def apply_map_rules(map_widget: MapWidget):
        w = map_widget.widget
        w.add_text_color_rule('P', tiles.get_color(tiles.TileCode.Player), 'contains', match_type='regex')
        w.add_text_color_rule('B', tiles.get_color(tiles.TileCode.Boss), 'contains', match_type='regex')
        w.add_text_color_rule('\d', tiles.get_color(tiles.TileCode.Enemy), 'contains', match_type='regex')
        w.add_text_color_rule('#', tiles.get_color(tiles.TileCode.Wall), 'contains', match_type='regex')

    @staticmethod
    def apply_stv_rules(stv_widget: StateVectorWidget, diff_rules: bool = False):
        stv_widget.widget.add_text_color_rule("~.*~", py_cui.colors.CYAN_ON_BLACK, 'contains', match_type='regex')

        if diff_rules:
            stv_widget.widget.add_text_color_rule("0j", py_cui.colors.BLACK_ON_GREEN, "startswith", match_type="regex")

    @staticmethod
    def apply_selection_rules(sel_widget: SelectionWidget):
        length = 0 #sel_widget.choice_length + 2 # +2 to include the leading and trailing whitespace
        sel_widget.widget.add_text_color_rule(f"->.{{{length}}}", py_cui.colors.BLACK_ON_WHITE,
                                              'contains', match_type='regex')

    @staticmethod
    def apply_circuit_rules(circuit_widget: CircuitWidget):
        regex = "(\{.*?\}|\|.*?\>|\<.*?\|)"
        circuit_widget.widget.add_text_color_rule(regex, py_cui.colors.BLACK_ON_WHITE, 'contains', match_type='regex')
        #circuit_widget.widget.add_text_color_rule("\|.*?\>", py_cui.colors.BLACK_ON_YELLOW,
        #                                      'contains', match_type='regex')
        #circuit_widget.widget.add_text_color_rule("\<.*?\|", py_cui.colors.BLACK_ON_YELLOW,
        #                                      'contains', match_type='regex')
