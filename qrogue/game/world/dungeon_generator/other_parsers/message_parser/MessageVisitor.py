# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\Message.g4 by ANTLR 4.10.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by MessageParser.

class MessageVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MessageParser#messages.
    def visitMessages(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MessageParser#message.
    def visitMessage(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MessageParser#integer.
    def visitInteger(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MessageParser#complex_number.
    def visitComplex_number(self, ctx):
        return self.visitChildren(ctx)


