# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers/QrogueBasics.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .QrogueBasicsParser import QrogueBasicsParser
else:
    from QrogueBasicsParser import QrogueBasicsParser

# This class defines a complete generic visitor for a parse tree produced by QrogueBasicsParser.

class QrogueBasicsVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueBasicsParser#integer.
    def visitInteger(self, ctx:QrogueBasicsParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueBasicsParser#complex_number.
    def visitComplex_number(self, ctx:QrogueBasicsParser.Complex_numberContext):
        return self.visitChildren(ctx)



del QrogueBasicsParser