#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib


#------------------------------Project Imports-----------------------------#
from utils import Utils

class DataParser():
    def __init__(self) -> None:
        self.default_auth_filename = "default_app_auth.json"
        self.expected_auth_filename = "app_auth.json"

        self.default_auth_path = Utils.get_data_dir_path() / self.default_auth_filename
        self.expected_auth_path = Utils.get_data_dir_path() / self.expected_auth_filename

        if self._check_if_auth_file_exists():
            pass

    def get_auth_info(self) -> dict:
        print(f"self.expected_auth_path = {self.expected_auth_path}")
        with open(str(self.expected_auth_path)) as auth_file:
            return json.load(auth_file)

    def _check_if_auth_file_exists(self) -> bool:
        """Ensures the non-default auth file was created properly.
        :return True if it exists"""
        if not pathlib.Path(self.expected_auth_path).is_file():
            print(f"Expected authorization data file not found at {self.expected_auth_path}")
            print("Please see the /README.md for details about it's creation")
            exit
        else:
            return True

if __name__ == "__main__":
    data_parser = DataParser()
    print(data_parser.get_auth_info())
