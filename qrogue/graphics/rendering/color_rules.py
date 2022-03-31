from py_cui.widgets import Widget

from qrogue.game.logic.actors.controllables import ControllableType
from qrogue.game.world.tiles import TileCode, TileColorer


class ColorRules:
    @staticmethod
    def apply_map_rules(widget: Widget) -> None:
        for ct in ControllableType.values():
            widget.add_text_color_rule(ct.name, TileColorer.get_color(TileCode.Controllable), 'contains',
                                       match_type='regex')
        widget.add_text_color_rule('B', TileColorer.get_color(TileCode.Boss), 'contains', match_type='regex')
        widget.add_text_color_rule('\d', TileColorer.get_color(TileCode.Enemy), 'contains', match_type='regex')
        widget.add_text_color_rule('#', TileColorer.get_color(TileCode.Wall), 'contains', match_type='regex')
        widget.add_text_color_rule('o', TileColorer.get_color(TileCode.Wall), 'contains', match_type='regex')

    @staticmethod
    def apply_spaceship_rules(widget: Widget):
        widget.add_text_color_rule('\.', TileColorer.get_color(TileCode.SpaceshipWalk), 'contains', match_type='regex')
        widget.add_text_color_rule('M', TileColorer.get_color(TileCode.Controllable), 'contains', match_type='regex')
        widget.add_text_color_rule('R', TileColorer.get_color(TileCode.Npc), 'contains', match_type='regex')
        widget.add_text_color_rule('(B|W|N|G)', TileColorer.get_color(TileCode.SpaceshipWalk), 'contains',
                                   match_type='regex')

    @staticmethod
    def apply_navigation_rules(widget: Widget):
        widget.add_text_color_rule('#', TileColorer.get_color(TileCode.Wall), 'contains', match_type='regex')
