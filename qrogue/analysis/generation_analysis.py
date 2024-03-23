import time
from typing import Optional, Any

from qrogue.game.logic.actors.controllables import BaseBot
from qrogue.game.world.dungeon_generator import DungeonGenerator
from qrogue.game.world.dungeon_generator.random_generator import RandomLayoutGenerator, ExpeditionGenerator
from qrogue.game.world.map import CallbackPack
from qrogue.test import test_util


printing = True


def __print(msg: Optional[Any] = None, force: bool = False):
    if printing or force:
        print(msg)


def test_layout():
    min_duration = (1, -1)
    duration_sum = 0
    max_duration = (0, -1)

    start_seed = 50000
    end_seed = 55000
    failing_seeds = []
    wrong_specials_seeds = []
    # seeds that "look weird": [603]
    # [47765, 58456, 65084, 74241, 85971]
    # [629, 774, 991, 3280, 5326, 6062, 7289, 8588, 8604, ]

    i = 0
    for seed in range(start_seed, end_seed):
        if i % 5000 == 0:
            __print(f"Run {i + 1}): seed = {seed}")
        map_gen = RandomLayoutGenerator(seed, DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)

        now_time = time.time()
        if not map_gen.generate(debug=False):
            failing_seeds.append(map_gen)
        duration = time.time() - now_time

        duration_sum += duration
        if duration < min_duration[0]:
            min_duration = (duration, seed)
        elif duration > max_duration[0]:
            max_duration = (duration, seed)
        i += 1

    __print(f"Average time needed for generating a map: {duration_sum / (end_seed - start_seed)} seconds")
    __print(f"Fastest generation time = {min_duration[0]} for seed = {min_duration[1]}")
    __print(f"Longest generation time = {max_duration[0]} for seed = {max_duration[1]}")
    __print()

    __print("Failing Seeds:")
    __print([str(mg.seed) for mg in failing_seeds])
    __print()
    __print("Wrong SpecialRooms in Seeds: ")
    __print(wrong_specials_seeds)
    __print()

    for mg in failing_seeds:
        map_gen = RandomLayoutGenerator(mg.seed, DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)
        map_gen.generate(debug=True)


def test_dungeon():
    min_duration = (1, -1)
    duration_sum = 0
    max_duration = (0, -1)

    start_seed = 0
    end_seed = 100
    failing_seeds = []

    robot = BaseBot(lambda: None)
    i = 0
    for seed in range(start_seed, end_seed):
        if i % 1000 == 0:
            __print(f"Run {i + 1}): seed = {seed}")
        generator = ExpeditionGenerator(seed, lambda s: True, lambda s: None, lambda s: None, CallbackPack.dummy())

        start_time = time.time()
        map_, success = generator.generate(robot)
        duration = time.time() - start_time
        duration_sum += duration

        if not success:
            failing_seeds.append((generator, seed))
            __print(f"Failed for seed = {seed}")

        if duration < min_duration[0]:
            min_duration = (duration, seed)
        elif duration > max_duration[0]:
            max_duration = (duration, seed)

        i += 1

    # last result: 0.3 seconds per (wfc) map on average
    __print(f"Average time needed for generating a map: {duration_sum / (end_seed - start_seed)} seconds")
    __print(f"Fastest generation time = {min_duration[0]} for seed = {min_duration[1]}")
    __print(f"Longest generation time = {max_duration[0]} for seed = {max_duration[1]}")
    __print()

    if len(failing_seeds) > 0:
        __print("Failing Seeds:", force=True)
        seeds = []
        for mg, seed in failing_seeds:
            __print(mg, force=True)
            seeds.append(seed)
        __print(seeds, force=True)
        __print(force=True)


if __name__ == '__main__':
    if test_util.init_singletons(include_config=True):
        #SaveData()
        test_layout()
        print()
        print("#####################################################################################################")
        print()
        test_dungeon()
    else:
        raise Exception("Could not initialize singletons")
