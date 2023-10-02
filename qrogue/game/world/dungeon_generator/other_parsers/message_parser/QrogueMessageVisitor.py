# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\QrogueMessage.g4 by ANTLR 4.12.0
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .QrogueMessageParser import QrogueMessageParser
else:
    from QrogueMessageParser import QrogueMessageParser

# This class defines a complete generic visitor for a parse tree produced by QrogueMessageParser.

class QrogueMessageVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by QrogueMessageParser#messages.
    def visitMessages(self, ctx:QrogueMessageParser.MessagesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#message.
    def visitMessage(self, ctx:QrogueMessageParser.MessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#message_body.
    def visitMessage_body(self, ctx:QrogueMessageParser.Message_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#integer.
    def visitInteger(self, ctx:QrogueMessageParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by QrogueMessageParser#complex_number.
    def visitComplex_number(self, ctx:QrogueMessageParser.Complex_numberContext):
        return self.visitChildren(ctx)



del QrogueMessageParser