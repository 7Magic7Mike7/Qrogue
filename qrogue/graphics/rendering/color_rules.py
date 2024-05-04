from qrogue.game.logic.actors.controllables import ControllableType
from qrogue.game.world.tiles import TileCode
from qrogue.graphics import WidgetWrapper
from qrogue.util import PyCuiColors, ColorConfig


class _TileColorer:      # todo: move to ColorConfig? (only value of dictionary since the keys are TileCodes)
    __color_manager = {
        TileCode.Invalid: PyCuiColors.RED_ON_BLUE,
        TileCode.Void: PyCuiColors.CYAN_ON_BLACK,
        TileCode.FogOfWar: PyCuiColors.CYAN_ON_BLACK,

        TileCode.Floor: PyCuiColors.CYAN_ON_BLACK,
        TileCode.Wall: PyCuiColors.BLACK_ON_WHITE,
        TileCode.Obstacle: PyCuiColors.BLACK_ON_WHITE,
        TileCode.Door: PyCuiColors.CYAN_ON_BLACK,

        TileCode.Collectible: PyCuiColors.CYAN_ON_BLACK,
        TileCode.Teleport: PyCuiColors.CYAN_ON_BLACK,
        TileCode.Message: PyCuiColors.CYAN_ON_BLACK,
        TileCode.Goal: PyCuiColors.GREEN_ON_BLACK,

        TileCode.Controllable: PyCuiColors.WHITE_ON_GREEN,
        TileCode.Npc: PyCuiColors.BLUE_ON_BLACK,
        TileCode.Enemy: PyCuiColors.RED_ON_BLACK,
        TileCode.Boss: PyCuiColors.BLACK_ON_RED,

        TileCode.SpaceshipWalk: PyCuiColors.BLACK_ON_WHITE,
    }

    @staticmethod
    def get_color(tile_code: TileCode) -> int:
        """

        :param tile_code: code of the Tile we want to get the default color of
        :return: integer representing one of the possible foreground-background color comibnations, None for invalid
        input
        """
        if tile_code in _TileColorer.__color_manager:
            return _TileColorer.__color_manager[tile_code]


class ColorRules:
    @staticmethod
    def apply_map_rules(widget: WidgetWrapper) -> None:
        # controllables
        for ct in ControllableType.values():
            widget.add_text_color_rule(ct.name, _TileColorer.get_color(TileCode.Controllable), 'contains',
                                       match_type='regex')
        # puzzles
        widget.add_text_color_rule(TileCode.Boss.representation, _TileColorer.get_color(TileCode.Boss), 'contains',
                                   match_type='regex')
        widget.add_text_color_rule('\d', _TileColorer.get_color(TileCode.Enemy), 'contains', match_type='regex')
        widget.add_text_color_rule(f"\{TileCode.Riddler.representation}", _TileColorer.get_color(TileCode.Enemy),
                                   'contains', match_type='regex')
        widget.add_text_color_rule(TileCode.Challenger.representation, _TileColorer.get_color(TileCode.Enemy),
                                   'contains', match_type='regex')

        # blocking
        widget.add_text_color_rule(TileCode.Wall.representation, _TileColorer.get_color(TileCode.Wall), 'contains',
                                   match_type='regex')
        widget.add_text_color_rule(TileCode.Obstacle.representation, _TileColorer.get_color(TileCode.Obstacle),
                                   'contains', match_type='regex')

        # collectibles
        for ct in TileCode.collectible_subtypes():
            widget.add_text_color_rule(ct.representation, _TileColorer.get_color(TileCode.Collectible), 'contains',
                                       match_type='regex')

        # goal
        widget.add_text_color_rule(TileCode.Goal.representation, _TileColorer.get_color(TileCode.Goal),
                                   'contains', match_type='regex')

    @staticmethod
    def apply_spaceship_rules(widget: WidgetWrapper):
        widget.add_text_color_rule('\.', _TileColorer.get_color(TileCode.SpaceshipWalk), 'contains', match_type='regex')
        widget.add_text_color_rule('M', _TileColorer.get_color(TileCode.Controllable), 'contains', match_type='regex')
        widget.add_text_color_rule('R', _TileColorer.get_color(TileCode.Npc), 'contains', match_type='regex')
        widget.add_text_color_rule('(B|W|N|G)', _TileColorer.get_color(TileCode.SpaceshipWalk), 'contains',
                                   match_type='regex')

    @staticmethod
    def apply_navigation_rules(widget: WidgetWrapper):
        widget.add_text_color_rule('#', _TileColorer.get_color(TileCode.Wall), 'contains', match_type='regex')
        widget.add_text_color_rule('M', _TileColorer.get_color(TileCode.Controllable), 'contains', match_type='regex')
        widget.add_text_color_rule('t', _TileColorer.get_color(TileCode.Teleport), 'contains', match_type='regex')
        widget.add_text_color_rule('\.', _TileColorer.get_color(TileCode.Message), 'contains', match_type='regex')

    @staticmethod
    def apply_circuit_rules(widget: WidgetWrapper):
        # highlight everything between {} (gates), |> (start) or <| (end) or | | (In/Out label)
        regex_gates = "\{.*?\}"
        regex_start = "\|.*?\>"
        regex_end = "\<.*?\|"
        widget.add_text_color_rule(f"({regex_gates}|{regex_start}|{regex_end})", ColorConfig.CIRCUIT_COLOR, 'contains',
                                   match_type='regex')
        regex_label = "In|Out"
        widget.add_text_color_rule(f"({regex_label})", ColorConfig.CIRCUIT_LABEL_COLOR, 'contains', match_type='regex')

    @staticmethod
    def apply_heading_rules(widget: WidgetWrapper):
        widget.add_text_color_rule("~.*~", ColorConfig.STV_HEADING_COLOR, 'contains', match_type='regex')

    @staticmethod
    def apply_qubit_config_rules(widget: WidgetWrapper):
        widget.add_text_color_rule("\|.*>", ColorConfig.QUBIT_CONFIG_COLOR, 'contains', match_type='regex')

    @staticmethod
    def apply_level_selection_seed_rules(widget: WidgetWrapper):
        widget.add_text_color_rule("Seed:", ColorConfig.LEVEL_SELECTION_HEADER_COLOR, 'contains', match_type='regex')

    @staticmethod
    def apply_level_selection_level_rules(widget: WidgetWrapper):
        widget.add_text_color_rule("Level:", ColorConfig.LEVEL_SELECTION_HEADER_COLOR, 'contains', match_type='regex')
