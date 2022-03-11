# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/dungeon_editor\QrogueWorld.g4 by ANTLR 4.9.2
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by QrogueWorldParser.

class QrogueWorldVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueWorldParser#start.
    def visitStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#layout.
    def visitLayout(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#l_room_row.
    def visitL_room_row(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#l_hallway_row.
    def visitL_hallway_row(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#rooms.
    def visitRooms(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#room.
    def visitRoom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#r_attributes.
    def visitR_attributes(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#r_visibility.
    def visitR_visibility(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#r_type.
    def visitR_type(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#hallways.
    def visitHallways(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#hallway.
    def visitHallway(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueWorldParser#h_attributes.
    def visitH_attributes(self, ctx):
        return self.visitChildren(ctx)


