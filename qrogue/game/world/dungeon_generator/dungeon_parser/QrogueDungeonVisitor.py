# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueDungeon.g4 by ANTLR 4.12.0
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


    # Visit a parse tree produced by QrogueDungeonParser#meta.
    def visitMeta(self, ctx:QrogueDungeonParser.MetaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#robot.
    def visitRobot(self, ctx:QrogueDungeonParser.RobotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#room_content.
    def visitRoom_content(self, ctx:QrogueDungeonParser.Room_contentContext):
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


    # Visit a parse tree produced by QrogueDungeonParser#t_descriptor.
    def visitT_descriptor(self, ctx:QrogueDungeonParser.T_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#trigger_descriptor.
    def visitTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#teleport_descriptor.
    def visitTeleport_descriptor(self, ctx:QrogueDungeonParser.Teleport_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#message_descriptor.
    def visitMessage_descriptor(self, ctx:QrogueDungeonParser.Message_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#collectible_descriptor.
    def visitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#energy_descriptor.
    def visitEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#shop_descriptor.
    def visitShop_descriptor(self, ctx:QrogueDungeonParser.Shop_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#enemy_descriptor.
    def visitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#boss_descriptor.
    def visitBoss_descriptor(self, ctx:QrogueDungeonParser.Boss_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#riddle_descriptor.
    def visitRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#challenge_descriptor.
    def visitChallenge_descriptor(self, ctx:QrogueDungeonParser.Challenge_descriptorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#puzzle_parameter.
    def visitPuzzle_parameter(self, ctx:QrogueDungeonParser.Puzzle_parameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#input_stv.
    def visitInput_stv(self, ctx:QrogueDungeonParser.Input_stvContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#boss_puzzle.
    def visitBoss_puzzle(self, ctx:QrogueDungeonParser.Boss_puzzleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#circuit_stv.
    def visitCircuit_stv(self, ctx:QrogueDungeonParser.Circuit_stvContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#circuit_gate_single.
    def visitCircuit_gate_single(self, ctx:QrogueDungeonParser.Circuit_gate_singleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#circuit_gate_multi.
    def visitCircuit_gate_multi(self, ctx:QrogueDungeonParser.Circuit_gate_multiContext):
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


    # Visit a parse tree produced by QrogueDungeonParser#stv_ref.
    def visitStv_ref(self, ctx:QrogueDungeonParser.Stv_refContext):
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


    # Visit a parse tree produced by QrogueDungeonParser#hallways.
    def visitHallways(self, ctx:QrogueDungeonParser.HallwaysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#hallway.
    def visitHallway(self, ctx:QrogueDungeonParser.HallwayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#h_attributes.
    def visitH_attributes(self, ctx:QrogueDungeonParser.H_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#messages.
    def visitMessages(self, ctx:QrogueDungeonParser.MessagesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#message.
    def visitMessage(self, ctx:QrogueDungeonParser.MessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueDungeonParser#message_body.
    def visitMessage_body(self, ctx:QrogueDungeonParser.Message_bodyContext):
        return self.visitChildren(ctx)



del QrogueDungeonParser