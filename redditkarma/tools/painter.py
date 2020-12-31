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
    """ Abstract class. This group of classes represent different 'border' / 'box'
    ASCII designs. """

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
    """ A heavy border drawing box, mostly for important messages only. """

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
    """ A light border drawing box, for regular messages. """

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


class Draw(ABC):
    """ An abstract class. Has important and basic methods that are critical for
    objects that print stuff to the console. 😊 """

    def __init__(self, box: DrawingBox = None):
        if box is None:
            box = LightDrawingBox
        self.__box = box

    @property
    def width(self,) -> int:
        """ The current width of the terminal window. Returned as an integer
        that represents the number of characters that the window can fit in
        a single line. """
        return os.get_terminal_size()[0]

    @property
    def box(self,) -> DrawingBox:
        """ An object that inherits 'DrawingBox' and has the same properties.
        Will be used as a template while printing things to the screen! """
        return self.__box

    def set_box(self, box: DrawingBox) -> None:
        """ Sets the drawing box of the current instance. This will be used
        as a template while printing things to the screen! """
        self.__box = box

    def check_fits(self, text: str):
        """ Returns `True` only if the given text will fit in the screen and won't
        overflow in a single line. """
        return text <= self.width

    @abstractmethod
    def generate(self,) -> typing.Union[typing.List[str], str]:
        """ An abstract method that must be implemented in the child classes.
        Can return a string or a list of strings, which represent the object
        as a string and will be printed on the screen when calling the `show`
        method. """

    def show(self,) -> None:
        """ Prints the object to the screen (uses the string generated with the
        `generate` method). """

        text = self.generate()

        if isinstance(text, list):
            # If a list of strings, combine to one string
            text = '\n'.join(text)

        print(text)


class DirectionalDraw(Draw, ABC):  # pylint: disable=abstract-method

    """ Same as `Draw`, but with one small additional feature:
    The `align` property - that lets you set the alignment of the
    `Draw` object to the right, left, or the center. """

    _POSSIBLE_ALIGNMENTS = {'r', 'l', 'c'}

    def __init__(self, box: DrawingBox = None):
        super().__init__(box)
        self.__align = 'l'  # align to left by default

    def set_align(self, direction: str):
        """ Sets the direction in which the text will be aligned.
        Can be one of three: `l` (left - default), `r` (right), or
        `c` (center, middle). """

        direction = direction.lower()

        # Check if follows the valid alignment string
        if not (isinstance(direction, str) and len(direction) == 1):
            raise TypeError(
                "Align direction must be a single character string")

        # Check if valid alignment
        if direction not in self._POSSIBLE_ALIGNMENTS:
            raise ValueError("Invalid align direction")

        # Save the alignment
        self.__align = direction

    @property
    def align(self,) -> str:
        """ Returns the direction in which the text in the `Draw` object
        should be aligned in - as a singal character string. """
        return self.__align


class TextSection(DirectionalDraw):
    """ Represents a section of text (generally a paragraph).
    Used by the `TextBox` object to print text to the screen. """

    def __init__(self,
                 text: typing.Union[str, typing.List[str]] = '',
                 box: DrawingBox = None,
                 ):
        super().__init__(box)
        self.__sentences = list()  # empty
        self.set_text(text)

    def set_text(self, text: typing.Union[str, typing.List[str]]) -> None:
        """ Recives sentences, and saves them as the text to the current section.
        If the text is given as a string, it will be split into sentenced between
        the `\n` characters. If the text is given as a list of strings, each item
        in the list will be converted to a sentence. """

        if isinstance(text, str):
            text = text.split('\n')

        if isinstance(text, list):
            self.__sentences = text

        else:
            raise TypeError("Text must be string or list of strings")

    def add_line(self, text: str) -> None:
        """ Adds the given string as a sentence to the section. """

        sentences = self.sentences
        sentences.append(text)
        self.set_text(sentences)

    def _cut_to_lines(self,
                      text_words: typing.List[str],
                      removed_words: typing.List[str] = None,
                      ) -> typing.List[str]:
        """ Recives a list of words, and returns a list of STRINGS that represent
        sentences that fit inside a single row in the terminal. In other words:
        divides the given words into lines in the terminal. """

        # GENERAL IDEA:
        # recursive function. Starts when all of the words are in
        # the `text_words` list and moves them one by one to the
        # `removed_words` list. After moving each word, it checks if
        # the remaining words in `text_words` fit in a single terminal
        # row. If they do, saves the row and starts all over again but
        # now with ONLY the words that left in the `removed_words` list
        # The function finally stops when there are no words in both
        # of the lists.

        # Stop condition - if no words are given
        if not text_words:
            return list()

        if removed_words is None:
            # Default value - recursive call starts when all
            # of the words are in the `text_words` and `removed_words`
            # is empty
            removed_words = list()

        # join word list to a sentence
        text = ' '.join(text_words)

        # check if the sentence fits in a single terminal row
        if len(text) <= self.max_char_line:

            # If it does, saved the result and calls the function again
            # but only with the removed words, that doesn't appear in the
            # added sentence
            return [text] + self._cut_to_lines(text_words=removed_words)

        # Special case: if a word is longer then the terminal row
        if len(text_words) == 1:

            # Cuts the word in two parts: head and tail.
            # treats them as two separate lines
            word = text_words[0]
            head = word[:self.max_char_line]
            tail = word[self.max_char_line:]

            # Calls the recursive function again with the split word.
            # Because the length of the `head` is exactly the maximum
            # size of terminal, it will in a single row in the next
            # recursive call.
            return self._cut_to_lines([head], [tail] + removed_words)

        # If the sentence doesn't fit in a single terminal line: Takes
        # the last word from the sentence and moves it to the `removed_words`
        # and calls the funcion again with the new and updated lists!
        removed = text_words.pop()
        removed_words.insert(0, removed)
        return self._cut_to_lines(text_words, removed_words)

    def __generate_text(self, text: str,):
        """ Recives the text, and formats it (without padding) """
        border = self.box.VERTICAL
        return f"{border} {text} {border}"

    def _generate_line(self, text: str) -> str:
        """ Recives the text, and formats it to match the format and the
        terminal size (adds ASCII borders and padding if needed). """

        # Calculates the additional needed padding to fill the whole
        # characters in the terminal line.
        text_width = len(self.__generate_text(text))
        padding_amount = max([
            self.width - text_width,
            0,
        ])

        # Adds the padding (3 different options)

        if self.align == 'c':
            # Align to center
            # Adds half of the padding before the text,
            # and half of the padding after the text.

            amount_before = int(padding_amount / 2)
            amount_after = amount_before + (padding_amount % 2)

            padding_before = ' ' * amount_before
            padding_after = ' ' * amount_after

            text = f"{padding_before}{text}{padding_after}"

        elif self.align == 'r':
            # Align to right
            # Adds the padding before the text
            text = (' ' * padding_amount) + text

        else:
            # align to left - default
            # Adds the padding after the text
            text += ' ' * padding_amount

        return self.__generate_text(text)

    def generate(self,):
        """ Generates and returns a list of strings that if printed to the
        terminal, represent the text section. """

        lines = list()
        for sentence in self.sentences:
            for line in self._cut_to_lines(sentence.split()):
                lines.append(self._generate_line(line))

        return lines

    @property
    def text(self,) -> str:
        """ The section text, as a one long string. """
        return '\n'.join(self.__sentences)

    @property
    def sentences(self,) -> typing.List[str]:
        """ The section text, as a list of strings (sentences). """
        return self.__sentences

    @property
    def max_char_line(self,) -> int:
        """ The max length (in characters) of a text that will fit in
        a single terminal row. """
        return self.width - len(self.__generate_text(''))


class TextBox(DirectionalDraw):
    """ A group of `TextSection` instances, that when together result in
    a `TextBox`! A `TextBox` can be displayed to the user in the console,
    and used in almost (if not in all) the scripts of KarmaRex. """

    def __init__(self,
                 sections: typing.Union[TextSection, typing.List[TextSection]] = '',
                 box: DrawingBox = None,
                 ):
        super().__init__(box)
        self.__sections = list()  # empty by default
        self.set_sections(sections)

    def set_sections(self, sections: typing.List[TextSection]) -> None:
        """ Recives a list on `TextSection` instances, and saves them while
        overwriting the old saved sections. """

        if not isinstance(sections, list):
            raise TypeError("Text must be string or list of strings")

        for item in sections:
            if not isinstance(item, TextSection):
                raise TypeError(
                    "One or more of the items in the list are not `TextSection` instances")

        self.__sections = sections

    def add_section(self, section: TextSection) -> None:
        """ Adds a single section instance to the box. """

        if not isinstance(section, TextSection):
            raise TypeError(
                f"Received a non `TextSection` instance ({section})")

        sections = self.sections
        sections.append(section)
        self.set_sections(sections)

    def generate(self,) -> typing.List[str]:
        """ Generates a list of strings that represent the text box,
        and contains the sections inside the box. """

        lines = list()
        for section_i, section in enumerate(self.sections):

            if section_i:
                # if not the first section - if between sections
                # adds the breaking line between sections
                lines.append(self._generate_break())

            lines += section.generate()

        return [self._generate_top()] + lines + [self._generate_bottom()]

    def __generate_border_line(self,
                               left: str,
                               right: str,
                               line: str
                               ) -> str:
        """ A function that helps to generate the top, bottom and
        break lines in the text box. Returns a string. """

        line_len = int(
            (self.width - len(left) - len(right))
            / len(line)
        )

        return f"{left}{line * line_len}{right}"

    def _generate_break(self,):
        """ Returns the breaking line between the text sections. """
        return self.__generate_border_line(
            left=self.box.JUNCTION_RIGHT,
            right=self.box.JUNCTION_LEFT,
            line=self.box.HORIZONTAL,
        )

    def _generate_top(self,) -> str:
        """ Returns the top (first) line in the text box. """
        return self.__generate_border_line(
            left=self.box.TOP_LEFT,
            right=self.box.TOP_RIGHT,
            line=self.box.HORIZONTAL,
        )

    def _generate_bottom(self,) -> str:
        """ Returns the bottom (last) line in the text box. """
        return self.__generate_border_line(
            left=self.box.BOTTOM_LEFT,
            right=self.box.BOTTOM_RIGHT,
            line=self.box.HORIZONTAL,
        )

    def set_align(self, direction: str) -> None:
        """ Updates the alignment of the sections currently in the box.
        Can be one of three values: `l` (left), `r` (right), or `c` (center).
        """

        # Update alignment of self
        super().set_align(direction)

        # Updated alignment of sections inside the box
        for section in self.sections:
            section.set_align(direction)

    @property
    def sections(self,) -> typing.List[TextSection]:
        """ Returns a list of `TextSection` instances that are contained
        by the current box instance. """
        return self.__sections
