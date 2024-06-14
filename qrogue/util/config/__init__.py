from .config import Config
from .error_config import ErrorConfig
from .gameplay_config import CheatConfig, GameplayConfig, Options
from .gameplay_config import ExpeditionConfig, MapConfig
from .gameplay_config import InstructionConfig, QuantumSimulationConfig, PuzzleConfig, ScoreConfig
from .grammar_config import MapGrammarConfig, PuzzleGrammarConfig
from .path_config import FileTypes, PathConfig
from .py_cui_config import PyCuiConfig, PyCuiColors
from .test_config import TestConfig
from .visual_config import ColorCode, ColorConfig, HudConfig, PopupConfig, UIConfig, split_text

GameplayConfig.init_options()
