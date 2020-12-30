""" This folder contains useful scripts that you might want to use while using
the project! """


import os
import sys
import typing


class AsciiKarmaRexBanner:
    """
    This object has one main method 'to_screen', that generates and prints
    the `Karma Rex` banner art into the screen.
    It will be printed in every script that imports this one.

    The are is generated using the `art` module by sepandhaghighi.
    Check it out! --> https://github.com/sepandhaghighi/art (:
    """

    HORIZONTAL_SPACING_TEXT_ART = 3
    VERTICAL_SPACING_TEXT_ART = 0
    MIN_SCREEN_SIZE_TO_ART = 45

    KARMA_ART = [  # art.tprint("Karma", "big")
        r" _  __",
        r"| |/ /  __ _  _ __  _ __ ___    __ _",
        r"| ' /  / _` || '__|| '_ ` _ \  / _` |",
        r"| . \ | (_| || |   | | | | | || (_| |",
        r"|_|\_\ \__,_||_|   |_| |_| |_| \__,_|",
    ]

    REX_ART = [  # art.tprint("Rex", "big")
        r" ____",
        r"|  _ \   ___ __  __",
        r"| |_) | / _ \\ \/ /",
        r"|  _ < |  __/ >  <",
        r"|_| \_\ \___|/_/\_\ ",
    ]

    TITLE_TEXT = "GAIN REDDIT KARMA. FAST."

    SUBTITLE_TEXT = "ᴬ ᵗᵒᵒˡ ᶜʳᵉᵃᵗᵉᵈ ᵇʸ ᴿᵉᵃˡᴬ¹⁰ᴺ"
    # art.tprint("A tool created by RealA10N", "fancytext69")

    @classmethod
    def width_of_art(cls, artlines: typing.List[str]) -> int:
        """ Returns the width of the ascii art (in characters) """
        return max(len(line) for line in artlines)

    @classmethod
    def generate_art(cls,) -> typing.List[str]:
        """ Generates the logo text, and returns it as a list of strings. """

        return [
            cls.empty_line(),
            *cls.paste_middle_art(cls.generate_banner_text_art()),
            cls.empty_line(),
            cls.paste_middle_text(cls.TITLE_TEXT),
            cls.paste_middle_text(cls.SUBTITLE_TEXT),
            cls.empty_line(),
        ]

    @classmethod
    def generate_banner_text_art(cls,) -> typing.List[str]:
        """ Returns a list of strings that represent the title of the whole banner
        (the big "Karma Rex" text!) """

        width, _ = os.get_terminal_size()

        karma_width = cls.width_of_art(cls.KARMA_ART)
        rex_width = cls.width_of_art(cls.REX_ART)
        combined_width = karma_width + rex_width + cls.HORIZONTAL_SPACING_TEXT_ART

        if combined_width <= width:
            return cls.horizontal_text_art()

        else:
            return cls.vertical_text_art()

    @classmethod
    def horizontal_text_art(cls,):

        art_list = [
            cls.KARMA_ART,
            cls.REX_ART,
        ]

        # Add whitespaces to the art, if needed
        lines = max(len(art) for art in art_list)

        for art_i, art in enumerate(art_list):
            art_len = cls.width_of_art(art)

            for line_i in range(lines):

                if line_i > len(art):
                    # If index out of range, create a new empty line
                    # and add it to the current art.
                    art_list[art_i].append(cls.empty_line(art_len))

                else:
                    art_list[art_i][line_i] = cls._whitespace(
                        art_list[art_i][line_i], art_len)

        final = list()
        spacing = cls.HORIZONTAL_SPACING_TEXT_ART * ' '
        for line_i in range(lines):

            line_from_arts = list()
            for art in art_list:
                line_from_arts.append(art[line_i])

            final.append(spacing.join(line_from_arts))

        return final

    @classmethod
    def vertical_text_art(cls,):

        art_list = [
            cls.KARMA_ART,
            cls.REX_ART,
        ]

        width = max(cls.width_of_art(art) for art in art_list)

        final = list()
        for art_i, art in enumerate(art_list):

            background = cls.empty_line(width)
            for line in art:
                art_width = cls.width_of_art(art)
                line = cls._whitespace(line, art_width)
                final.append(cls.paste_middle_text(line, background))

            if art_i != len(art) - 1:
                # If not the last iteration
                # Add vertical padding
                final += [cls.empty_line(width)] * \
                    cls.VERTICAL_SPACING_TEXT_ART

        return final

    @staticmethod
    def _whitespace(text: str, to_len: int):
        if len(text) < to_len:
            text += ' ' * (to_len - len(text))

        elif len(text) > to_len:
            text = text[:to_len]

        return text

    @classmethod
    def empty_line(cls, length: int = None):
        if length is None:
            length = os.get_terminal_size()[0]  # width of console
        return length * ' '

    @classmethod
    def paste_middle_text(cls,
                          text: str,
                          background: str = None
                          ) -> str:

        if background is None:
            background = cls.empty_line()

        paste_index = int((len(background) - len(text)) / 2)

        if paste_index < 0:
            # If the text is larger then the background,
            # cuts the edges of the text.
            text = text[-paste_index:len(background)+paste_index]
            paste_index = 0

        background = [char for char in background]  # convert to list of chars
        background[paste_index:paste_index+len(text)] = text  # paste text
        return ''.join(background)  # convert back to string

    @classmethod
    def paste_middle_art(cls,
                         art: typing.List[str],
                         background: str = None,
                         ) -> typing.List[str]:
        return [
            cls.paste_middle_text(line, background)
            for line in art
        ]

    @classmethod
    def pprint(cls, text: str):
        """ Prints the given text to the screen. """

        if isinstance(text, list):
            text = '\n'.join(text)

        print(text)

    @classmethod
    def to_screen(cls,) -> None:
        cls.pprint(cls.generate_art())


# Add the actual module into the python path, so it can be imported.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Print the ascii banner to the screen
AsciiKarmaRexBanner.to_screen()
