import praw
from .database import UsingDatabase, Data


class UserDatabase(UsingDatabase):

    _DEFAULT_USER_AGENT = r'https://github.com/RealA10N/reddit-karma/'
    _NEEDED_PRAW_CREDENTIALS = ["username", "password",
                                "client_id", "client_secret", "user_agent"]

    def __get_user_credentials(self, username: str) -> Data:
        """ Returns the `Data` instance that represents the login information of
        the given reddit username. """

        return self._access_db("users", username, "credentials")

    def generate_praw_instance(self,
                               username: str,
                               validate: bool = True,
                               ):
        """ Loads the login credentials from the database, generates an
        `praw.Reddit` instance and returns it.

        Raises an error of some credentials are missing!"""

        credentials = self.__get_user_credentials(username).get()
        if (not isinstance(credentials, dict)) or (
            not all(
                credential in credentials
                for credential in self._NEEDED_PRAW_CREDENTIALS
            )
        ):
                # If not all credentials are provided
            raise MissingCredentialsError(
                "One or more of the needed credentials for a request to reddit are not provided")

        # Create the praw instance
        reddit = praw.Reddit(**credentials)

        if validate and not self.check_valid_praw_instance(reddit):
            raise InvalidCredentialsError(
                f"Invalid credentials for Reddit username '{username}'")

        return reddit

    @staticmethod
    def check_valid_praw_instance(api: praw.Reddit):
        """ Sends a "dummy" request to the Reddit with the given `praw.Reddit`
        instance. If something is wrong, or the credentails are invalid, will
        return `False`. If everyting gone to plan, returns `True`. """

        try:
            # Requests information about the logged in user.
            # This forces the api to use the credentials - and validate them!
            api.user.me()

        except Exception:  # pylint: disable=broad-except
            # If something goes wrong, an exception will be raised.
            # This means the function should return `False`
            return False

        else:
            return True

    def update_user_credentials(self,
                                username: str,
                                password: str = None,
                                client_id: str = None,
                                client_secret: str = None,
                                ):
        """ Recives a Reddit username and additional login credentials, and
        saved the additional data in the user database. """

        login_db = self.__get_user_credentials(username)

        # Save the data given as arguments
        new_credentials = {
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "user_agent": self._DEFAULT_USER_AGENT
        }

        # Clear `None` values from the new data
        new_credentials = {
            key: new_credentials[key]
            for key in new_credentials
            if new_credentials[key] is not None
        }

        # Load the data that is not `None` from the database
        old_credentials = login_db.get()

        # Merge the new data with the old data
        credentials = dict()
        for key in self._NEEDED_PRAW_CREDENTIALS:
            if key in new_credentials:
                # If provided in the new data, save it.
                credentials[key] = new_credentials[key]

            elif key in old_credentials:
                # If already saved in the database, but not overwritted by new data
                credentials[key] = old_credentials[key]

        # Save the new generated credentials back to the database
        login_db.set(credentials)


class CredentialsError(Exception):
    """ Raised when trying to log in to a Reddit account, but something is
    wrong with the login credentials. """


class MissingCredentialsError(CredentialsError):
    """ Raised when trying to generate a request to the Reddit API,
    but not all of the needed credentials are provided (username, password,
    client_id, client_secret). """


class InvalidCredentialsError(CredentialsError):
    """ Raised when typing to log in to a Reddit account, but recives
    an error, which means some credentials are not correct. """
