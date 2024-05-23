from abc import ABC, abstractmethod
from typing import List, Callable, Any, Tuple


class WidgetWrapper(ABC):
    @abstractmethod
    def get_pos(self) -> Tuple[int, int]:
        """
        Get logical position (e.g. grid cell).

        :return: x, y / column, row
        """
        pass

    @abstractmethod
    def get_abs_pos(self) -> Tuple[int, int]:
        """
        Get absolute position (e.g. absolute screen position of top left character).

        :return: x, y / column, row
        """
        pass

    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        """
        Get logical size (e.g. span of grid cells).

        :return: width, height
        """
        pass

    @abstractmethod
    def get_abs_size(self) -> Tuple[int, int]:
        """
        Get absolute size (e.g. number of characters per row, number of renderable rows).

        :return: width, height
        """
        pass

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
                            region: List[int] = None, include_whitespace: bool = False, selected_color=None) \
            -> None:
        pass

    @abstractmethod
    def reset_text_color_rules(self) -> None:
        pass

    @abstractmethod
    def activate_individual_coloring(self):
        pass

    @abstractmethod
    def add_key_command(self, keys: List[int], command: Callable[[], Any], overwrite: bool = True) -> Any:
        pass

    @abstractmethod
    def toggle_border(self):
        pass
