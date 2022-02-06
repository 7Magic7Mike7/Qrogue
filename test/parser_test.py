import os

from dungeon_editor.parser.QrogueGrammarListener import TextBasedDungeonGenerator
from game.actors.robot import TestBot, Robot
from game.callbacks import CallbackPack
from util.config import FileTypes
from util.my_random import RandomManager, MyRandom


def start_gp(map):
    print("started game")


def start_fight(**kwargs):
    pass


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


def generation_test(rm: MyRandom, robot: Robot, text: str):
    cbp = CallbackPack(start_gp, start_fight, start_fight, start_fight, start_fight)

    generator = TextBasedDungeonGenerator(7)
    map, success = generator.generate(robot, cbp, text)
    debugging = True



rm = RandomManager(11)
t = TestBot(7)
data = read_dungeon("tutorial")
generation_test(rm, t, data)
