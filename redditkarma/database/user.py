import os
import praw
from .database import Database


class UserDatabase(Database):

    _DB_FOLDER = "db"
    _DEFAULT_USER_AGENT = r'https://github.com/RealA10N/reddit-karma/'

    def __init__(self,
                 username: str,
                 password: str = None,
                 client_id: str = None,
                 client_secret: str = None,
                 ):
        self.__username = username

        super().__init__(
            path=os.path.join(self._DB_FOLDER, self.username)
        )

        self.__praw = self.__generate_praw_instance(
            username=username,
            password=password,
            client_id=client_id,
            client_secret=client_secret,
            user_agent=self._DEFAULT_USER_AGENT,
        )

    def __generate_praw_instance(self, **new_credentials):
        """ Loads the login credentials from the database, generates an
        `praw.Reddit` instance and returns it.

        Raises an error of some credentials are missing!"""

        old_credentials = self.access("login").get()
        if old_credentials is None:
            old_credentials = dict()

        new_credentials = {
            credential: new_credentials[credential]
            for credential in new_credentials
            if new_credentials[credential] is not None
        }

        credentials = {
            **old_credentials,
            **new_credentials,
        }

        self.access("login").set(credentials)

        needed_credentials = ["username", "password",
                              "client_id", "client_secret", "user_agent"]

        if not all(credential in credentials for credential in needed_credentials):
            # If not all credentials are provided
            raise MissingCredentialsError(
                "One or more of the needed credentials for a request to reddit are not provided.")

        return praw.Reddit(**credentials)

    # - - P R O P E R T I E S - - #

    @property
    def username(self,) -> str:
        """ The reddit username to which the data belongs. """
        return self.__username

    @property
    def _database_path(self,) -> str:
        """ The path to the folder in which the database files are saved. """
        return os.path.join(self._DB_FOLDER, self.username)

    @property
    def reddit_api(self,):
        """ An `praw.Reddit` instance that matches the user credentials. """
        return self.__praw


class MissingCredentialsError(Exception):
    """ Raised when trying to generate a request to the Reddit API,
    but not all of the needed credentials are provided (username, password,
    client_id, client_secret). """
