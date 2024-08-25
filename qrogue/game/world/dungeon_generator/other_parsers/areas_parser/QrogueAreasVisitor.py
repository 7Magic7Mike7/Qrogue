# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers/QrogueAreas.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .QrogueAreasParser import QrogueAreasParser
else:
    from QrogueAreasParser import QrogueAreasParser

# This class defines a complete generic visitor for a parse tree produced by QrogueAreasParser.

class QrogueAreasVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueAreasParser#layout.
    def visitLayout(self, ctx:QrogueAreasParser.LayoutContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#l_room_row.
    def visitL_room_row(self, ctx:QrogueAreasParser.L_room_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#l_hallway_row.
    def visitL_hallway_row(self, ctx:QrogueAreasParser.L_hallway_rowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#rooms.
    def visitRooms(self, ctx:QrogueAreasParser.RoomsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#room.
    def visitRoom(self, ctx:QrogueAreasParser.RoomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#r_attributes.
    def visitR_attributes(self, ctx:QrogueAreasParser.R_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#r_visibility.
    def visitR_visibility(self, ctx:QrogueAreasParser.R_visibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#r_type.
    def visitR_type(self, ctx:QrogueAreasParser.R_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#room_content.
    def visitRoom_content(self, ctx:QrogueAreasParser.Room_contentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#hallways.
    def visitHallways(self, ctx:QrogueAreasParser.HallwaysContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#hallway.
    def visitHallway(self, ctx:QrogueAreasParser.HallwayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#h_attributes.
    def visitH_attributes(self, ctx:QrogueAreasParser.H_attributesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#integer.
    def visitInteger(self, ctx:QrogueAreasParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueAreasParser#complex_number.
    def visitComplex_number(self, ctx:QrogueAreasParser.Complex_numberContext):
        return self.visitChildren(ctx)



del QrogueAreasParser