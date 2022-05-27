# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator/other_parsers\QrogueAreas.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,50,137,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,1,0,5,0,27,8,0,
        10,0,12,0,30,9,0,1,0,1,0,1,0,1,0,5,0,36,8,0,10,0,12,0,39,9,0,1,0,
        5,0,42,8,0,10,0,12,0,45,9,0,1,1,1,1,1,1,1,1,5,1,51,8,1,10,1,12,1,
        54,9,1,1,1,1,1,1,2,1,2,4,2,60,8,2,11,2,12,2,61,1,2,1,2,1,3,1,3,5,
        3,68,8,3,10,3,12,3,71,9,3,1,4,1,4,1,4,1,4,1,4,1,5,1,5,1,5,1,5,1,
        5,1,6,3,6,84,8,6,1,7,1,7,1,8,1,8,1,9,1,9,5,9,92,8,9,10,9,12,9,95,
        9,9,1,10,1,10,1,10,1,11,1,11,1,11,1,11,1,11,1,11,3,11,106,8,11,1,
        11,1,11,1,11,3,11,111,8,11,3,11,113,8,11,1,11,1,11,1,11,1,11,1,11,
        5,11,120,8,11,10,11,12,11,123,9,11,1,11,3,11,126,8,11,1,11,1,11,
        1,11,3,11,131,8,11,1,11,1,11,3,11,135,8,11,1,11,0,0,12,0,2,4,6,8,
        10,12,14,16,18,20,22,0,4,2,0,38,38,44,44,2,0,37,37,45,45,1,0,11,
        12,1,0,15,21,141,0,24,1,0,0,0,2,46,1,0,0,0,4,57,1,0,0,0,6,65,1,0,
        0,0,8,72,1,0,0,0,10,77,1,0,0,0,12,83,1,0,0,0,14,85,1,0,0,0,16,87,
        1,0,0,0,18,89,1,0,0,0,20,96,1,0,0,0,22,99,1,0,0,0,24,28,5,8,0,0,
        25,27,5,33,0,0,26,25,1,0,0,0,27,30,1,0,0,0,28,26,1,0,0,0,28,29,1,
        0,0,0,29,31,1,0,0,0,30,28,1,0,0,0,31,37,3,2,1,0,32,33,3,4,2,0,33,
        34,3,2,1,0,34,36,1,0,0,0,35,32,1,0,0,0,36,39,1,0,0,0,37,35,1,0,0,
        0,37,38,1,0,0,0,38,43,1,0,0,0,39,37,1,0,0,0,40,42,5,33,0,0,41,40,
        1,0,0,0,42,45,1,0,0,0,43,41,1,0,0,0,43,44,1,0,0,0,44,1,1,0,0,0,45,
        43,1,0,0,0,46,47,5,34,0,0,47,52,7,0,0,0,48,49,7,1,0,0,49,51,7,0,
        0,0,50,48,1,0,0,0,51,54,1,0,0,0,52,50,1,0,0,0,52,53,1,0,0,0,53,55,
        1,0,0,0,54,52,1,0,0,0,55,56,5,34,0,0,56,3,1,0,0,0,57,59,5,34,0,0,
        58,60,7,1,0,0,59,58,1,0,0,0,60,61,1,0,0,0,61,59,1,0,0,0,61,62,1,
        0,0,0,62,63,1,0,0,0,63,64,5,34,0,0,64,5,1,0,0,0,65,69,5,9,0,0,66,
        68,3,8,4,0,67,66,1,0,0,0,68,71,1,0,0,0,69,67,1,0,0,0,69,70,1,0,0,
        0,70,7,1,0,0,0,71,69,1,0,0,0,72,73,5,44,0,0,73,74,3,10,5,0,74,75,
        5,1,0,0,75,76,3,16,8,0,76,9,1,0,0,0,77,78,5,2,0,0,78,79,3,12,6,0,
        79,80,3,14,7,0,80,81,5,3,0,0,81,11,1,0,0,0,82,84,7,2,0,0,83,82,1,
        0,0,0,83,84,1,0,0,0,84,13,1,0,0,0,85,86,7,3,0,0,86,15,1,0,0,0,87,
        88,5,4,0,0,88,17,1,0,0,0,89,93,5,10,0,0,90,92,3,20,10,0,91,90,1,
        0,0,0,92,95,1,0,0,0,93,91,1,0,0,0,93,94,1,0,0,0,94,19,1,0,0,0,95,
        93,1,0,0,0,96,97,5,45,0,0,97,98,3,22,11,0,98,21,1,0,0,0,99,105,5,
        2,0,0,100,106,5,22,0,0,101,106,5,23,0,0,102,106,5,24,0,0,103,104,
        5,25,0,0,104,106,5,46,0,0,105,100,1,0,0,0,105,101,1,0,0,0,105,102,
        1,0,0,0,105,103,1,0,0,0,106,112,1,0,0,0,107,108,5,5,0,0,108,110,
        5,32,0,0,109,111,5,26,0,0,110,109,1,0,0,0,110,111,1,0,0,0,111,113,
        1,0,0,0,112,107,1,0,0,0,112,113,1,0,0,0,113,125,1,0,0,0,114,115,
        5,27,0,0,115,116,5,6,0,0,116,121,5,45,0,0,117,118,5,35,0,0,118,120,
        5,45,0,0,119,117,1,0,0,0,120,123,1,0,0,0,121,119,1,0,0,0,121,122,
        1,0,0,0,122,124,1,0,0,0,123,121,1,0,0,0,124,126,5,7,0,0,125,114,
        1,0,0,0,125,126,1,0,0,0,126,127,1,0,0,0,127,130,5,3,0,0,128,129,
        5,28,0,0,129,131,5,46,0,0,130,128,1,0,0,0,130,131,1,0,0,0,131,134,
        1,0,0,0,132,133,5,29,0,0,133,135,5,46,0,0,134,132,1,0,0,0,134,135,
        1,0,0,0,135,23,1,0,0,0,15,28,37,43,52,61,69,83,93,105,110,112,121,
        125,130,134
    ]

class QrogueAreasParser ( Parser ):

    grammarFileName = "QrogueAreas.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"':'", u"'('", u"')'", u"'TODO: implement in importing grammar #override'", 
                     u"'one way'", u"'['", u"']'", u"'[Layout]'", u"<INVALID>", 
                     u"'[Hallways]'", u"'visible'", u"'foggy'", u"'World'", 
                     u"'Level'", u"'Spawn'", u"'Wild'", u"'Shop'", u"'Riddle'", 
                     u"'Boss'", u"'Gate'", u"'Treasure'", u"'open'", u"'closed'", 
                     u"'locked'", u"'event'", u"'permanent'", u"'entangled'", 
                     u"'tutorial'", u"'trigger'", u"'Qrogue<'", u"'>Qrogue'", 
                     u"<INVALID>", u"'~'", u"'|'", u"','", u"'#'", u"'..'", 
                     u"'__'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"LAYOUT", u"ROOMS", u"HALLWAYS", u"VISIBLE_LITERAL", 
                      u"FOGGY_LITERAL", u"WORLD_LITERAL", u"LEVEL_LITERAL", 
                      u"SPAWN_LITERAL", u"WILD_LITERAL", u"SHOP_LITERAL", 
                      u"RIDDLE_LITERAL", u"BOSS_LITERAL", u"GATE_ROOM_LITERAL", 
                      u"TREASURE_LITERAL", u"OPEN_LITERAL", u"CLOSED_LITERAL", 
                      u"LOCKED_LITERAL", u"EVENT_LITERAL", u"PERMANENT_LITERAL", 
                      u"ENTANGLED_LITERAL", u"TUTORIAL_LITERAL", u"TRIGGER_LITERAL", 
                      u"HEADER", u"ENDER", u"DIRECTION", u"HORIZONTAL_SEPARATOR", 
                      u"VERTICAL_SEPARATOR", u"LIST_SEPARATOR", u"WALL", 
                      u"EMPTY_HALLWAY", u"EMPTY_ROOM", u"DIGIT", u"CHARACTER_LOW", 
                      u"CHARACTER_UP", u"CHARACTER", u"TEXT", u"ROOM_ID", 
                      u"HALLWAY_ID", u"REFERENCE", u"WS", u"UNIVERSAL_SEPARATOR", 
                      u"COMMENT", u"LINE_COMMENT" ]

    RULE_layout = 0
    RULE_l_room_row = 1
    RULE_l_hallway_row = 2
    RULE_rooms = 3
    RULE_room = 4
    RULE_r_attributes = 5
    RULE_r_visibility = 6
    RULE_r_type = 7
    RULE_room_content = 8
    RULE_hallways = 9
    RULE_hallway = 10
    RULE_h_attributes = 11

    ruleNames =  [ u"layout", u"l_room_row", u"l_hallway_row", u"rooms", 
                   u"room", u"r_attributes", u"r_visibility", u"r_type", 
                   u"room_content", u"hallways", u"hallway", u"h_attributes" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    LAYOUT=8
    ROOMS=9
    HALLWAYS=10
    VISIBLE_LITERAL=11
    FOGGY_LITERAL=12
    WORLD_LITERAL=13
    LEVEL_LITERAL=14
    SPAWN_LITERAL=15
    WILD_LITERAL=16
    SHOP_LITERAL=17
    RIDDLE_LITERAL=18
    BOSS_LITERAL=19
    GATE_ROOM_LITERAL=20
    TREASURE_LITERAL=21
    OPEN_LITERAL=22
    CLOSED_LITERAL=23
    LOCKED_LITERAL=24
    EVENT_LITERAL=25
    PERMANENT_LITERAL=26
    ENTANGLED_LITERAL=27
    TUTORIAL_LITERAL=28
    TRIGGER_LITERAL=29
    HEADER=30
    ENDER=31
    DIRECTION=32
    HORIZONTAL_SEPARATOR=33
    VERTICAL_SEPARATOR=34
    LIST_SEPARATOR=35
    WALL=36
    EMPTY_HALLWAY=37
    EMPTY_ROOM=38
    DIGIT=39
    CHARACTER_LOW=40
    CHARACTER_UP=41
    CHARACTER=42
    TEXT=43
    ROOM_ID=44
    HALLWAY_ID=45
    REFERENCE=46
    WS=47
    UNIVERSAL_SEPARATOR=48
    COMMENT=49
    LINE_COMMENT=50

    def __init__(self, input, output=sys.stdout):
        super(QrogueAreasParser, self).__init__(input, output=output)
        self.checkVersion("4.10.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class LayoutContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.LayoutContext, self).__init__(parent, invokingState)
            self.parser = parser

        def LAYOUT(self):
            return self.getToken(QrogueAreasParser.LAYOUT, 0)

        def l_room_row(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueAreasParser.L_room_rowContext)
            else:
                return self.getTypedRuleContext(QrogueAreasParser.L_room_rowContext,i)


        def HORIZONTAL_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.HORIZONTAL_SEPARATOR)
            else:
                return self.getToken(QrogueAreasParser.HORIZONTAL_SEPARATOR, i)

        def l_hallway_row(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueAreasParser.L_hallway_rowContext)
            else:
                return self.getTypedRuleContext(QrogueAreasParser.L_hallway_rowContext,i)


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_layout

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

        localctx = QrogueAreasParser.LayoutContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_layout)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 24
            self.match(QrogueAreasParser.LAYOUT)
            self.state = 28
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueAreasParser.HORIZONTAL_SEPARATOR:
                self.state = 25
                self.match(QrogueAreasParser.HORIZONTAL_SEPARATOR)
                self.state = 30
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 31
            self.l_room_row()
            self.state = 37
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueAreasParser.VERTICAL_SEPARATOR:
                self.state = 32
                self.l_hallway_row()
                self.state = 33
                self.l_room_row()
                self.state = 39
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 43
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueAreasParser.HORIZONTAL_SEPARATOR:
                self.state = 40
                self.match(QrogueAreasParser.HORIZONTAL_SEPARATOR)
                self.state = 45
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
            super(QrogueAreasParser.L_room_rowContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VERTICAL_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.VERTICAL_SEPARATOR)
            else:
                return self.getToken(QrogueAreasParser.VERTICAL_SEPARATOR, i)

        def ROOM_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.ROOM_ID)
            else:
                return self.getToken(QrogueAreasParser.ROOM_ID, i)

        def EMPTY_ROOM(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.EMPTY_ROOM)
            else:
                return self.getToken(QrogueAreasParser.EMPTY_ROOM, i)

        def HALLWAY_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.HALLWAY_ID)
            else:
                return self.getToken(QrogueAreasParser.HALLWAY_ID, i)

        def EMPTY_HALLWAY(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.EMPTY_HALLWAY)
            else:
                return self.getToken(QrogueAreasParser.EMPTY_HALLWAY, i)

        def getRuleIndex(self):
            return QrogueAreasParser.RULE_l_room_row

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

        localctx = QrogueAreasParser.L_room_rowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_l_room_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            self.match(QrogueAreasParser.VERTICAL_SEPARATOR)
            self.state = 47
            _la = self._input.LA(1)
            if not(_la==QrogueAreasParser.EMPTY_ROOM or _la==QrogueAreasParser.ROOM_ID):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 52
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueAreasParser.EMPTY_HALLWAY or _la==QrogueAreasParser.HALLWAY_ID:
                self.state = 48
                _la = self._input.LA(1)
                if not(_la==QrogueAreasParser.EMPTY_HALLWAY or _la==QrogueAreasParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 49
                _la = self._input.LA(1)
                if not(_la==QrogueAreasParser.EMPTY_ROOM or _la==QrogueAreasParser.ROOM_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 54
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 55
            self.match(QrogueAreasParser.VERTICAL_SEPARATOR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class L_hallway_rowContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.L_hallway_rowContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VERTICAL_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.VERTICAL_SEPARATOR)
            else:
                return self.getToken(QrogueAreasParser.VERTICAL_SEPARATOR, i)

        def HALLWAY_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.HALLWAY_ID)
            else:
                return self.getToken(QrogueAreasParser.HALLWAY_ID, i)

        def EMPTY_HALLWAY(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.EMPTY_HALLWAY)
            else:
                return self.getToken(QrogueAreasParser.EMPTY_HALLWAY, i)

        def getRuleIndex(self):
            return QrogueAreasParser.RULE_l_hallway_row

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

        localctx = QrogueAreasParser.L_hallway_rowContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_l_hallway_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 57
            self.match(QrogueAreasParser.VERTICAL_SEPARATOR)
            self.state = 59 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 58
                _la = self._input.LA(1)
                if not(_la==QrogueAreasParser.EMPTY_HALLWAY or _la==QrogueAreasParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 61 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueAreasParser.EMPTY_HALLWAY or _la==QrogueAreasParser.HALLWAY_ID):
                    break

            self.state = 63
            self.match(QrogueAreasParser.VERTICAL_SEPARATOR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RoomsContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.RoomsContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ROOMS(self):
            return self.getToken(QrogueAreasParser.ROOMS, 0)

        def room(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueAreasParser.RoomContext)
            else:
                return self.getTypedRuleContext(QrogueAreasParser.RoomContext,i)


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_rooms

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

        localctx = QrogueAreasParser.RoomsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_rooms)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self.match(QrogueAreasParser.ROOMS)
            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueAreasParser.ROOM_ID:
                self.state = 66
                self.room()
                self.state = 71
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
            super(QrogueAreasParser.RoomContext, self).__init__(parent, invokingState)
            self.parser = parser

        def ROOM_ID(self):
            return self.getToken(QrogueAreasParser.ROOM_ID, 0)

        def r_attributes(self):
            return self.getTypedRuleContext(QrogueAreasParser.R_attributesContext,0)


        def room_content(self):
            return self.getTypedRuleContext(QrogueAreasParser.Room_contentContext,0)


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_room

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

        localctx = QrogueAreasParser.RoomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_room)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(QrogueAreasParser.ROOM_ID)
            self.state = 73
            self.r_attributes()
            self.state = 74
            self.match(QrogueAreasParser.T__0)
            self.state = 75
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
            super(QrogueAreasParser.R_attributesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def r_visibility(self):
            return self.getTypedRuleContext(QrogueAreasParser.R_visibilityContext,0)


        def r_type(self):
            return self.getTypedRuleContext(QrogueAreasParser.R_typeContext,0)


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_r_attributes

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

        localctx = QrogueAreasParser.R_attributesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_r_attributes)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            self.match(QrogueAreasParser.T__1)
            self.state = 78
            self.r_visibility()
            self.state = 79
            self.r_type()
            self.state = 80
            self.match(QrogueAreasParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class R_visibilityContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.R_visibilityContext, self).__init__(parent, invokingState)
            self.parser = parser

        def VISIBLE_LITERAL(self):
            return self.getToken(QrogueAreasParser.VISIBLE_LITERAL, 0)

        def FOGGY_LITERAL(self):
            return self.getToken(QrogueAreasParser.FOGGY_LITERAL, 0)

        def getRuleIndex(self):
            return QrogueAreasParser.RULE_r_visibility

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

        localctx = QrogueAreasParser.R_visibilityContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_r_visibility)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueAreasParser.VISIBLE_LITERAL or _la==QrogueAreasParser.FOGGY_LITERAL:
                self.state = 82
                _la = self._input.LA(1)
                if not(_la==QrogueAreasParser.VISIBLE_LITERAL or _la==QrogueAreasParser.FOGGY_LITERAL):
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


    class R_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.R_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def SPAWN_LITERAL(self):
            return self.getToken(QrogueAreasParser.SPAWN_LITERAL, 0)

        def BOSS_LITERAL(self):
            return self.getToken(QrogueAreasParser.BOSS_LITERAL, 0)

        def WILD_LITERAL(self):
            return self.getToken(QrogueAreasParser.WILD_LITERAL, 0)

        def SHOP_LITERAL(self):
            return self.getToken(QrogueAreasParser.SHOP_LITERAL, 0)

        def RIDDLE_LITERAL(self):
            return self.getToken(QrogueAreasParser.RIDDLE_LITERAL, 0)

        def GATE_ROOM_LITERAL(self):
            return self.getToken(QrogueAreasParser.GATE_ROOM_LITERAL, 0)

        def TREASURE_LITERAL(self):
            return self.getToken(QrogueAreasParser.TREASURE_LITERAL, 0)

        def getRuleIndex(self):
            return QrogueAreasParser.RULE_r_type

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

        localctx = QrogueAreasParser.R_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_r_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << QrogueAreasParser.SPAWN_LITERAL) | (1 << QrogueAreasParser.WILD_LITERAL) | (1 << QrogueAreasParser.SHOP_LITERAL) | (1 << QrogueAreasParser.RIDDLE_LITERAL) | (1 << QrogueAreasParser.BOSS_LITERAL) | (1 << QrogueAreasParser.GATE_ROOM_LITERAL) | (1 << QrogueAreasParser.TREASURE_LITERAL))) != 0)):
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


    class Room_contentContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.Room_contentContext, self).__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_room_content

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

        localctx = QrogueAreasParser.Room_contentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_room_content)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            self.match(QrogueAreasParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HallwaysContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueAreasParser.HallwaysContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HALLWAYS(self):
            return self.getToken(QrogueAreasParser.HALLWAYS, 0)

        def hallway(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(QrogueAreasParser.HallwayContext)
            else:
                return self.getTypedRuleContext(QrogueAreasParser.HallwayContext,i)


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_hallways

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

        localctx = QrogueAreasParser.HallwaysContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_hallways)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(QrogueAreasParser.HALLWAYS)
            self.state = 93
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueAreasParser.HALLWAY_ID:
                self.state = 90
                self.hallway()
                self.state = 95
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
            super(QrogueAreasParser.HallwayContext, self).__init__(parent, invokingState)
            self.parser = parser

        def HALLWAY_ID(self):
            return self.getToken(QrogueAreasParser.HALLWAY_ID, 0)

        def h_attributes(self):
            return self.getTypedRuleContext(QrogueAreasParser.H_attributesContext,0)


        def getRuleIndex(self):
            return QrogueAreasParser.RULE_hallway

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

        localctx = QrogueAreasParser.HallwayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_hallway)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 96
            self.match(QrogueAreasParser.HALLWAY_ID)
            self.state = 97
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
            super(QrogueAreasParser.H_attributesContext, self).__init__(parent, invokingState)
            self.parser = parser

        def OPEN_LITERAL(self):
            return self.getToken(QrogueAreasParser.OPEN_LITERAL, 0)

        def CLOSED_LITERAL(self):
            return self.getToken(QrogueAreasParser.CLOSED_LITERAL, 0)

        def LOCKED_LITERAL(self):
            return self.getToken(QrogueAreasParser.LOCKED_LITERAL, 0)

        def EVENT_LITERAL(self):
            return self.getToken(QrogueAreasParser.EVENT_LITERAL, 0)

        def REFERENCE(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.REFERENCE)
            else:
                return self.getToken(QrogueAreasParser.REFERENCE, i)

        def DIRECTION(self):
            return self.getToken(QrogueAreasParser.DIRECTION, 0)

        def ENTANGLED_LITERAL(self):
            return self.getToken(QrogueAreasParser.ENTANGLED_LITERAL, 0)

        def HALLWAY_ID(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.HALLWAY_ID)
            else:
                return self.getToken(QrogueAreasParser.HALLWAY_ID, i)

        def TUTORIAL_LITERAL(self):
            return self.getToken(QrogueAreasParser.TUTORIAL_LITERAL, 0)

        def TRIGGER_LITERAL(self):
            return self.getToken(QrogueAreasParser.TRIGGER_LITERAL, 0)

        def PERMANENT_LITERAL(self):
            return self.getToken(QrogueAreasParser.PERMANENT_LITERAL, 0)

        def LIST_SEPARATOR(self, i=None):
            if i is None:
                return self.getTokens(QrogueAreasParser.LIST_SEPARATOR)
            else:
                return self.getToken(QrogueAreasParser.LIST_SEPARATOR, i)

        def getRuleIndex(self):
            return QrogueAreasParser.RULE_h_attributes

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

        localctx = QrogueAreasParser.H_attributesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_h_attributes)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 99
            self.match(QrogueAreasParser.T__1)
            self.state = 105
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueAreasParser.OPEN_LITERAL]:
                self.state = 100
                self.match(QrogueAreasParser.OPEN_LITERAL)
                pass
            elif token in [QrogueAreasParser.CLOSED_LITERAL]:
                self.state = 101
                self.match(QrogueAreasParser.CLOSED_LITERAL)
                pass
            elif token in [QrogueAreasParser.LOCKED_LITERAL]:
                self.state = 102
                self.match(QrogueAreasParser.LOCKED_LITERAL)
                pass
            elif token in [QrogueAreasParser.EVENT_LITERAL]:
                self.state = 103
                self.match(QrogueAreasParser.EVENT_LITERAL)
                self.state = 104
                self.match(QrogueAreasParser.REFERENCE)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 112
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueAreasParser.T__4:
                self.state = 107
                self.match(QrogueAreasParser.T__4)
                self.state = 108
                self.match(QrogueAreasParser.DIRECTION)
                self.state = 110
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==QrogueAreasParser.PERMANENT_LITERAL:
                    self.state = 109
                    self.match(QrogueAreasParser.PERMANENT_LITERAL)




            self.state = 125
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueAreasParser.ENTANGLED_LITERAL:
                self.state = 114
                self.match(QrogueAreasParser.ENTANGLED_LITERAL)
                self.state = 115
                self.match(QrogueAreasParser.T__5)
                self.state = 116
                self.match(QrogueAreasParser.HALLWAY_ID)
                self.state = 121
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==QrogueAreasParser.LIST_SEPARATOR:
                    self.state = 117
                    self.match(QrogueAreasParser.LIST_SEPARATOR)
                    self.state = 118
                    self.match(QrogueAreasParser.HALLWAY_ID)
                    self.state = 123
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 124
                self.match(QrogueAreasParser.T__6)


            self.state = 127
            self.match(QrogueAreasParser.T__2)
            self.state = 130
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueAreasParser.TUTORIAL_LITERAL:
                self.state = 128
                self.match(QrogueAreasParser.TUTORIAL_LITERAL)
                self.state = 129
                self.match(QrogueAreasParser.REFERENCE)


            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueAreasParser.TRIGGER_LITERAL:
                self.state = 132
                self.match(QrogueAreasParser.TRIGGER_LITERAL)
                self.state = 133
                self.match(QrogueAreasParser.REFERENCE)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





