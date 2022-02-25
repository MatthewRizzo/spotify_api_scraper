#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib
from typing import Tuple
from datetime import datetime, timedelta


class Utils():
    """Uility class to handle common things such as pathing"""
    src_dir_path = pathlib.Path(__file__).parent.resolve()
    root_dir_path = src_dir_path.parent.resolve()
    path_to_data_dir = pathlib.Path(root_dir_path / "data")
    frontend_dir_path = pathlib.Path(src_dir_path / "frontend")
    static_dir_path = pathlib.Path(frontend_dir_path / "static")
    templates_dir_path = pathlib.Path(frontend_dir_path / "templates")

    # url related stuff
    base_spotify_uri = "https://api.spotify.com"
    base_spotify_accounts_uri = 'https://accounts.spotify.com'

    @classmethod
    def get_src_dir_path(cls) -> pathlib.Path:
        return cls.src_dir_path

    @classmethod
    def get_root_dir_path(cls) -> pathlib.Path:
        return cls.root_dir_path

    @classmethod
    def get_data_dir_path(cls) -> pathlib.Path:
        return cls.path_to_data_dir

    @classmethod
    def get_frontend_dir_path(cls) -> pathlib.Path:
        return cls.frontend_dir_path

    @classmethod
    def get_static_dir_path(cls) -> pathlib.Path:
        return cls.static_dir_path

    @classmethod
    def get_templates_dir_path(cls) -> pathlib.Path:
        return cls.templates_dir_path

    @classmethod
    def get_base_spotify_api_uri(cls) -> pathlib.Path:
        return cls.base_spotify_uri

    @classmethod
    def get_base_spotify_accounts_uri(cls) -> pathlib.Path:
        return cls.base_spotify_accounts_uri

    @classmethod
    def escape_html_special_char(cls, str_to_escape: str) -> str:
        """:return Escaped string"""
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
            "\"": '\\"'
        }
        return "".join(html_escape_table.get(c, c) for c in str_to_escape)

    @classmethod
    def validate_key_format(cls, dict_to_check: dict, single_quote_escape_seq: str, double_quote_escape_seq: str) -> dict:
        """Given a dictionary, ensures all keys are formatted properly. i.e. that there are no " in the key name
        :param single_quote_escape_seq An escape sequence to denote this SHOULD be a single quote.
        \n:return the properly formatted dictionary and list of keys that were changed"""
        keys_to_change_single = []
        keys_to_change_double = []
        for key in dict_to_check.keys():
            if single_quote_escape_seq in key:
                keys_to_change_single.append(key)
            if double_quote_escape_seq in key:
                keys_to_change_double.append(key)

        for old_key in keys_to_change_single:
            new_key = str(old_key).replace(single_quote_escape_seq, "'")
            dict_to_check[new_key] = dict_to_check.pop(old_key)

            # also update the key to get changed for double quotes (if it has both)
            keys_to_change_double = list(map(lambda x: x.replace(old_key, new_key), keys_to_change_double))

        for old_key in keys_to_change_double:
            # make sure to escape the " so the html doesnt think a value is ending
            new_key = str(old_key).replace(double_quote_escape_seq, '\\"')
            dict_to_check[new_key] = dict_to_check.pop(old_key)

        return dict_to_check



    @classmethod
    def calc_end_time(cls, start_time : datetime, time_diff_sec : float) -> datetime:
        """Given a start time and time difference in seconds,
            calculates the end datetime in %m/%d/%Y %H:%M:%S notation"""

        datetime_delta = timedelta(seconds=time_diff_sec)
        end_time = (start_time + datetime_delta).strftime("%m/%d/%Y %H:%M:%S")
        return end_time
