import time

from qrogue.game.achievements import AchievementManager
from qrogue.game.actors.robot import TestBot
from qrogue.game.callbacks import CallbackPack
from qrogue.game.map.generator import RandomLayoutGenerator, RandomDungeonGenerator
from qrogue.game.map.tiles import *
from qrogue.util.config import Config


def start_gp(args):
    print("started game")


def start_fight(robot: Robot, enemy: Enemy, direction: Direction):
    pass


def start_boss_fight(robot: Robot, boss: Boss, direction: Direction):
    pass


def load_map(map_name: str):
    print(f"Load map: {map_name}")


def layout_test():
    min_duration = (1, -1)
    duration_sum = 0
    max_duration = (0, -1)
    start_seed = 0#50000
    end_seed = 100000
    failing_seeds = []
    wrong_specials_seeds = []
    # seeds that "look weird": [603]
    # [47765, 58456, 65084, 74241, 85971]
    seeds = list(range(start_seed, end_seed))       #[629, 774, 991, 3280, 5326, 6062, 7289, 8588, 8604, ]
    num_of_seeds = len(seeds)
    i = 0
    for seed in seeds:
        if i % 50000 == 0:
            print(f"Run {i + 1}): seed = {seed}")
        mapgen = RandomLayoutGenerator(seed, RandomDungeonGenerator.WIDTH, RandomDungeonGenerator.HEIGHT)
        now_time = time.time()
        if not mapgen.generate(debug=False):
            failing_seeds.append(mapgen)
        duration = time.time() - now_time
        duration_sum += duration
        if duration < min_duration[0]:
            min_duration = (duration, seed)
        elif duration > max_duration[0]:
            max_duration = (duration, seed)
        if not mapgen.check_special_rooms():
            wrong_specials_seeds.append(seed)
        i += 1
        #print(mapgen)
    print(f"Average time needed for generating a map: {duration_sum / num_of_seeds} seconds")
    print(f"Fastest generation time = {min_duration[0]} for seed = {min_duration[1]}")
    print(f"Longest generation time = {max_duration[0]} for seed = {max_duration[1]}")
    print()
    print("Failing Seeds:")
    seeds = []
    for mg in failing_seeds:
        seeds.append(mg.seed)
    print(seeds)
    print("Wrong SpecialRooms in Seeds: ")
    print(wrong_specials_seeds)
    print()

    for mg in failing_seeds:
        mapgen = RandomLayoutGenerator(mg.seed, RandomDungeonGenerator.WIDTH, RandomDungeonGenerator.HEIGHT)
        mapgen.generate(debug=True)


def dungeon_test(robot: Robot, cbp: CallbackPack):
    min_duration = (1, -1)
    duration_sum = 0
    max_duration = (0, -1)
    start_seed = 0
    end_seed = 50000
    failing_seeds = []
    seeds = list(range(start_seed, end_seed))
    num_of_seeds = len(seeds)
    i = -1
    for seed in seeds:
        i += 1
        if i % 5000 == 0:
            print(f"Run {i + 1}): seed = {seed}")
        generator = RandomDungeonGenerator(seed, load_map, AchievementManager())
        start_time = time.time()
        map, success = generator.generate(cbp, robot)
        if not success:
            failing_seeds.append((generator, seed))
            print(f"Failed for seed = {seed}")
        duration = time.time() - start_time
        duration_sum += duration
        if duration < min_duration[0]:
            min_duration = (duration, seed)
        elif duration > max_duration[0]:
            max_duration = (duration, seed)
    print(f"Average time needed for generating a map: {duration_sum / num_of_seeds} seconds")
    print(f"Fastest generation time = {min_duration[0]} for seed = {min_duration[1]}")
    print(f"Longest generation time = {max_duration[0]} for seed = {max_duration[1]}")
    print()
    print("Failing Seeds:")
    seeds = []
    for mg, seed in failing_seeds:
        print(mg)
        seeds.append(seed)
    print(seeds)
    print()


return_code = Config.load()
if return_code != 0:
    print(f"Error #{return_code}")

RandomManager(7)    # initialize RandomManager
p = TestBot()
c = CallbackPack(start_gp, start_fight, start_boss_fight, start_fight, start_fight)

layout_test()
dungeon_test(p, c)
