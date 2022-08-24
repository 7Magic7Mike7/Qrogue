# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\QrogueMessage.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,32,54,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,5,0,13,
        8,0,10,0,12,0,16,9,0,1,1,1,1,1,1,1,1,1,1,1,1,3,1,24,8,1,1,2,1,2,
        3,2,28,8,2,1,2,3,2,31,8,2,1,2,4,2,34,8,2,11,2,12,2,35,1,3,1,3,1,
        4,3,4,41,8,4,1,4,1,4,1,4,3,4,46,8,4,1,4,1,4,3,4,50,8,4,3,4,52,8,
        4,1,4,0,0,5,0,2,4,6,8,0,1,2,0,17,18,27,27,57,0,10,1,0,0,0,2,17,1,
        0,0,0,4,27,1,0,0,0,6,37,1,0,0,0,8,40,1,0,0,0,10,14,5,1,0,0,11,13,
        3,2,1,0,12,11,1,0,0,0,13,16,1,0,0,0,14,12,1,0,0,0,14,15,1,0,0,0,
        15,1,1,0,0,0,16,14,1,0,0,0,17,18,5,28,0,0,18,23,3,4,2,0,19,20,5,
        2,0,0,20,21,5,28,0,0,21,22,5,3,0,0,22,24,5,28,0,0,23,19,1,0,0,0,
        23,24,1,0,0,0,24,3,1,0,0,0,25,26,5,4,0,0,26,28,5,25,0,0,27,25,1,
        0,0,0,27,28,1,0,0,0,28,30,1,0,0,0,29,31,5,5,0,0,30,29,1,0,0,0,30,
        31,1,0,0,0,31,33,1,0,0,0,32,34,5,25,0,0,33,32,1,0,0,0,34,35,1,0,
        0,0,35,33,1,0,0,0,35,36,1,0,0,0,36,5,1,0,0,0,37,38,7,0,0,0,38,7,
        1,0,0,0,39,41,5,21,0,0,40,39,1,0,0,0,40,41,1,0,0,0,41,51,1,0,0,0,
        42,52,5,20,0,0,43,46,3,6,3,0,44,46,5,19,0,0,45,43,1,0,0,0,45,44,
        1,0,0,0,46,49,1,0,0,0,47,48,5,21,0,0,48,50,5,20,0,0,49,47,1,0,0,
        0,49,50,1,0,0,0,50,52,1,0,0,0,51,42,1,0,0,0,51,45,1,0,0,0,52,9,1,
        0,0,0,9,14,23,27,30,35,40,45,49,51
    ]

class QrogueMessageParser ( Parser ):

    grammarFileName = "QrogueMessage.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'[Messages]'", u"'when'", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"'tutorial'", 
                     u"'trigger'", u"'Qrogue<'", u"'>Qrogue'", u"'~'", u"'|'", 
                     u"','", u"'#'", u"'..'", u"'__'" ]

    symbolicNames = [ u"<INVALID>", u"MESSAGES", u"MSG_EVENT", u"MSG_ALTERNATIVE", 
                      u"MSG_SPEAKER", u"MSG_PRIORITY", u"DIRECTION", u"TUTORIAL_LITERAL", 
                      u"TRIGGER_LITERAL", u"HEADER", u"ENDER", u"HORIZONTAL_SEPARATOR", 
                      u"VERTICAL_SEPARATOR", u"LIST_SEPARATOR", u"WALL", 
                      u"EMPTY_HALLWAY", u"EMPTY_ROOM", u"DIGIT", u"INTEGER", 
                      u"FLOAT", u"IMAG_NUMBER", u"SIGN", u"CHARACTER_LOW", 
                      u"CHARACTER_UP", u"CHARACTER", u"TEXT", u"ROOM_ID", 
                      u"HALLWAY_ID", u"REFERENCE", u"WS", u"UNIVERSAL_SEPARATOR", 
                      u"COMMENT", u"LINE_COMMENT" ]

    RULE_messages = 0
    RULE_message = 1
    RULE_message_body = 2
    RULE_integer = 3
    RULE_complex_number = 4

    ruleNames =  [ u"messages", u"message", u"message_body", u"integer", 
                   u"complex_number" ]

    EOF = Token.EOF
    MESSAGES=1
    MSG_EVENT=2
    MSG_ALTERNATIVE=3
    MSG_SPEAKER=4
    MSG_PRIORITY=5
    DIRECTION=6
    TUTORIAL_LITERAL=7
    TRIGGER_LITERAL=8
    HEADER=9
    ENDER=10
    HORIZONTAL_SEPARATOR=11
    VERTICAL_SEPARATOR=12
    LIST_SEPARATOR=13
    WALL=14
    EMPTY_HALLWAY=15
    EMPTY_ROOM=16
    DIGIT=17
    INTEGER=18
    FLOAT=19
    IMAG_NUMBER=20
    SIGN=21
    CHARACTER_LOW=22
    CHARACTER_UP=23
    CHARACTER=24
    TEXT=25
    ROOM_ID=26
    HALLWAY_ID=27
    REFERENCE=28
    WS=29
    UNIVERSAL_SEPARATOR=30
    COMMENT=31
    LINE_COMMENT=32

    def __init__(self, input, output=sys.stdout):
        super(QrogueMessageParser, self).__init__(input, output=output)
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class MessagesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueMessageParser.MessagesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MESSAGES(self):
            return self.getToken(QrogueMessageParser.MESSAGES, 0)

        def message(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueMessageParser.MessageContext)
            else:
                return self.getTypedRuleContext(QrogueMessageParser.MessageContext,i)


        def getRuleIndex(self):
            return QrogueMessageParser.RULE_messages

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

        localctx = QrogueMessageParser.MessagesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_messages)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self.match(QrogueMessageParser.MESSAGES)
            self.state = 14
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueMessageParser.REFERENCE:
                self.state = 11
                self.message()
                self.state = 16
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
            super(QrogueMessageParser.MessageContext, self).__init__(parent, invokingState)
            self.parser = parser

        def REFERENCE(self, i=None):
            if i is None:
                return self.getTokens(QrogueMessageParser.REFERENCE)
            else:
                return self.getToken(QrogueMessageParser.REFERENCE, i)

        def message_body(self):
            return self.getTypedRuleContext(QrogueMessageParser.Message_bodyContext,0)


        def MSG_EVENT(self):
            return self.getToken(QrogueMessageParser.MSG_EVENT, 0)

        def MSG_ALTERNATIVE(self):
            return self.getToken(QrogueMessageParser.MSG_ALTERNATIVE, 0)

        def getRuleIndex(self):
            return QrogueMessageParser.RULE_message

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

        localctx = QrogueMessageParser.MessageContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_message)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17
            self.match(QrogueMessageParser.REFERENCE)
            self.state = 18
            self.message_body()
            self.state = 23
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueMessageParser.MSG_EVENT:
                self.state = 19
                self.match(QrogueMessageParser.MSG_EVENT)
                self.state = 20
                self.match(QrogueMessageParser.REFERENCE)
                self.state = 21
                self.match(QrogueMessageParser.MSG_ALTERNATIVE)
                self.state = 22
                self.match(QrogueMessageParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Message_bodyContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueMessageParser.Message_bodyContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MSG_SPEAKER(self):
            return self.getToken(QrogueMessageParser.MSG_SPEAKER, 0)

        def TEXT(self, i=None):
            if i is None:
                return self.getTokens(QrogueMessageParser.TEXT)
            else:
                return self.getToken(QrogueMessageParser.TEXT, i)

        def MSG_PRIORITY(self):
            return self.getToken(QrogueMessageParser.MSG_PRIORITY, 0)

        def getRuleIndex(self):
            return QrogueMessageParser.RULE_message_body

        def enterRule(self, listener):
            if hasattr(listener, "enterMessage_body"):
                listener.enterMessage_body(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMessage_body"):
                listener.exitMessage_body(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMessage_body"):
                return visitor.visitMessage_body(self)
            else:
                return visitor.visitChildren(self)




    def message_body(self):

        localctx = QrogueMessageParser.Message_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_message_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueMessageParser.MSG_SPEAKER:
                self.state = 25
                self.match(QrogueMessageParser.MSG_SPEAKER)
                self.state = 26
                self.match(QrogueMessageParser.TEXT)


            self.state = 30
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueMessageParser.MSG_PRIORITY:
                self.state = 29
                self.match(QrogueMessageParser.MSG_PRIORITY)


            self.state = 33 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 32
                self.match(QrogueMessageParser.TEXT)
                self.state = 35 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueMessageParser.TEXT):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IntegerContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueMessageParser.IntegerContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self):
            return self.getToken(QrogueMessageParser.DIGIT, 0)

        def HALLWAY_ID(self):
            return self.getToken(QrogueMessageParser.HALLWAY_ID, 0)

        def INTEGER(self):
            return self.getToken(QrogueMessageParser.INTEGER, 0)

        def getRuleIndex(self):
            return QrogueMessageParser.RULE_integer

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

        localctx = QrogueMessageParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 37
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << QrogueMessageParser.DIGIT) | (1 << QrogueMessageParser.INTEGER) | (1 << QrogueMessageParser.HALLWAY_ID))) != 0)):
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
            super(QrogueMessageParser.Complex_numberContext, self).__init__(parent, invokingState)
            self.parser = parser

        def IMAG_NUMBER(self):
            return self.getToken(QrogueMessageParser.IMAG_NUMBER, 0)

        def SIGN(self, i=None):
            if i is None:
                return self.getTokens(QrogueMessageParser.SIGN)
            else:
                return self.getToken(QrogueMessageParser.SIGN, i)

        def integer(self):
            return self.getTypedRuleContext(QrogueMessageParser.IntegerContext,0)


        def FLOAT(self):
            return self.getToken(QrogueMessageParser.FLOAT, 0)

        def getRuleIndex(self):
            return QrogueMessageParser.RULE_complex_number

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

        localctx = QrogueMessageParser.Complex_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueMessageParser.SIGN:
                self.state = 39
                self.match(QrogueMessageParser.SIGN)


            self.state = 51
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueMessageParser.IMAG_NUMBER]:
                self.state = 42
                self.match(QrogueMessageParser.IMAG_NUMBER)
                pass
            elif token in [QrogueMessageParser.DIGIT, QrogueMessageParser.INTEGER, QrogueMessageParser.FLOAT, QrogueMessageParser.HALLWAY_ID]:
                self.state = 45
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [QrogueMessageParser.DIGIT, QrogueMessageParser.INTEGER, QrogueMessageParser.HALLWAY_ID]:
                    self.state = 43
                    self.integer()
                    pass
                elif token in [QrogueMessageParser.FLOAT]:
                    self.state = 44
                    self.match(QrogueMessageParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueMessageParser.SIGN:
                    self.state = 47
                    self.match(QrogueMessageParser.SIGN)
                    self.state = 48
                    self.match(QrogueMessageParser.IMAG_NUMBER)


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





