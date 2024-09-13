import unittest

from qrogue.test import SaveDataOverhaulTests
from qrogue.test import MyOptionsTest, ControlTests, FusionTestCase, LayoutGenTestCase, LevelGenTestCase, \
    MyPopupTests, ManuelPuzzleGenTestCase, MyRandomTests, ValidationTests, \
    WFCGeneratorTestCases, WaveFunctionTestCase
# for some reason KeyLoggingTestCase cannot find test_data it's called from here
# from qrogue.test import KeyLoggingTestCase

if __name__ == '__main__':
    unittest.main()
