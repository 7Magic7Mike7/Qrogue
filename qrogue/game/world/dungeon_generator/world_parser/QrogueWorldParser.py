# Generated from D:/Documents/pycharm_workspace/Qrogue/qrogue/game/world/dungeon_generator\QrogueWorld.g4 by ANTLR 4.10.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    return [
        4,1,39,125,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,1,0,1,0,1,0,3,
        0,29,8,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,5,1,38,8,1,10,1,12,1,41,9,1,
        1,1,1,1,1,1,1,1,5,1,47,8,1,10,1,12,1,50,9,1,1,1,5,1,53,8,1,10,1,
        12,1,56,9,1,1,2,1,2,1,2,1,2,5,2,62,8,2,10,2,12,2,65,9,2,1,2,1,2,
        1,3,1,3,4,3,71,8,3,11,3,12,3,72,1,3,1,3,1,4,1,4,5,4,79,8,4,10,4,
        12,4,82,9,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,
        3,6,97,8,6,1,6,1,6,1,6,1,7,3,7,103,8,7,1,8,1,8,1,9,1,9,5,9,109,8,
        9,10,9,12,9,112,9,9,1,10,1,10,1,10,1,11,1,11,1,11,1,11,3,11,121,
        8,11,1,11,1,11,1,11,0,0,12,0,2,4,6,8,10,12,14,16,18,20,22,0,4,2,
        0,29,29,33,33,2,0,28,28,34,34,1,0,12,13,1,0,30,31,123,0,24,1,0,0,
        0,2,35,1,0,0,0,4,57,1,0,0,0,6,68,1,0,0,0,8,76,1,0,0,0,10,83,1,0,
        0,0,12,91,1,0,0,0,14,102,1,0,0,0,16,104,1,0,0,0,18,106,1,0,0,0,20,
        113,1,0,0,0,22,116,1,0,0,0,24,28,5,16,0,0,25,26,5,18,0,0,26,27,5,
        1,0,0,27,29,5,11,0,0,28,25,1,0,0,0,28,29,1,0,0,0,29,30,1,0,0,0,30,
        31,3,2,1,0,31,32,3,8,4,0,32,33,3,18,9,0,33,34,5,17,0,0,34,1,1,0,
        0,0,35,39,5,20,0,0,36,38,5,24,0,0,37,36,1,0,0,0,38,41,1,0,0,0,39,
        37,1,0,0,0,39,40,1,0,0,0,40,42,1,0,0,0,41,39,1,0,0,0,42,48,3,4,2,
        0,43,44,3,6,3,0,44,45,3,4,2,0,45,47,1,0,0,0,46,43,1,0,0,0,47,50,
        1,0,0,0,48,46,1,0,0,0,48,49,1,0,0,0,49,54,1,0,0,0,50,48,1,0,0,0,
        51,53,5,24,0,0,52,51,1,0,0,0,53,56,1,0,0,0,54,52,1,0,0,0,54,55,1,
        0,0,0,55,3,1,0,0,0,56,54,1,0,0,0,57,58,5,25,0,0,58,63,7,0,0,0,59,
        60,7,1,0,0,60,62,7,0,0,0,61,59,1,0,0,0,62,65,1,0,0,0,63,61,1,0,0,
        0,63,64,1,0,0,0,64,66,1,0,0,0,65,63,1,0,0,0,66,67,5,25,0,0,67,5,
        1,0,0,0,68,70,5,25,0,0,69,71,7,1,0,0,70,69,1,0,0,0,71,72,1,0,0,0,
        72,70,1,0,0,0,72,73,1,0,0,0,73,74,1,0,0,0,74,75,5,25,0,0,75,7,1,
        0,0,0,76,80,5,21,0,0,77,79,3,10,5,0,78,77,1,0,0,0,79,82,1,0,0,0,
        80,78,1,0,0,0,80,81,1,0,0,0,81,9,1,0,0,0,82,80,1,0,0,0,83,84,5,33,
        0,0,84,85,3,12,6,0,85,86,5,2,0,0,86,87,5,3,0,0,87,88,5,11,0,0,88,
        89,5,4,0,0,89,90,5,35,0,0,90,11,1,0,0,0,91,92,5,5,0,0,92,93,3,14,
        7,0,93,94,3,16,8,0,94,96,5,7,0,0,95,97,5,7,0,0,96,95,1,0,0,0,96,
        97,1,0,0,0,97,98,1,0,0,0,98,99,5,32,0,0,99,100,5,6,0,0,100,13,1,
        0,0,0,101,103,7,2,0,0,102,101,1,0,0,0,102,103,1,0,0,0,103,15,1,0,
        0,0,104,105,7,3,0,0,105,17,1,0,0,0,106,110,5,22,0,0,107,109,3,20,
        10,0,108,107,1,0,0,0,109,112,1,0,0,0,110,108,1,0,0,0,110,111,1,0,
        0,0,111,19,1,0,0,0,112,110,1,0,0,0,113,114,5,34,0,0,114,115,3,22,
        11,0,115,21,1,0,0,0,116,120,5,5,0,0,117,121,5,14,0,0,118,119,5,15,
        0,0,119,121,5,35,0,0,120,117,1,0,0,0,120,118,1,0,0,0,121,122,1,0,
        0,0,122,123,5,6,0,0,123,23,1,0,0,0,11,28,39,48,54,63,72,80,96,102,
        110,120
    ]

class QrogueWorldParser ( Parser ):

    grammarFileName = "QrogueWorld.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'='", u"':'", u"'description'", u"'teleport'", 
                     u"'('", u"')'", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"'visible'", u"'foggy'", 
                     u"'open'", u"'event'", u"'Qrogue<'", u"'>Qrogue'", 
                     u"'Name'", u"'[Robot]'", u"'[Layout]'", u"'[Rooms]'", 
                     u"'[Hallways]'", u"'[Messages]'", u"'~'", u"'|'", u"','", 
                     u"'#'", u"'..'", u"'__'", u"'World'", u"'Level'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"DIGIT", 
                      u"CHARACTER_LOW", u"CHARACTER_UP", u"CHARACTER", u"TEXT", 
                      u"VISIBLE_LITERAL", u"FOGGY_LITERAL", u"OPEN_LITERAL", 
                      u"EVENT_LITERAL", u"HEADER", u"ENDER", u"NAME", u"ROBOT", 
                      u"LAYOUT", u"ROOMS", u"HALLWAYS", u"MESSAGES", u"HORIZONTAL_SEPARATOR", 
                      u"VERTICAL_SEPARATOR", u"LIST_SEPARATOR", u"WALL", 
                      u"EMPTY_HALLWAY", u"EMPTY_ROOM", u"WORLD_LITERAL", 
                      u"LEVEL_LITERAL", u"DIRECTION", u"ROOM_ID", u"HALLWAY_ID", 
                      u"REFERENCE", u"WS", u"UNIVERSAL_SEPARATOR", u"COMMENT", 
                      u"LINE_COMMENT" ]

    RULE_start = 0
    RULE_layout = 1
    RULE_l_room_row = 2
    RULE_l_hallway_row = 3
    RULE_rooms = 4
    RULE_room = 5
    RULE_r_attributes = 6
    RULE_r_visibility = 7
    RULE_r_type = 8
    RULE_hallways = 9
    RULE_hallway = 10
    RULE_h_attributes = 11

    ruleNames =  [ u"start", u"layout", u"l_room_row", u"l_hallway_row", 
                   u"rooms", u"room", u"r_attributes", u"r_visibility", 
                   u"r_type", u"hallways", u"hallway", u"h_attributes" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    DIGIT=7
    CHARACTER_LOW=8
    CHARACTER_UP=9
    CHARACTER=10
    TEXT=11
    VISIBLE_LITERAL=12
    FOGGY_LITERAL=13
    OPEN_LITERAL=14
    EVENT_LITERAL=15
    HEADER=16
    ENDER=17
    NAME=18
    ROBOT=19
    LAYOUT=20
    ROOMS=21
    HALLWAYS=22
    MESSAGES=23
    HORIZONTAL_SEPARATOR=24
    VERTICAL_SEPARATOR=25
    LIST_SEPARATOR=26
    WALL=27
    EMPTY_HALLWAY=28
    EMPTY_ROOM=29
    WORLD_LITERAL=30
    LEVEL_LITERAL=31
    DIRECTION=32
    ROOM_ID=33
    HALLWAY_ID=34
    REFERENCE=35
    WS=36
    UNIVERSAL_SEPARATOR=37
    COMMENT=38
    LINE_COMMENT=39

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

        def NAME(self):
            return self.getToken(QrogueWorldParser.NAME, 0)

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
            self.state = 24
            self.match(QrogueWorldParser.HEADER)
            self.state = 28
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.NAME:
                self.state = 25
                self.match(QrogueWorldParser.NAME)
                self.state = 26
                self.match(QrogueWorldParser.T__0)
                self.state = 27
                self.match(QrogueWorldParser.TEXT)


            self.state = 30
            self.layout()
            self.state = 31
            self.rooms()
            self.state = 32
            self.hallways()
            self.state = 33
            self.match(QrogueWorldParser.ENDER)
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
        self.enterRule(localctx, 2, self.RULE_layout)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self.match(QrogueWorldParser.LAYOUT)
            self.state = 39
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 36
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 42
            self.l_room_row()
            self.state = 48
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.VERTICAL_SEPARATOR:
                self.state = 43
                self.l_hallway_row()
                self.state = 44
                self.l_room_row()
                self.state = 50
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 54
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HORIZONTAL_SEPARATOR:
                self.state = 51
                self.match(QrogueWorldParser.HORIZONTAL_SEPARATOR)
                self.state = 56
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
        self.enterRule(localctx, 4, self.RULE_l_room_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 57
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 58
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 59
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 60
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_ROOM or _la==QrogueWorldParser.ROOM_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 65
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 66
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
        self.enterRule(localctx, 6, self.RULE_l_hallway_row)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(QrogueWorldParser.VERTICAL_SEPARATOR)
            self.state = 70 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 69
                _la = self._input.LA(1)
                if not(_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 72 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==QrogueWorldParser.EMPTY_HALLWAY or _la==QrogueWorldParser.HALLWAY_ID):
                    break

            self.state = 74
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
        self.enterRule(localctx, 8, self.RULE_rooms)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            self.match(QrogueWorldParser.ROOMS)
            self.state = 80
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.ROOM_ID:
                self.state = 77
                self.room()
                self.state = 82
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


        def TEXT(self):
            return self.getToken(QrogueWorldParser.TEXT, 0)

        def REFERENCE(self):
            return self.getToken(QrogueWorldParser.REFERENCE, 0)

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
        self.enterRule(localctx, 10, self.RULE_room)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(QrogueWorldParser.ROOM_ID)
            self.state = 84
            self.r_attributes()
            self.state = 85
            self.match(QrogueWorldParser.T__1)
            self.state = 86
            self.match(QrogueWorldParser.T__2)
            self.state = 87
            self.match(QrogueWorldParser.TEXT)
            self.state = 88
            self.match(QrogueWorldParser.T__3)
            self.state = 89
            self.match(QrogueWorldParser.REFERENCE)
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


        def DIGIT(self, i=None):
            if i is None:
                return self.getTokens(QrogueWorldParser.DIGIT)
            else:
                return self.getToken(QrogueWorldParser.DIGIT, i)

        def DIRECTION(self):
            return self.getToken(QrogueWorldParser.DIRECTION, 0)

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
        self.enterRule(localctx, 12, self.RULE_r_attributes)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 91
            self.match(QrogueWorldParser.T__4)
            self.state = 92
            self.r_visibility()
            self.state = 93
            self.r_type()
            self.state = 94
            self.match(QrogueWorldParser.DIGIT)
            self.state = 96
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.DIGIT:
                self.state = 95
                self.match(QrogueWorldParser.DIGIT)


            self.state = 98
            self.match(QrogueWorldParser.DIRECTION)
            self.state = 99
            self.match(QrogueWorldParser.T__5)
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
        self.enterRule(localctx, 14, self.RULE_r_visibility)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 102
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==QrogueWorldParser.VISIBLE_LITERAL or _la==QrogueWorldParser.FOGGY_LITERAL:
                self.state = 101
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


    class R_typeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(QrogueWorldParser.R_typeContext, self).__init__(parent, invokingState)
            self.parser = parser

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
        self.enterRule(localctx, 16, self.RULE_r_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 104
            _la = self._input.LA(1)
            if not(_la==QrogueWorldParser.WORLD_LITERAL or _la==QrogueWorldParser.LEVEL_LITERAL):
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
        self.enterRule(localctx, 18, self.RULE_hallways)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 106
            self.match(QrogueWorldParser.HALLWAYS)
            self.state = 110
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==QrogueWorldParser.HALLWAY_ID:
                self.state = 107
                self.hallway()
                self.state = 112
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
        self.enterRule(localctx, 20, self.RULE_hallway)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.match(QrogueWorldParser.HALLWAY_ID)
            self.state = 114
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

        def EVENT_LITERAL(self):
            return self.getToken(QrogueWorldParser.EVENT_LITERAL, 0)

        def REFERENCE(self):
            return self.getToken(QrogueWorldParser.REFERENCE, 0)

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
        self.enterRule(localctx, 22, self.RULE_h_attributes)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 116
            self.match(QrogueWorldParser.T__4)
            self.state = 120
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [QrogueWorldParser.OPEN_LITERAL]:
                self.state = 117
                self.match(QrogueWorldParser.OPEN_LITERAL)
                pass
            elif token in [QrogueWorldParser.EVENT_LITERAL]:
                self.state = 118
                self.match(QrogueWorldParser.EVENT_LITERAL)
                self.state = 119
                self.match(QrogueWorldParser.REFERENCE)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 122
            self.match(QrogueWorldParser.T__5)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





