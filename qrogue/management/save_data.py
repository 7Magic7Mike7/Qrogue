from datetime import datetime
from typing import Tuple, Optional, List, Union, Dict

from antlr4 import InputStream, CommonTokenStream

from qrogue.game.logic.collectibles import Instruction, InstructionManager
from qrogue.graphics.popups import Popup
from qrogue.management.save_grammar.SaveDataLexer import SaveDataLexer
from qrogue.management.save_grammar.SaveDataParser import SaveDataParser
from qrogue.management.save_grammar.SaveDataVisitor import SaveDataVisitor
from qrogue.util import Logger, CommonInfos, LevelInfo, LevelData, Config, PathConfig, FileTypes, ParserErrorListener
from qrogue.util.achievements import Achievement, Unlocks
from qrogue.util.util_functions import cur_datetime, datetime2str


class NewSaveData:
    __instance = None

    @staticmethod
    def load(path: str, in_user_path: bool = True) -> "NewSaveData":
        if not path.endswith(FileTypes.Save.value):
            path += FileTypes.Save.value
        try:
            save_data = PathConfig.read(path, in_user_path)
            return NewSaveData(save_data)

        except FileNotFoundError as ex:
            Popup.error(f"Could not load save file at \"{path}\": {ex}.\nPlease make sure that you did not move your "
                        f"files manually. If this error occurs even though the stated path points to a "
                        f"{FileTypes.Save.value}-file:", add_report_note=True)

    @staticmethod
    def empty_save_state() -> str:
        save_state =  f"{_SaveDataGenerator.header()}\n"
        save_state += f"{datetime2str(cur_datetime())}\n"
        save_state += f"{_SaveDataGenerator.gates_header()}\n"
        save_state += f"{_SaveDataGenerator.levels_header()}\n"
        save_state += f"{_SaveDataGenerator.unlocks_header()}\n"
        save_state += f"{_SaveDataGenerator.achievements_header()}\n"
        save_state += f"{_SaveDataGenerator.ender()}\n"
        return save_state

    @staticmethod
    def _init_fresh_save(save_data: "NewSaveData"):
        # some achievements need to be present right from the start
        expeditions = Achievement(Achievement.CompletedExpedition, 0, 100)
        save_data.__achievements[expeditions.name] = expeditions

        # some unlocks are present by default for backwards compatibility   # todo: fix this because it's confusing on the Achievement-screen
        save_data.unlock(Unlocks.GateRemove)

    def __init__(self, save_data: Optional[str] = None):
        """

        Args:
            save_data: if None is provided, the data is loaded from the latest save file
        """

        if save_data is None:
            path = PathConfig.find_latest_save_file()
            # a fresh save has no digit before the file ending
            self.__is_fresh_save = not path[-len(FileTypes.Save.value) - 1].isdigit()
            if not self.__is_fresh_save:
                try:
                    save_data = PathConfig.read(path, in_user_path=True)#.splitlines()
                except FileNotFoundError:
                    Logger.instance().throw(NotImplementedError("This line should not be reachable! Please send us the "
                                                                "log files so we can fix the issue as soon as "
                                                                "possible. Thank you!"))
        else:
            self.__is_fresh_save = False

        self.__date_time = cur_datetime()    # date and time of the latest save
        self.__gates: List[Instruction] = []
        self.__levels: Dict[str, LevelData] = {}    # key is a level's internal name
        self.__achievements: Dict[str, Achievement] = {}
        self.__unlocks: Dict[str, datetime] = {}
        self.__has_unsaved_changes = False

        if save_data is not None and len(save_data.strip()) > 0:
            generator = _SaveDataGenerator()
            self.__date_time, gates, levels, unlocks, achievement_list = generator.load(save_data)
            self.__gates = gates.copy()
            for level in levels: self.__levels[level.name] = level
            for ach in achievement_list: self.__achievements[ach.name] = ach
            for name, date_time2 in unlocks: self.__unlocks[name] = date_time2

        if self.__is_fresh_save:
            NewSaveData._init_fresh_save(self)

    @property
    def is_fresh_save(self) -> bool:
        return self.__is_fresh_save

    def check_level(self, internal_name: str) -> bool:
        return internal_name in self.__levels

    def check_unlocks(self, unlock: Union[str, Unlocks]) -> bool:
        if isinstance(unlock, Unlocks): unlock = unlock.ach_name
        return unlock in self.__unlocks

    def check_achievement(self, name: str) -> bool:
        return name in self.__achievements and self.__achievements[name].is_done()

    def check(self, name: str) -> bool:
        if self.check_level(name): return True
        if self.check_unlocks(name): return True
        if self.check_achievement(name): return True
        return False

    def complete_level(self, name: str, duration: int, date_time: Optional[datetime] = None, score: int = -1) \
            -> LevelData:
        # NOTE: name might still have the "done" suffix! Use level_data.name if you need the normalized name.
        # compute date_time and duration based on current time if not provided
        if date_time is None: date_time = cur_datetime()

        level_data = LevelData(name, date_time, duration, score)
        if level_data.name in self.__levels and level_data.total_score >= self.__levels[level_data.name].total_score:
            # save the better score for the replayed level
            self.__levels[level_data.name] = level_data
            self.__has_unsaved_changes = True

        elif level_data.name not in self.__levels:
            # save the level because it has never been completed before
            self.__levels[level_data.name] = level_data
            self.__has_unsaved_changes = True

            # add potential unlocks corresponding to the level
            for unlock in LevelInfo.get_level_completion_unlocks(level_data.name, self.check_level):
                self.unlock(unlock, date_time)

        return level_data

    def unlock(self, unlock: Union[str, Unlocks], date_time: Optional[datetime] = None):
        if date_time is None: date_time = cur_datetime()
        if isinstance(unlock, Unlocks): unlock = unlock.ach_name
        if unlock in self.__unlocks:
            return
        self.__unlocks[unlock] = date_time
        self.__has_unsaved_changes = True

    def get_level_data(self, level_name: str) -> Optional[LevelData]:
        if level_name in self.__levels:
            return self.__levels[level_name]
        return None

    def to_achievements_string(self) -> str:
        # todo: improve readability
        text = ""
        if len(self.__levels) > 0:
            text += f"-- Completed Levels --\n"
            text += "\n".join([f"{level.name} @ {datetime2str(level.date_time)} "
                               f"{level.duration} {_SaveDataGenerator.duration_unit()} Score = {level.score}"
                               for level in self.__levels.values()])
            text += "\n\n"

        if len(self.__unlocks) > 0:
            text += f"-- Unlocks --\n"
            text += "\n".join([f"{unlock} @ {datetime2str(self.__unlocks[unlock])}"
                               for unlock in self.__unlocks])
            text += "\n\n"

        text += f"-- Achievements --\n"
        text += "\n".join([f"{ach.name} @ {datetime2str(ach.date_time)} "
                           f"Score = {ach.score} out of {ach.done_score}"
                           for ach in self.__achievements.values()])
        return text

    def to_keylog_string(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        text = f"{_SaveDataGenerator.header()}\n"
        text += f"{datetime2str(self.__date_time)}\n"

        text += f"{_SaveDataGenerator.gates_header()}\n"
        text += _SaveDataGenerator.gate_separator().join([gate.gate_type.short_name for gate in self.__gates])
        text += "\n"

        text += f"{_SaveDataGenerator.levels_header()}\n"
        text += "\n".join([f"{level.name} @ {datetime2str(level.date_time)} "
                           f"{level.duration} {_SaveDataGenerator.duration_unit()} Score = {level.score}"
                           for level in self.__levels.values()])
        text += "\n"

        text += f"{_SaveDataGenerator.unlocks_header()}\n"
        text += "\n".join([f"{unlock} @ {datetime2str(self.__unlocks[unlock])}"
                           for unlock in self.__unlocks])
        text += "\n"

        text += f"{_SaveDataGenerator.achievements_header()}\n"
        text += "\n".join([f"{ach.name} @ {datetime2str(ach.date_time)} "
                           f"Score = {ach.score} out of {ach.done_score}"
                           for ach in self.__achievements.values()])
        text += "\n"

        return text + f"{_SaveDataGenerator.ender()}\n"

    def save(self, is_auto_save: bool = False) -> Tuple[bool, CommonInfos]:
        """
        Returns:
            False if an error occurred during saving, True if saving behaved as expected (i.e., latest save state is
            persisted)
        """
        if Config.forbid_saving():
            return False, CommonInfos.NoSavingWithCheats
        if not self.__has_unsaved_changes:
            return True, CommonInfos.NothingToSave

        try:
            self.__date_time = cur_datetime()   # update datetime of the latest save (=now)
            data = self.to_string()
            if is_auto_save:
                PathConfig.write_auto_save(data)
            else:
                PathConfig.new_save_file(data)
                self.__has_unsaved_changes = False  # only change flag if it was a manual (i.e., no auto) save
            return True, CommonInfos.SavingSuccessful

        except:
            return False, CommonInfos.SavingFailed

    def compare(self, other: "NewSaveData") -> Tuple[List[Instruction], List[str], List[Unlocks], List[Achievement]]:
        """
        Args:
            other: the NewSaveData to compare with
        Returns:
            List of Instructions, level names, Unlocks and Achievement other has and self does not
        """
        gate_diff = []
        for gate in other.__gates:
            if gate in self.__gates: continue
            gate_diff.append(gate)
        gate_diff = [gate for gate in other.__gates if gate not in self.__gates]

        level_diff = []
        for level in other.__levels:
            if self.check_level(level): continue
            level_diff.append(level)

        unlocks_diff = []
        for unlock in other.__unlocks:
            if self.check_unlocks(unlock): continue
            unlocks_diff.append(Unlocks.from_name(unlock))

        achievement_diff = []
        for ach_name in other.__achievements:
            if self.check_achievement(ach_name): continue
            achievement_diff.append(other.__achievements[ach_name])

        return gate_diff, level_diff, unlocks_diff, achievement_diff

    def get_completed_levels(self) -> List[LevelData]:
        return list(self.__levels.values())

    def add_to_achievement(self, name: str, score: float = 1):
        if name not in self.__achievements:
            raise Exception("Use add_achievement() for new achievements!")

        self.__achievements[name].add_score(score)
        self.__has_unsaved_changes = True


class _SaveDataGenerator(SaveDataVisitor):
    @staticmethod
    def header() -> str:
        return "Qrogue<"

    @staticmethod
    def gates_header() -> str:
        return "[GATES]"

    @staticmethod
    def levels_header() -> str:
        return "[LEVELS]"

    @staticmethod
    def unlocks_header() -> str:
        return "[UNLOCKS]"

    @staticmethod
    def achievements_header() -> str:
        return "[ACHIEVEMENTS]"

    @staticmethod
    def ender() -> str:
        return ">Qrogue"

    @staticmethod
    def duration_unit() -> str:
        return "seconds"

    @staticmethod
    def gate_separator() -> str:
        return ";"      # the general separator can be used to separate gates for improved readability

    def load(self, file_data) -> Tuple[datetime, List[Instruction],
            List[LevelData], List[Tuple[str, datetime]], List[Achievement]]:
        input_stream = InputStream(file_data)
        lexer = SaveDataLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaveDataParser(token_stream)
        parser.addErrorListener(ParserErrorListener())

        return self.visitStart(parser.start())

    #####################################

    def visitDate_time(self, ctx: SaveDataParser.Date_timeContext) -> datetime:
        date: str = ctx.DATE().getText()
        day = int(date[0:2])
        month = int(date[3:5])
        year = int(date[6:10])

        time: str = ctx.TIME().getText()
        hour = int(time[0:2])
        minute = int(time[3:5])
        second = int(time[6:8])

        return datetime(year, month, day, hour, minute, second)

    def visitValue(self, ctx: SaveDataParser.ValueContext) -> int:
        return int(ctx.VALUE().getText())

    def visitDuration(self, ctx: SaveDataParser.DurationContext) -> int:
        return self.visitValue(ctx.value())

    def visitScore(self, ctx: SaveDataParser.ScoreContext) -> int:
        return self.visitValue(ctx.value())

    #####################################

    def visitGate(self, ctx: SaveDataParser.GateContext) -> Optional[Instruction]:
        return InstructionManager.from_name(ctx.NAME_STD().getText())

    def visitGates(self, ctx: SaveDataParser.GatesContext) -> List[Instruction]:
        gates = []
        for gate_ctx in ctx.gate():
            gate = self.visitGate(gate_ctx)
            if gate is not None:
                gates.append(gate)
        return gates

    #####################################

    def visitLevel(self, ctx: SaveDataParser.LevelContext) -> LevelData:
        name = ctx.NAME_SPECIAL().getText()
        date_time = self.visitDate_time(ctx.date_time())
        duration = self.visitDuration(ctx.duration())
        score = self.visitScore(ctx.score())
        return LevelData(name, date_time, duration, score)

    def visitLevels(self, ctx: SaveDataParser.LevelsContext) -> List[LevelData]:
        return [self.visitLevel(level) for level in ctx.level()]

    #####################################
    def visitUnlock(self, ctx: SaveDataParser.UnlockContext) -> Tuple[str, datetime]:
        name = ctx.NAME_STD().getText()
        date_time = self.visitDate_time(ctx.date_time())
        return name, date_time

    def visitUnlocks(self, ctx: SaveDataParser.UnlocksContext) -> List[Tuple[str, datetime]]:
        return [self.visitUnlock(unlock) for unlock in ctx.unlock()]

    #####################################
    def visitAchievement(self, ctx: SaveDataParser.AchievementContext) -> Achievement:
        name = ctx.NAME_STD().getText()
        date_time = self.visitDate_time(ctx.date_time())
        actual_score = self.visitScore(ctx.score())
        required_score = self.visitValue(ctx.value())

        return Achievement(name, actual_score, required_score, date_time)

    def visitAchievements(self, ctx: SaveDataParser.AchievementsContext) -> List[Achievement]:
        return [self.visitAchievement(achievement) for achievement in ctx.achievement()]

    #####################################

    def visitStart(self, ctx: SaveDataParser.StartContext) -> Tuple[datetime, List[Instruction], List[LevelData],
            List[Tuple[str, datetime]], List[Achievement]]:
        date_time = self.visitDate_time(ctx.date_time())
        gates = self.visitGates(ctx.gates())
        levels = self.visitLevels(ctx.levels())
        unlocks = self.visitUnlocks(ctx.unlocks())
        achievement_list = self.visitAchievements(ctx.achievements())
        return date_time, gates, levels, unlocks, achievement_list
