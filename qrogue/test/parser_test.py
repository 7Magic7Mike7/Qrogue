import os

from qrogue.dungeon_editor.dungeon_parser.QrogueLevelGenerator import QrogueLevelGenerator
from qrogue.dungeon_editor.world_parser.QrogueWorldGenerator import QrogueWorldGenerator
from qrogue.game.world.map import CallbackPack
from qrogue.management.save_data import SaveData
from qrogue.util.config import FileTypes
from qrogue.util.my_random import RandomManager


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
    SaveData()
    player = SaveData.instance().player
    check_achievement = SaveData.instance().achievement_manager.check_achievement
    trigger_event = SaveData.instance().achievement_manager.trigger_level_event
    if world:
        generator = QrogueWorldGenerator(7, player, check_achievement, load_level)
    else:
        generator = QrogueLevelGenerator(7, check_achievement, trigger_event, load_level)
    map, success = generator.generate(file_name, False)
    if success:
        print(map)
    debugging = True


def general_python_test():
    def print_i(i: int):
        print(i)

    size = 10
    indices = list(range(size))
    lambdas = [lambda : print_i(i) for i in range(size)]
    lambdas += [lambda : print_i(size)]
    size += 1
    lambdas += [lambda : print_i(size)]
    lambdas += [lambda : print_i(size+1)]

    lambdas += [lambda : print_i(-11111111)]

    indices = list(range(size))
    lambdas += [lambda : print_i(indices[0])]
    lambdas += [lambda : print_i(indices[1])]
    lambdas += [lambda : print_i(indices[2])]
    lambdas += [lambda : print_i(indices[3])]
    lambdas += [lambda : print_i(indices[4])]
    lambdas += [lambda : print_i(indices[5])]
    lambdas += [lambda : print_i(indices[6])]

    #for l in lambdas:
    #    l()


#general_python_test()
RandomManager(7)    # needs to be initialized
CallbackPack(start_gp, start_fight, start_fight, start_fight, start_fight)

file_name = "l1v1"
path = os.path.join(BASE_PATH, "dungeons", file_name)
generation_test(path, world=False)
