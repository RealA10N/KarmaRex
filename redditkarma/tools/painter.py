import typing
import os
from abc import ABC, abstractmethod


def decorate_methods(decorator):
    """ Decorate all methods in the class with the given decorator.
    This is a class decorator! """
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


@decorate_methods(property)
@decorate_methods(abstractmethod)
class DrawingBox(ABC):

    # pylint: disable=missing-docstring, multiple-statements, invalid-name, no-self-use

    def TOP_LEFT(self): return
    def TOP_RIGHT(self): return
    def BOTTOM_LEFT(self): return
    def BOTTOM_RIGHT(self): return
    def HORIZONTAL(self): return
    def VERTICAL(self): return

    def CROSS(self): return
    def JUNCTION_BOTTOM(self): return
    def JUNCTION_TOP(self): return
    def JUNCTION_LEFT(self): return
    def JUNCTION_RIGHT(self): return


class HeavyDrawingBox(DrawingBox):

    TOP_LEFT = '╔'
    TOP_RIGHT = '╗'
    BOTTOM_LEFT = '╚'
    BOTTOM_RIGHT = '╝'
    HORIZONTAL = '═'
    VERTICAL = '║'

    CROSS = '╬'
    JUNCTION_BOTTOM = '╦'
    JUNCTION_TOP = '╩'
    JUNCTION_LEFT = '╣'
    JUNCTION_RIGHT = '╠'


class LightDrawingBox(DrawingBox):

    TOP_LEFT = '┌'
    TOP_RIGHT = '┐'
    BOTTOM_LEFT = '└'
    BOTTOM_RIGHT = '┘'
    HORIZONTAL = '─'
    VERTICAL = '│'

    CROSS = '┼'
    JUNCTION_BOTTOM = '┬'
    JUNCTION_TOP = '┴'
    JUNCTION_LEFT = '┤'
    JUNCTION_RIGHT = '├'


class Draw:

    def __init__(self, box: DrawingBox = None):
        if box is None:
            box = LightDrawingBox
        self.__box = box

    @property
    def width(self,):
        return os.get_terminal_size()[0]

    @property
    def box(self,):
        return self.__box

    def set_box(self, box: DrawingBox):
        self.__box = box

    def check_fits(self, text: str):
        return text <= self.width

    @abstractmethod
    def generate(self,) -> typing.Union[typing.List[str], str]:
        return

    def show(self,) -> None:

        text = self.generate()

        if isinstance(text, str):
            print(text)

        elif isinstance(text, list):
            for line in text:
                print(line)


class TextParagraph(Draw):

    def __init__(self,
                 text: typing.Union[str, typing.List[str]] = '',
                 box: DrawingBox = None,
                 ):
        super().__init__(box)
        self.__sentences = list()  # empty
        self.set_text(text)

    def set_text(self, text: typing.Union[str, typing.List[str]]) -> None:

        if isinstance(text, str):
            text = text.split('\n')

        if isinstance(text, list):
            self.__sentences = text

        else:
            raise TypeError("Text must be string or list of strings")

    def add_line(self, text: str) -> None:
        sentences = self.sentences
        sentences.append(text)
        self.set_text(sentences)

    def _cut_to_lines(self,
                      text_words: typing.List[str],
                      removed_words: typing.List[str] = list()
                      ) -> typing.List[str]:

        if not text_words:
            return list()

        text = ' '.join(text_words)
        if len(text) <= self.max_char_line:
            return [text] + self._cut_to_lines(text_words=removed_words, removed_words=list())

        if len(text_words) == 1:

            word = text_words[0]
            half_one = word[:self.max_char_line]
            half_two = word[self.max_char_line:]

            return self._cut_to_lines([half_one], [half_two] + removed_words)

        # Move the last word in `text_words` to the first postion in `removed_words`
        removed_word = text_words.pop()
        removed_words.insert(0, removed_word)
        return self._cut_to_lines(text_words, removed_words)

    def __generate_text(self, text: str,):
        border = self.box.VERTICAL
        return f"{border} {text} {border}"

    def _generate_line(self, text: str):

        text_width = len(self.__generate_text(text))
        padding_amount = max([
            self.width - text_width,
            0,
        ])

        text += ' ' * padding_amount
        return self.__generate_text(text)

    def generate(self,):

        lines = list()
        for sentence in self.sentences:
            for line in self._cut_to_lines(sentence.split()):
                lines.append(self._generate_line(line))

        return lines

    @property
    def text(self,) -> str:
        return '\n'.join(self.__sentences)

    @property
    def sentences(self,) -> typing.List[str]:
        return self.__sentences

    @property
    def max_char_line(self,) -> int:
        return self.width - len(self.__generate_text(''))


class TextBox(Draw):

    def __init__(self,
                 sections: typing.Union[TextParagraph, typing.List[TextParagraph]] = '',
                 box: DrawingBox = None,
                 ):
        super().__init__(box)
        self.__sections = list()  # empty
        self.set_sections(sections)

    def set_sections(self, sections: typing.List[TextParagraph]) -> None:

        if isinstance(sections, list):
            self.__sections = sections

        else:
            raise TypeError("Text must be string or list of strings")

    def add_section(self, section: TextParagraph) -> None:
        sections = self.sections
        sections.append(section)
        self.set_sections(sections)

    def generate(self,) -> None:

        lines = list()
        for section_i, section in enumerate(self.sections):

            if section_i:
                lines.append(self._generate_break())

            for line in section.generate():
                lines.append(line)

        return [self._generate_top()] + lines + [self._generate_bottom()]

    def _generate_break(self,):
        return self.__generate_border_line(
            left=self.box.JUNCTION_RIGHT,
            right=self.box.JUNCTION_LEFT,
            line=self.box.HORIZONTAL,
        )

    def __generate_border_line(self,
                               left: str,
                               right: str,
                               line: str
                               ) -> str:
        line_len = int(
            (self.width - len(left) - len(right))
            / len(line)
        )

        return f"{left}{line * line_len}{right}"

    def _generate_top(self,) -> str:
        return self.__generate_border_line(
            left=self.box.TOP_LEFT,
            right=self.box.TOP_RIGHT,
            line=self.box.HORIZONTAL,
        )

    def _generate_bottom(self,) -> str:
        return self.__generate_border_line(
            left=self.box.BOTTOM_LEFT,
            right=self.box.BOTTOM_RIGHT,
            line=self.box.HORIZONTAL,
        )

    @property
    def sections(self,) -> typing.List[TextParagraph]:
        return self.__sections
