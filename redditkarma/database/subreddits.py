"""
In this file you will find classes that help manage the data related to subreddits
in the database.
The main object in this file is `SubredditGroupDatabase` - where each instance
of it represents different a different GROUP of subreddits.
The bot treats the subreddits in each group as one subreddit (for example, there
is no reason to treat 'r/doodles' and r'r/sketches' differently - both are
subreddits in which the submissions are related to art sketches).
"""
import typing
from .database import Database, UsingDatabase


class SubredditGroupDatabase(UsingDatabase):

    _SUBREDDITS_LIST_KEY = "subreddits"
    _DEFAULT_SUBREDDIT_GROUP_DB_STRUCTURE = {

        # list of subreddit names, without the 'r/' part (only actual name)
        _SUBREDDITS_LIST_KEY: list(),

    }

    def __init__(self, database: Database, group_name: str):
        super().__init__(database)
        self.__name = group_name

        self.__normalize_database()

    def _access_db(self, *args):
        return super()._access_db("subreddits", "groups", self.name, *args)

    def __normalize_database(self):
        """ Loads the saved data from the database about the current subreddits
        group. Makes sure the database structure is correct, and if not, updates
        the database. If the subreddits group is new and doesn't appear in the
        database yet, it will update the database to the default subreddits group
        database structure. """

        # Load the saved data about the current subreddits group form the database
        db = self._access_db()  # pylint: disable=invalid-name
        db_data = db.get()

        # If this group is not saved in the database,
        # or if the saved data doesn't match the structure (dict)
        if not isinstance(db_data, dict):
            # delete / update the database to an empty dictionary.
            db_data = dict()

        # For each property in the database structure, if not in the loaded
        # database, set to default value.
        for key in self._DEFAULT_SUBREDDIT_GROUP_DB_STRUCTURE:
            if key not in db_data:
                db_data[key] = self._DEFAULT_SUBREDDIT_GROUP_DB_STRUCTURE[key]

        db.set(db_data)

    def add_subreddits(self, *args: typing.Union[typing.List[str], str]) -> None:
        """ Adds the given subreddits to the current subreddit group. If a non
        string is given (or a list of non string), it will be ignored and will
        not raise an error. """

        # Generate the final list of subreddits to add from the arguments
        # if lists of subreddits are given, convert them to strings.
        to_add = list()
        for arg in args:
            if isinstance(arg, str):
                to_add.append(arg)
            elif isinstance(arg, list):
                for item in arg:
                    if isinstance(item, str):
                        to_add.append(item)

        # Get saved subreddit list
        data = self.subreddits_in_group  # Python 'Set' instance

        # Add the given subreddit to the list
        for subreddit in to_add:
            if subreddit not in data:
                data.add(subreddit)

        # Update the database with the new data
        self.set_subreddits(data)

    def add_subreddit(self, subreddit_name: str) -> None:
        """ Adds the given subreddit to the current subreddit group. """

        if not isinstance(subreddit_name, str):
            raise TypeError("Subreddit name must be a string.")

        self.add_subreddits(subreddit_name)

    def set_subreddits(self, subreddits: typing.Union[typing.List[str], typing.Set[str]]) -> None:
        """ Recives a list (or a set) of subreddits and sets it as the subreddits
        in the subreddit group. The subreddits must be represented as a string,
        without the 'r/' part (only the actual name). """

        # Convert to set (Remove duplicates)
        subreddits = list(set(subreddits))

        # Save to the database
        self._access_db(self._SUBREDDITS_LIST_KEY).set(subreddits)

    @property
    def name(self,):
        """ The name of the subreddits group - usually something general that
        is common between the subreddits. For example: "art", "tech", "news",
        etc. """
        return self.__name

    @property
    def subreddits_in_group(self,) -> typing.Set[str]:
        """ Returns a list of the subreddits that are in the current subreddit
        group. """
        return set(self._access_db(self._SUBREDDITS_LIST_KEY).get())
