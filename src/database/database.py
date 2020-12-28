import os
import logging
import typing
from praw import Reddit
import atexit
import json


class Data:

    """ This object is created by the `FileDatabase` object,
    and should not be created by the user. """

    def __init__(self, data):
        self.set(data)

    def _raw_to_data_structure(self, raw_data: dict) -> dict:

        if not isinstance(raw_data, dict):
            # If not a dict -> instant value.
            return raw_data, True

        # If a dictionary
        data = dict()
        for key in raw_data:

            # Makes sure that the keys are strings
            if not isinstance(key, str):
                raise DatabaseInvalidStructureError(
                    f"A database should cotain only string keys (not `{key}`)")

            data[key] = Data(raw_data[key])

        return data, False

    def get(self,):

        if self._instant:
            # If the data is instant, returns the data.
            return self._data

        else:
            # If the data is not instant, generates and returns the data.
            return {name: data_instance.get()
                    for name, data_instance in self._data.items()}

    def set(self, data):
        self._data, self._instant = self._raw_to_data_structure(data)

    def access(self, *args):

        if len(args) == 0:
            return self

        cur_arg = args[0]
        next_args = args[1:]

        if self._instant:
            # If instant -> converts to not instant.
            logging.warning(
                f"Overwriting database insant value ({self._data})")

            self.set({cur_arg: None})

        if cur_arg not in self._data:
            # If the next `Data` instance doesn't exist ->
            # Creates a new `empty` instance.
            self._data[cur_arg] = Data(None)

        return self._data[cur_arg].access(*next_args)


class FileDatabase:

    def __init__(self, path: str):
        self.__path = path
        self.__data = self._load_data()

        atexit.register(self.save,)

    def _load_data(self,) -> Data:
        """ Loads the `Data` instance that represents the current file, and
        returns it. """

        if os.path.exists(self._path):
            with open(self._path, 'r', encoding='utf8') as f:
                data = json.load(f)

        else:
            data = dict()

        return Data(data)

    @property
    def _path(self,):
        return self.__path

    def save(self,):
        """ Saves the data in memory into the database. """

        logging.debug(f"Saving database from memory - '{self._path}'")

        with open(self._path, 'w', encoding='utf8') as f:
            json.dump(self.__data.get(), f, indent=4)

    def access(self, *args):
        return self.__data.access(*args)


class UserDatabase:

    __USER_AGENT = "https://github.com/RealA10N/reddit-karma"
    __DB_FILES_EXTENCION = ".json"

    def __init__(self, username: str,):
        self.__username = username
        self.__files = self._load_files()

    @property
    def username(self,):
        """ The reddit username of the database. """
        return self.__username

    @property
    def _folder_path(self,):
        """ The path to the user database folder. """
        return os.path.join("db", self.username)

    def _load_files(self,) -> dict:
        """ Loads `FileDatabase` instances for all the files in the user
        database folder, and returns the instances in a dictionary, where the
        keys are the database names. """

        os.makedirs(self._folder_path, exist_ok=True)

        return {
            filename.replace(self.__DB_FILES_EXTENCION, ''): FileDatabase(
                os.path.join(self._folder_path, filename))
            for filename in os.listdir(self._folder_path)
            if filename.endswith(self.__DB_FILES_EXTENCION)
        }

    def _get_file_db(self, name: str) -> FileDatabase:
        """ Returns a `FileDatabase` instance. If already generated an instance,
        returns the saved one. If the instance is not yet generated: generates,
        saves and returns the new instance. """

        if name in self.__files:
            # If the database already exists (generated in the past)
            return self.__files[name]

        # If database is new and not yet generated
        db = FileDatabase(  # Create the database
            os.path.join(self._folder_path, name + self.__DB_FILES_EXTENCION))
        self.__files[name] = db  # Save the database locally
        return db

    def access(self, *args):

        if len(args) < 1:
            raise DatabaseAccessError("Database access path is not valid")

        file_db_name = args[0]
        file_db = self._get_file_db(file_db_name)

        data_args = args[1:]
        data = file_db.access(*data_args)
        return data


class DatabaseError(Exception):
    """ Raised when there is an error related to the database. """


class DatabaseAccessError(DatabaseError):
    """ Raised when trying to access a database with invalid path. """


class DatabaseInvalidStructureError(DatabaseError):
    """ Raised when trying to build a database from an invalid structure.
    The database should only contain dictionaries (string keys). """
