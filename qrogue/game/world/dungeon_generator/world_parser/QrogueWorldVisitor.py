# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueWorld.g4 by ANTLR 4.12.0
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .QrogueWorldParser import QrogueWorldParser
else:
    from QrogueWorldParser import QrogueWorldParser

# This class defines a complete generic visitor for a parse tree produced by QrogueWorldParser.

class QrogueWorldVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueWorldParser#start.
    def visitStart(self, ctx:QrogueWorldParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#meta.
    def visitMeta(self, ctx:QrogueWorldParser.MetaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#room_content.
    def visitRoom_content(self, ctx:QrogueWorldParser.Room_contentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#r_type.
    def visitR_type(self, ctx:QrogueWorldParser.R_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#integer.
    def visitInteger(self, ctx:QrogueWorldParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#complex_number.
    def visitComplex_number(self, ctx:QrogueWorldParser.Complex_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#layout.
    def visitLayout(self, ctx:QrogueWorldParser.LayoutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#l_room_row.
    def visitL_room_row(self, ctx:QrogueWorldParser.L_room_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#l_hallway_row.
    def visitL_hallway_row(self, ctx:QrogueWorldParser.L_hallway_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#rooms.
    def visitRooms(self, ctx:QrogueWorldParser.RoomsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#room.
    def visitRoom(self, ctx:QrogueWorldParser.RoomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#r_attributes.
    def visitR_attributes(self, ctx:QrogueWorldParser.R_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#r_visibility.
    def visitR_visibility(self, ctx:QrogueWorldParser.R_visibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#hallways.
    def visitHallways(self, ctx:QrogueWorldParser.HallwaysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#hallway.
    def visitHallway(self, ctx:QrogueWorldParser.HallwayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#h_attributes.
    def visitH_attributes(self, ctx:QrogueWorldParser.H_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#messages.
    def visitMessages(self, ctx:QrogueWorldParser.MessagesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#message.
    def visitMessage(self, ctx:QrogueWorldParser.MessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#message_body.
    def visitMessage_body(self, ctx:QrogueWorldParser.Message_bodyContext):
        return self.visitChildren(ctx)



del QrogueWorldParser