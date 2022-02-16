#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib
import io
from typing import Optional
from datetime import datetime
import os

#------------------------------Project Imports-----------------------------#
from utils import Utils

class DataManager():
    def __init__(self) -> None:
        self.default_auth_filename = "default_app_auth.json"
        self.expected_auth_filename = "app_auth.json"
        self.expected_user_data_filename = "user_info.json"

        self.default_auth_path = Utils.get_data_dir_path() / self.default_auth_filename
        self.expected_auth_path = Utils.get_data_dir_path() / self.expected_auth_filename
        self.expected_user_data_path = Utils.get_data_dir_path() / self.expected_user_data_filename

        if self._check_if_auth_file_exists():
            pass

        self._create_user_file_if_needed()

    def get_auth_info(self) -> dict:
        with open(str(self.expected_auth_path)) as auth_file:
            return json.load(auth_file)

    def save_users_access_token(self, access_token: int, user_id: int, valid_until: datetime) -> bool:
        """Stores the access token for the given user id within the user json.
        If the user already exists, replaces their old access_token value

        Args:
            access_token (int): the access token after authentication for this user
            user_id (int): User ID ACCORDING to spotify

        Returns:
            bool: True on success
        """
        # Read in the current json
        data_json = {}
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data_json = json.load(user_file)

        data_json[user_id] = {'access_token': access_token,
                              'valid_until': valid_until}

        # replace the data
        with open(pathlib.Path(self.expected_user_data_path), 'w') as user_file:
            json.dump(data_json, user_file, indent=2)

        return True

    def get_users_access_token(self, user_id) -> Optional[int]:
        """Gets the user's access token.
        :return int if access token found, None otherwise"""
        user_dict = self._get_user_dict(user_id)
        if user_dict is not None:
            return user_dict['access_token']
        else:
            return None

    def _is_token_valid(self, user_id) -> bool:
        """Given a user'is id, determines if their token is invalid.
        :Return True if expired, False otherwise."""
        user_dict = self._get_user_dict(user_id)
        token_expire_time_formatted = user_dict['valid_until']
        expire_time = datetime.strptime(token_expire_time_formatted, "%m/%d/%Y %H:%M:%S")

        present = datetime.now()
        if present > expire_time:
            return False
        else:
            return True


    def _check_if_auth_file_exists(self) -> bool:
        """Ensures the non-default auth file was created properly.
        :return True if it exists"""
        if not pathlib.Path(self.expected_auth_path).is_file():
            print(f"Expected authorization data file not found at {self.expected_auth_path}")
            print("Please see the /README.md for details about it's creation")
            exit
        else:
            return True

    def _create_user_file_if_needed(self):
        # Create the file if it doesn't exist
        if not os.path.exists(self.expected_user_data_path):
            print("creating user file")
            with io.open(self.expected_user_data_path, 'w') as user_file:
                user_file.write(json.dumps({}))

    def _get_user_dict(self, user_id) -> dict:
        with open(pathlib.Path(self.expected_user_data_path), 'r') as user_file:
            data_json = json.load(user_file)
            if user_id in data_json:
                return data_json[user_id]
            else:
                return None

if __name__ == "__main__":
    data_parser = DataManager()
    print(data_parser.get_auth_info())