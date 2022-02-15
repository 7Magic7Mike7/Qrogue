import os

from dungeon_editor.dungeon_parser.QrogueGrammarListener import TextBasedDungeonGenerator
from dungeon_editor.world_parser.QrogueWorldGenerator import QrogueWorldGenerator
from game.achievements import AchievementManager
from game.callbacks import CallbackPack
from game.save_data import SaveData
from util.config import FileTypes
from util.my_random import RandomManager, MyRandom


def start_gp(args):
    print("started game")


def start_fight(**kwargs):
    pass


def load_level(level: str):
    print(f"Pseudo-loading level: {level}")


BASE_PATH = os.path.join("D:\\", "Documents", "Studium", "Master", "3. Semester", "Qrogue", "QrogueData", "data")


def read_dungeon(file_name: str) -> str:
    if not file_name.endswith(FileTypes.Dungeon.value):
        file_name += FileTypes.Dungeon.value
    path = os.path.join(BASE_PATH, "dungeons", file_name)
    if os.path.exists(path):
        with open(path, "r") as file:
            content = file.read()
        return content
    else:
        raise FileNotFoundError(f"File \"{file_name}\" could not be found!")


def read_world(file_name: str) -> str:
    if not file_name.endswith(FileTypes.World.value):
        file_name += FileTypes.World.value
    path = os.path.join(BASE_PATH, "dungeons", file_name)
    if os.path.exists(path):
        with open(path, "r") as file:
            content = file.read()
        return content
    else:
        raise FileNotFoundError(f"File \"{file_name}\" could not be found!")


def generation_test(file_name: str, world: bool = False):
    cbp = CallbackPack(start_gp, start_fight, start_fight, start_fight, start_fight)

    if world:
        generator = QrogueWorldGenerator(7, SaveData(cbp), load_level)
    else:
        generator = TextBasedDungeonGenerator(7, load_level, AchievementManager())
    map, success = generator.generate(file_name, False)
    if success:
        print(map)
    debugging = True


RandomManager(7)    # needs to be initialized
file_name = "worlds"
path = os.path.join(BASE_PATH, "dungeons", file_name)
generation_test(path, world=True)
