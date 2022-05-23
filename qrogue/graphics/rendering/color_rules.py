from qrogue.game.logic.actors.controllables import ControllableType
from qrogue.game.world.tiles import TileCode
from qrogue.graphics import WidgetWrapper
from qrogue.util import PyCuiColors


class TileColorer:
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

        TileCode.Controllable: PyCuiColors.GREEN_ON_BLACK,
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
        if tile_code in TileColorer.__color_manager:
            return TileColorer.__color_manager[tile_code]


class ColorRules:
    @staticmethod
    def apply_map_rules(widget: WidgetWrapper) -> None:
        for ct in ControllableType.values():
            widget.add_text_color_rule(ct.name, TileColorer.get_color(TileCode.Controllable), 'contains',
                                       match_type='regex')
        widget.add_text_color_rule('B', TileColorer.get_color(TileCode.Boss), 'contains', match_type='regex')
        widget.add_text_color_rule('\d', TileColorer.get_color(TileCode.Enemy), 'contains', match_type='regex')
        widget.add_text_color_rule('#', TileColorer.get_color(TileCode.Wall), 'contains', match_type='regex')
        widget.add_text_color_rule('o', TileColorer.get_color(TileCode.Obstacle), 'contains', match_type='regex')
        widget.add_text_color_rule('c', TileColorer.get_color(TileCode.Collectible), 'contains', match_type='regex')

    @staticmethod
    def apply_spaceship_rules(widget: WidgetWrapper):
        widget.add_text_color_rule('\.', TileColorer.get_color(TileCode.SpaceshipWalk), 'contains', match_type='regex')
        widget.add_text_color_rule('M', TileColorer.get_color(TileCode.Controllable), 'contains', match_type='regex')
        widget.add_text_color_rule('R', TileColorer.get_color(TileCode.Npc), 'contains', match_type='regex')
        widget.add_text_color_rule('(B|W|N|G)', TileColorer.get_color(TileCode.SpaceshipWalk), 'contains',
                                   match_type='regex')

    @staticmethod
    def apply_navigation_rules(widget: WidgetWrapper):
        widget.add_text_color_rule('#', TileColorer.get_color(TileCode.Wall), 'contains', match_type='regex')
        widget.add_text_color_rule('M', TileColorer.get_color(TileCode.Controllable), 'contains', match_type='regex')
        widget.add_text_color_rule('t', TileColorer.get_color(TileCode.Teleport), 'contains', match_type='regex')
        widget.add_text_color_rule('\.', TileColorer.get_color(TileCode.Message), 'contains', match_type='regex')
