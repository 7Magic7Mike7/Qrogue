# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueDungeon.g4 by ANTLR 4.12.0
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


    # Enter a parse tree produced by QrogueDungeonParser#meta.
    def enterMeta(self, ctx:QrogueDungeonParser.MetaContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#meta.
    def exitMeta(self, ctx:QrogueDungeonParser.MetaContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#robot.
    def enterRobot(self, ctx:QrogueDungeonParser.RobotContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#robot.
    def exitRobot(self, ctx:QrogueDungeonParser.RobotContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#room_content.
    def enterRoom_content(self, ctx:QrogueDungeonParser.Room_contentContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#room_content.
    def exitRoom_content(self, ctx:QrogueDungeonParser.Room_contentContext):
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


    # Enter a parse tree produced by QrogueDungeonParser#t_descriptor.
    def enterT_descriptor(self, ctx:QrogueDungeonParser.T_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#t_descriptor.
    def exitT_descriptor(self, ctx:QrogueDungeonParser.T_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#trigger_descriptor.
    def enterTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#trigger_descriptor.
    def exitTrigger_descriptor(self, ctx:QrogueDungeonParser.Trigger_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#teleport_descriptor.
    def enterTeleport_descriptor(self, ctx:QrogueDungeonParser.Teleport_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#teleport_descriptor.
    def exitTeleport_descriptor(self, ctx:QrogueDungeonParser.Teleport_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#message_descriptor.
    def enterMessage_descriptor(self, ctx:QrogueDungeonParser.Message_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#message_descriptor.
    def exitMessage_descriptor(self, ctx:QrogueDungeonParser.Message_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#collectible_descriptor.
    def enterCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#collectible_descriptor.
    def exitCollectible_descriptor(self, ctx:QrogueDungeonParser.Collectible_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#energy_descriptor.
    def enterEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#energy_descriptor.
    def exitEnergy_descriptor(self, ctx:QrogueDungeonParser.Energy_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#enemy_descriptor.
    def enterEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#enemy_descriptor.
    def exitEnemy_descriptor(self, ctx:QrogueDungeonParser.Enemy_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#boss_descriptor.
    def enterBoss_descriptor(self, ctx:QrogueDungeonParser.Boss_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#boss_descriptor.
    def exitBoss_descriptor(self, ctx:QrogueDungeonParser.Boss_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#riddle_descriptor.
    def enterRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#riddle_descriptor.
    def exitRiddle_descriptor(self, ctx:QrogueDungeonParser.Riddle_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#challenge_descriptor.
    def enterChallenge_descriptor(self, ctx:QrogueDungeonParser.Challenge_descriptorContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#challenge_descriptor.
    def exitChallenge_descriptor(self, ctx:QrogueDungeonParser.Challenge_descriptorContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#puzzle_parameter.
    def enterPuzzle_parameter(self, ctx:QrogueDungeonParser.Puzzle_parameterContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#puzzle_parameter.
    def exitPuzzle_parameter(self, ctx:QrogueDungeonParser.Puzzle_parameterContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#input_stv.
    def enterInput_stv(self, ctx:QrogueDungeonParser.Input_stvContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#input_stv.
    def exitInput_stv(self, ctx:QrogueDungeonParser.Input_stvContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#boss_puzzle.
    def enterBoss_puzzle(self, ctx:QrogueDungeonParser.Boss_puzzleContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#boss_puzzle.
    def exitBoss_puzzle(self, ctx:QrogueDungeonParser.Boss_puzzleContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#circuit_stv.
    def enterCircuit_stv(self, ctx:QrogueDungeonParser.Circuit_stvContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#circuit_stv.
    def exitCircuit_stv(self, ctx:QrogueDungeonParser.Circuit_stvContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#circuit_gate_single.
    def enterCircuit_gate_single(self, ctx:QrogueDungeonParser.Circuit_gate_singleContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#circuit_gate_single.
    def exitCircuit_gate_single(self, ctx:QrogueDungeonParser.Circuit_gate_singleContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#circuit_gate_multi.
    def enterCircuit_gate_multi(self, ctx:QrogueDungeonParser.Circuit_gate_multiContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#circuit_gate_multi.
    def exitCircuit_gate_multi(self, ctx:QrogueDungeonParser.Circuit_gate_multiContext):
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


    # Enter a parse tree produced by QrogueDungeonParser#stv_ref.
    def enterStv_ref(self, ctx:QrogueDungeonParser.Stv_refContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#stv_ref.
    def exitStv_ref(self, ctx:QrogueDungeonParser.Stv_refContext):
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


    # Enter a parse tree produced by QrogueDungeonParser#messages.
    def enterMessages(self, ctx:QrogueDungeonParser.MessagesContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#messages.
    def exitMessages(self, ctx:QrogueDungeonParser.MessagesContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#message.
    def enterMessage(self, ctx:QrogueDungeonParser.MessageContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#message.
    def exitMessage(self, ctx:QrogueDungeonParser.MessageContext):
        pass


    # Enter a parse tree produced by QrogueDungeonParser#message_body.
    def enterMessage_body(self, ctx:QrogueDungeonParser.Message_bodyContext):
        pass

    # Exit a parse tree produced by QrogueDungeonParser#message_body.
    def exitMessage_body(self, ctx:QrogueDungeonParser.Message_bodyContext):
        pass



del QrogueDungeonParser