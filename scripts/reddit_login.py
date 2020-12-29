""" This script lets you save the data related to the reddit API locally,
so you don't have to type it everytime you want to run the bot! """

# pylint: disable=invalid-name,unused-import

import __init__  # to properly import the actual `redditkarma` module
from redditkarma.database import UserDatabase

REQUIRED = [
    'username',
    'password',
    'client_id',
    'client_secret',
]

credentials = dict()
for cur in REQUIRED:
    credentials[cur] = input(f"Please enter your reddit {cur}: ")

# Automatically saves the data when script ends
db = UserDatabase(**credentials)
print(f"Saved data for '{credentials['username']}'.")
