"""
This module contains two main classes: `Data` and `Database`.

The Data object
===============
The main data container. Each instance can contain two types of data:
1.  Instant data
2.  Not-instant data

Instant data can be any object that is supported by the `json` format (most
basic data structures in Python, e.g. boolean, string, integer, float, lists,
etc.)
Not-instant data actually saves a dictionary, where the keys are strings, and
the values are another `Data` objects.

The database can be seen like a some sort of a tree: Each point in the tree is a
`Data` instance (including the head of the tree), but only the leaves of the tree
are "Instant" `Data` instances.


The Database object
===================
Same as `Data` - this is the object that will be mostly used by the user.
It have one extra feature: when the program ends, it automatically makes sure
and saved the data in memory into the database files in the storage.

Again, if we thing that our database is some sort of a tree, the `Database`
object will usually represent only the head of the tree, and it will contain and
manage other `Data` instances.
"""

import os
import logging
import atexit
import json
import typing


class Data:
    """
    The main data container. Has four general methods:
    1.  Data.get()          Returns the data of the current instance.
    2.  Data.set(data)      Sets the data of the current instance.
    3.  Data.access(*args)  Lets you "travel" between the data instances.
    4.  Data.save()         Saves the data in the memory into the local storage.
    """

    _FILES_EXTENSION = '.json'

    def __init__(self, data=None, path: str = None,):
        self._folder = path

        if path is not None and data is None:
            data = self._load_folder()
            self.set(data)

        if path is None:
            self.set(data)

    # - - P U B L I C - M E T H O D S - - #

    def get(self,):
        """ Returns the value of the current instace. """

        if self.is_instant:
            # If the data is instant, returns the data.
            return self._data

        else:
            # If the data is not instant, generates and returns the data.
            return {name: data_instance.get()
                    for name, data_instance in self._data.items()}

    def set(self, data):
        """ Sets the value of the instance to the given data. """
        self._data, self._instant = self._raw_to_data_structure(data)

    def access(self, *args):
        """ Recursive functions that `travels` inside the database, until it
        gets to the wanted `Data` instance and returns it. If the `Data` instance
        doesn't exist yet, it creates new ones!

        Each argument represents a `Data` instance! for example, calling this
        method with the arguments[`'settings'`, `'background-color'`] will return
        a `Data` instance that is located inside the `settings` Data instance.
        """

        if not args:
            return self

        cur_arg = args[0]
        next_args = args[1:]

        if self.is_instant:
            # If instant -> converts to not instant.

            if self._data is not None:
                logging.warning(
                    "Overwriting database insant value (%s)", str(self._data))

            self.set({cur_arg: None})

        if cur_arg not in self._data:
            # If the next `Data` instance doesn't exist ->
            # Creates a new `empty` instance.
            self._data[cur_arg] = Data(None)

        return self._data[cur_arg].access(*next_args)

    def save(self, path=None):
        """ Saves the data in memory into the database, as `.json` files.

        This method should be called only for data that is represented in the
        storage in a folder or in a file, and not data that is a part of a file.
        The end user should only use this method with the `Database` object, and
        it will (recursively) save the data inside the database.
        """

        if self.is_folder:

            logging.debug(
                "Saving database folder - '%s'", self.folder_path)

            self._save_folder()

        else:  # If saving file
            if path is None:
                raise TypeError("While saving a file, you must provide a path")

            logging.debug(
                "Saving database file - '%s'", path)

            self._save_file(path)

    # - - P R O P E R T I E S - - #

    @property
    def is_folder(self,) -> bool:
        """ Returns `True` only if this Data is saved in a separate folder. """
        return self._folder is not None

    @property
    def folder_path(self,) -> typing.Optional[str]:
        """ Returns the path to the folder (if the data is saved inside a folder).
        If the data isn't saved in a folder, returns `None`. """
        return self._folder

    @property
    def is_instant(self,) -> bool:
        """ There are two general types of data: `instant` and `not-instant`.

        -   `instant` data is saved "as is", and can be any json supported object
        (e.g. list, string, integer, float, etc.)

        -   `not-instant` data is simply a data object that is a dictionary,
        in which the keys are strings, and the values are other `Data` instances.

        This property simply returns `True` if the current instance is `instant`,
        and `False` if the current instance is `non-instant`. """

        return self._instant

    # - - P R O T E C T E D - M E T H O D S - - #

    def _load_folder(self,):
        """ Called from the constructor, when the database is actually a folder,
        and loads the folder content. """

        if not os.path.exists(self.folder_path):
            # If the folder doesn't exist -> there's nothing to load!
            return dict()

        data = dict()
        # If folder exists -> scan files and load them as data.
        for filename in os.listdir(self.folder_path):

            name = self.__name_from_filename(filename)
            if name is not None:
                filepath = os.path.join(self.folder_path, filename)
                with open(filepath, 'r', encoding='utf8') as open_file:
                    data[name] = json.load(open_file)

        return data

    def _save_folder(self,):
        """ Called if the database represents a folder. Saved the data into
        the folder! """

        os.makedirs(self.folder_path, exist_ok=True)

        for db_name in self._data:
            filepath = os.path.join(
                self.folder_path,
                self.__filename_from_name(db_name)
            )
            self._data[db_name].save(filepath)

    def _save_file(self, filepath: str,):
        """ Saves one single file inside the folder. """

        with open(filepath, 'w', encoding='utf8') as open_file:
            json.dump(self.get(), open_file, indent=4)

    def _raw_to_data_structure(self, raw_data: dict) -> dict:
        """ Converts the raw data from the user into a dictionary of `Data` instances
        that is actually saved in memory.

        Returns a tuple that contains two elements:
        1.  The generated dictionary (or instant value)
        2.  A boolean -> `True` if instant value, otherwise `False`
        """

        if not isinstance(raw_data, dict):
            # If not a dict -> instant value.

            if self.is_folder:
                # The database can't save instant values in a folder,
                # and folders only support not-instant data! (raises an error)
                raise DatabaseInvalidStructureError(
                    f"Datebase can't contain instant data ({raw_data}) inside a folder.")

            return raw_data, True

        # If a dictionary
        data = dict()
        for key in raw_data:

            # Makes sure that the keys are strings
            if not isinstance(key, str):
                raise DatabaseInvalidStructureError(
                    f"A database should contain only string keys (not `{key}`)")

            data[key] = Data(raw_data[key])

        return data, False

    # - - P R I V A T E - M E T H O D S - - #

    def __filename_from_name(self, name: str):
        """ Generates the database filename from the database name string. """
        return f"{name}{self._FILES_EXTENSION}"

    def __name_from_filename(self, filename: str) -> typing.Optional[str]:
        """ Returns `None` if the given string is not formatted like a database
        file string, and if it is, returns the database name itself. """

        filename = os.path.basename(filename)
        if filename.endswith(self._FILES_EXTENSION):
            return filename.replace(self._FILES_EXTENSION, '')

        return None


class Database(Data):
    """
    Same as the `Data` object, but has one extra feature:
    When the program ends, it automatically calls the `save` method and makes
    sure that the data that is saved in the memory is saved in the storage.
    """

    def __init__(self, data=None, path: str = None,):
        super().__init__(data, path)

        # Save the database from memory when exiting the script.
        atexit.register(self.save)


class DatabaseError(Exception):
    """ Raised when there is an error related to the database. """


class DatabaseAccessError(DatabaseError):
    """ Raised when trying to access a database with invalid path. """


class DatabaseInvalidStructureError(DatabaseError):
    """ Raised when trying to build a database from an invalid structure.
    The database should only contain dictionaries (string keys). """
