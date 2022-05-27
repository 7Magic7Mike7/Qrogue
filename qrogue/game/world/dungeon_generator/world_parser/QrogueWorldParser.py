# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueWorld.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,57,178,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,1,0,1,0,1,0,1,0,3,0,35,8,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,
        1,1,1,1,1,1,1,2,1,2,1,2,3,2,50,8,2,1,2,1,2,1,3,1,3,1,4,3,4,57,8,
        4,1,4,1,4,1,4,3,4,62,8,4,1,4,1,4,3,4,66,8,4,3,4,68,8,4,1,5,1,5,5,
        5,72,8,5,10,5,12,5,75,9,5,1,5,1,5,1,5,1,5,5,5,81,8,5,10,5,12,5,84,
        9,5,1,5,5,5,87,8,5,10,5,12,5,90,9,5,1,6,1,6,1,6,1,6,5,6,96,8,6,10,
        6,12,6,99,9,6,1,6,1,6,1,7,1,7,4,7,105,8,7,11,7,12,7,106,1,7,1,7,
        1,8,1,8,5,8,113,8,8,10,8,12,8,116,9,8,1,9,1,9,1,9,1,9,1,9,1,10,1,
        10,1,10,1,10,1,10,1,11,3,11,129,8,11,1,12,1,12,5,12,133,8,12,10,
        12,12,12,136,9,12,1,13,1,13,1,13,1,14,1,14,1,14,1,14,1,14,1,14,3,
        14,147,8,14,1,14,1,14,1,14,3,14,152,8,14,3,14,154,8,14,1,14,1,14,
        1,14,1,14,1,14,5,14,161,8,14,10,14,12,14,164,9,14,1,14,3,14,167,
        8,14,1,14,1,14,1,14,3,14,172,8,14,1,14,1,14,3,14,176,8,14,1,14,0,
        0,15,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,0,5,1,0,41,42,2,0,20,
        21,30,30,2,0,19,19,29,29,2,0,18,18,30,30,1,0,39,40,185,0,30,1,0,
        0,0,2,41,1,0,0,0,4,46,1,0,0,0,6,53,1,0,0,0,8,56,1,0,0,0,10,69,1,
        0,0,0,12,91,1,0,0,0,14,102,1,0,0,0,16,110,1,0,0,0,18,117,1,0,0,0,
        20,122,1,0,0,0,22,128,1,0,0,0,24,130,1,0,0,0,26,137,1,0,0,0,28,140,
        1,0,0,0,30,34,5,12,0,0,31,32,5,1,0,0,32,33,5,2,0,0,33,35,5,28,0,
        0,34,31,1,0,0,0,34,35,1,0,0,0,35,36,1,0,0,0,36,37,3,10,5,0,37,38,
        3,16,8,0,38,39,3,24,12,0,39,40,5,13,0,0,40,1,1,0,0,0,41,42,5,3,0,
        0,42,43,5,28,0,0,43,44,5,4,0,0,44,45,5,31,0,0,45,3,1,0,0,0,46,47,
        7,0,0,0,47,49,5,20,0,0,48,50,5,20,0,0,49,48,1,0,0,0,49,50,1,0,0,
        0,50,51,1,0,0,0,51,52,5,11,0,0,52,5,1,0,0,0,53,54,7,1,0,0,54,7,1,
        0,0,0,55,57,5,24,0,0,56,55,1,0,0,0,56,57,1,0,0,0,57,67,1,0,0,0,58,
        68,5,23,0,0,59,62,3,6,3,0,60,62,5,22,0,0,61,59,1,0,0,0,61,60,1,0,
        0,0,62,65,1,0,0,0,63,64,5,24,0,0,64,66,5,23,0,0,65,63,1,0,0,0,65,
        66,1,0,0,0,66,68,1,0,0,0,67,58,1,0,0,0,67,61,1,0,0,0,68,9,1,0,0,
        0,69,73,5,36,0,0,70,72,5,14,0,0,71,70,1,0,0,0,72,75,1,0,0,0,73,71,
        1,0,0,0,73,74,1,0,0,0,74,76,1,0,0,0,75,73,1,0,0,0,76,82,3,12,6,0,
        77,78,3,14,7,0,78,79,3,12,6,0,79,81,1,0,0,0,80,77,1,0,0,0,81,84,
        1,0,0,0,82,80,1,0,0,0,82,83,1,0,0,0,83,88,1,0,0,0,84,82,1,0,0,0,
        85,87,5,14,0,0,86,85,1,0,0,0,87,90,1,0,0,0,88,86,1,0,0,0,88,89,1,
        0,0,0,89,11,1,0,0,0,90,88,1,0,0,0,91,92,5,15,0,0,92,97,7,2,0,0,93,
        94,7,3,0,0,94,96,7,2,0,0,95,93,1,0,0,0,96,99,1,0,0,0,97,95,1,0,0,
        0,97,98,1,0,0,0,98,100,1,0,0,0,99,97,1,0,0,0,100,101,5,15,0,0,101,
        13,1,0,0,0,102,104,5,15,0,0,103,105,7,3,0,0,104,103,1,0,0,0,105,
        106,1,0,0,0,106,104,1,0,0,0,106,107,1,0,0,0,107,108,1,0,0,0,108,
        109,5,15,0,0,109,15,1,0,0,0,110,114,5,37,0,0,111,113,3,18,9,0,112,
        111,1,0,0,0,113,116,1,0,0,0,114,112,1,0,0,0,114,115,1,0,0,0,115,
        17,1,0,0,0,116,114,1,0,0,0,117,118,5,29,0,0,118,119,3,20,10,0,119,
        120,5,5,0,0,120,121,3,2,1,0,121,19,1,0,0,0,122,123,5,6,0,0,123,124,
        3,22,11,0,124,125,3,4,2,0,125,126,5,7,0,0,126,21,1,0,0,0,127,129,
        7,4,0,0,128,127,1,0,0,0,128,129,1,0,0,0,129,23,1,0,0,0,130,134,5,
        38,0,0,131,133,3,26,13,0,132,131,1,0,0,0,133,136,1,0,0,0,134,132,
        1,0,0,0,134,135,1,0,0,0,135,25,1,0,0,0,136,134,1,0,0,0,137,138,5,
        30,0,0,138,139,3,28,14,0,139,27,1,0,0,0,140,146,5,6,0,0,141,147,
        5,50,0,0,142,147,5,51,0,0,143,147,5,52,0,0,144,145,5,53,0,0,145,
        147,5,31,0,0,146,141,1,0,0,0,146,142,1,0,0,0,146,143,1,0,0,0,146,
        144,1,0,0,0,147,153,1,0,0,0,148,149,5,8,0,0,149,151,5,11,0,0,150,
        152,5,54,0,0,151,150,1,0,0,0,151,152,1,0,0,0,152,154,1,0,0,0,153,
        148,1,0,0,0,153,154,1,0,0,0,154,166,1,0,0,0,155,156,5,55,0,0,156,
        157,5,9,0,0,157,162,5,30,0,0,158,159,5,16,0,0,159,161,5,30,0,0,160,
        158,1,0,0,0,161,164,1,0,0,0,162,160,1,0,0,0,162,163,1,0,0,0,163,
        165,1,0,0,0,164,162,1,0,0,0,165,167,5,10,0,0,166,155,1,0,0,0,166,
        167,1,0,0,0,167,168,1,0,0,0,168,171,5,7,0,0,169,170,5,56,0,0,170,
        172,5,31,0,0,171,169,1,0,0,0,171,172,1,0,0,0,172,175,1,0,0,0,173,
        174,5,57,0,0,174,176,5,31,0,0,175,173,1,0,0,0,175,176,1,0,0,0,176,
        29,1,0,0,0,21,34,49,56,61,65,67,73,82,88,97,106,114,128,134,146,
        151,153,162,166,171,175
    ]

class QrogueWorldParser ( Parser ):

    grammarFileName = "QrogueWorld.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'Name'", u"'='", u"'description'", 
                     u"'teleport'", u"':'", u"'('", u"')'", u"'one way'", 
                     u"'['", u"']'", u"<INVALID>", u"'Qrogue<'", u"'>Qrogue'", 
                     u"'~'", u"'|'", u"','", u"'#'", u"'..'", u"'__'", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"'[Layout]'", 
                     u"<INVALID>", u"'[Hallways]'", u"'visible'", u"'foggy'", 
                     u"'World'", u"'Level'", u"'Spawn'", u"'Wild'", u"'Shop'", 
                     u"'Riddle'", u"'Boss'", u"'Gate'", u"'Treasure'", u"'open'", 
                     u"'closed'", u"'locked'", u"'event'", u"'permanent'", 
                     u"'entangled'", u"'tutorial'", u"'trigger'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"DIRECTION", 
                      u"HEADER", u"ENDER", u"HORIZONTAL_SEPARATOR", u"VERTICAL_SEPARATOR", 
                      u"LIST_SEPARATOR", u"WALL", u"EMPTY_HALLWAY", u"EMPTY_ROOM", 
                      u"DIGIT", u"INTEGER", u"FLOAT", u"IMAG_NUMBER", u"SIGN", 
                      u"CHARACTER_LOW", u"CHARACTER_UP", u"CHARACTER", u"TEXT", 
                      u"ROOM_ID", u"HALLWAY_ID", u"REFERENCE", u"WS", u"UNIVERSAL_SEPARATOR", 
                      u"COMMENT", u"LINE_COMMENT", u"LAYOUT", u"ROOMS", 
                      u"HALLWAYS", u"VISIBLE_LITERAL", u"FOGGY_LITERAL", 
                      u"WORLD_LITERAL", u"LEVEL_LITERAL", u"SPAWN_LITERAL", 
                      u"WILD_LITERAL", u"SHOP_LITERAL", u"RIDDLE_LITERAL", 
                      u"BOSS_LITERAL", u"GATE_ROOM_LITERAL", u"TREASURE_LITERAL", 
                      u"OPEN_LITERAL", u"CLOSED_LITERAL", u"LOCKED_LITERAL", 
                      u"EVENT_LITERAL", u"PERMANENT_LITERAL", u"ENTANGLED_LITERAL", 
                      u"TUTORIAL_LITERAL", u"TRIGGER_LITERAL" ]

    RULE_start = 0
    RULE_room_content = 1
    RULE_r_type = 2
    RULE_integer = 3
    RULE_complex_number = 4
    RULE_layout = 5
    RULE_l_room_row = 6
    RULE_l_hallway_row = 7
    RULE_rooms = 8
    RULE_room = 9
    RULE_r_attributes = 10
    RULE_r_visibility = 11
    RULE_hallways = 12
    RULE_hallway = 13
    RULE_h_attributes = 14

    ruleNames =  [ u"start", u"room_content", u"r_type", u"integer", u"complex_number", 
                   u"layout", u"l_room_row", u"l_hallway_row", u"rooms", 
                   u"room", u"r_attributes", u"r_visibility", u"hallways", 
                   u"hallway", u"h_attributes" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    DIRECTION=11
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
    LAYOUT=36
    ROOMS=37
    HALLWAYS=38
    VISIBLE_LITERAL=39
    FOGGY_LITERAL=40
    WORLD_LITERAL=41
    LEVEL_LITERAL=42
    SPAWN_LITERAL=43
    WILD_LITERAL=44
    SHOP_LITERAL=45
    RIDDLE_LITERAL=46
    BOSS_LITERAL=47
    GATE_ROOM_LITERAL=48
    TREASURE_LITERAL=49
    OPEN_LITERAL=50
    CLOSED_LITERAL=51
    LOCKED_LITERAL=52
    EVENT_LITERAL=53
    PERMANENT_LITERAL=54
    ENTANGLED_LITERAL=55
    TUTORIAL_LITERAL=56
    TRIGGER_LITERAL=57

    def __init__(self, input, output=sys.stdout):
        super(QrogueWorldParser, self).__init__(input, output=output)
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class StartContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.StartContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HEADER(self):
            return self.getToken(QrogueWorldParser.HEADER, 0)

        def layout(self):
            return self.getTypedRuleContext(QrogueWorldParser.LayoutContext,0)


        def rooms(self):
            return self.getTypedRuleContext(QrogueWorldParser.RoomsContext,0)


        def hallways(self):
            return self.getTypedRuleContext(QrogueWorldParser.HallwaysContext,0)


        def ENDER(self):
            return self.getToken(QrogueWorldParser.ENDER, 0)

        def TEXT(self):
            return self.getToken(QrogueWorldParser.TEXT, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_start

        def enterRule(self, listener):
            if hasattr(listener, "enterStart"):
                listener.enterStart(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitStart"):
                listener.exitStart(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitStart"):
                return visitor.visitStart(self)
            else:
                return visitor.visitChildren(self)




    def start(self):

        localctx = QrogueWorldParser.StartContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_start)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self.match(QrogueWorldParser.HEADER)
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__0:
                self.state = 31
                self.match(QrogueWorldParser.T__0)
                self.state = 32
                self.match(QrogueWorldParser.T__1)
                self.state = 33
                self.match(QrogueWorldParser.TEXT)


            self.state = 36
            self.layout()
            self.state = 37
            self.rooms()
            self.state = 38
            self.hallways()
            self.state = 39
            self.match(QrogueWorldParser.ENDER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Room_contentContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.Room_contentContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(QrogueWorldParser.TEXT, 0)

        def REFERENCE(self):
            return self.getToken(QrogueWorldParser.REFERENCE, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_room_content

        def enterRule(self, listener):
            if hasattr(listener, "enterRoom_content"):
                listener.enterRoom_content(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRoom_content"):
                listener.exitRoom_content(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRoom_content"):
                return visitor.visitRoom_content(self)
            else:
                return visitor.visitChildren(self)




    def room_content(self):

        localctx = QrogueWorldParser.Room_contentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_room_content)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            self.match(QrogueWorldParser.T__2)
            self.state = 42
            self.match(QrogueWorldParser.TEXT)
            self.state = 43
            self.match(QrogueWorldParser.T__3)
            self.state = 44
            self.match(QrogueWorldParser.REFERENCE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class R_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.R_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.DIGIT)
            else:
                return self.getToken(QrogueWorldParser.DIGIT, i)

        def DIRECTION(self):
            return self.getToken(QrogueWorldParser.DIRECTION, 0)

        def WORLD_LITERAL(self):
            return self.getToken(QrogueWorldParser.WORLD_LITERAL, 0)

        def LEVEL_LITERAL(self):
            return self.getToken(QrogueWorldParser.LEVEL_LITERAL, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_r_type

        def enterRule(self, listener):
            if hasattr(listener, "enterR_type"):
                listener.enterR_type(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitR_type"):
                listener.exitR_type(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitR_type"):
                return visitor.visitR_type(self)
            else:
                return visitor.visitChildren(self)




    def r_type(self):

        localctx = QrogueWorldParser.R_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_r_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.WORLD_LITERAL or _la==QrogueWorldParser.LEVEL_LITERAL):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 47
            self.match(QrogueWorldParser.DIGIT)
            self.state = 49
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.DIGIT:
                self.state = 48
                self.match(QrogueWorldParser.DIGIT)


            self.state = 51
            self.match(QrogueWorldParser.DIRECTION)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IntegerContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.IntegerContext, self).__init__(parent, invokingState)
            self.parser = parser

        def DIGIT(self):
            return self.getToken(QrogueWorldParser.DIGIT, 0)

        def HALLWAY_ID(self):
            return self.getToken(QrogueWorldParser.HALLWAY_ID, 0)

        def INTEGER(self):
            return self.getToken(QrogueWorldParser.INTEGER, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_integer

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

        localctx = QrogueWorldParser.IntegerContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << QrogueWorldParser.DIGIT) | (1 << QrogueWorldParser.INTEGER) | (1 << QrogueWorldParser.HALLWAY_ID))) != 0)):
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
            super(QrogueWorldParser.Complex_numberContext, self).__init__(parent, invokingState)
            self.parser = parser

        def IMAG_NUMBER(self):
            return self.getToken(QrogueWorldParser.IMAG_NUMBER, 0)

        def SIGN(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.SIGN)
            else:
                return self.getToken(QrogueWorldParser.SIGN, i)

        def integer(self):
            return self.getTypedRuleContext(QrogueWorldParser.IntegerContext,0)


        def FLOAT(self):
            return self.getToken(QrogueWorldParser.FLOAT, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_complex_number

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

        localctx = QrogueWorldParser.Complex_numberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 56
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.SIGN:
                self.state = 55
                self.match(QrogueWorldParser.SIGN)


            self.state = 67
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.IMAG_NUMBER]:
                self.state = 58
                self.match(QrogueWorldParser.IMAG_NUMBER)
                pass
            elif token in [QrogueWorldParser.DIGIT, QrogueWorldParser.INTEGER, QrogueWorldParser.FLOAT, QrogueWorldParser.HALLWAY_ID]:
                self.state = 61
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [QrogueWorldParser.DIGIT, QrogueWorldParser.INTEGER, QrogueWorldParser.HALLWAY_ID]:
                    self.state = 59
                    self.integer()
                    pass
                elif token in [QrogueWorldParser.FLOAT]:
                    self.state = 60
                    self.match(QrogueWorldParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 65
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.SIGN:
                    self.state = 63
                    self.match(QrogueWorldParser.SIGN)
                    self.state = 64
                    self.match(QrogueWorldParser.IMAG_NUMBER)


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


    class LayoutContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.LayoutContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LAYOUT(self):
            return self.getToken(QrogueWorldParser.LAYOUT, 0)

        def l_room_row(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueWorldParser.L_room_rowContext)
            else:
                return self.getTypedRuleContext(QrogueWorldParser.L_room_rowContext,i)


        def HORIZONTAL_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.HORIZONTAL_SEPARATOR)
            else:
                return self.getToken(QrogueWorldParser.HORIZONTAL_SEPARATOR, i)

        def l_hallway_row(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueWorldParser.L_hallway_rowContext)
            else:
                return self.getTypedRuleContext(QrogueWorldParser.L_hallway_rowContext,i)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_layout

        def enterRule(self, listener):
            if hasattr(listener, "enterLayout"):
                listener.enterLayout(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitLayout"):
                listener.exitLayout(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitLayout"):
                return visitor.visitLayout(self)
            else:
                return visitor.visitChildren(self)




    def layout(self):

        localctx = QrogueWorldParser.LayoutContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_layout)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self.match(QrogueWorldParser.LAYOUT)
            self.state = 73
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 70
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 75
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 76
            self.l_room_row()
            self.state = 82
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.VERTICAL_SEPARATOR:
                self.state = 77
                self.l_hallway_row()
                self.state = 78
                self.l_room_row()
                self.state = 84
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 85
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 90
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class L_room_rowContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.L_room_rowContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VERTICAL_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.VERTICAL_SEPARATOR)
            else:
                return self.getToken(QrogueWorldParser.VERTICAL_SEPARATOR, i)

        def ROOM_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.ROOM_ID)
            else:
                return self.getToken(QrogueWorldParser.ROOM_ID, i)

        def EMPTY_ROOM(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.EMPTY_ROOM)
            else:
                return self.getToken(QrogueWorldParser.EMPTY_ROOM, i)

        def HALLWAY_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.HALLWAY_ID)
            else:
                return self.getToken(QrogueWorldParser.HALLWAY_ID, i)

        def EMPTY_HALLWAY(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.EMPTY_HALLWAY)
            else:
                return self.getToken(QrogueWorldParser.EMPTY_HALLWAY, i)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_l_room_row

        def enterRule(self, listener):
            if hasattr(listener, "enterL_room_row"):
                listener.enterL_room_row(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitL_room_row"):
                listener.exitL_room_row(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitL_room_row"):
                return visitor.visitL_room_row(self)
            else:
                return visitor.visitChildren(self)




    def l_room_row(self):

        localctx = QrogueWorldParser.L_room_rowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_l_room_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 92
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 97
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 93
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 94
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 99
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 100
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class L_hallway_rowContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.L_hallway_rowContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VERTICAL_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.VERTICAL_SEPARATOR)
            else:
                return self.getToken(QrogueWorldParser.VERTICAL_SEPARATOR, i)

        def HALLWAY_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.HALLWAY_ID)
            else:
                return self.getToken(QrogueWorldParser.HALLWAY_ID, i)

        def EMPTY_HALLWAY(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.EMPTY_HALLWAY)
            else:
                return self.getToken(QrogueWorldParser.EMPTY_HALLWAY, i)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_l_hallway_row

        def enterRule(self, listener):
            if hasattr(listener, "enterL_hallway_row"):
                listener.enterL_hallway_row(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitL_hallway_row"):
                listener.exitL_hallway_row(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitL_hallway_row"):
                return visitor.visitL_hallway_row(self)
            else:
                return visitor.visitChildren(self)




    def l_hallway_row(self):

        localctx = QrogueWorldParser.L_hallway_rowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_l_hallway_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 102
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 104 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 103
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 106 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    break

            self.state = 108
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RoomsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.RoomsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ROOMS(self):
            return self.getToken(QrogueWorldParser.ROOMS, 0)

        def room(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueWorldParser.RoomContext)
            else:
                return self.getTypedRuleContext(QrogueWorldParser.RoomContext,i)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_rooms

        def enterRule(self, listener):
            if hasattr(listener, "enterRooms"):
                listener.enterRooms(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRooms"):
                listener.exitRooms(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRooms"):
                return visitor.visitRooms(self)
            else:
                return visitor.visitChildren(self)




    def rooms(self):

        localctx = QrogueWorldParser.RoomsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_rooms)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 110
            self.match(QrogueWorldParser.ROOMS)
            self.state = 114
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.ROOM_ID:
                self.state = 111
                self.room()
                self.state = 116
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RoomContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.RoomContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ROOM_ID(self):
            return self.getToken(QrogueWorldParser.ROOM_ID, 0)

        def r_attributes(self):
            return self.getTypedRuleContext(QrogueWorldParser.R_attributesContext,0)


        def room_content(self):
            return self.getTypedRuleContext(QrogueWorldParser.Room_contentContext,0)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_room

        def enterRule(self, listener):
            if hasattr(listener, "enterRoom"):
                listener.enterRoom(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitRoom"):
                listener.exitRoom(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitRoom"):
                return visitor.visitRoom(self)
            else:
                return visitor.visitChildren(self)




    def room(self):

        localctx = QrogueWorldParser.RoomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_room)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 117
            self.match(QrogueWorldParser.ROOM_ID)
            self.state = 118
            self.r_attributes()
            self.state = 119
            self.match(QrogueWorldParser.T__4)
            self.state = 120
            self.room_content()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class R_attributesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.R_attributesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def r_visibility(self):
            return self.getTypedRuleContext(QrogueWorldParser.R_visibilityContext,0)


        def r_type(self):
            return self.getTypedRuleContext(QrogueWorldParser.R_typeContext,0)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_r_attributes

        def enterRule(self, listener):
            if hasattr(listener, "enterR_attributes"):
                listener.enterR_attributes(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitR_attributes"):
                listener.exitR_attributes(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitR_attributes"):
                return visitor.visitR_attributes(self)
            else:
                return visitor.visitChildren(self)




    def r_attributes(self):

        localctx = QrogueWorldParser.R_attributesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_r_attributes)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 122
            self.match(QrogueWorldParser.T__5)
            self.state = 123
            self.r_visibility()
            self.state = 124
            self.r_type()
            self.state = 125
            self.match(QrogueWorldParser.T__6)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class R_visibilityContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.R_visibilityContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VISIBLE_LITERAL(self):
            return self.getToken(QrogueWorldParser.VISIBLE_LITERAL, 0)

        def FOGGY_LITERAL(self):
            return self.getToken(QrogueWorldParser.FOGGY_LITERAL, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_r_visibility

        def enterRule(self, listener):
            if hasattr(listener, "enterR_visibility"):
                listener.enterR_visibility(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitR_visibility"):
                listener.exitR_visibility(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitR_visibility"):
                return visitor.visitR_visibility(self)
            else:
                return visitor.visitChildren(self)




    def r_visibility(self):

        localctx = QrogueWorldParser.R_visibilityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_r_visibility)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 128
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.VISIBLE_LITERAL or _la==QrogueWorldParser.FOGGY_LITERAL:
                self.state = 127
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.VISIBLE_LITERAL or _la==QrogueWorldParser.FOGGY_LITERAL):
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


    class HallwaysContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.HallwaysContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HALLWAYS(self):
            return self.getToken(QrogueWorldParser.HALLWAYS, 0)

        def hallway(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueWorldParser.HallwayContext)
            else:
                return self.getTypedRuleContext(QrogueWorldParser.HallwayContext,i)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_hallways

        def enterRule(self, listener):
            if hasattr(listener, "enterHallways"):
                listener.enterHallways(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitHallways"):
                listener.exitHallways(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitHallways"):
                return visitor.visitHallways(self)
            else:
                return visitor.visitChildren(self)




    def hallways(self):

        localctx = QrogueWorldParser.HallwaysContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_hallways)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 130
            self.match(QrogueWorldParser.HALLWAYS)
            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 131
                self.hallway()
                self.state = 136
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HallwayContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.HallwayContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HALLWAY_ID(self):
            return self.getToken(QrogueWorldParser.HALLWAY_ID, 0)

        def h_attributes(self):
            return self.getTypedRuleContext(QrogueWorldParser.H_attributesContext,0)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_hallway

        def enterRule(self, listener):
            if hasattr(listener, "enterHallway"):
                listener.enterHallway(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitHallway"):
                listener.exitHallway(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitHallway"):
                return visitor.visitHallway(self)
            else:
                return visitor.visitChildren(self)




    def hallway(self):

        localctx = QrogueWorldParser.HallwayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_hallway)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 137
            self.match(QrogueWorldParser.HALLWAY_ID)
            self.state = 138
            self.h_attributes()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class H_attributesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.H_attributesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def OPEN_LITERAL(self):
            return self.getToken(QrogueWorldParser.OPEN_LITERAL, 0)

        def CLOSED_LITERAL(self):
            return self.getToken(QrogueWorldParser.CLOSED_LITERAL, 0)

        def LOCKED_LITERAL(self):
            return self.getToken(QrogueWorldParser.LOCKED_LITERAL, 0)

        def EVENT_LITERAL(self):
            return self.getToken(QrogueWorldParser.EVENT_LITERAL, 0)

        def REFERENCE(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.REFERENCE)
            else:
                return self.getToken(QrogueWorldParser.REFERENCE, i)

        def DIRECTION(self):
            return self.getToken(QrogueWorldParser.DIRECTION, 0)

        def ENTANGLED_LITERAL(self):
            return self.getToken(QrogueWorldParser.ENTANGLED_LITERAL, 0)

        def HALLWAY_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.HALLWAY_ID)
            else:
                return self.getToken(QrogueWorldParser.HALLWAY_ID, i)

        def TUTORIAL_LITERAL(self):
            return self.getToken(QrogueWorldParser.TUTORIAL_LITERAL, 0)

        def TRIGGER_LITERAL(self):
            return self.getToken(QrogueWorldParser.TRIGGER_LITERAL, 0)

        def PERMANENT_LITERAL(self):
            return self.getToken(QrogueWorldParser.PERMANENT_LITERAL, 0)

        def LIST_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.LIST_SEPARATOR)
            else:
                return self.getToken(QrogueWorldParser.LIST_SEPARATOR, i)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_h_attributes

        def enterRule(self, listener):
            if hasattr(listener, "enterH_attributes"):
                listener.enterH_attributes(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitH_attributes"):
                listener.exitH_attributes(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitH_attributes"):
                return visitor.visitH_attributes(self)
            else:
                return visitor.visitChildren(self)




    def h_attributes(self):

        localctx = QrogueWorldParser.H_attributesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_h_attributes)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 140
            self.match(QrogueWorldParser.T__5)
            self.state = 146
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.OPEN_LITERAL]:
                self.state = 141
                self.match(QrogueWorldParser.OPEN_LITERAL)
                pass
            elif token in [QrogueWorldParser.CLOSED_LITERAL]:
                self.state = 142
                self.match(QrogueWorldParser.CLOSED_LITERAL)
                pass
            elif token in [QrogueWorldParser.LOCKED_LITERAL]:
                self.state = 143
                self.match(QrogueWorldParser.LOCKED_LITERAL)
                pass
            elif token in [QrogueWorldParser.EVENT_LITERAL]:
                self.state = 144
                self.match(QrogueWorldParser.EVENT_LITERAL)
                self.state = 145
                self.match(QrogueWorldParser.REFERENCE)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 153
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__7:
                self.state = 148
                self.match(QrogueWorldParser.T__7)
                self.state = 149
                self.match(QrogueWorldParser.DIRECTION)
                self.state = 151
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.PERMANENT_LITERAL:
                    self.state = 150
                    self.match(QrogueWorldParser.PERMANENT_LITERAL)




            self.state = 166
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.ENTANGLED_LITERAL:
                self.state = 155
                self.match(QrogueWorldParser.ENTANGLED_LITERAL)
                self.state = 156
                self.match(QrogueWorldParser.T__8)
                self.state = 157
                self.match(QrogueWorldParser.HALLWAY_ID)
                self.state = 162
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==QrogueWorldParser.LIST_SEPARATOR:
                    self.state = 158
                    self.match(QrogueWorldParser.LIST_SEPARATOR)
                    self.state = 159
                    self.match(QrogueWorldParser.HALLWAY_ID)
                    self.state = 164
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 165
                self.match(QrogueWorldParser.T__9)


            self.state = 168
            self.match(QrogueWorldParser.T__6)
            self.state = 171
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.TUTORIAL_LITERAL:
                self.state = 169
                self.match(QrogueWorldParser.TUTORIAL_LITERAL)
                self.state = 170
                self.match(QrogueWorldParser.REFERENCE)


            self.state = 175
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.TRIGGER_LITERAL:
                self.state = 173
                self.match(QrogueWorldParser.TRIGGER_LITERAL)
                self.state = 174
                self.match(QrogueWorldParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





