import unittest

from qrogue.management import NewSaveData
from qrogue.test import test_util
from qrogue.util.achievements import Unlocks


class SaveDataOverhaulTests(test_util.SingletonSetupTestCase):
    def test_fresh_save(self):
        self.set_printing(False)

        new_save_data = NewSaveData.empty_save_state()
        new_save = NewSaveData(new_save_data)
        self.assertEqual(new_save_data, new_save.to_string())

    def test_filled_save(self):
        self.set_printing(False)

        new_save_data = "\n".join([
            "Qrogue<",
            "19d01m2024y 04:16:55",
            "[INVENTORY]",
            "QuantumFuser 0",
            "[GATES]",
            "X;H;CX",
            "[LEVELS]",
            "l0k0v0 @ 19d01m2024y 02:23:23 1234 seconds Score = 988",
            "[UNLOCKS]",
            "Continue @ 12d02m2034y 04:12:00",
            "[ACHIEVEMENTS]",
            "Racer @ 12d02m2034y 04:12:22 Score = 20 out of 100",
            ">Qrogue",
            "",
        ])
        new_save = NewSaveData(new_save_data)
        self.assertEqual(new_save_data, new_save.to_string())

    def test_generated_save(self):
        self.set_printing(False)

        new_save_data = "\n".join([
            "Qrogue<",
            "14d03m2024y 15:47:37",
            "[INVENTORY]",
            "QuantumFuser 0",
            "[GATES]",
            "[LEVELS]",
            "l0k0v0 @ 14d03m2024y 15:49:03 74 seconds Score = 0",
            "[UNLOCKS]",
            "gateremove @ 14d03m2024y 15:47:39",
            "[ACHIEVEMENTS]",
            "CompletedExpedition @ 14d03m2024y 15:47:39 Score = 1 out of 100",
            "EnteredPauseMenu @ 14d03m2024y 15:49:34 Score = 1 out of 1",
            ">Qrogue",
            "",
        ])
        new_save = NewSaveData(new_save_data)
        self.assertEqual(new_save_data, new_save.to_string())

    def test_unlocks(self):
        save_data = NewSaveData(NewSaveData.empty_save_state())
        save_data.unlock(Unlocks.ShowEquation)
        self.assertTrue(save_data.check_unlocks(Unlocks.ShowEquation))


class SaveEncodingTestCases(test_util.SingletonSetupTestCase):
    class _TestSaveData(NewSaveData):
        def test_encode(self) -> str:
            return super()._encode(self.to_string(), force=True)

        def test_decode(self) -> str:
            return super()._decode(self.to_string())

    def test_encoding(self):
        new_save_data = "\n".join([
            "Qrogue<",
            "19d01m2024y 04:16:55",
            "[INVENTORY]",
            "QuantumFuser 0",
            "[GATES]",
            "X;H;CX",
            "[LEVELS]",
            "l0k0v0 @ 19d01m2024y 02:23:23 1234 seconds Score = 988",
            "[UNLOCKS]",
            "Continue @ 12d02m2034y 04:12:00",
            "[ACHIEVEMENTS]",
            "Racer @ 12d02m2034y 04:12:22 Score = 20 out of 100",
            ">Qrogue",
        ])
        new_sd = NewSaveData(new_save_data)
        enc_sd = self._TestSaveData(new_save_data)

        # sanity check to make sure the test class behaves as expected
        self.assertEqual(new_sd.to_string(), enc_sd.to_string())

        # check if decoding results in the same save-state
        enc_sd2 = self._TestSaveData(enc_sd.test_encode())
        self.assertEqual(enc_sd.to_string(), enc_sd2.test_decode())

        # check if encoding results in the same save-state
        new_sd2 = NewSaveData(enc_sd.test_encode())
        self.assertEqual(new_sd.to_string(), new_sd2.to_string())


if __name__ == '__main__':
    # warnings regarding *Failed to set knowledge mode to "None"* can be ignored
    unittest.main()
