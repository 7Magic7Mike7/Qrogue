import unittest

from qrogue.util import RandomManager


class MyRandomTests(unittest.TestCase):
    def test_get(self):
        rm1 = RandomManager.create_new(7)
        rm2 = RandomManager.create_new(7)
        rm3 = RandomManager.create_new(70)

        n = 1_000_000
        counter = 0
        for _ in range(n):
            val1, val2, val3 = rm1.get(), rm2.get(), rm3.get()
            self.assertEqual(val1, val2, f"Identical seeds produced different values: {val1} != {val2}")
            counter += val1 == val3
        self.assertGreater(n / 10.0, counter, f"Seeds are too similar: {100 * counter / n:2f}% of values were equal!")

    def test_shuffle(self):
        rm1 = RandomManager.create_new(7)
        rm2 = RandomManager.create_new(7)
        rm3 = RandomManager.create_new(70)

        n = 250
        sequence = list(range(n))
        seq1, seq2, seq3 = sequence.copy(), sequence.copy(), sequence.copy()

        rm1.shuffle_list(seq1)
        rm2.shuffle_list(seq2)
        rm3.shuffle_list(seq3)

        self.assertEqual(seq1, seq2, f"Identical seeds produced different shuffle: {seq1} != {seq2}")
        self.assertNotEqual(seq1, seq3, f"Different seeds produced identical shuffle: {seq1} == {seq3}")


if __name__ == '__main__':
    unittest.main()
