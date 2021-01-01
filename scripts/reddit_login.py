""" This script lets you save the data related to the reddit API locally,
so you don't have to type it everytime you want to run the bot! """

# pylint: disable=unused-import, invalid-name

import __init__  # to properly import the actual `KarmaRex` module
from KarmaRex.database import Database, UserDatabase
from KarmaRex.tools import DrawingBox


REQUIRED = [
    'username',
    'password',
    'client_id',
    'client_secret',
]

credentials = dict()
for cur in REQUIRED:
    credentials[cur] = input(f"Please enter your reddit {cur}: ")

user_db = UserDatabase(Database())
user_db.update_user_credentials(**credentials)

print(f"Saved credentials for '{credentials['username']}'.")
