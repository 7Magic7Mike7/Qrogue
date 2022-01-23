# Generated from D:/Documents/pycharm_workspace/Qrogue/dungeon_editor\QrogueDungeon.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .QrogueDungeonParser import QrogueDungeonParser
else:
    from QrogueDungeonParser import QrogueDungeonParser

# This class defines a complete listener for a parse tree produced by QrogueDungeonParser.
class QrogueDungeonListener(ParseTreeListener):

    # Enter a parse tree produced by QrogueDungeonParser#start.
    def enterStart(self, ctx:QrogueDungeonParser.StartContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#start.
    def exitStart(self, ctx:QrogueDungeonParser.StartContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#integer.
    def enterInteger(self, ctx:QrogueDungeonParser.IntegerContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#integer.
    def exitInteger(self, ctx:QrogueDungeonParser.IntegerContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#complex_number.
    def enterComplex_number(self, ctx:QrogueDungeonParser.Complex_numberContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#complex_number.
    def exitComplex_number(self, ctx:QrogueDungeonParser.Complex_numberContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#layout.
    def enterLayout(self, ctx:QrogueDungeonParser.LayoutContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#layout.
    def exitLayout(self, ctx:QrogueDungeonParser.LayoutContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#l_room_row.
    def enterL_room_row(self, ctx:QrogueDungeonParser.L_room_rowContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#l_room_row.
    def exitL_room_row(self, ctx:QrogueDungeonParser.L_room_rowContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#l_hallway_row.
    def enterL_hallway_row(self, ctx:QrogueDungeonParser.L_hallway_rowContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#l_hallway_row.
    def exitL_hallway_row(self, ctx:QrogueDungeonParser.L_hallway_rowContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#rooms.
    def enterRooms(self, ctx:QrogueDungeonParser.RoomsContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#rooms.
    def exitRooms(self, ctx:QrogueDungeonParser.RoomsContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#room.
    def enterRoom(self, ctx:QrogueDungeonParser.RoomContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#room.
    def exitRoom(self, ctx:QrogueDungeonParser.RoomContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#r_attributes.
    def enterR_attributes(self, ctx:QrogueDungeonParser.R_attributesContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#r_attributes.
    def exitR_attributes(self, ctx:QrogueDungeonParser.R_attributesContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#r_visibility.
    def enterR_visibility(self, ctx:QrogueDungeonParser.R_visibilityContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#r_visibility.
    def exitR_visibility(self, ctx:QrogueDungeonParser.R_visibilityContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#r_type.
    def enterR_type(self, ctx:QrogueDungeonParser.R_typeContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#r_type.
    def exitR_type(self, ctx:QrogueDungeonParser.R_typeContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#r_row.
    def enterR_row(self, ctx:QrogueDungeonParser.R_rowContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#r_row.
    def exitR_row(self, ctx:QrogueDungeonParser.R_rowContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#tile.
    def enterTile(self, ctx:QrogueDungeonParser.TileContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#tile.
    def exitTile(self, ctx:QrogueDungeonParser.TileContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#tile_descriptor.
    def enterTile_descriptor(self, ctx:QrogueDungeonParser.Tile_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#tile_descriptor.
    def exitTile_descriptor(self, ctx:QrogueDungeonParser.Tile_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#enemy_descriptor.
    def enterEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#enemy_descriptor.
    def exitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#collectible_descriptor.
    def enterCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#collectible_descriptor.
    def exitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#trigger_descriptor.
    def enterTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#trigger_descriptor.
    def exitTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#energy_descriptor.
    def enterEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#energy_descriptor.
    def exitEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#riddle_descriptor.
    def enterRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#riddle_descriptor.
    def exitRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#shop_descriptor.
    def enterShop_descriptor(self, ctx:QrogueDungeonParser.Shop_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#shop_descriptor.
    def exitShop_descriptor(self, ctx:QrogueDungeonParser.Shop_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#hallways.
    def enterHallways(self, ctx:QrogueDungeonParser.HallwaysContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#hallways.
    def exitHallways(self, ctx:QrogueDungeonParser.HallwaysContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#hallway.
    def enterHallway(self, ctx:QrogueDungeonParser.HallwayContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#hallway.
    def exitHallway(self, ctx:QrogueDungeonParser.HallwayContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#h_attributes.
    def enterH_attributes(self, ctx:QrogueDungeonParser.H_attributesContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#h_attributes.
    def exitH_attributes(self, ctx:QrogueDungeonParser.H_attributesContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#draw_strategy.
    def enterDraw_strategy(self, ctx:QrogueDungeonParser.Draw_strategyContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#draw_strategy.
    def exitDraw_strategy(self, ctx:QrogueDungeonParser.Draw_strategyContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#stv_pools.
    def enterStv_pools(self, ctx:QrogueDungeonParser.Stv_poolsContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#stv_pools.
    def exitStv_pools(self, ctx:QrogueDungeonParser.Stv_poolsContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#default_stv_pool.
    def enterDefault_stv_pool(self, ctx:QrogueDungeonParser.Default_stv_poolContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#default_stv_pool.
    def exitDefault_stv_pool(self, ctx:QrogueDungeonParser.Default_stv_poolContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#stv_pool.
    def enterStv_pool(self, ctx:QrogueDungeonParser.Stv_poolContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#stv_pool.
    def exitStv_pool(self, ctx:QrogueDungeonParser.Stv_poolContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#stvs.
    def enterStvs(self, ctx:QrogueDungeonParser.StvsContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#stvs.
    def exitStvs(self, ctx:QrogueDungeonParser.StvsContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#stv.
    def enterStv(self, ctx:QrogueDungeonParser.StvContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#stv.
    def exitStv(self, ctx:QrogueDungeonParser.StvContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#reward_pools.
    def enterReward_pools(self, ctx:QrogueDungeonParser.Reward_poolsContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#reward_pools.
    def exitReward_pools(self, ctx:QrogueDungeonParser.Reward_poolsContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#default_reward_pool.
    def enterDefault_reward_pool(self, ctx:QrogueDungeonParser.Default_reward_poolContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#default_reward_pool.
    def exitDefault_reward_pool(self, ctx:QrogueDungeonParser.Default_reward_poolContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#reward_pool.
    def enterReward_pool(self, ctx:QrogueDungeonParser.Reward_poolContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#reward_pool.
    def exitReward_pool(self, ctx:QrogueDungeonParser.Reward_poolContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#collectibles.
    def enterCollectibles(self, ctx:QrogueDungeonParser.CollectiblesContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#collectibles.
    def exitCollectibles(self, ctx:QrogueDungeonParser.CollectiblesContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#collectible.
    def enterCollectible(self, ctx:QrogueDungeonParser.CollectibleContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#collectible.
    def exitCollectible(self, ctx:QrogueDungeonParser.CollectibleContext):
        pass



del QrogueDungeonParser