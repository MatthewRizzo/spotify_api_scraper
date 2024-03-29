#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib
import io
from typing import Dict, Optional
from datetime import datetime
import os
import sys

#------------------------------Project Imports-----------------------------#
from utils import Utils
import constants

class DataManager():
    def __init__(self) -> None:
        self._default_auth_filename = constants.DEFAULT_AUTH_FILENAME
        self._expected_auth_filename = constants.EXPECTED_AUTH_FILENAME
        self._expected_user_data_filename = constants.EXPECTED_USER_DATA_FILENAME
        self._expected_artist_genre_filename = constants.EXPECTED_ARTIST_TO_GENRE_MAP_FILENAME

        self.default_auth_path = Utils.get_data_dir_path() / self._default_auth_filename
        self.expected_auth_path = Utils.get_data_dir_path() / self._expected_auth_filename
        self.expected_user_data_path = Utils.get_data_dir_path() / self._expected_user_data_filename
        self.expected_artist_genre_path = Utils.get_data_dir_path() / self._expected_artist_genre_filename

        if not self._check_if_auth_file_exists():
            sys.exit()

        if not self._check_if_auth_file_valid():
            sys.exit()

        self._create_json_file_if_not_exist(self.expected_user_data_path)
        self._create_json_file_if_not_exist(self.expected_artist_genre_path)

    def get_auth_info(self) -> dict:
        with open(str(self.expected_auth_path)) as auth_file:
            return json.load(auth_file)

    def save_users_access_token(self, access_token: int, user_id: int, valid_until: datetime, refresh_token : str) -> bool:
        """Stores the access token for the given user id within the user json.
        If the user already exists, replaces their old access_token value

        Args:
            access_token (int): the access token after authentication for this user
            user_id (int): User ID ACCORDING to spotify
            refresh_token (str): The refresh token given by spotify on user auth to make refreshing easier

        Returns:
            bool: True on success
        """
        # Read in the current json
        data_json = {}
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data_json = json.load(user_file)

        data_json[user_id] = {'access_token': access_token,
                              'valid_until': valid_until,
                              'refresh_token': refresh_token}

        # replace the data
        with open(pathlib.Path(self.expected_user_data_path), 'w') as user_file:
            json.dump(data_json, user_file, indent=2)

        return True

    def get_users_access_token(self, user_id) -> Optional[str]:
        """Gets the user's access token.
        :return int if access token found, None otherwise"""
        user_dict = self._get_user_dict(user_id)
        if user_dict is not None:
            return user_dict['access_token']
        else:
            return None

    def get_users_refresh_token(self, user_id) -> Optional[str]:
        user_dict = self._get_user_dict(user_id)
        if user_dict is not None:
            refresh_token = user_dict['refresh_token']
            return refresh_token
        else:
            return None

    def remove_users_refresh_token(self, user_id) -> bool:
        """Removes a users refresh token. useful on logout"""
        # Read in the current json
        data_json = {}
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data_json = json.load(user_file)

        if user_id in data_json:
            data_json[user_id]['refresh_token'] = None

        # replace the data
        with open(pathlib.Path(self.expected_user_data_path), 'w') as user_file:
            json.dump(data_json, user_file, indent=2)

        return True

    def is_token_valid(self, user_id) -> bool:
        """Given a user'is id, determines if their token is invalid.
        :Return True if expired, False otherwise."""
        user_dict = self._get_user_dict(user_id)
        if user_dict is not None:
            token_expire_time_formatted = user_dict['valid_until']
            time_frmt_str = constants.TIME_FORMAT_STR
            expire_time = datetime.strptime(token_expire_time_formatted, time_frmt_str)

            present = datetime.now()
            if present > expire_time:
                return False
            else:
                return True
        else:
            return False

    def does_user_exist(self, user_id) ->bool:
        """True if user exists, false otherwise"""
        data = None
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data = dict(json.load(user_file))
        return user_id in data

    def remove_user_login_info(self, user_id) -> None:
        """Call when a user logs out to remove all of their auth info
        \n`:precondition` The user exists
        \n`:postcondition` All information relating to the user is deleted"""
        # Read in the current json
        data_json = {}
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data_json = json.load(user_file)

        if user_id in data_json:
            del data_json[user_id]

        # replace the data
        self._write_to_json_file(self.expected_user_data_path, data_json)

        return True

    def get_artist_genre_mappings(self) -> Dict:
        """:return The Existing map of artist_name -> List[genres] saved locally"""
        mapping_dict = {}
        with open(pathlib.Path(self.expected_artist_genre_path), 'r') as artist_to_genre_map_file:
            mapping_dict = json.load(artist_to_genre_map_file)
        return mapping_dict

    def update_artist_genre_mappings(self, new_mappings : dict) -> bool:
        """Given a dictionary of artist_name -> List[genres], adds these new mapping to the map file"""
        self._update_json_file(self.expected_artist_genre_path, new_mappings)

    def _check_if_auth_file_exists(self) -> bool:
        """Ensures the non-default auth file was created properly.
        :return True if it exists"""
        if not pathlib.Path(self.expected_auth_path).is_file():
            print(f"Expected authorization data file not found at {self.expected_auth_path}")
            print("Please see the /README.md for details about it's creation")
            False
        else:
            return True

    def _check_if_auth_file_valid(self) -> bool:
        """:return true if the file is in the right format, false otherwise
        \n:pre The file exists"""
        auth_dict = {}
        is_valid = True
        with open(pathlib.Path(self.expected_auth_path), 'r') as auth_file:

            auth_dict = json.load(auth_file)

        # file should contain VALID strs for client_id and client_secret
        # i.e. not the default values
        is_valid &= "client_id" in auth_dict.keys()
        if(is_valid):
            is_valid &= auth_dict["client_id"] != constants.DEFAULT_CLIENT_ID
        is_valid &= "client_secret" in auth_dict.keys()
        if(is_valid):
            is_valid &= auth_dict["client_secret"] != constants.DEFAULT_CLIENT_SECRET

        if is_valid is False:
            print(f"The format of your {self._expected_auth_filename} is incorrect")
            print('Please be sure to have "client_id": <value>, "client_secret": <value>')
            print(f'Where <value> is NOT the word seen in the default file {self._default_auth_filename}')

        return is_valid

    def _create_json_file_if_not_exist(self, full_path):
        # create the file if it doesn't exist
        if not os.path.exists(full_path):
            with io.open(full_path, 'w') as new_file:
                new_file.write(json.dumps({}))

    def _get_user_dict(self, user_id) -> dict:
        res = None
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data_json = dict(json.load(user_file))
            if user_id in data_json:
                res = dict(data_json[user_id])
        return res

    def _write_to_json_file(self, path_to_json : str, dict_to_write : dict) -> None:
        """Given a json file's path and the FULL data to `overwrite` it with, write it to the file
        \n:NOTE: THIS WILL OVERWRITE THE CURRENT FILE CONTENTS"""
        with open(pathlib.Path(path_to_json), 'w') as file:
            json.dump(dict_to_write, file, indent=2)

    def _read_from_json_file(self, path_to_json : str) -> dict:
        """:return the entire json file"""
        data = {}
        with open(pathlib.Path(path_to_json), 'r') as file:
            data = dict(json.load(file))
        return data

    def _update_json_file(self, path_to_json: str, dict_to_update_with: dict) -> None:
        """Given a json file's path, updates the file with the information given.
        \n:NOTE: it WILL modify existing values if dict_to_update_with has a key that already exists in the file"""
        json_data = self._read_from_json_file(path_to_json)
        json_data.update(dict_to_update_with)
        self._write_to_json_file(path_to_json, json_data)

if __name__ == "__main__":
    data_parser = DataManager()
    print(data_parser.get_auth_info())
