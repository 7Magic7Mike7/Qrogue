from abc import ABC, abstractmethod
from typing import List, Callable, Any


class WidgetWrapper(ABC):
    @abstractmethod
    def is_selected(self) -> bool:
        pass

    @abstractmethod
    def reposition(self, row: int = None, column: int = None, row_span: int = None, column_span: int = None):
        pass

    @abstractmethod
    def set_title(self, title: str) -> None:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def add_text_color_rule(self, regex: str, color: int, rule_type: str, match_type: str = 'line',
                            region: List[int] = [0, 1], include_whitespace: bool = False, selected_color = None)\
            -> None:
        pass

    @abstractmethod
    def activate_individual_coloring(self):
        pass

    @abstractmethod
    def add_key_command(self, keys: List[int], command: Callable[[], Any]) -> Any:
        pass

    @abstractmethod
    def toggle_border(self):
        pass
