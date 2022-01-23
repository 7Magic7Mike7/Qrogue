# Generated from D:/Documents/pycharm_workspace/Qrogue/dungeon_editor\QrogueDungeon.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .QrogueDungeonParser import QrogueDungeonParser
else:
    from QrogueDungeonParser import QrogueDungeonParser

# This class defines a complete generic visitor for a parse tree produced by QrogueDungeonParser.

class QrogueDungeonVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueDungeonParser#start.
    def visitStart(self, ctx:QrogueDungeonParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#integer.
    def visitInteger(self, ctx:QrogueDungeonParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#complex_number.
    def visitComplex_number(self, ctx:QrogueDungeonParser.Complex_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#layout.
    def visitLayout(self, ctx:QrogueDungeonParser.LayoutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#l_room_row.
    def visitL_room_row(self, ctx:QrogueDungeonParser.L_room_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#l_hallway_row.
    def visitL_hallway_row(self, ctx:QrogueDungeonParser.L_hallway_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#rooms.
    def visitRooms(self, ctx:QrogueDungeonParser.RoomsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#room.
    def visitRoom(self, ctx:QrogueDungeonParser.RoomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#r_attributes.
    def visitR_attributes(self, ctx:QrogueDungeonParser.R_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#r_visibility.
    def visitR_visibility(self, ctx:QrogueDungeonParser.R_visibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#r_type.
    def visitR_type(self, ctx:QrogueDungeonParser.R_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#r_row.
    def visitR_row(self, ctx:QrogueDungeonParser.R_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#tile.
    def visitTile(self, ctx:QrogueDungeonParser.TileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#tile_descriptor.
    def visitTile_descriptor(self, ctx:QrogueDungeonParser.Tile_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#enemy_descriptor.
    def visitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#collectible_descriptor.
    def visitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#trigger_descriptor.
    def visitTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#energy_descriptor.
    def visitEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#riddle_descriptor.
    def visitRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#shop_descriptor.
    def visitShop_descriptor(self, ctx:QrogueDungeonParser.Shop_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#hallways.
    def visitHallways(self, ctx:QrogueDungeonParser.HallwaysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#hallway.
    def visitHallway(self, ctx:QrogueDungeonParser.HallwayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#h_attributes.
    def visitH_attributes(self, ctx:QrogueDungeonParser.H_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#draw_strategy.
    def visitDraw_strategy(self, ctx:QrogueDungeonParser.Draw_strategyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#stv_pools.
    def visitStv_pools(self, ctx:QrogueDungeonParser.Stv_poolsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#default_stv_pool.
    def visitDefault_stv_pool(self, ctx:QrogueDungeonParser.Default_stv_poolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#stv_pool.
    def visitStv_pool(self, ctx:QrogueDungeonParser.Stv_poolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#stvs.
    def visitStvs(self, ctx:QrogueDungeonParser.StvsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#stv.
    def visitStv(self, ctx:QrogueDungeonParser.StvContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#reward_pools.
    def visitReward_pools(self, ctx:QrogueDungeonParser.Reward_poolsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#default_reward_pool.
    def visitDefault_reward_pool(self, ctx:QrogueDungeonParser.Default_reward_poolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#reward_pool.
    def visitReward_pool(self, ctx:QrogueDungeonParser.Reward_poolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#collectibles.
    def visitCollectibles(self, ctx:QrogueDungeonParser.CollectiblesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#collectible.
    def visitCollectible(self, ctx:QrogueDungeonParser.CollectibleContext):
        return self.visitChildren(ctx)



del QrogueDungeonParser