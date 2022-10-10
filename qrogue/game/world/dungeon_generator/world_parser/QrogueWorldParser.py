# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueWorld.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,66,240,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,1,0,1,0,1,0,1,
        0,1,0,1,0,3,0,45,8,0,1,0,1,0,1,1,1,1,1,1,3,1,52,8,1,1,1,1,1,1,1,
        1,1,3,1,58,8,1,3,1,60,8,1,1,2,3,2,63,8,2,1,2,1,2,1,2,1,2,1,2,1,3,
        1,3,1,3,3,3,73,8,3,1,3,1,3,1,4,1,4,1,5,3,5,80,8,5,1,5,1,5,1,5,3,
        5,85,8,5,1,5,1,5,3,5,89,8,5,3,5,91,8,5,1,6,1,6,5,6,95,8,6,10,6,12,
        6,98,9,6,1,6,1,6,1,6,1,6,5,6,104,8,6,10,6,12,6,107,9,6,1,6,5,6,110,
        8,6,10,6,12,6,113,9,6,1,7,1,7,1,7,1,7,5,7,119,8,7,10,7,12,7,122,
        9,7,1,7,1,7,1,8,1,8,4,8,128,8,8,11,8,12,8,129,1,8,1,8,1,9,1,9,5,
        9,136,8,9,10,9,12,9,139,9,9,1,10,1,10,1,10,1,10,1,10,1,11,1,11,1,
        11,1,11,1,11,1,12,3,12,152,8,12,1,13,1,13,5,13,156,8,13,10,13,12,
        13,159,9,13,1,14,1,14,1,14,1,15,1,15,1,15,1,15,1,15,1,15,3,15,170,
        8,15,1,15,1,15,1,15,3,15,175,8,15,3,15,177,8,15,1,15,1,15,1,15,1,
        15,1,15,5,15,184,8,15,10,15,12,15,187,9,15,1,15,3,15,190,8,15,1,
        15,1,15,1,15,3,15,195,8,15,1,15,1,15,3,15,199,8,15,1,16,1,16,1,16,
        1,16,3,16,205,8,16,1,16,5,16,208,8,16,10,16,12,16,211,9,16,1,17,
        1,17,1,17,1,17,1,17,1,17,3,17,219,8,17,1,18,1,18,3,18,223,8,18,1,
        18,3,18,226,8,18,1,18,1,18,3,18,230,8,18,1,18,3,18,233,8,18,1,18,
        4,18,236,8,18,11,18,12,18,237,1,18,0,0,19,0,2,4,6,8,10,12,14,16,
        18,20,22,24,26,28,30,32,34,36,0,5,1,0,47,48,2,0,26,27,36,36,2,0,
        25,25,35,35,2,0,24,24,36,36,1,0,45,46,255,0,38,1,0,0,0,2,51,1,0,
        0,0,4,62,1,0,0,0,6,69,1,0,0,0,8,76,1,0,0,0,10,79,1,0,0,0,12,92,1,
        0,0,0,14,114,1,0,0,0,16,125,1,0,0,0,18,133,1,0,0,0,20,140,1,0,0,
        0,22,145,1,0,0,0,24,151,1,0,0,0,26,153,1,0,0,0,28,160,1,0,0,0,30,
        163,1,0,0,0,32,200,1,0,0,0,34,212,1,0,0,0,36,222,1,0,0,0,38,39,5,
        18,0,0,39,40,3,2,1,0,40,41,3,12,6,0,41,42,3,18,9,0,42,44,3,26,13,
        0,43,45,3,32,16,0,44,43,1,0,0,0,44,45,1,0,0,0,45,46,1,0,0,0,46,47,
        5,19,0,0,47,1,1,0,0,0,48,49,5,1,0,0,49,50,5,2,0,0,50,52,5,34,0,0,
        51,48,1,0,0,0,51,52,1,0,0,0,52,59,1,0,0,0,53,54,5,3,0,0,54,57,5,
        2,0,0,55,58,3,36,18,0,56,58,5,37,0,0,57,55,1,0,0,0,57,56,1,0,0,0,
        58,60,1,0,0,0,59,53,1,0,0,0,59,60,1,0,0,0,60,3,1,0,0,0,61,63,5,14,
        0,0,62,61,1,0,0,0,62,63,1,0,0,0,63,64,1,0,0,0,64,65,5,4,0,0,65,66,
        3,36,18,0,66,67,5,5,0,0,67,68,5,37,0,0,68,5,1,0,0,0,69,70,7,0,0,
        0,70,72,5,26,0,0,71,73,5,26,0,0,72,71,1,0,0,0,72,73,1,0,0,0,73,74,
        1,0,0,0,74,75,5,15,0,0,75,7,1,0,0,0,76,77,7,1,0,0,77,9,1,0,0,0,78,
        80,5,30,0,0,79,78,1,0,0,0,79,80,1,0,0,0,80,90,1,0,0,0,81,91,5,29,
        0,0,82,85,3,8,4,0,83,85,5,28,0,0,84,82,1,0,0,0,84,83,1,0,0,0,85,
        88,1,0,0,0,86,87,5,30,0,0,87,89,5,29,0,0,88,86,1,0,0,0,88,89,1,0,
        0,0,89,91,1,0,0,0,90,81,1,0,0,0,90,84,1,0,0,0,91,11,1,0,0,0,92,96,
        5,42,0,0,93,95,5,20,0,0,94,93,1,0,0,0,95,98,1,0,0,0,96,94,1,0,0,
        0,96,97,1,0,0,0,97,99,1,0,0,0,98,96,1,0,0,0,99,105,3,14,7,0,100,
        101,3,16,8,0,101,102,3,14,7,0,102,104,1,0,0,0,103,100,1,0,0,0,104,
        107,1,0,0,0,105,103,1,0,0,0,105,106,1,0,0,0,106,111,1,0,0,0,107,
        105,1,0,0,0,108,110,5,20,0,0,109,108,1,0,0,0,110,113,1,0,0,0,111,
        109,1,0,0,0,111,112,1,0,0,0,112,13,1,0,0,0,113,111,1,0,0,0,114,115,
        5,21,0,0,115,120,7,2,0,0,116,117,7,3,0,0,117,119,7,2,0,0,118,116,
        1,0,0,0,119,122,1,0,0,0,120,118,1,0,0,0,120,121,1,0,0,0,121,123,
        1,0,0,0,122,120,1,0,0,0,123,124,5,21,0,0,124,15,1,0,0,0,125,127,
        5,21,0,0,126,128,7,3,0,0,127,126,1,0,0,0,128,129,1,0,0,0,129,127,
        1,0,0,0,129,130,1,0,0,0,130,131,1,0,0,0,131,132,5,21,0,0,132,17,
        1,0,0,0,133,137,5,43,0,0,134,136,3,20,10,0,135,134,1,0,0,0,136,139,
        1,0,0,0,137,135,1,0,0,0,137,138,1,0,0,0,138,19,1,0,0,0,139,137,1,
        0,0,0,140,141,5,35,0,0,141,142,3,22,11,0,142,143,5,6,0,0,143,144,
        3,4,2,0,144,21,1,0,0,0,145,146,5,7,0,0,146,147,3,24,12,0,147,148,
        3,6,3,0,148,149,5,8,0,0,149,23,1,0,0,0,150,152,7,4,0,0,151,150,1,
        0,0,0,151,152,1,0,0,0,152,25,1,0,0,0,153,157,5,44,0,0,154,156,3,
        28,14,0,155,154,1,0,0,0,156,159,1,0,0,0,157,155,1,0,0,0,157,158,
        1,0,0,0,158,27,1,0,0,0,159,157,1,0,0,0,160,161,5,36,0,0,161,162,
        3,30,15,0,162,29,1,0,0,0,163,169,5,7,0,0,164,170,5,56,0,0,165,170,
        5,57,0,0,166,170,5,58,0,0,167,168,5,59,0,0,168,170,5,37,0,0,169,
        164,1,0,0,0,169,165,1,0,0,0,169,166,1,0,0,0,169,167,1,0,0,0,170,
        176,1,0,0,0,171,172,5,9,0,0,172,174,5,15,0,0,173,175,5,60,0,0,174,
        173,1,0,0,0,174,175,1,0,0,0,175,177,1,0,0,0,176,171,1,0,0,0,176,
        177,1,0,0,0,177,189,1,0,0,0,178,179,5,61,0,0,179,180,5,10,0,0,180,
        185,5,36,0,0,181,182,5,22,0,0,182,184,5,36,0,0,183,181,1,0,0,0,184,
        187,1,0,0,0,185,183,1,0,0,0,185,186,1,0,0,0,186,188,1,0,0,0,187,
        185,1,0,0,0,188,190,5,11,0,0,189,178,1,0,0,0,189,190,1,0,0,0,190,
        191,1,0,0,0,191,194,5,8,0,0,192,193,5,16,0,0,193,195,5,37,0,0,194,
        192,1,0,0,0,194,195,1,0,0,0,195,198,1,0,0,0,196,197,5,17,0,0,197,
        199,5,37,0,0,198,196,1,0,0,0,198,199,1,0,0,0,199,31,1,0,0,0,200,
        204,5,62,0,0,201,202,5,12,0,0,202,203,5,65,0,0,203,205,5,34,0,0,
        204,201,1,0,0,0,204,205,1,0,0,0,205,209,1,0,0,0,206,208,3,34,17,
        0,207,206,1,0,0,0,208,211,1,0,0,0,209,207,1,0,0,0,209,210,1,0,0,
        0,210,33,1,0,0,0,211,209,1,0,0,0,212,213,5,37,0,0,213,218,3,36,18,
        0,214,215,5,63,0,0,215,216,5,37,0,0,216,217,5,64,0,0,217,219,5,37,
        0,0,218,214,1,0,0,0,218,219,1,0,0,0,219,35,1,0,0,0,220,221,5,65,
        0,0,221,223,5,34,0,0,222,220,1,0,0,0,222,223,1,0,0,0,223,225,1,0,
        0,0,224,226,5,66,0,0,225,224,1,0,0,0,225,226,1,0,0,0,226,232,1,0,
        0,0,227,229,5,13,0,0,228,230,5,2,0,0,229,228,1,0,0,0,229,230,1,0,
        0,0,230,231,1,0,0,0,231,233,5,26,0,0,232,227,1,0,0,0,232,233,1,0,
        0,0,233,235,1,0,0,0,234,236,5,34,0,0,235,234,1,0,0,0,236,237,1,0,
        0,0,237,235,1,0,0,0,237,238,1,0,0,0,238,37,1,0,0,0,33,44,51,57,59,
        62,72,79,84,88,90,96,105,111,120,129,137,151,157,169,174,176,185,
        189,194,198,204,209,218,222,225,229,232,237
    ]

class QrogueWorldParser ( Parser ):

    grammarFileName = "QrogueWorld.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'Name'", u"'='", u"'Description'", 
                     u"'description'", u"'teleport'", u"':'", u"'('", u"')'", 
                     u"'one way'", u"'['", u"']'", u"'default'", u"'pos'", 
                     u"'optional'", u"<INVALID>", u"'tutorial'", u"'trigger'", 
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
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"OPTIONAL_LEVEL", u"DIRECTION", 
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
                      u"MESSAGES", u"MSG_EVENT", u"MSG_ALTERNATIVE", u"MSG_SPEAKER", 
                      u"MSG_PRIORITY" ]

    RULE_start = 0
    RULE_meta = 1
    RULE_room_content = 2
    RULE_r_type = 3
    RULE_integer = 4
    RULE_complex_number = 5
    RULE_layout = 6
    RULE_l_room_row = 7
    RULE_l_hallway_row = 8
    RULE_rooms = 9
    RULE_room = 10
    RULE_r_attributes = 11
    RULE_r_visibility = 12
    RULE_hallways = 13
    RULE_hallway = 14
    RULE_h_attributes = 15
    RULE_messages = 16
    RULE_message = 17
    RULE_message_body = 18

    ruleNames =  [ u"start", u"meta", u"room_content", u"r_type", u"integer", 
                   u"complex_number", u"layout", u"l_room_row", u"l_hallway_row", 
                   u"rooms", u"room", u"r_attributes", u"r_visibility", 
                   u"hallways", u"hallway", u"h_attributes", u"messages", 
                   u"message", u"message_body" ]

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
    T__10=11
    T__11=12
    T__12=13
    OPTIONAL_LEVEL=14
    DIRECTION=15
    TUTORIAL_LITERAL=16
    TRIGGER_LITERAL=17
    HEADER=18
    ENDER=19
    HORIZONTAL_SEPARATOR=20
    VERTICAL_SEPARATOR=21
    LIST_SEPARATOR=22
    WALL=23
    EMPTY_HALLWAY=24
    EMPTY_ROOM=25
    DIGIT=26
    INTEGER=27
    FLOAT=28
    IMAG_NUMBER=29
    SIGN=30
    CHARACTER_LOW=31
    CHARACTER_UP=32
    CHARACTER=33
    TEXT=34
    ROOM_ID=35
    HALLWAY_ID=36
    REFERENCE=37
    WS=38
    UNIVERSAL_SEPARATOR=39
    COMMENT=40
    LINE_COMMENT=41
    LAYOUT=42
    ROOMS=43
    HALLWAYS=44
    VISIBLE_LITERAL=45
    FOGGY_LITERAL=46
    WORLD_LITERAL=47
    LEVEL_LITERAL=48
    SPAWN_LITERAL=49
    WILD_LITERAL=50
    SHOP_LITERAL=51
    RIDDLE_LITERAL=52
    BOSS_LITERAL=53
    GATE_ROOM_LITERAL=54
    TREASURE_LITERAL=55
    OPEN_LITERAL=56
    CLOSED_LITERAL=57
    LOCKED_LITERAL=58
    EVENT_LITERAL=59
    PERMANENT_LITERAL=60
    ENTANGLED_LITERAL=61
    MESSAGES=62
    MSG_EVENT=63
    MSG_ALTERNATIVE=64
    MSG_SPEAKER=65
    MSG_PRIORITY=66

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

        def meta(self):
            return self.getTypedRuleContext(QrogueWorldParser.MetaContext,0)


        def layout(self):
            return self.getTypedRuleContext(QrogueWorldParser.LayoutContext,0)


        def rooms(self):
            return self.getTypedRuleContext(QrogueWorldParser.RoomsContext,0)


        def hallways(self):
            return self.getTypedRuleContext(QrogueWorldParser.HallwaysContext,0)


        def ENDER(self):
            return self.getToken(QrogueWorldParser.ENDER, 0)

        def messages(self):
            return self.getTypedRuleContext(QrogueWorldParser.MessagesContext,0)


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
            self.state = 38
            self.match(QrogueWorldParser.HEADER)
            self.state = 39
            self.meta()
            self.state = 40
            self.layout()
            self.state = 41
            self.rooms()
            self.state = 42
            self.hallways()
            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.MESSAGES:
                self.state = 43
                self.messages()


            self.state = 46
            self.match(QrogueWorldParser.ENDER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MetaContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.MetaContext, self).__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(QrogueWorldParser.TEXT, 0)

        def message_body(self):
            return self.getTypedRuleContext(QrogueWorldParser.Message_bodyContext,0)


        def REFERENCE(self):
            return self.getToken(QrogueWorldParser.REFERENCE, 0)

        def getRuleIndex(self):
            return QrogueWorldParser.RULE_meta

        def enterRule(self, listener):
            if hasattr(listener, "enterMeta"):
                listener.enterMeta(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitMeta"):
                listener.exitMeta(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitMeta"):
                return visitor.visitMeta(self)
            else:
                return visitor.visitChildren(self)




    def meta(self):

        localctx = QrogueWorldParser.MetaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_meta)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 51
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__0:
                self.state = 48
                self.match(QrogueWorldParser.T__0)
                self.state = 49
                self.match(QrogueWorldParser.T__1)
                self.state = 50
                self.match(QrogueWorldParser.TEXT)


            self.state = 59
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__2:
                self.state = 53
                self.match(QrogueWorldParser.T__2)
                self.state = 54
                self.match(QrogueWorldParser.T__1)
                self.state = 57
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [QrogueWorldParser.T__12, QrogueWorldParser.TEXT, QrogueWorldParser.MSG_SPEAKER, QrogueWorldParser.MSG_PRIORITY]:
                    self.state = 55
                    self.message_body()
                    pass
                elif token in [QrogueWorldParser.REFERENCE]:
                    self.state = 56
                    self.match(QrogueWorldParser.REFERENCE)
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


    class Room_contentContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.Room_contentContext, self).__init__(parent, invokingState)
            self.parser = parser

        def message_body(self):
            return self.getTypedRuleContext(QrogueWorldParser.Message_bodyContext,0)


        def REFERENCE(self):
            return self.getToken(QrogueWorldParser.REFERENCE, 0)

        def OPTIONAL_LEVEL(self):
            return self.getToken(QrogueWorldParser.OPTIONAL_LEVEL, 0)

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
        self.enterRule(localctx, 4, self.RULE_room_content)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 62
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.OPTIONAL_LEVEL:
                self.state = 61
                self.match(QrogueWorldParser.OPTIONAL_LEVEL)


            self.state = 64
            self.match(QrogueWorldParser.T__3)
            self.state = 65
            self.message_body()
            self.state = 66
            self.match(QrogueWorldParser.T__4)
            self.state = 67
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
        self.enterRule(localctx, 6, self.RULE_r_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.WORLD_LITERAL or _la==QrogueWorldParser.LEVEL_LITERAL):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 70
            self.match(QrogueWorldParser.DIGIT)
            self.state = 72
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.DIGIT:
                self.state = 71
                self.match(QrogueWorldParser.DIGIT)


            self.state = 74
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
        self.enterRule(localctx, 8, self.RULE_integer)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
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
        self.enterRule(localctx, 10, self.RULE_complex_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 79
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.SIGN:
                self.state = 78
                self.match(QrogueWorldParser.SIGN)


            self.state = 90
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.IMAG_NUMBER]:
                self.state = 81
                self.match(QrogueWorldParser.IMAG_NUMBER)
                pass
            elif token in [QrogueWorldParser.DIGIT, QrogueWorldParser.INTEGER, QrogueWorldParser.FLOAT, QrogueWorldParser.HALLWAY_ID]:
                self.state = 84
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [QrogueWorldParser.DIGIT, QrogueWorldParser.INTEGER, QrogueWorldParser.HALLWAY_ID]:
                    self.state = 82
                    self.integer()
                    pass
                elif token in [QrogueWorldParser.FLOAT]:
                    self.state = 83
                    self.match(QrogueWorldParser.FLOAT)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 88
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.SIGN:
                    self.state = 86
                    self.match(QrogueWorldParser.SIGN)
                    self.state = 87
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
        self.enterRule(localctx, 12, self.RULE_layout)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 92
            self.match(QrogueWorldParser.LAYOUT)
            self.state = 96
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 93
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 98
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 99
            self.l_room_row()
            self.state = 105
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.VERTICAL_SEPARATOR:
                self.state = 100
                self.l_hallway_row()
                self.state = 101
                self.l_room_row()
                self.state = 107
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 111
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 108
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 113
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
        self.enterRule(localctx, 14, self.RULE_l_room_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 114
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 115
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 120
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 116
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 117
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 122
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 123
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
        self.enterRule(localctx, 16, self.RULE_l_hallway_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 125
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 127 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 126
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 129 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    break

            self.state = 131
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
        self.enterRule(localctx, 18, self.RULE_rooms)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 133
            self.match(QrogueWorldParser.ROOMS)
            self.state = 137
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.ROOM_ID:
                self.state = 134
                self.room()
                self.state = 139
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
        self.enterRule(localctx, 20, self.RULE_room)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 140
            self.match(QrogueWorldParser.ROOM_ID)
            self.state = 141
            self.r_attributes()
            self.state = 142
            self.match(QrogueWorldParser.T__5)
            self.state = 143
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
        self.enterRule(localctx, 22, self.RULE_r_attributes)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 145
            self.match(QrogueWorldParser.T__6)
            self.state = 146
            self.r_visibility()
            self.state = 147
            self.r_type()
            self.state = 148
            self.match(QrogueWorldParser.T__7)
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
        self.enterRule(localctx, 24, self.RULE_r_visibility)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.VISIBLE_LITERAL or _la==QrogueWorldParser.FOGGY_LITERAL:
                self.state = 150
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
        self.enterRule(localctx, 26, self.RULE_hallways)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 153
            self.match(QrogueWorldParser.HALLWAYS)
            self.state = 157
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 154
                self.hallway()
                self.state = 159
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
        self.enterRule(localctx, 28, self.RULE_hallway)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            self.match(QrogueWorldParser.HALLWAY_ID)
            self.state = 161
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
        self.enterRule(localctx, 30, self.RULE_h_attributes)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 163
            self.match(QrogueWorldParser.T__6)
            self.state = 169
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.OPEN_LITERAL]:
                self.state = 164
                self.match(QrogueWorldParser.OPEN_LITERAL)
                pass
            elif token in [QrogueWorldParser.CLOSED_LITERAL]:
                self.state = 165
                self.match(QrogueWorldParser.CLOSED_LITERAL)
                pass
            elif token in [QrogueWorldParser.LOCKED_LITERAL]:
                self.state = 166
                self.match(QrogueWorldParser.LOCKED_LITERAL)
                pass
            elif token in [QrogueWorldParser.EVENT_LITERAL]:
                self.state = 167
                self.match(QrogueWorldParser.EVENT_LITERAL)
                self.state = 168
                self.match(QrogueWorldParser.REFERENCE)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 176
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__8:
                self.state = 171
                self.match(QrogueWorldParser.T__8)
                self.state = 172
                self.match(QrogueWorldParser.DIRECTION)
                self.state = 174
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.PERMANENT_LITERAL:
                    self.state = 173
                    self.match(QrogueWorldParser.PERMANENT_LITERAL)




            self.state = 189
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.ENTANGLED_LITERAL:
                self.state = 178
                self.match(QrogueWorldParser.ENTANGLED_LITERAL)
                self.state = 179
                self.match(QrogueWorldParser.T__9)
                self.state = 180
                self.match(QrogueWorldParser.HALLWAY_ID)
                self.state = 185
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==QrogueWorldParser.LIST_SEPARATOR:
                    self.state = 181
                    self.match(QrogueWorldParser.LIST_SEPARATOR)
                    self.state = 182
                    self.match(QrogueWorldParser.HALLWAY_ID)
                    self.state = 187
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 188
                self.match(QrogueWorldParser.T__10)


            self.state = 191
            self.match(QrogueWorldParser.T__7)
            self.state = 194
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.TUTORIAL_LITERAL:
                self.state = 192
                self.match(QrogueWorldParser.TUTORIAL_LITERAL)
                self.state = 193
                self.match(QrogueWorldParser.REFERENCE)


            self.state = 198
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.TRIGGER_LITERAL:
                self.state = 196
                self.match(QrogueWorldParser.TRIGGER_LITERAL)
                self.state = 197
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

        def MSG_SPEAKER(self):
            return self.getToken(QrogueWorldParser.MSG_SPEAKER, 0)

        def TEXT(self):
            return self.getToken(QrogueWorldParser.TEXT, 0)

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
        self.enterRule(localctx, 32, self.RULE_messages)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 200
            self.match(QrogueWorldParser.MESSAGES)
            self.state = 204
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__11:
                self.state = 201
                self.match(QrogueWorldParser.T__11)
                self.state = 202
                self.match(QrogueWorldParser.MSG_SPEAKER)
                self.state = 203
                self.match(QrogueWorldParser.TEXT)


            self.state = 209
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.REFERENCE:
                self.state = 206
                self.message()
                self.state = 211
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
        self.enterRule(localctx, 34, self.RULE_message)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 212
            self.match(QrogueWorldParser.REFERENCE)
            self.state = 213
            self.message_body()
            self.state = 218
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.MSG_EVENT:
                self.state = 214
                self.match(QrogueWorldParser.MSG_EVENT)
                self.state = 215
                self.match(QrogueWorldParser.REFERENCE)
                self.state = 216
                self.match(QrogueWorldParser.MSG_ALTERNATIVE)
                self.state = 217
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

        def MSG_PRIORITY(self):
            return self.getToken(QrogueWorldParser.MSG_PRIORITY, 0)

        def DIGIT(self):
            return self.getToken(QrogueWorldParser.DIGIT, 0)

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
        self.enterRule(localctx, 36, self.RULE_message_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 222
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.MSG_SPEAKER:
                self.state = 220
                self.match(QrogueWorldParser.MSG_SPEAKER)
                self.state = 221
                self.match(QrogueWorldParser.TEXT)


            self.state = 225
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.MSG_PRIORITY:
                self.state = 224
                self.match(QrogueWorldParser.MSG_PRIORITY)


            self.state = 232
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.T__12:
                self.state = 227
                self.match(QrogueWorldParser.T__12)
                self.state = 229
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueWorldParser.T__1:
                    self.state = 228
                    self.match(QrogueWorldParser.T__1)


                self.state = 231
                self.match(QrogueWorldParser.DIGIT)


            self.state = 235 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 234
                self.match(QrogueWorldParser.TEXT)
                self.state = 237 
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





