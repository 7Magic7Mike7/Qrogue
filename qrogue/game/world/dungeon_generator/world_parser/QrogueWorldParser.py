# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueWorld.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,61,208,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,1,0,1,0,1,0,1,0,3,0,41,8,
        0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,3,2,56,8,2,
        1,2,1,2,1,3,1,3,1,4,3,4,63,8,4,1,4,1,4,1,4,3,4,68,8,4,1,4,1,4,3,
        4,72,8,4,3,4,74,8,4,1,5,1,5,5,5,78,8,5,10,5,12,5,81,9,5,1,5,1,5,
        1,5,1,5,5,5,87,8,5,10,5,12,5,90,9,5,1,5,5,5,93,8,5,10,5,12,5,96,
        9,5,1,6,1,6,1,6,1,6,5,6,102,8,6,10,6,12,6,105,9,6,1,6,1,6,1,7,1,
        7,4,7,111,8,7,11,7,12,7,112,1,7,1,7,1,8,1,8,5,8,119,8,8,10,8,12,
        8,122,9,8,1,9,1,9,1,9,1,9,1,9,1,10,1,10,1,10,1,10,1,10,1,11,3,11,
        135,8,11,1,12,1,12,5,12,139,8,12,10,12,12,12,142,9,12,1,13,1,13,
        1,13,1,14,1,14,1,14,1,14,1,14,1,14,3,14,153,8,14,1,14,1,14,1,14,
        3,14,158,8,14,3,14,160,8,14,1,14,1,14,1,14,1,14,1,14,5,14,167,8,
        14,10,14,12,14,170,9,14,1,14,3,14,173,8,14,1,14,1,14,1,14,3,14,178,
        8,14,1,14,1,14,3,14,182,8,14,1,15,1,15,5,15,186,8,15,10,15,12,15,
        189,9,15,1,16,1,16,1,16,1,16,1,16,1,16,3,16,197,8,16,1,17,1,17,3,
        17,201,8,17,1,17,4,17,204,8,17,11,17,12,17,205,1,17,0,0,18,0,2,4,
        6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,0,5,1,0,43,44,2,0,22,
        23,32,32,2,0,21,21,31,31,2,0,20,20,32,32,1,0,41,42,216,0,36,1,0,
        0,0,2,47,1,0,0,0,4,52,1,0,0,0,6,59,1,0,0,0,8,62,1,0,0,0,10,75,1,
        0,0,0,12,97,1,0,0,0,14,108,1,0,0,0,16,116,1,0,0,0,18,123,1,0,0,0,
        20,128,1,0,0,0,22,134,1,0,0,0,24,136,1,0,0,0,26,143,1,0,0,0,28,146,
        1,0,0,0,30,183,1,0,0,0,32,190,1,0,0,0,34,200,1,0,0,0,36,40,5,14,
        0,0,37,38,5,1,0,0,38,39,5,2,0,0,39,41,5,30,0,0,40,37,1,0,0,0,40,
        41,1,0,0,0,41,42,1,0,0,0,42,43,3,10,5,0,43,44,3,16,8,0,44,45,3,24,
        12,0,45,46,5,15,0,0,46,1,1,0,0,0,47,48,5,3,0,0,48,49,3,34,17,0,49,
        50,5,4,0,0,50,51,5,33,0,0,51,3,1,0,0,0,52,53,7,0,0,0,53,55,5,22,
        0,0,54,56,5,22,0,0,55,54,1,0,0,0,55,56,1,0,0,0,56,57,1,0,0,0,57,
        58,5,11,0,0,58,5,1,0,0,0,59,60,7,1,0,0,60,7,1,0,0,0,61,63,5,26,0,
        0,62,61,1,0,0,0,62,63,1,0,0,0,63,73,1,0,0,0,64,74,5,25,0,0,65,68,
        3,6,3,0,66,68,5,24,0,0,67,65,1,0,0,0,67,66,1,0,0,0,68,71,1,0,0,0,
        69,70,5,26,0,0,70,72,5,25,0,0,71,69,1,0,0,0,71,72,1,0,0,0,72,74,
        1,0,0,0,73,64,1,0,0,0,73,67,1,0,0,0,74,9,1,0,0,0,75,79,5,38,0,0,
        76,78,5,16,0,0,77,76,1,0,0,0,78,81,1,0,0,0,79,77,1,0,0,0,79,80,1,
        0,0,0,80,82,1,0,0,0,81,79,1,0,0,0,82,88,3,12,6,0,83,84,3,14,7,0,
        84,85,3,12,6,0,85,87,1,0,0,0,86,83,1,0,0,0,87,90,1,0,0,0,88,86,1,
        0,0,0,88,89,1,0,0,0,89,94,1,0,0,0,90,88,1,0,0,0,91,93,5,16,0,0,92,
        91,1,0,0,0,93,96,1,0,0,0,94,92,1,0,0,0,94,95,1,0,0,0,95,11,1,0,0,
        0,96,94,1,0,0,0,97,98,5,17,0,0,98,103,7,2,0,0,99,100,7,3,0,0,100,
        102,7,2,0,0,101,99,1,0,0,0,102,105,1,0,0,0,103,101,1,0,0,0,103,104,
        1,0,0,0,104,106,1,0,0,0,105,103,1,0,0,0,106,107,5,17,0,0,107,13,
        1,0,0,0,108,110,5,17,0,0,109,111,7,3,0,0,110,109,1,0,0,0,111,112,
        1,0,0,0,112,110,1,0,0,0,112,113,1,0,0,0,113,114,1,0,0,0,114,115,
        5,17,0,0,115,15,1,0,0,0,116,120,5,39,0,0,117,119,3,18,9,0,118,117,
        1,0,0,0,119,122,1,0,0,0,120,118,1,0,0,0,120,121,1,0,0,0,121,17,1,
        0,0,0,122,120,1,0,0,0,123,124,5,31,0,0,124,125,3,20,10,0,125,126,
        5,5,0,0,126,127,3,2,1,0,127,19,1,0,0,0,128,129,5,6,0,0,129,130,3,
        22,11,0,130,131,3,4,2,0,131,132,5,7,0,0,132,21,1,0,0,0,133,135,7,
        4,0,0,134,133,1,0,0,0,134,135,1,0,0,0,135,23,1,0,0,0,136,140,5,40,
        0,0,137,139,3,26,13,0,138,137,1,0,0,0,139,142,1,0,0,0,140,138,1,
        0,0,0,140,141,1,0,0,0,141,25,1,0,0,0,142,140,1,0,0,0,143,144,5,32,
        0,0,144,145,3,28,14,0,145,27,1,0,0,0,146,152,5,6,0,0,147,153,5,52,
        0,0,148,153,5,53,0,0,149,153,5,54,0,0,150,151,5,55,0,0,151,153,5,
        33,0,0,152,147,1,0,0,0,152,148,1,0,0,0,152,149,1,0,0,0,152,150,1,
        0,0,0,153,159,1,0,0,0,154,155,5,8,0,0,155,157,5,11,0,0,156,158,5,
        56,0,0,157,156,1,0,0,0,157,158,1,0,0,0,158,160,1,0,0,0,159,154,1,
        0,0,0,159,160,1,0,0,0,160,172,1,0,0,0,161,162,5,57,0,0,162,163,5,
        9,0,0,163,168,5,32,0,0,164,165,5,18,0,0,165,167,5,32,0,0,166,164,
        1,0,0,0,167,170,1,0,0,0,168,166,1,0,0,0,168,169,1,0,0,0,169,171,
        1,0,0,0,170,168,1,0,0,0,171,173,5,10,0,0,172,161,1,0,0,0,172,173,
        1,0,0,0,173,174,1,0,0,0,174,177,5,7,0,0,175,176,5,12,0,0,176,178,
        5,33,0,0,177,175,1,0,0,0,177,178,1,0,0,0,178,181,1,0,0,0,179,180,
        5,13,0,0,180,182,5,33,0,0,181,179,1,0,0,0,181,182,1,0,0,0,182,29,
        1,0,0,0,183,187,5,58,0,0,184,186,3,32,16,0,185,184,1,0,0,0,186,189,
        1,0,0,0,187,185,1,0,0,0,187,188,1,0,0,0,188,31,1,0,0,0,189,187,1,
        0,0,0,190,191,5,33,0,0,191,196,3,34,17,0,192,193,5,59,0,0,193,194,
        5,33,0,0,194,195,5,60,0,0,195,197,5,33,0,0,196,192,1,0,0,0,196,197,
        1,0,0,0,197,33,1,0,0,0,198,199,5,61,0,0,199,201,5,30,0,0,200,198,
        1,0,0,0,200,201,1,0,0,0,201,203,1,0,0,0,202,204,5,30,0,0,203,202,
        1,0,0,0,204,205,1,0,0,0,205,203,1,0,0,0,205,206,1,0,0,0,206,35,1,
        0,0,0,25,40,55,62,67,71,73,79,88,94,103,112,120,134,140,152,157,
        159,168,172,177,181,187,196,200,205
    ]

class QrogueWorldParser ( Parser ):

    grammarFileName = "QrogueWorld.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'Name'", u"'='", u"'description'", 
                     u"'teleport'", u"':'", u"'('", u"')'", u"'one way'", 
                     u"'['", u"']'", u"<INVALID>", u"'tutorial'", u"'trigger'", 
                     u"'Qrogue<'", u"'>Qrogue'", u"'~'", u"'|'", u"','", 
                     u"'#'", u"'..'", u"'__'", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"'[Layout]'", u"<INVALID>", 
                     u"'[Hallways]'", u"'visible'", u"'foggy'", u"'World'", 
                     u"'Level'", u"'Spawn'", u"'Wild'", u"'Shop'", u"'Riddle'", 
                     u"'Boss'", u"'Gate'", u"'Treasure'", u"'open'", u"'closed'", 
                     u"'locked'", u"'event'", u"'permanent'", u"'entangled'", 
                     u"'[Messages]'", u"'when'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"DIRECTION", 
                      u"TUTORIAL_LITERAL", u"TRIGGER_LITERAL", u"HEADER", 
                      u"ENDER", u"HORIZONTAL_SEPARATOR", u"VERTICAL_SEPARATOR", 
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
                      u"MESSAGES", u"MSG_EVENT", u"MSG_ALTERNATIVE", u"MSG_SPEAKER" ]

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
    RULE_messages = 15
    RULE_message = 16
    RULE_message_body = 17

    ruleNames =  [ u"start", u"room_content", u"r_type", u"integer", u"complex_number", 
                   u"layout", u"l_room_row", u"l_hallway_row", u"rooms", 
                   u"room", u"r_attributes", u"r_visibility", u"hallways", 
                   u"hallway", u"h_attributes", u"messages", u"message", 
                   u"message_body" ]

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
    TUTORIAL_LITERAL=12
    TRIGGER_LITERAL=13
    HEADER=14
    ENDER=15
    HORIZONTAL_SEPARATOR=16
    VERTICAL_SEPARATOR=17
    LIST_SEPARATOR=18
    WALL=19
    EMPTY_HALLWAY=20
    EMPTY_ROOM=21
    DIGIT=22
    INTEGER=23
    FLOAT=24
    IMAG_NUMBER=25
    SIGN=26
    CHARACTER_LOW=27
    CHARACTER_UP=28
    CHARACTER=29
    TEXT=30
    ROOM_ID=31
    HALLWAY_ID=32
    REFERENCE=33
    WS=34
    UNIVERSAL_SEPARATOR=35
    COMMENT=36
    LINE_COMMENT=37
    LAYOUT=38
    ROOMS=39
    HALLWAYS=40
    VISIBLE_LITERAL=41
    FOGGY_LITERAL=42
    WORLD_LITERAL=43
    LEVEL_LITERAL=44
    SPAWN_LITERAL=45
    WILD_LITERAL=46
    SHOP_LITERAL=47
    RIDDLE_LITERAL=48
    BOSS_LITERAL=49
    GATE_ROOM_LITERAL=50
    TREASURE_LITERAL=51
    OPEN_LITERAL=52
    CLOSED_LITERAL=53
    LOCKED_LITERAL=54
    EVENT_LITERAL=55
    PERMANENT_LITERAL=56
    ENTANGLED_LITERAL=57
    MESSAGES=58
    MSG_EVENT=59
    MSG_ALTERNATIVE=60
    MSG_SPEAKER=61

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
            self.state = 36
            self.match(QrogueWorldParser.HEADER)
            self.state = 40
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__0:
                self.state = 37
                self.match(QrogueWorldParser.T__0)
                self.state = 38
                self.match(QrogueWorldParser.T__1)
                self.state = 39
                self.match(QrogueWorldParser.TEXT)


            self.state = 42
            self.layout()
            self.state = 43
            self.rooms()
            self.state = 44
            self.hallways()
            self.state = 45
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

        def message_body(self):
            return self.getTypedRuleContext(QrogueWorldParser.Message_bodyContext,0)


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
            self.state = 47
            self.match(QrogueWorldParser.T__2)
            self.state = 48
            self.message_body()
            self.state = 49
            self.match(QrogueWorldParser.T__3)
            self.state = 50
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
            self.state = 52
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.WORLD_LITERAL or _la==QrogueWorldParser.LEVEL_LITERAL):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 53
            self.match(QrogueWorldParser.DIGIT)
            self.state = 55
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.DIGIT:
                self.state = 54
                self.match(QrogueWorldParser.DIGIT)


            self.state = 57
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
            self.state = 59
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
            self.state = 62
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.SIGN:
                self.state = 61
                self.match(QrogueWorldParser.SIGN)


            self.state = 73
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.IMAG_NUMBER]:
                self.state = 64
                self.match(QrogueWorldParser.IMAG_NUMBER)
                pass
            elif token in [QrogueWorldParser.DIGIT, QrogueWorldParser.INTEGER, QrogueWorldParser.FLOAT, QrogueWorldParser.HALLWAY_ID]:
                self.state = 67
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [QrogueWorldParser.DIGIT, QrogueWorldParser.INTEGER, QrogueWorldParser.HALLWAY_ID]:
                    self.state = 65
                    self.integer()
                    pass
                elif token in [QrogueWorldParser.FLOAT]:
                    self.state = 66
                    self.match(QrogueWorldParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 71
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.SIGN:
                    self.state = 69
                    self.match(QrogueWorldParser.SIGN)
                    self.state = 70
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
            self.state = 75
            self.match(QrogueWorldParser.LAYOUT)
            self.state = 79
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 76
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 81
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 82
            self.l_room_row()
            self.state = 88
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.VERTICAL_SEPARATOR:
                self.state = 83
                self.l_hallway_row()
                self.state = 84
                self.l_room_row()
                self.state = 90
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 91
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 96
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
            self.state = 97
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 98
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 103
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 99
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 100
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 105
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 106
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
            self.state = 108
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 110 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 109
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 112 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    break

            self.state = 114
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
            self.state = 116
            self.match(QrogueWorldParser.ROOMS)
            self.state = 120
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.ROOM_ID:
                self.state = 117
                self.room()
                self.state = 122
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
            self.state = 123
            self.match(QrogueWorldParser.ROOM_ID)
            self.state = 124
            self.r_attributes()
            self.state = 125
            self.match(QrogueWorldParser.T__4)
            self.state = 126
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
            self.state = 128
            self.match(QrogueWorldParser.T__5)
            self.state = 129
            self.r_visibility()
            self.state = 130
            self.r_type()
            self.state = 131
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
            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.VISIBLE_LITERAL or _la==QrogueWorldParser.FOGGY_LITERAL:
                self.state = 133
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
            self.state = 136
            self.match(QrogueWorldParser.HALLWAYS)
            self.state = 140
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 137
                self.hallway()
                self.state = 142
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
            self.state = 143
            self.match(QrogueWorldParser.HALLWAY_ID)
            self.state = 144
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
            self.state = 146
            self.match(QrogueWorldParser.T__5)
            self.state = 152
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.OPEN_LITERAL]:
                self.state = 147
                self.match(QrogueWorldParser.OPEN_LITERAL)
                pass
            elif token in [QrogueWorldParser.CLOSED_LITERAL]:
                self.state = 148
                self.match(QrogueWorldParser.CLOSED_LITERAL)
                pass
            elif token in [QrogueWorldParser.LOCKED_LITERAL]:
                self.state = 149
                self.match(QrogueWorldParser.LOCKED_LITERAL)
                pass
            elif token in [QrogueWorldParser.EVENT_LITERAL]:
                self.state = 150
                self.match(QrogueWorldParser.EVENT_LITERAL)
                self.state = 151
                self.match(QrogueWorldParser.REFERENCE)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 159
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__7:
                self.state = 154
                self.match(QrogueWorldParser.T__7)
                self.state = 155
                self.match(QrogueWorldParser.DIRECTION)
                self.state = 157
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.PERMANENT_LITERAL:
                    self.state = 156
                    self.match(QrogueWorldParser.PERMANENT_LITERAL)




            self.state = 172
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.ENTANGLED_LITERAL:
                self.state = 161
                self.match(QrogueWorldParser.ENTANGLED_LITERAL)
                self.state = 162
                self.match(QrogueWorldParser.T__8)
                self.state = 163
                self.match(QrogueWorldParser.HALLWAY_ID)
                self.state = 168
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==QrogueWorldParser.LIST_SEPARATOR:
                    self.state = 164
                    self.match(QrogueWorldParser.LIST_SEPARATOR)
                    self.state = 165
                    self.match(QrogueWorldParser.HALLWAY_ID)
                    self.state = 170
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 171
                self.match(QrogueWorldParser.T__9)


            self.state = 174
            self.match(QrogueWorldParser.T__6)
            self.state = 177
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.TUTORIAL_LITERAL:
                self.state = 175
                self.match(QrogueWorldParser.TUTORIAL_LITERAL)
                self.state = 176
                self.match(QrogueWorldParser.REFERENCE)


            self.state = 181
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.TRIGGER_LITERAL:
                self.state = 179
                self.match(QrogueWorldParser.TRIGGER_LITERAL)
                self.state = 180
                self.match(QrogueWorldParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MessagesContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.MessagesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MESSAGES(self):
            return self.getToken(QrogueWorldParser.MESSAGES, 0)

        def message(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueWorldParser.MessageContext)
            else:
                return self.getTypedRuleContext(QrogueWorldParser.MessageContext,i)


        def getRuleIndex(self):
            return QrogueWorldParser.RULE_messages

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

        localctx = QrogueWorldParser.MessagesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_messages)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 183
            self.match(QrogueWorldParser.MESSAGES)
            self.state = 187
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.REFERENCE:
                self.state = 184
                self.message()
                self.state = 189
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
            super(QrogueWorldParser.MessageContext, self).__init__(parent, invokingState)
            self.parser = parser

        def REFERENCE(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.REFERENCE)
            else:
                return self.getToken(QrogueWorldParser.REFERENCE, i)

        def message_body(self):
            return self.getTypedRuleContext(QrogueWorldParser.Message_bodyContext,0)


        def MSG_EVENT(self):
            return self.getToken(QrogueWorldParser.MSG_EVENT, 0)

        def MSG_ALTERNATIVE(self):
            return self.getToken(QrogueWorldParser.MSG_ALTERNATIVE, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_message

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

        localctx = QrogueWorldParser.MessageContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_message)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.match(QrogueWorldParser.REFERENCE)
            self.state = 191
            self.message_body()
            self.state = 196
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.MSG_EVENT:
                self.state = 192
                self.match(QrogueWorldParser.MSG_EVENT)
                self.state = 193
                self.match(QrogueWorldParser.REFERENCE)
                self.state = 194
                self.match(QrogueWorldParser.MSG_ALTERNATIVE)
                self.state = 195
                self.match(QrogueWorldParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Message_bodyContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.Message_bodyContext, self).__init__(parent, invokingState)
            self.parser = parser

        def MSG_SPEAKER(self):
            return self.getToken(QrogueWorldParser.MSG_SPEAKER, 0)

        def TEXT(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.TEXT)
            else:
                return self.getToken(QrogueWorldParser.TEXT, i)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_message_body

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

        localctx = QrogueWorldParser.Message_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_message_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 200
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.MSG_SPEAKER:
                self.state = 198
                self.match(QrogueWorldParser.MSG_SPEAKER)
                self.state = 199
                self.match(QrogueWorldParser.TEXT)


            self.state = 203 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 202
                self.match(QrogueWorldParser.TEXT)
                self.state = 205 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueWorldParser.TEXT):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





