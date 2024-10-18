from datetime import datetime
from typing import Tuple, Optional, List, Union, Dict

from antlr4 import InputStream, CommonTokenStream

from qrogue.game.logic.collectibles import InstructionManager, Instruction
from qrogue.game.logic.collectibles.instruction import CombinedGate
from qrogue.graphics.popups import Popup
from qrogue.management.save_grammar.SaveDataLexer import SaveDataLexer
from qrogue.management.save_grammar.SaveDataParser import SaveDataParser
from qrogue.management.save_grammar.SaveDataVisitor import SaveDataVisitor
from qrogue.util import Logger, CommonInfos, LevelInfo, LevelData, Config, PathConfig, FileTypes, ParserErrorListener, \
    GateType, GameplayConfig
from qrogue.util.achievements import Achievement, Unlocks
from qrogue.util.util_functions import cur_datetime, datetime2str, simple_decode, simple_encode


class NewSaveData:
    __instance = None
    __ENCODING_KEY = "6l5f5BqbldikHYpqE240"

    @staticmethod
    def _encode(data: str, force: bool = False) -> str:
        if not Config.debugging() or force:
            data = simple_encode(NewSaveData.__ENCODING_KEY, data)
        return data

    @staticmethod
    def _decode(data: str) -> str:
        if data.startswith(_SaveDataGenerator.header()):
            return data
        return simple_decode(NewSaveData.__ENCODING_KEY, data)

    @staticmethod
    def load(path: str, in_user_path: bool = True) -> "NewSaveData":
        if not path.endswith(FileTypes.Save.value):
            path += FileTypes.Save.value
        try:
            save_data = NewSaveData._decode(PathConfig.read(path, in_user_path))
            return NewSaveData(save_data)

        except FileNotFoundError as ex:
            Popup.error(f"Could not load save file at \"{path}\": {ex}.\nPlease make sure that you did not move your "
                        f"files manually. If this error occurs even though the stated path points to a "
                        f"{FileTypes.Save.value}-file:", add_report_note=True)

    @staticmethod
    def empty_save_state() -> str:
        save_state = f"{_SaveDataGenerator.header()}\n"
        save_state += f"{datetime2str(cur_datetime())}\n"
        save_state += f"{_SaveDataGenerator.inventory_header()}\n"
        save_state += f"{_SaveDataGenerator.quantum_fuser()} 0\n"
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
                    save_data = PathConfig.read(path, in_user_path=True)
                except FileNotFoundError:
                    Logger.instance().throw(NotImplementedError("This line should not be reachable! Please send us the "
                                                                "log files so we can fix the issue as soon as "
                                                                "possible. Thank you!"))
        else:
            self.__is_fresh_save = False

        self.__date_time = cur_datetime()  # date and time of the latest save
        self.__inventory = _SaveDataGenerator.Inventory.default()
        self.__gates: List[Instruction] = []
        self.__levels: Dict[str, LevelData] = {}  # key is a level's internal name
        self.__achievements: Dict[str, Achievement] = {}
        self.__unlocks: Dict[str, datetime] = {}
        self.__has_unsaved_changes = False

        if save_data is not None and len(save_data.strip()) > 0:
            save_data = self._decode(save_data)
            generator = _SaveDataGenerator()
            self.__date_time, self.__inventory, gates, levels, unlocks, achievement_list = generator.load(save_data)
            self.__gates = gates.copy()
            for level in levels: self.__levels[level.name] = level
            for ach in achievement_list: self.__achievements[ach.name] = ach
            for name, date_time2 in unlocks: self.__unlocks[name] = date_time2

        if self.__is_fresh_save:
            NewSaveData._init_fresh_save(self)

    @property
    def is_fresh_save(self) -> bool:
        return self.__is_fresh_save

    @property
    def num_quantum_fusers(self) -> int:
        return self.__inventory.quantum_fuser

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

    def _complete_map(self, name: str, duration: int, date_time: Optional[datetime] = None, score: int = -1) \
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

            # save the Instructions corresponding to the gate types that were unlocked
            for gate_type in LevelInfo.get_level_completion_unlocked_gates(level_data.name, self.check_level):
                self.__gates.append(InstructionManager.from_type(gate_type))

        return level_data

    def complete_level(self, name: str, duration: int, date_time: Optional[datetime] = None, score: int = -1) \
            -> LevelData:
        return self._complete_map(name, duration, date_time, score)

    def complete_expedition(self, name: str, duration: int, difficulty_level: int, gate_type: GateType,
                            date_time: Optional[datetime] = None, score: int = -1) \
            -> LevelData:
        level_data = self._complete_map(name, duration, date_time, score)
        self.add_to_achievement(Achievement.CompletedExpedition, difficulty_level)
        self.__gates.append(InstructionManager.from_type(gate_type))
        self.__inventory.quantum_fuser += 1     # todo: should an expedition's Boss always give 1 QuantumFuser?
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

    def get_progress(self, achievement: str) -> Tuple[float, float]:
        if achievement in self.__achievements:
            ach = self.__achievements[achievement]
            return ach.score, ach.done_score
        return -1, -1

    def get_gates(self) -> List[Instruction]:
        return [gate.copy() for gate in self.__gates]

    def get_original_gates(self) -> List[Instruction]:
        return self.__gates.copy()

    def decompose(self, gates: Union[Instruction, List[Instruction]]) -> bool:
        if isinstance(gates, Instruction):
            if gates in self.__gates:
                self.__gates.remove(gates)
                self.__inventory.quantum_fuser += 1     # decomposing a gate gives 1 QuantumFuser
                self.__has_unsaved_changes = True
                return True
        else:
            # check if all gates we want to decompose are indeed among our gates
            if False not in [gate in self.__gates for gate in gates]:
                for gate in gates: self.__gates.remove(gate)
                self.__inventory.quantum_fuser += len(gates)
                self.__has_unsaved_changes = True
                return True
        return False

    def add_gate(self, gate: Instruction):
        # copy and reset the new gate
        gate = gate.copy()
        gate.reset()
        self.__gates.append(gate)
        self.__has_unsaved_changes = True

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

        text += f"{_SaveDataGenerator.inventory_header()}\n"
        text += f"{self.__inventory.to_string()}\n"

        text += f"{_SaveDataGenerator.gates_header()}\n"
        if len(self.__gates) > 0:
            text += _SaveDataGenerator.gate_separator().join([gate.to_save_string() for gate in self.__gates])
            text += "\n"

        text += f"{_SaveDataGenerator.levels_header()}\n"
        for level in self.__levels.values():
            text += f"{level.name} @ {datetime2str(level.date_time)} {level.duration} " \
                    f"{_SaveDataGenerator.duration_unit()} Score = {level.score}\n"

        text += f"{_SaveDataGenerator.unlocks_header()}\n"
        for unlock in self.__unlocks:
            text += f"{unlock} @ {datetime2str(self.__unlocks[unlock])}\n"

        text += f"{_SaveDataGenerator.achievements_header()}\n"
        for ach in self.__achievements.values():
            text += f"{ach.name} @ {datetime2str(ach.date_time)} Score = {ach.score} out of {ach.done_score}\n"

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
            self.__date_time = cur_datetime()  # update datetime of the latest save (=now)
            data = self._encode(self.to_string())
            if is_auto_save:
                PathConfig.write_auto_save(data)
            else:
                PathConfig.new_save_file(data)
                self.__has_unsaved_changes = False  # only change flag if it was a manual (i.e., no auto) save
            return True, CommonInfos.SavingSuccessful

        except Exception as ex:
            Logger.instance().error(f"Exception occurred during saving: {ex}", False, False)
            return False, CommonInfos.SavingFailed

    def compare(self, other: "NewSaveData") -> Tuple[List[Instruction], List[str], List[Unlocks], List[Achievement]]:
        """
        Args:
            other: the NewSaveData to compare with
        Returns:
            List of Instructions, level names, Unlocks and Achievement other has and self does not
        """
        other_gates = other.__gates.copy()
        self_gates = self.__gates.copy()
        gate_diff = []
        # find gates that are in other_gates but not in self_gates
        for gate in other_gates:
            if gate in self_gates:
                # remove gate from self_gates, so we can also check if the number of specific gate_types match
                self_gates.remove(gate)
                continue
            gate_diff.append(gate.copy())   # append a copy so the outside cannot manipulate the actual gate

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
    class Inventory:
        @staticmethod
        def default() -> "_SaveDataGenerator.Inventory":
            return _SaveDataGenerator.Inventory(0)

        def __init__(self, quantum_fuser: int):
            # for every gate we want to fuse, we need to pay one quantum fuser
            # e.g., fusing HGate@q1 with CXGate@q1q0 costs two quantum fuser
            self.quantum_fuser = quantum_fuser

        def to_string(self) -> str:
            return f"{_SaveDataGenerator.quantum_fuser()} {self.quantum_fuser}"

        def __str__(self):
            return f"Inventory({self.quantum_fuser})"

    @staticmethod
    def header() -> str:
        return "Qrogue<"

    @staticmethod
    def inventory_header() -> str:
        return "[INVENTORY]"

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
    def quantum_fuser() -> str:
        return "QuantumFuser"

    @staticmethod
    def gate_separator() -> str:
        return ";"  # the general separator can be used to separate gates for improved readability

    def __init__(self):
        self.__knowledge_mode = None
        self.__highest_knowledge_level = -1

    def load(self, file_data: str) -> Tuple[datetime, Inventory, List[Instruction], List[LevelData],
             List[Tuple[str, datetime]], List[Achievement]]:
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

    def visitInventory(self, ctx: SaveDataParser.InventoryContext) -> Inventory:
        quantum_fuser = self.visitValue(ctx.value())
        return _SaveDataGenerator.Inventory(quantum_fuser)

    #####################################

    def visitBackground_gate(self, ctx: SaveDataParser.Background_gateContext) -> Optional[Instruction]:
        gate = InstructionManager.instruction_from_name(ctx.NAME_STD().getText())
        if gate is None: return None

        qubits = [self.visitValue(val) for val in ctx.value()]
        gate.setup(qubits)
        return gate

    def visitCombined_gate(self, ctx: SaveDataParser.Combined_gateContext) -> Optional[Instruction]:
        name = ctx.TEXT().getText()[1:-1]   # remove leading and trailing quotation mark
        num_of_qubits = self.visitValue(ctx.value())

        gate_list = [self.visitBackground_gate(bg_ctx) for bg_ctx in ctx.background_gate()]
        if None in gate_list:
            Logger.instance().error(f"Failed to load a background gate of CombinedGate \"{name}\"")
            return None
        return CombinedGate(gate_list, num_of_qubits, name)

    def visitGate(self, ctx: SaveDataParser.GateContext) -> Optional[Instruction]:
        if ctx.combined_gate() is None:
            return InstructionManager.instruction_from_name(ctx.NAME_STD().getText())
        else:
            return self.visitCombined_gate(ctx.combined_gate())

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
        level_data = LevelData(name, date_time, duration, score)

        # find out which knowledge mode the highest level has
        km, ln = level_data.knowledge_mode, level_data.level_num
        if self.__knowledge_mode is None:
            # initialize knowledge mode regardless (could still be null if level has no knowledge mode)
            self.__knowledge_mode = km
        elif km is not None and ln is not None:
            # only set it if km and ln are not None (if km is None, we don't have any information anyways, and if ln is
            #  None we cannot compare it to the highest level anyways)
            if km != self.__knowledge_mode and ln is not None and ln > self.__highest_knowledge_level:
                # set new value for knowledge mode if km differs and comes from a higher level
                self.__knowledge_mode = km
            # store new highest level regardless of whether knowledge mode changed (if it did, we already know that ln
            #  is greater than the current highest level, else we stay in the same mode and also want to update highest
            #  level)
            self.__highest_knowledge_level = max(self.__highest_knowledge_level, ln)

        return level_data

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

    def visitStart(self, ctx: SaveDataParser.StartContext) -> Tuple[datetime, Inventory, List[Instruction],
            List[LevelData], List[Tuple[str, datetime]], List[Achievement]]:
        date_time = self.visitDate_time(ctx.date_time())

        if ctx.inventory():
            inventory = self.visitInventory(ctx.inventory())
        else:
            inventory = _SaveDataGenerator.Inventory.default()

        gates = self.visitGates(ctx.gates())
        levels = self.visitLevels(ctx.levels())
        unlocks = self.visitUnlocks(ctx.unlocks())
        achievement_list = self.visitAchievements(ctx.achievements())

        if not GameplayConfig.set_knowledge_mode(self.__knowledge_mode):
            Logger.instance().warn(f"Failed to set knowledge mode to \"{self.__knowledge_mode}\"", from_pycui=False)

        return date_time, inventory, gates, levels, unlocks, achievement_list
