# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\QrogueBasics.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,27,21,2,0,7,0,2,1,7,1,1,0,1,0,1,1,3,1,8,8,1,1,1,1,1,1,1,3,1,
        13,8,1,1,1,1,1,3,1,17,8,1,3,1,19,8,1,1,1,0,0,2,0,2,0,1,2,0,12,13,
        22,22,22,0,4,1,0,0,0,2,7,1,0,0,0,4,5,7,0,0,0,5,1,1,0,0,0,6,8,5,16,
        0,0,7,6,1,0,0,0,7,8,1,0,0,0,8,18,1,0,0,0,9,19,5,15,0,0,10,13,3,0,
        0,0,11,13,5,14,0,0,12,10,1,0,0,0,12,11,1,0,0,0,13,16,1,0,0,0,14,
        15,5,16,0,0,15,17,5,15,0,0,16,14,1,0,0,0,16,17,1,0,0,0,17,19,1,0,
        0,0,18,9,1,0,0,0,18,12,1,0,0,0,19,3,1,0,0,0,4,7,12,16,18
    ]

class QrogueBasicsParser ( Parser ):

    grammarFileName = "QrogueBasics.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"'tutorial'", u"'trigger'", 
                     u"'Qrogue<'", u"'>Qrogue'", u"'~'", u"'|'", u"','", 
                     u"'#'", u"'..'", u"'__'" ]

    symbolicNames = [ u"<INVALID>", u"DIRECTION", u"TUTORIAL_LITERAL", u"TRIGGER_LITERAL", 
                      u"HEADER", u"ENDER", u"HORIZONTAL_SEPARATOR", u"VERTICAL_SEPARATOR", 
                      u"LIST_SEPARATOR", u"WALL", u"EMPTY_HALLWAY", u"EMPTY_ROOM", 
                      u"DIGIT", u"INTEGER", u"FLOAT", u"IMAG_NUMBER", u"SIGN", 
                      u"CHARACTER_LOW", u"CHARACTER_UP", u"CHARACTER", u"TEXT", 
                      u"ROOM_ID", u"HALLWAY_ID", u"REFERENCE", u"WS", u"UNIVERSAL_SEPARATOR", 
                      u"COMMENT", u"LINE_COMMENT" ]

    RULE_integer = 0
    RULE_complex_number = 1

    ruleNames =  [ u"integer", u"complex_number" ]

    EOF = Token.EOF
    DIRECTION=1
    TUTORIAL_LITERAL=2
    TRIGGER_LITERAL=3
    HEADER=4
    ENDER=5
    HORIZONTAL_SEPARATOR=6
    VERTICAL_SEPARATOR=7
    LIST_SEPARATOR=8
    WALL=9
    EMPTY_HALLWAY=10
    EMPTY_ROOM=11
    DIGIT=12
    INTEGER=13
    FLOAT=14
    IMAG_NUMBER=15
    SIGN=16
    CHARACTER_LOW=17
    CHARACTER_UP=18
    CHARACTER=19
    TEXT=20
    ROOM_ID=21
    HALLWAY_ID=22
    REFERENCE=23
    WS=24
    UNIVERSAL_SEPARATOR=25
    COMMENT=26
    LINE_COMMENT=27

    def __init__(self, input, output=sys.stdout):
        super(QrogueBasicsParser, self).__init__(input, output=output)
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class IntegerContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueBasicsParser.IntegerContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self):
            return self.getToken(QrogueBasicsParser.DIGIT, 0)

        def HALLWAY_ID(self):
            return self.getToken(QrogueBasicsParser.HALLWAY_ID, 0)

        def INTEGER(self):
            return self.getToken(QrogueBasicsParser.INTEGER, 0)

        def getRuleIndex(self):
            return QrogueBasicsParser.RULE_integer

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

        localctx = QrogueBasicsParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 4
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << QrogueBasicsParser.DIGIT) | (1 << QrogueBasicsParser.INTEGER) | (1 << QrogueBasicsParser.HALLWAY_ID))) != 0)):
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
            super(QrogueBasicsParser.Complex_numberContext, self).__init__(parent, invokingState)
            self.parser = parser

        def IMAG_NUMBER(self):
            return self.getToken(QrogueBasicsParser.IMAG_NUMBER, 0)

        def SIGN(self, i=None):
            if i is None:
                return self.getTokens(QrogueBasicsParser.SIGN)
            else:
                return self.getToken(QrogueBasicsParser.SIGN, i)

        def integer(self):
            return self.getTypedRuleContext(QrogueBasicsParser.IntegerContext,0)


        def FLOAT(self):
            return self.getToken(QrogueBasicsParser.FLOAT, 0)

        def getRuleIndex(self):
            return QrogueBasicsParser.RULE_complex_number

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

        localctx = QrogueBasicsParser.Complex_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 7
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueBasicsParser.SIGN:
                self.state = 6
                self.match(QrogueBasicsParser.SIGN)


            self.state = 18
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueBasicsParser.IMAG_NUMBER]:
                self.state = 9
                self.match(QrogueBasicsParser.IMAG_NUMBER)
                pass
            elif token in [QrogueBasicsParser.DIGIT, QrogueBasicsParser.INTEGER, QrogueBasicsParser.FLOAT, QrogueBasicsParser.HALLWAY_ID]:
                self.state = 12
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [QrogueBasicsParser.DIGIT, QrogueBasicsParser.INTEGER, QrogueBasicsParser.HALLWAY_ID]:
                    self.state = 10
                    self.integer()
                    pass
                elif token in [QrogueBasicsParser.FLOAT]:
                    self.state = 11
                    self.match(QrogueBasicsParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 16
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueBasicsParser.SIGN:
                    self.state = 14
                    self.match(QrogueBasicsParser.SIGN)
                    self.state = 15
                    self.match(QrogueBasicsParser.IMAG_NUMBER)


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





