import os.path
from typing import Tuple, Optional, List, Union, Iterator, Dict

from antlr4 import InputStream, CommonTokenStream
from datetime import datetime

from qrogue.game.logic.actors import Player, Robot
from qrogue.game.logic.actors.controllables import BaseBot, LukeBot
from qrogue.game.logic.collectibles import Instruction
from qrogue.game.logic.collectibles.instruction import InstructionManager
from qrogue.game.world.dungeon_generator import parser_util
from qrogue.game.world.map import CallbackPack
from qrogue.management import LevelInfo
from qrogue.management.save_grammar.SaveDataLexer import SaveDataLexer
from qrogue.management.save_grammar.SaveDataParser import SaveDataParser
from qrogue.management.save_grammar.SaveDataVisitor import SaveDataVisitor
from qrogue.util import Logger, PathConfig, FileTypes, RandomManager, CommonPopups, Config, \
    TestConfig, ErrorConfig, achievements, MapConfig
from qrogue.util.achievements import Achievement, Unlocks, Ach
from qrogue.util.util_functions import cur_datetime, time_diff


class SaveData:
    pass


class NewSaveData:
    __instance = None

    class LevelData:
        def __init__(self, name: str, date_time: datetime, duration: int, score: int):
            if name.endswith("done"):
                self.__name = name[:-len("done")]
            else:
                self.__name = name
            self.__date_time = date_time
            self.__duration = duration
            self.__score = score

        @property
        def name(self) -> str:
            """

            Returns: internal name of the map

            """
            return self.__name

        @property
        def date_time(self) -> datetime:
            return self.__date_time

        @property
        def duration(self) -> int:
            return self.__duration

        @property
        def score(self) -> int:
            return self.__score

        def __str__(self) -> str:
            return f"{self.__name} ({_SaveDataGenerator.datetime2str(self.__date_time)}, {self.__duration}s, " \
                   f"#{self.__score})"

    @staticmethod
    def _init_fresh_save(save_data: "NewSaveData"):
        # some achievements need to be present right from the start
        save_data.add_achievement(Achievement(achievements.CompletedExpedition, 0, 100))    # todo: change system?

        # some unlocks are present by default for backwards compatibility   # todo: fix this because it's confusing on the Achievement-screen
        save_data.unlock(Unlocks.GateRemove)

    def __init__(self, save_data: Optional[str] = None):
        """

        Args:
            save_data: if None is provided, the data is loaded from the latest save file
            is_global_save:
        """
        self.__level_timer = cur_datetime()
        self.__temp_level_storage: Dict[str, Tuple[int, int]] = {}  # event name -> score, done_score
        #achievement_list = []   # todo: init differently?

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

        self.__date_time = datetime.now()    # date and time of the latest save
        self.__gates: List[Instruction] = []
        self.__levels: Dict[str, NewSaveData.LevelData] = {}
        self.__achievements: Dict[str, Achievement] = {}
        self.__unlocks: Dict[str, datetime] = {}

        if save_data is not None and len(save_data.strip()) > 0:
            generator = _SaveDataGenerator()
            self.__date_time, gates, levels, unlocks, achievement_list = generator.load(save_data)
            self.__gates = gates.copy()
            for level in levels: self.__levels[level.name] = level
            for ach in achievement_list: self.__achievements[ach.name] = ach
            for name, date_time2 in unlocks: self.__unlocks[name] = date_time2

        #self.__player = Player()    # todo: most likely no longer needed
        #self.__robot = BaseBot(CallbackPack.instance().game_over)

        if self.__is_fresh_save:
            NewSaveData._init_fresh_save(self)

    @property
    def is_fresh_save(self) -> bool:
        return self.__is_fresh_save

    @property
    def player(self) -> Player:
        return self.__player

    def available_robots(self) -> Iterator[Robot]:
        return []       # todo: most likely no longer needed

    def get_robot(self, index: int) -> Optional[Robot]:
        ErrorConfig.raise_deletion_exception()
        #if index != 0:
        #    raise Exception("Unexpected behaviour!")
        #return self.__robot

    def check_level(self, name: str) -> bool:
        return name in self.__levels

    def check_unlock(self, unlock: Union[str, Unlocks]) -> bool:
        if isinstance(unlock, Unlocks): unlock = unlock.ach_name
        return unlock in self.__unlocks

    def check_achievement(self, name: str) -> bool:
        return name in self.__achievements and self.__achievements[name].is_done()

    def check(self, name: str) -> bool:
        if self.check_level(name): return True
        if self.check_unlock(name): return True
        if self.check_achievement(name): return True
        return False

    def complete_level(self, name: str, date_time: Optional[datetime] = None, duration: int = -1, score: int = -1):
        # NOTE: name might still have the "done" suffix! Use level_data.name if you need the normalized name.
        # compute date_time and duration based on current time if not provided
        if date_time is None: date_time = datetime.now()
        if duration < 0: duration, _ = time_diff(cur_datetime(), self.__level_timer)

        level_data = NewSaveData.LevelData(name, date_time, duration, score)
        self.__levels[level_data.name] = level_data

        for unlock in LevelInfo.get_level_completion_unlocks(level_data.name, self.check_level):
            self.unlock(unlock, date_time)

    def unlock(self, unlock: Union[str, Unlocks], date_time: Optional[datetime] = None):
        if date_time is None: date_time = datetime.now()
        if isinstance(unlock, Unlocks): unlock = unlock.ach_name
        if unlock in self.__unlocks:
            return
        self.__unlocks[unlock] = date_time

    def add_achievement(self, achievement: Achievement):
        if achievement.name in self.__achievements:
            raise Exception("Use score_achievement() for existing achievements!")

        self.__achievements[achievement.name] = achievement

    def score_achievement(self, name: str, score: int = 1):
        if name not in self.__achievements:
            raise Exception("Use add_achievement() for new achievements!")

        self.__achievements[name].add_score(score)

    def to_achievements_string(self) -> str:
        # todo: improve readability
        text = ""
        if len(self.__levels) > 0:
            text += f"-- Completed Levels --\n"
            text += "\n".join([f"{level.name} @ {_SaveDataGenerator.datetime2str(level.date_time)} "
                               f"{level.duration} {_SaveDataGenerator.duration_unit()} Score = {level.score}"
                               for level in self.__levels.values()])
            text += "\n\n"

        if len(self.__unlocks) > 0:
            text += f"-- Unlocks --\n"
            text += "\n".join([f"{unlock} @ {_SaveDataGenerator.datetime2str(self.__unlocks[unlock])}"
                               for unlock in self.__unlocks])
            text += "\n\n"

        text += f"-- Achievements --\n"
        text += "\n".join([f"{ach.name} @ {_SaveDataGenerator.datetime2str(ach.date_time)} "
                           f"Score = {ach.score} out of {ach.done_score}"
                           for ach in self.__achievements.values()])
        return text

    def to_keylog_string(self) -> str:
        return self.to_string()

    def to_string(self) -> str:
        text = f"{_SaveDataGenerator.header()}\n"
        text += f"{_SaveDataGenerator.datetime2str(self.__date_time)}\n"

        text += f"{_SaveDataGenerator.gates_header()}\n"
        text += _SaveDataGenerator.gate_separator().join([gate.gate_type.short_name for gate in self.__gates])
        text += "\n"

        text += f"{_SaveDataGenerator.levels_header()}\n"
        text += "\n".join([f"{level.name} @ {_SaveDataGenerator.datetime2str(level.date_time)} "
                           f"{level.duration} {_SaveDataGenerator.duration_unit()} Score = {level.score}"
                           for level in self.__levels.values()])
        text += "\n"

        text += f"{_SaveDataGenerator.unlocks_header()}\n"
        text += "\n".join([f"{unlock} @ {_SaveDataGenerator.datetime2str(self.__unlocks[unlock])}"
                           for unlock in self.__unlocks])
        text += "\n"

        text += f"{_SaveDataGenerator.achievements_header()}\n"
        text += "\n".join([f"{ach.name} @ {_SaveDataGenerator.datetime2str(ach.date_time)} "
                           f"Score = {ach.score} out of {ach.done_score}"
                           for ach in self.__achievements.values()])
        text += "\n"

        return text + f"{_SaveDataGenerator.ender()}\n"

    def save(self, is_auto_save: bool = False) -> Tuple[bool, CommonPopups]:
        if Config.forbid_saving():
            return False, CommonPopups.NoSavingWithCheats
        try:
            self.__date_time = datetime.now()   # update datetime of the latest save (=now)
            data = self.to_string()
            if is_auto_save:
                PathConfig.write_auto_save(data)
            else:
                PathConfig.new_save_file(data)
            return True, CommonPopups.SavingSuccessful
        except:
            return False, CommonPopups.SavingFailed

    ################################## TRANSITION TO NEW SYSTEM ##################################

    def achievement_iterator(self) -> Iterator[Achievement]:
        # todo: test
        return iter(self.__achievements.values())

    def restart_level_timer(self):
        self.__level_timer = cur_datetime()

    def check_unlocks(self, unlocks: Union[str, Unlocks]) -> bool:
        return self.check_unlock(unlocks)       # todo: fix naming

    def reset_level_events(self):
        # todo: test
        self.__temp_level_storage.clear()

    def add_to_achievement(self, name: str, score: float = 1):
        # todo: test
        self.score_achievement(name, int(score))

    def trigger_global_event(self, name: str, score: float = 1):
        # todo: I think this is only used for EnteredPauseMenu -> handle EnteredPauseMenu differently
        #self.add_achievement(Achievement(name, AchievementType.NewInternalFlag, 1, 1))
        raise Exception("Should no longer be used!")

    def trigger_event(self, name: str, score: float = 1):
        """
        Triggers an event (either global or local/level-wise) by creating or adding to the corresponding achievement.

        :param name: name of the event (needs to be unique)
        :param score: by how much the event should progress (only relevant if it can be triggered multiple times from
                        different sources
        """
        score = int(score)
        # todo: test and rethink whether we actually need this
        if name.startswith(MapConfig.global_event_prefix()):
            name = name[len(MapConfig.global_event_prefix()):]  # remove prefix
            self.trigger_global_event(name)

        elif name.startswith(MapConfig.unlock_prefix()):
            name = name[len(MapConfig.unlock_prefix()):]    # remove prefix
            self.unlock(name)
            #self.add_achievement(Achievement(name, AchievementType.Unlock, score, score))

        elif name.startswith("l") and name.endswith("done"):
            ErrorConfig.raise_deletion_exception()

        else:
            if name in self.__temp_level_storage:
                event_score, event_done_score = self.__temp_level_storage[name]
                self.__temp_level_storage[name] = event_score + score, event_done_score
            else:
                self.__temp_level_storage[name] = score, score

    def finished_level(self, internal_name: str, display_name: str = None) -> bool:
        # todo: test
        return self.check_level(internal_name)


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

    @staticmethod
    def datetime2str(date_time: datetime) -> str:
        return date_time.strftime('%dd%mm%Yy %H:%M:%S')

    def load(self, file_data) -> Tuple[datetime, List[Instruction],
            List[NewSaveData.LevelData], List[Tuple[str, datetime]], List[Achievement]]:
        input_stream = InputStream(file_data)
        lexer = SaveDataLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = SaveDataParser(token_stream)
        parser.addErrorListener(parser_util.MyErrorListener())

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

    def visitLevel(self, ctx: SaveDataParser.LevelContext) -> NewSaveData.LevelData:
        name = ctx.NAME_SPECIAL().getText()
        date_time = self.visitDate_time(ctx.date_time())
        duration = self.visitDuration(ctx.duration())
        score = self.visitScore(ctx.score())
        return NewSaveData.LevelData(name, date_time, duration, score)

    def visitLevels(self, ctx: SaveDataParser.LevelsContext) -> List[NewSaveData.LevelData]:
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

    def visitStart(self, ctx: SaveDataParser.StartContext) -> Tuple[datetime, List[Instruction],
            List[NewSaveData.LevelData], List[Tuple[str, datetime]], List[Achievement]]:
        date_time = self.visitDate_time(ctx.date_time())
        gates = self.visitGates(ctx.gates())
        levels = self.visitLevels(ctx.levels())
        unlocks = self.visitUnlocks(ctx.unlocks())
        achievement_list = self.visitAchievements(ctx.achievements())
        return date_time, gates, levels, unlocks, achievement_list
