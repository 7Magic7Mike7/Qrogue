
from .test_config import TestConfig
from .path_config import FileTypes, PathConfig
from .grammar_config import MapGrammarConfig
from .py_cui_config import PyCuiConfig, PyCuiColors
from .visual_config import ColorCode, ColorConfig, PopupConfig, UIConfig, HudConfig, split_text
from .gameplay_config import GameplayConfig, CheatConfig, MapConfig, PuzzleConfig, ScoreConfig, \
    QuantumSimulationConfig, ShopConfig, InstructionConfig, Options, ExpeditionConfig
from .error_config import ErrorConfig
from .config import Config


GameplayConfig.init_options()
