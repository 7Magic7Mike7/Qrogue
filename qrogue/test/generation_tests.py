import unittest
from typing import List, Tuple, Optional

import test_util
from qrogue.game.logic.actors.controllables.robot import RoboProperties
from qrogue.game.logic.collectibles import instruction as gates
from qrogue.game.world import tiles
from qrogue.game.world.dungeon_generator import DungeonGenerator
from qrogue.game.world.dungeon_generator.random_generator import RandomLayoutGenerator, ExpeditionGenerator
from qrogue.game.world.dungeon_generator.wave_function_collapse import WFCManager
from qrogue.game.world.map import Room, Hallway, CallbackPack, ExpeditionMap
from qrogue.game.world.navigation import Direction, Coordinate
from qrogue.management import MapManager
from qrogue.util import CheatConfig, StvDifficulty, MapConfig


class LayoutGenTestCase(test_util.SingletonSetupTestCase):
    def test_single_seed(self):
        seed = 297
        map_gen = RandomLayoutGenerator(DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)
        self.assertTrue(map_gen.generate(seed, validate=True, debug=False), f"Failed to generate: {map_gen}")
        self._print(map_gen)

    def test_layout(self):
        # took ~10 seconds for seeds 50_000 to 55_000, succeeded
        # ~3:20 min for 0 to 100_000, succeeded
        start_seed = 50000
        end_seed = 50005
        failing_seeds: List[int] = []
        wrong_specials_seeds = []

        i = 0
        for seed in range(start_seed, end_seed):
            if i % 5000 == 0:
                self._print(f"Run {i + 1}): seed = {seed}")
            map_gen = RandomLayoutGenerator(DungeonGenerator.WIDTH, DungeonGenerator.HEIGHT)
            if not map_gen.generate(seed, validate=True, debug=False):
                failing_seeds.append(seed)
                self._print(f"Invalid layout: {map_gen}")
            i += 1

        if len(failing_seeds) > 0:
            self._print("Failing Seeds:")
            self._print(failing_seeds)
            self.assertGreater(len(failing_seeds), 0, "Layout for some seeds failed!")

        if len(wrong_specials_seeds) > 0:
            self._print("Wrong SpecialRooms in Seeds: ")
            self._print(wrong_specials_seeds)
            self._print()


class LevelGenTestCase(test_util.SingletonSetupTestCase):
    @staticmethod
    def __create_expedition_generator() -> ExpeditionGenerator:
        wfc_manager = WFCManager()
        wfc_manager.load()
        return ExpeditionGenerator(wfc_manager, lambda s: True, lambda s: None, lambda: None, lambda: [HGate()],
                                        CallbackPack.dummy())

    def test_single_seed(self):
        CheatConfig.use_cheat("Illuminati")
        robo_props = test_util.DummyRoboProps()
        diff_code = "1" * StvDifficulty.degrees_of_freedom()
        difficulty = StvDifficulty.from_difficulty_code(diff_code, robo_props.num_of_qubits, robo_props.circuit_space)

        generator = self.__create_expedition_generator()
        map_seed = 297
        puzzle_seed = 7
        map_, success = generator.generate(map_seed, (robo_props, difficulty, puzzle_seed))
        self.assertTrue(success, "Failed to generate.")
        self._print(map_)

    def test_expedition(self):
        # ~1min per 666 seeds
        # 1_000 seeds per ~1.5min
        start_seed = 0
        end_seed = 5
        failing_seeds = []

        robo_props = test_util.DummyRoboProps()
        diff_code = "1" * StvDifficulty.degrees_of_freedom()
        difficulty = StvDifficulty.from_difficulty_code(diff_code, robo_props.num_of_qubits, robo_props.circuit_space)

        generator = self.__create_expedition_generator()
        puzzle_seed = 7
        for i, map_seed in enumerate(range(start_seed, end_seed)):
            if i % 1000 == 0:
                self._print(f"Run {i + 1}): map_seed = {map_seed}")
            map_, success = generator.generate(map_seed, (robo_props, difficulty, puzzle_seed))
            if not success:
                failing_seeds.append((generator, map_seed))
                self._print(f"Failed for map_seed = {map_seed}")

        if len(failing_seeds) > 0:
            self._print("Failing Seeds:", force=True)
            seeds = []
            for mg, map_seed in failing_seeds:
                self._print(mg, force=True)
                seeds.append(map_seed)
            self._print(seeds, force=True)
            self._print(force=True)
            self.assertTrue(False, "Some seeds failed!")

    def test_room_correction(self):
        tile_list = Room.dic_to_tile_list({
            Coordinate(3, 0): tiles.Obstacle(),
            Coordinate(4, 0): tiles.Obstacle(),

            Coordinate(0, 1): tiles.Obstacle(),
            Coordinate(1, 1): tiles.Obstacle(),
            Coordinate(2, 1): tiles.Obstacle(),
            Coordinate(3, 1): tiles.Obstacle(),
            Coordinate(4, 1): tiles.Obstacle(),

            Coordinate(0, 2): tiles.Obstacle(),
            Coordinate(1, 2): tiles.Obstacle(),
            Coordinate(2, 2): tiles.Obstacle(),

            Coordinate(1, 3): tiles.Obstacle(),
            Coordinate(2, 3): tiles.Obstacle(),
            Coordinate(3, 3): tiles.Obstacle(),

            Coordinate(2, 4): tiles.Obstacle(),
            Coordinate(4, 4): tiles.Obstacle(),
        })
        hallways = {
            Direction.North: Hallway(tiles.Door(Direction.North)),
            Direction.South: Hallway(tiles.Door(Direction.South)),
        }
        """
        print("Before correction:")
        before_room = DefinedWildRoom(tile_list, north_hallway=hallways[Direction.North], south_hallway=hallways[Direction.South])
        print(before_room.to_string())
        """
        num_of_changes = ExpeditionGenerator.correct_tile_list(tile_list, hallways)
        self.assertGreater(num_of_changes, -1, "Could not correct the given tile_list!")
        """
        print("After correction:")
        after_room = DefinedWildRoom(tile_list, north_hallway=hallways[Direction.North],
                                     south_hallway=hallways[Direction.South])
        print(after_room.to_string())
        """

    def test_astar(self):
        tile_dic = {
            Coordinate(0, 2): tiles.Obstacle(),
            Coordinate(1, 2): tiles.Obstacle(),
            Coordinate(2, 2): tiles.Obstacle(),
            Coordinate(3, 2): tiles.Obstacle(),
            Coordinate(4, 2): tiles.Obstacle(),
            Coordinate(4, 3): tiles.Obstacle(),
        }
        tile_list = Room.dic_to_tile_list(tile_dic)

        def get_weight(pos: Coordinate) -> int:
            if pos in tile_dic:
                return 2
            if pos.x == 2 and pos.y in [0, 4]:
                # one of the entrances
                return 0
            return 1

        visited = set()
        success, tiles_to_remove = ExpeditionGenerator.path_search(tile_list,
                                                                   lambda t: t.code == tiles.TileCode.Obstacle,
                                                                   get_weight, visited, target_pos=Coordinate(2, 4),
                                                                   cur_pos=Coordinate(2, 0))
        self.assertTrue(success, "Didn't find a removable tile.")
        """
        print([str(elem) for elem in tiles_to_remove])
        visited = list(visited)
        visited.sort(key=lambda c: c.x + c.y * 10)
        print(f"Visited: {[str(elem) for elem in visited]}")
        """

    def test_expedition_parameters(self):
        prefix = MapConfig.expedition_map_prefix()
        dc_sep = MapConfig.diff_code_separator()
        ps_sep = MapConfig.puzzle_seed_separator()
        expeditions = [
            (f"{prefix}12345", None),   # only map_seed provided
            (f"{prefix}12{ps_sep}12345", None),    # no difficulty, puzzle and map seed in name
            (f"{prefix}2", 12345),  # difficulty in name, separate map seed
            (f"{prefix}2{dc_sep}12", 12345),  # difficulty and puzzle seed in name, separate map seed
            (f"{prefix}2{dc_sep}12{ps_sep}12345", None),    # everything in name
        ]
        expedition_progress = 1

        expected_values: List[Tuple[str, int, Optional[int]]] = [
            ("0", 12345, None),
            ("0", 12345, 12),
            ("2", 12345, None),
            ("2", 12345, 12),
            ("2", 12345, 12),
        ]
        for i, data in enumerate(expeditions):
            map_name, map_seed = data
            r_diff_code, r_map_seed, r_puzzle_seed = MapManager.parse_expedition_parameters(map_name, map_seed,
                                                                                            expedition_progress)
            e_diff_code, e_map_seed, e_puzzle_seed = expected_values[i]
            self.assertEqual(e_diff_code, r_diff_code, f"Unexpected diff_code! @{i}")
            self.assertEqual(e_map_seed, r_map_seed, f"Unexpected map_seed! @{i}")
            self.assertEqual(e_puzzle_seed, r_puzzle_seed, f"Unexpected puzzle_seed! @{i}")

    def test_robo_props(self):
        generator = self.__create_expedition_generator()
        difficulty = StvDifficulty.from_difficulty_code("2")

        robo_props = RoboProperties(2, 5, [gates.XGate()])
        _, success = generator.generate(map_seed=7, data=(robo_props, difficulty, 7))
        self.assertFalse(success, "Failed to recognize illegal gates for the given difficulty")

        robo_props = RoboProperties(2, 5, [gates.XGate(), gates.SGate(), gates.HGate(), gates.RYGate()])
        _, success = generator.generate(map_seed=7, data=(robo_props, difficulty, 7))
        self.assertTrue(success, "Failed to recognize legal gates for the given difficulty")

    def test_random_gate_subset_selection(self):
        difficulty = StvDifficulty.from_difficulty_code("2")
        # this list of Instruction over-fulfills the criteria
        available_gates = [gates.XGate(), gates.XGate(), gates.SGate(), gates.HGate(), gates.HGate(), gates.RYGate(),
                           gates.RZGate()]
        picked_gates = ExpeditionGenerator.get_random_gates(available_gates.copy(), difficulty, 7)
        val_code, val_data = ExpeditionMap.validate_gates_for_difficulty(difficulty, picked_gates)
        self.assertEqual(0, val_code, f"Failed to pick a valid subset: code={val_code}, data={val_data}")

        # this list of Instructions exactly-fulfills the criteria
        available_gates = [gates.SGate(), gates.SGate(), gates.HGate(), gates.RYGate()]
        picked_gates = ExpeditionGenerator.get_random_gates(available_gates.copy(), difficulty, 7)
        val_code, val_data = ExpeditionMap.validate_gates_for_difficulty(difficulty, picked_gates)
        self.assertEqual(0, val_code, f"Failed to pick a valid subset: code={val_code}, data={val_data}")

        # this list of Instructions exactly-fulfills the unique-criteria but has many dupes to choose from
        available_gates = [gates.HGate(), gates.RYGate()] + [gates.SGate()] * 12
        picked_gates = ExpeditionGenerator.get_random_gates(available_gates.copy(), difficulty, 7)
        val_code, val_data = ExpeditionMap.validate_gates_for_difficulty(difficulty, picked_gates)
        self.assertEqual(0, val_code, f"Failed to pick a valid subset: code={val_code}, data={val_data}")


if __name__ == '__main__':
    unittest.main()
