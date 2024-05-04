
from .error_config import ErrorConfig
from .grammar_config import MapGrammarConfig
from .path_config import FileTypes, PathConfig
from .py_cui_config import PyCuiConfig, PyCuiColors
from .test_config import TestConfig
from .visual_config import ColorCode, ColorConfig, HudConfig, PopupConfig, UIConfig, split_text
from .gameplay_config import CheatConfig, GameplayConfig, Options
from .gameplay_config import ExpeditionConfig, MapConfig, ShopConfig
from .gameplay_config import InstructionConfig, QuantumSimulationConfig, PuzzleConfig, ScoreConfig
from .config import Config


GameplayConfig.init_options()
