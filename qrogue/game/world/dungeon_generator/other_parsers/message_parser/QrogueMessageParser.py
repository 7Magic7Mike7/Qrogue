# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\QrogueMessage.g4 by ANTLR 4.12.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,35,66,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,0,1,
        0,3,0,15,8,0,1,0,5,0,18,8,0,10,0,12,0,21,9,0,1,1,1,1,1,1,1,1,1,1,
        1,1,3,1,29,8,1,1,2,1,2,3,2,33,8,2,1,2,3,2,36,8,2,1,2,1,2,3,2,40,
        8,2,1,2,3,2,43,8,2,1,2,4,2,46,8,2,11,2,12,2,47,1,3,1,3,1,4,3,4,53,
        8,4,1,4,1,4,1,4,3,4,58,8,4,1,4,1,4,3,4,62,8,4,3,4,64,8,4,1,4,0,0,
        5,0,2,4,6,8,0,1,2,0,20,21,30,30,72,0,10,1,0,0,0,2,22,1,0,0,0,4,32,
        1,0,0,0,6,49,1,0,0,0,8,52,1,0,0,0,10,14,5,4,0,0,11,12,5,1,0,0,12,
        13,5,7,0,0,13,15,5,28,0,0,14,11,1,0,0,0,14,15,1,0,0,0,15,19,1,0,
        0,0,16,18,3,2,1,0,17,16,1,0,0,0,18,21,1,0,0,0,19,17,1,0,0,0,19,20,
        1,0,0,0,20,1,1,0,0,0,21,19,1,0,0,0,22,23,5,31,0,0,23,28,3,4,2,0,
        24,25,5,5,0,0,25,26,5,31,0,0,26,27,5,6,0,0,27,29,5,31,0,0,28,24,
        1,0,0,0,28,29,1,0,0,0,29,3,1,0,0,0,30,31,5,7,0,0,31,33,5,28,0,0,
        32,30,1,0,0,0,32,33,1,0,0,0,33,35,1,0,0,0,34,36,5,8,0,0,35,34,1,
        0,0,0,35,36,1,0,0,0,36,42,1,0,0,0,37,39,5,2,0,0,38,40,5,3,0,0,39,
        38,1,0,0,0,39,40,1,0,0,0,40,41,1,0,0,0,41,43,5,20,0,0,42,37,1,0,
        0,0,42,43,1,0,0,0,43,45,1,0,0,0,44,46,5,28,0,0,45,44,1,0,0,0,46,
        47,1,0,0,0,47,45,1,0,0,0,47,48,1,0,0,0,48,5,1,0,0,0,49,50,7,0,0,
        0,50,7,1,0,0,0,51,53,5,24,0,0,52,51,1,0,0,0,52,53,1,0,0,0,53,63,
        1,0,0,0,54,64,5,23,0,0,55,58,3,6,3,0,56,58,5,22,0,0,57,55,1,0,0,
        0,57,56,1,0,0,0,58,61,1,0,0,0,59,60,5,24,0,0,60,62,5,23,0,0,61,59,
        1,0,0,0,61,62,1,0,0,0,62,64,1,0,0,0,63,54,1,0,0,0,63,57,1,0,0,0,
        64,9,1,0,0,0,12,14,19,28,32,35,39,42,47,52,57,61,63
    ]

class QrogueMessageParser ( Parser ):

    grammarFileName = "QrogueMessage.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'default'", "'pos'", "'='", "'[Messages]'", 
                     "'when'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'tutorial'", "'trigger'", "'Qrogue<'", "'>Qrogue'", 
                     "'~'", "'|'", "','", "'#'", "'..'", "'__'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "MESSAGES", "MSG_EVENT", "MSG_ALTERNATIVE", "MSG_SPEAKER", 
                      "MSG_PRIORITY", "DIRECTION", "TUTORIAL_LITERAL", "TRIGGER_LITERAL", 
                      "HEADER", "ENDER", "HORIZONTAL_SEPARATOR", "VERTICAL_SEPARATOR", 
                      "LIST_SEPARATOR", "WALL", "EMPTY_HALLWAY", "EMPTY_ROOM", 
                      "DIGIT", "INTEGER", "FLOAT", "IMAG_NUMBER", "SIGN", 
                      "CHARACTER_LOW", "CHARACTER_UP", "CHARACTER", "TEXT", 
                      "ROOM_ID", "HALLWAY_ID", "REFERENCE", "WS", "UNIVERSAL_SEPARATOR", 
                      "COMMENT", "LINE_COMMENT" ]

    RULE_messages = 0
    RULE_message = 1
    RULE_message_body = 2
    RULE_integer = 3
    RULE_complex_number = 4

    ruleNames =  [ "messages", "message", "message_body", "integer", "complex_number" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    MESSAGES=4
    MSG_EVENT=5
    MSG_ALTERNATIVE=6
    MSG_SPEAKER=7
    MSG_PRIORITY=8
    DIRECTION=9
    TUTORIAL_LITERAL=10
    TRIGGER_LITERAL=11
    HEADER=12
    ENDER=13
    HORIZONTAL_SEPARATOR=14
    VERTICAL_SEPARATOR=15
    LIST_SEPARATOR=16
    WALL=17
    EMPTY_HALLWAY=18
    EMPTY_ROOM=19
    DIGIT=20
    INTEGER=21
    FLOAT=22
    IMAG_NUMBER=23
    SIGN=24
    CHARACTER_LOW=25
    CHARACTER_UP=26
    CHARACTER=27
    TEXT=28
    ROOM_ID=29
    HALLWAY_ID=30
    REFERENCE=31
    WS=32
    UNIVERSAL_SEPARATOR=33
    COMMENT=34
    LINE_COMMENT=35

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.12.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class MessagesContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MESSAGES(self):
            return self.getToken(QrogueMessageParser.MESSAGES, 0)

        def MSG_SPEAKER(self):
            return self.getToken(QrogueMessageParser.MSG_SPEAKER, 0)

        def TEXT(self):
            return self.getToken(QrogueMessageParser.TEXT, 0)

        def message(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueMessageParser.MessageContext)
            else:
                return self.getTypedRuleContext(QrogueMessageParser.MessageContext,i)


        def getRuleIndex(self):
            return QrogueMessageParser.RULE_messages

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMessages" ):
                listener.enterMessages(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMessages" ):
                listener.exitMessages(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMessages" ):
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
            if _la==1:
                self.state = 11
                self.match(QrogueMessageParser.T__0)
                self.state = 12
                self.match(QrogueMessageParser.MSG_SPEAKER)
                self.state = 13
                self.match(QrogueMessageParser.TEXT)


            self.state = 19
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==31:
                self.state = 16
                self.message()
                self.state = 21
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
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REFERENCE(self, i:int=None):
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

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMessage" ):
                listener.enterMessage(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMessage" ):
                listener.exitMessage(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMessage" ):
                return visitor.visitMessage(self)
            else:
                return visitor.visitChildren(self)




    def message(self):

        localctx = QrogueMessageParser.MessageContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_message)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(QrogueMessageParser.REFERENCE)
            self.state = 23
            self.message_body()
            self.state = 28
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 24
                self.match(QrogueMessageParser.MSG_EVENT)
                self.state = 25
                self.match(QrogueMessageParser.REFERENCE)
                self.state = 26
                self.match(QrogueMessageParser.MSG_ALTERNATIVE)
                self.state = 27
                self.match(QrogueMessageParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Message_bodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def MSG_SPEAKER(self):
            return self.getToken(QrogueMessageParser.MSG_SPEAKER, 0)

        def TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(QrogueMessageParser.TEXT)
            else:
                return self.getToken(QrogueMessageParser.TEXT, i)

        def MSG_PRIORITY(self):
            return self.getToken(QrogueMessageParser.MSG_PRIORITY, 0)

        def DIGIT(self):
            return self.getToken(QrogueMessageParser.DIGIT, 0)

        def getRuleIndex(self):
            return QrogueMessageParser.RULE_message_body

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMessage_body" ):
                listener.enterMessage_body(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMessage_body" ):
                listener.exitMessage_body(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMessage_body" ):
                return visitor.visitMessage_body(self)
            else:
                return visitor.visitChildren(self)




    def message_body(self):

        localctx = QrogueMessageParser.Message_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_message_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==7:
                self.state = 30
                self.match(QrogueMessageParser.MSG_SPEAKER)
                self.state = 31
                self.match(QrogueMessageParser.TEXT)


            self.state = 35
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==8:
                self.state = 34
                self.match(QrogueMessageParser.MSG_PRIORITY)


            self.state = 42
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 37
                self.match(QrogueMessageParser.T__1)
                self.state = 39
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 38
                    self.match(QrogueMessageParser.T__2)


                self.state = 41
                self.match(QrogueMessageParser.DIGIT)


            self.state = 45 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 44
                self.match(QrogueMessageParser.TEXT)
                self.state = 47 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==28):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IntegerContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self):
            return self.getToken(QrogueMessageParser.DIGIT, 0)

        def HALLWAY_ID(self):
            return self.getToken(QrogueMessageParser.HALLWAY_ID, 0)

        def INTEGER(self):
            return self.getToken(QrogueMessageParser.INTEGER, 0)

        def getRuleIndex(self):
            return QrogueMessageParser.RULE_integer

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInteger" ):
                listener.enterInteger(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInteger" ):
                listener.exitInteger(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInteger" ):
                return visitor.visitInteger(self)
            else:
                return visitor.visitChildren(self)




    def integer(self):

        localctx = QrogueMessageParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 49
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1076887552) != 0)):
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
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IMAG_NUMBER(self):
            return self.getToken(QrogueMessageParser.IMAG_NUMBER, 0)

        def SIGN(self, i:int=None):
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

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComplex_number" ):
                listener.enterComplex_number(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComplex_number" ):
                listener.exitComplex_number(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComplex_number" ):
                return visitor.visitComplex_number(self)
            else:
                return visitor.visitChildren(self)




    def complex_number(self):

        localctx = QrogueMessageParser.Complex_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==24:
                self.state = 51
                self.match(QrogueMessageParser.SIGN)


            self.state = 63
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [23]:
                self.state = 54
                self.match(QrogueMessageParser.IMAG_NUMBER)
                pass
            elif token in [20, 21, 22, 30]:
                self.state = 57
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [20, 21, 30]:
                    self.state = 55
                    self.integer()
                    pass
                elif token in [22]:
                    self.state = 56
                    self.match(QrogueMessageParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 61
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==24:
                    self.state = 59
                    self.match(QrogueMessageParser.SIGN)
                    self.state = 60
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





