# Generated from D:/Workspaces/pycharm-workspace/Qrogue/qrogue/management/save_grammar/SaveData.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .SaveDataParser import SaveDataParser
else:
    from SaveDataParser import SaveDataParser

# This class defines a complete generic visitor for a parse tree produced by SaveDataParser.

class SaveDataVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SaveDataParser#start.
    def visitStart(self, ctx:SaveDataParser.StartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#date_time.
    def visitDate_time(self, ctx:SaveDataParser.Date_timeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#duration.
    def visitDuration(self, ctx:SaveDataParser.DurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#inventory.
    def visitInventory(self, ctx:SaveDataParser.InventoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#gates.
    def visitGates(self, ctx:SaveDataParser.GatesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#gate.
    def visitGate(self, ctx:SaveDataParser.GateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#combined_gate.
    def visitCombined_gate(self, ctx:SaveDataParser.Combined_gateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#background_gate.
    def visitBackground_gate(self, ctx:SaveDataParser.Background_gateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#levels.
    def visitLevels(self, ctx:SaveDataParser.LevelsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#level.
    def visitLevel(self, ctx:SaveDataParser.LevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#score.
    def visitScore(self, ctx:SaveDataParser.ScoreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#value.
    def visitValue(self, ctx:SaveDataParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#unlocks.
    def visitUnlocks(self, ctx:SaveDataParser.UnlocksContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#unlock.
    def visitUnlock(self, ctx:SaveDataParser.UnlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#achievements.
    def visitAchievements(self, ctx:SaveDataParser.AchievementsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#achievement.
    def visitAchievement(self, ctx:SaveDataParser.AchievementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#integer.
    def visitInteger(self, ctx:SaveDataParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SaveDataParser#complex_number.
    def visitComplex_number(self, ctx:SaveDataParser.Complex_numberContext):
        return self.visitChildren(ctx)



del SaveDataParser