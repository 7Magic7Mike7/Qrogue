import os
import sys

from qrogue.game.logic.actors import Player
from qrogue.game.world.dungeon_generator import QrogueWorldGenerator, QrogueLevelGenerator
from qrogue.game.world.map import CallbackPack
from qrogue.management import NewSaveData
from qrogue.test import test_util

BASE_PATH = os.path.join("D:\\", "Documents", "Studium", "Master", "3. Semester", "Qrogue", "QrogueData", "data")

# todo: rewrite tests

def generation_test(file_name: str, world: bool = False):
    save_data = NewSaveData()   # todo: use lambdas instead of real functions since the functions do not matter?
    check_achievement = save_data.check_achievement
    trigger_event = save_data.trigger_event
    if world:
        player = Player()
        generator = QrogueWorldGenerator(7, player, check_achievement, trigger_event, test_util.load_map,
                                         test_util.message_popup)
    else:
        generator = QrogueLevelGenerator(7, check_achievement, trigger_event, test_util.load_map,
                                         test_util.message_popup, CallbackPack.dummy())
    map, success = generator.generate(file_name, True)
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
user_data_path = sys.argv[1]
test_util.init_singletons(include_config=True, custom_user_path=user_data_path)

file_name = "l1v1"
generation_test(file_name, world=False)
