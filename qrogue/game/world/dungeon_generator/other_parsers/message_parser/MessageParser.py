# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\Message.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,29,48,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,1,0,1,0,5,0,11,8,0,10,
        0,12,0,14,9,0,1,1,1,1,1,1,3,1,19,8,1,1,1,4,1,22,8,1,11,1,12,1,23,
        1,1,1,1,1,1,1,1,3,1,30,8,1,1,2,1,2,1,3,3,3,35,8,3,1,3,1,3,1,3,3,
        3,40,8,3,1,3,1,3,3,3,44,8,3,3,3,46,8,3,1,3,0,0,4,0,2,4,6,0,1,2,0,
        14,15,24,24,51,0,8,1,0,0,0,2,15,1,0,0,0,4,31,1,0,0,0,6,34,1,0,0,
        0,8,12,5,1,0,0,9,11,3,2,1,0,10,9,1,0,0,0,11,14,1,0,0,0,12,10,1,0,
        0,0,12,13,1,0,0,0,13,1,1,0,0,0,14,12,1,0,0,0,15,18,5,25,0,0,16,17,
        5,4,0,0,17,19,5,22,0,0,18,16,1,0,0,0,18,19,1,0,0,0,19,21,1,0,0,0,
        20,22,5,22,0,0,21,20,1,0,0,0,22,23,1,0,0,0,23,21,1,0,0,0,23,24,1,
        0,0,0,24,29,1,0,0,0,25,26,5,2,0,0,26,27,5,25,0,0,27,28,5,3,0,0,28,
        30,5,25,0,0,29,25,1,0,0,0,29,30,1,0,0,0,30,3,1,0,0,0,31,32,7,0,0,
        0,32,5,1,0,0,0,33,35,5,18,0,0,34,33,1,0,0,0,34,35,1,0,0,0,35,45,
        1,0,0,0,36,46,5,17,0,0,37,40,3,4,2,0,38,40,5,16,0,0,39,37,1,0,0,
        0,39,38,1,0,0,0,40,43,1,0,0,0,41,42,5,18,0,0,42,44,5,17,0,0,43,41,
        1,0,0,0,43,44,1,0,0,0,44,46,1,0,0,0,45,36,1,0,0,0,45,39,1,0,0,0,
        46,7,1,0,0,0,8,12,18,23,29,34,39,43,45
    ]

class MessageParser ( Parser ):

    grammarFileName = "Message.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'[Messages]'", u"'event'", u"'alternative'", 
                     u"<INVALID>", u"<INVALID>", u"'Qrogue<'", u"'>Qrogue'", 
                     u"'~'", u"'|'", u"','", u"'#'", u"'..'", u"'__'" ]

    symbolicNames = [ u"<INVALID>", u"MESSAGES", u"MSG_EVENT", u"MSG_ALTERNATIVE", 
                      u"MSG_SPEAKER", u"DIRECTION", u"HEADER", u"ENDER", 
                      u"HORIZONTAL_SEPARATOR", u"VERTICAL_SEPARATOR", u"LIST_SEPARATOR", 
                      u"WALL", u"EMPTY_HALLWAY", u"EMPTY_ROOM", u"DIGIT", 
                      u"INTEGER", u"FLOAT", u"IMAG_NUMBER", u"SIGN", u"CHARACTER_LOW", 
                      u"CHARACTER_UP", u"CHARACTER", u"TEXT", u"ROOM_ID", 
                      u"HALLWAY_ID", u"REFERENCE", u"WS", u"UNIVERSAL_SEPARATOR", 
                      u"COMMENT", u"LINE_COMMENT" ]

    RULE_messages = 0
    RULE_message = 1
    RULE_integer = 2
    RULE_complex_number = 3

    ruleNames =  [ u"messages", u"message", u"integer", u"complex_number" ]

    EOF = Token.EOF
    MESSAGES=1
    MSG_EVENT=2
    MSG_ALTERNATIVE=3
    MSG_SPEAKER=4
    DIRECTION=5
    HEADER=6
    ENDER=7
    HORIZONTAL_SEPARATOR=8
    VERTICAL_SEPARATOR=9
    LIST_SEPARATOR=10
    WALL=11
    EMPTY_HALLWAY=12
    EMPTY_ROOM=13
    DIGIT=14
    INTEGER=15
    FLOAT=16
    IMAG_NUMBER=17
    SIGN=18
    CHARACTER_LOW=19
    CHARACTER_UP=20
    CHARACTER=21
    TEXT=22
    ROOM_ID=23
    HALLWAY_ID=24
    REFERENCE=25
    WS=26
    UNIVERSAL_SEPARATOR=27
    COMMENT=28
    LINE_COMMENT=29

    def __init__(self, input, output=sys.stdout):
        super(MessageParser, self).__init__(input, output=output)
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class MessagesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MessageParser.MessagesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MESSAGES(self):
            return self.getToken(MessageParser.MESSAGES, 0)

        def message(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(MessageParser.MessageContext)
            else:
                return self.getTypedRuleContext(MessageParser.MessageContext,i)


        def getRuleIndex(self):
            return MessageParser.RULE_messages

        def enterRule(self, listener):
            if hasattr(listener, "enterMessages"):
                listener.enterMessages(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMessages"):
                listener.exitMessages(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMessages"):
                return visitor.visitMessages(self)
            else:
                return visitor.visitChildren(self)




    def messages(self):

        localctx = MessageParser.MessagesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_messages)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 8
            self.match(MessageParser.MESSAGES)
            self.state = 12
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==MessageParser.REFERENCE:
                self.state = 9
                self.message()
                self.state = 14
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MessageContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MessageParser.MessageContext, self).__init__(parent, invokingState)
            self.parser = parser

        def REFERENCE(self, i=None):
            if i is None:
                return self.getTokens(MessageParser.REFERENCE)
            else:
                return self.getToken(MessageParser.REFERENCE, i)

        def MSG_SPEAKER(self):
            return self.getToken(MessageParser.MSG_SPEAKER, 0)

        def TEXT(self, i=None):
            if i is None:
                return self.getTokens(MessageParser.TEXT)
            else:
                return self.getToken(MessageParser.TEXT, i)

        def MSG_EVENT(self):
            return self.getToken(MessageParser.MSG_EVENT, 0)

        def MSG_ALTERNATIVE(self):
            return self.getToken(MessageParser.MSG_ALTERNATIVE, 0)

        def getRuleIndex(self):
            return MessageParser.RULE_message

        def enterRule(self, listener):
            if hasattr(listener, "enterMessage"):
                listener.enterMessage(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMessage"):
                listener.exitMessage(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMessage"):
                return visitor.visitMessage(self)
            else:
                return visitor.visitChildren(self)




    def message(self):

        localctx = MessageParser.MessageContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_message)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self.match(MessageParser.REFERENCE)
            self.state = 18
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MessageParser.MSG_SPEAKER:
                self.state = 16
                self.match(MessageParser.MSG_SPEAKER)
                self.state = 17
                self.match(MessageParser.TEXT)


            self.state = 21 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 20
                self.match(MessageParser.TEXT)
                self.state = 23 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==MessageParser.TEXT):
                    break

            self.state = 29
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MessageParser.MSG_EVENT:
                self.state = 25
                self.match(MessageParser.MSG_EVENT)
                self.state = 26
                self.match(MessageParser.REFERENCE)
                self.state = 27
                self.match(MessageParser.MSG_ALTERNATIVE)
                self.state = 28
                self.match(MessageParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IntegerContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MessageParser.IntegerContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self):
            return self.getToken(MessageParser.DIGIT, 0)

        def HALLWAY_ID(self):
            return self.getToken(MessageParser.HALLWAY_ID, 0)

        def INTEGER(self):
            return self.getToken(MessageParser.INTEGER, 0)

        def getRuleIndex(self):
            return MessageParser.RULE_integer

        def enterRule(self, listener):
            if hasattr(listener, "enterInteger"):
                listener.enterInteger(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitInteger"):
                listener.exitInteger(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitInteger"):
                return visitor.visitInteger(self)
            else:
                return visitor.visitChildren(self)




    def integer(self):

        localctx = MessageParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << MessageParser.DIGIT) | (1 << MessageParser.INTEGER) | (1 << MessageParser.HALLWAY_ID))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Complex_numberContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(MessageParser.Complex_numberContext, self).__init__(parent, invokingState)
            self.parser = parser

        def IMAG_NUMBER(self):
            return self.getToken(MessageParser.IMAG_NUMBER, 0)

        def SIGN(self, i=None):
            if i is None:
                return self.getTokens(MessageParser.SIGN)
            else:
                return self.getToken(MessageParser.SIGN, i)

        def integer(self):
            return self.getTypedRuleContext(MessageParser.IntegerContext,0)


        def FLOAT(self):
            return self.getToken(MessageParser.FLOAT, 0)

        def getRuleIndex(self):
            return MessageParser.RULE_complex_number

        def enterRule(self, listener):
            if hasattr(listener, "enterComplex_number"):
                listener.enterComplex_number(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitComplex_number"):
                listener.exitComplex_number(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitComplex_number"):
                return visitor.visitComplex_number(self)
            else:
                return visitor.visitChildren(self)




    def complex_number(self):

        localctx = MessageParser.Complex_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==MessageParser.SIGN:
                self.state = 33
                self.match(MessageParser.SIGN)


            self.state = 45
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [MessageParser.IMAG_NUMBER]:
                self.state = 36
                self.match(MessageParser.IMAG_NUMBER)
                pass
            elif token in [MessageParser.DIGIT, MessageParser.INTEGER, MessageParser.FLOAT, MessageParser.HALLWAY_ID]:
                self.state = 39
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [MessageParser.DIGIT, MessageParser.INTEGER, MessageParser.HALLWAY_ID]:
                    self.state = 37
                    self.integer()
                    pass
                elif token in [MessageParser.FLOAT]:
                    self.state = 38
                    self.match(MessageParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==MessageParser.SIGN:
                    self.state = 41
                    self.match(MessageParser.SIGN)
                    self.state = 42
                    self.match(MessageParser.IMAG_NUMBER)


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





