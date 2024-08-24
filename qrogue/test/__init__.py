
from .test_util import *
from .config_tests import MyOptionsTest
from .control_tests import ControlTests
from .fusion_tests import FusionTestCase
from .generation_tests import LayoutGenTestCase, LevelGenTestCase
from .key_logger_tests import KeyLoggingTestCase
from .popup_tests import MyPopupTests
from .puzzle_generation_tests import ManuelPuzzleGenTestCase
from .random_tests import MyRandomTests
from .save_load_test import SaveDataOverhaulTests
from .validation_tests import ValidationTests
from .wfc_tests import WFCGeneratorTestCases, WaveFunctionTestCase

# manuel tests:
# - simulation_tests.py (needs to simulate a terminal)
# - transition_tests.py (needs to simulate a terminal)
# - state_vector_tests.py
# - parser_test.py
# - selection_tests.py
