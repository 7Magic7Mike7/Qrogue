# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\QrogueMessage.g4 by ANTLR 4.10.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by QrogueMessageParser.

class QrogueMessageVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueMessageParser#messages.
    def visitMessages(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#message.
    def visitMessage(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#message_body.
    def visitMessage_body(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#integer.
    def visitInteger(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#complex_number.
    def visitComplex_number(self, ctx):
        return self.visitChildren(ctx)


