""" A collection of object that are built on top of the basic `praw` modules
like `Subreddit`, `Comment` and `Submission`. The new object can generate
and print information about the basic praw instances, in a clean, formatted
design to the terminal. """

import typing
from abc import ABC, abstractmethod
from datetime import datetime

from praw.models import Subreddit, Comment
from .general import TextBox, TextSection, DirectionalDraw


class PrintReddit(DirectionalDraw, ABC):
    """ An abstract class. Objects that inherent from this object are used to
    represent different reddit object to the terminal (printing informtation
    about subreddits, comments, submissions, and more!) """

    def __init__(self, api_obj, box=None, align=None):
        super().__init__(box=box, align=align)

        self._validate_api(api_obj)
        self.__api = api_obj

    def _update_textbox(self, textbox: TextBox):
        """ Updated the alignment and box of the given textbox to match the
        alignment and the box style of the current object. """
        textbox.set_align(self.align)
        textbox.set_box(self.box)

    @abstractmethod
    def _validate_api(self, api_obj):
        """ Called by the constructor, and recives the praw api object (can be
        a subreddit, comment, etc. Depends on the inherited class). Checks if
        the object is valid, and if it isn't, raises an error. """

    @property
    def api(self,):
        """ The basic `praw` instance that this object represents. """
        return self.__api

    @property
    def created(self,) -> str:
        """ Returns a human readable short string that represents how long
        ago the reddit api object was created (for example, if the object is
        a comment, the string will represent how long ago the comment was
        posted) """

        amount, string_type = self.__generate_created_string()
        if amount > 1:
            string_type += 's'

        return f'{int(amount)} {string_type} ago'

    _TIME_DIFFERENCES = [
        # Used by the `__generate_created_string` method to
        # generate the `created` string.
        # pylint: disable=bad-whitespace

        (60,   "second"),
        (60,   "minute"),
        (24,   "hour"),
        (30.4, "day"),
        (12,   "month"),
        (None, "year"),
    ]

    def __generate_created_string(self,) -> typing.Tuple[int, str]:
        """ A function that helps to generate the `created` property.
        Returns a tuple: the first element in the tuple is an integer,
        and the second element in the tuple indicated what the number
        represents. For example, (12, "year"), (32, "second"), etc. """

        # Get the unix timestamp in which the api object was created,
        # and current unix timestamp . Calculate the difference
        # between the timestamps. The result is the number of seconds
        # the have passed from the creation of the object until now!
        created_unix = self.api.created_utc
        now_unix = datetime.now().timestamp()
        seconds_ago = now_unix - created_unix
        return self.__recursive_created_string(value=seconds_ago)

    def __recursive_created_string(self,
                                   value: float,
                                   type_index: int = 0,
                                   ) -> typing.Tuple[int, str]:
        """ A recursive function used by the `__generate_created_string` to
        generate the `created` property. """

        max_value_for_type, cur_type = self._TIME_DIFFERENCES[type_index]

        if max_value_for_type is not None and value >= max_value_for_type:
            value /= max_value_for_type
            type_index += 1
            return self.__recursive_created_string(value, type_index)

        return value, cur_type


class PrintSubreddit(PrintReddit):
    """ An object that is built on top of a praw `Subreddit` instance,
    and can generate and print information about the subreddit to the
    terminal. """

    def _validate_api(self, api_obj: Subreddit):
        """ Called by superclass constructor. Checks if the given subreddit
        instance is actually a subreddit, and raises an error even if its
        represent more then one subreddit. """

        if not isinstance(api_obj, Subreddit):
            raise TypeError(
                "'Subreddit' must be an instance of the praw subreddit object")

        if '+' in api_obj.display_name:
            # If not a single subreddit, but a subreddit group
            raise ValueError(
                "This method supports printing information about a single subreddit (and not multiple subreddits)")

    def generate(self,) -> typing.List[str]:
        """ Generates and returns a list of strings that when printed to
        the terminal, represent the current subreddit. """

        title = TextSection(f"r/{self.api.display_name}")
        body = TextSection(self.api.public_description)
        information = TextSection(' | '.join([
            f"{self.api.subscribers:,} subscribers",
            "NSFW" if self.api.over18 else "SFW",
            f"Created {self.created}"
        ]))

        group = TextBox([title, body, information])
        self._update_textbox(group)
        return group.generate()


class PrintComment(PrintReddit):
    """ An object that is built on top of a praw `Comment` instance,
    and can generate and print information about the comment to the
    terminal. """

    def _validate_api(self, api_obj: Comment):
        """ Called by superclass constructor. Checks if the given comment
        instance is actually a comment, and raises an error if not. """

        if not isinstance(api_obj, Comment):
            raise TypeError(
                "Comment must be an instance of the praw comment object")

    def generate(self,) -> typing.List[str]:
        """ Generates and returns a list of strings that when printed to
        the terminal, represent the current comment. """

        body = TextSection(self.api.body)
        information = TextSection([
            f'❤ {self.api.score} | {self.created}',
            f'A comment by u/{self.api.author}',
        ])
        group = TextBox([body, information])
        self._update_textbox(group)
        return group.generate()
