from py_cui.renderer import Renderer

from qrogue.game.world.tiles import Tile
from qrogue.util import ColorConfig, Logger, ErrorConfig


class TileRenderer:
    __instance = None

    @staticmethod
    def instance() -> "TileRenderer":
        if TileRenderer.__instance is None:
            TileRenderer()
        return TileRenderer.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if TileRenderer.__instance is not None:
            Logger.instance().throw(Exception(ErrorConfig.singleton("TileRenderer")))
        else:
            TileRenderer.__instance = self

    @staticmethod
    def render(tile: Tile):
        return tile.get_img()


class Fragment:
    def __init__(self, start: int, text: str, color: int):
        self.__start = start
        self.__text = text
        self.__color = color

    @property
    def text(self) -> str:
        return self.__text

    @property
    def start(self) -> int:
        return self.__start

    @property
    def length(self) -> int:
        return len(self.text)

    @property
    def end(self) -> int:
        return self.start + self.length

    @property
    def color(self) -> int:
        return self.__color

    def format(self) -> "[str, int]":
        if self.text.startswith(ColorConfig.TEXT_HIGHLIGHT) and self.text.endswith(ColorConfig.TEXT_HIGHLIGHT):
            hl = len(ColorConfig.TEXT_HIGHLIGHT)
            color = int(ColorConfig.get(self.text[hl:hl + ColorConfig.CODE_WIDTH]))
            text = self.text[hl + ColorConfig.CODE_WIDTH:-hl]
            return [text, color]
        return [self.text, self.color]

    def __len__(self):
        return self.length

    def __lt__(self, other) -> bool:
        if self.start == other.start:
            return self.end < other.end
        return self.start < other.start

    def __str__(self) -> str:
        return f"({self.start}-{self.end}) {self.text} ({self.color})"


class FragmentStorage:
    def __init__(self, og_text: str, og_color: int):
        self.__og_text = og_text
        self.__og_color = og_color
        self.__fragments = []

    def append(self, fragment: Fragment):
        if fragment.color != self.__og_color:
            self.__fragments.append(fragment)

    def sort(self):
        self.__fragments.sort()

    def fill_blanks(self) -> "list of [int, str]":
        if len(self.__fragments) <= 0:
            return [[self.__og_text, self.__og_color]]
        formatted_frags = []
        prev = self.__fragments[0]

        # append the text before the first color
        if prev.start != 0:
            formatted_frags.append([self.__og_text[0:prev.start], self.__og_color])
        # appended the colored text with potentially the normal text in between
        for i in range(1, len(self.__fragments)):
            formatted_frags.append(prev.format())
            cur = self.__fragments[i]
            if prev.end != cur.start:
                formatted_frags.append([self.__og_text[prev.end:cur.start], self.__og_color])
            prev = cur
        formatted_frags.append(prev.format())   # append the last color
        # append the text after the last color
        if prev.end != len(self.__og_text):
            formatted_frags.append([self.__og_text[prev.end:], self.__og_color])

        return formatted_frags

    def __iter__(self):
        return iter(self.__fragments)


class MultiColorRenderer(Renderer):
    def __init__(self, root, stdscr, logger):
        super().__init__(root, stdscr, logger)

    def _get_render_text(self, ui_element, line, centered, bordered, selected, start_pos):
        """Internal function that computes the scope of the text that should be drawn

        Parameters
        ----------
        ui_element : py_cui.ui.UIElement
            The ui_element being drawn
        line : str
            the line of text being drawn
        centered : bool
            flag to set if the text should be centered
        bordered : bool
            a flag to set if the text should be bordered
        start_pos : int
            position to start rendering the text from.

        Returns
        -------
        render_text : str
            The text shortened to fit within given space
        """

        padx, _       = ui_element.get_padding()
        _, width      = ui_element.get_absolute_dimensions()

        render_text_length = width - (2 * padx)
        # this line is the only difference to the original (super) function
        render_text_length += ColorConfig.count_meta_characters(line, render_text_length, self._logger)

        if bordered:
            render_text_length = render_text_length - 4

        if len(line) - start_pos < render_text_length:
            if centered:
                render_text = '{}'.format(  line[start_pos:].center(render_text_length,
                                            ' '))
            else:
                render_text = '{}{}'.format(line[start_pos:],
                                            ' ' * (render_text_length - len(line[start_pos:])))
        else:
            render_text = line[start_pos:start_pos + render_text_length]

        render_text_fragments = self._generate_text_color_fragments(ui_element, line, render_text, selected)
        return render_text_fragments

    def _generate_text_color_fragments(self, ui_element, line, render_text, selected):
        """Function that applies color rules to text, dividing them if match is found

        Parameters
        ----------
        ui_element : py_cui.ui.UIElement
            The ui_element being drawn
        line : str
            the line of text being drawn
        render_text : str
            The text shortened to fit within given space

        Returns
        -------
        fragments : list of [int, str]
            list of text - color code combinations to write
        """
        if selected:
            meta_fragments = FragmentStorage(render_text, ui_element.get_selected_color())
        else:
            meta_fragments = FragmentStorage(render_text, ui_element.get_color())

        for color_rule in self._color_rules:
            fragments, match = color_rule.generate_fragments(ui_element, line, render_text, selected)
            if match:
                cur_pos = 0
                for frag in fragments:
                    start = cur_pos
                    text = frag[0]
                    color = frag[1]
                    cur_pos += len(text)
                    meta_fragments.append(Fragment(start, text, color))
        meta_fragments.sort()
        full = meta_fragments.fill_blanks()
        text = ""
        for frag in full:
            text += str(frag)
        text += "\n"
        return full
