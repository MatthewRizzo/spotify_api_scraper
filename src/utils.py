#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib
from typing import Tuple, List
from datetime import datetime, timedelta

#------------------------------Project Imports-----------------------------#
import constants

class Utils():
    """Uility class to handle common things such as pathing"""
    src_dir_path = pathlib.Path(__file__).parent.resolve()
    root_dir_path = src_dir_path.parent.resolve()
    path_to_data_dir = pathlib.Path(root_dir_path / constants.DATA_DIR_NAME)
    frontend_dir_path = pathlib.Path(src_dir_path / constants.FRONTEND_DIR_NAME)
    static_dir_path = pathlib.Path(frontend_dir_path / constants.STATIC_DIR_NAME)
    templates_dir_path = pathlib.Path(frontend_dir_path / constants.TEMPLATE_DIR_NAME)


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
    def get_spotify_accounts_base_uri(cls) -> pathlib.Path:
        return constants.SPOTIFY_ACCOUNTS_BASE_URI

    @classmethod
    def escape_html_special_char(cls, str_to_escape: str) -> str:
        """:return Escaped string"""
        escape_char_map = constants.HTML_CHAR_ESCAPE_TABLE
        return "".join(escape_char_map.get(c, c) for c in str_to_escape)

    @classmethod
    def swap_dict_keys(cls, dict_to_swap :dict, replace_key : List[Tuple[str, str]]) -> None:
        """Given a dictionary that needs some of its keys swapped, swap `old_key` with `new_key` in place
        \n:param replace_key (old_key, new_key)"""
        for swap_pair in replace_key:
            dict_to_swap[swap_pair[1]] = dict_to_swap.pop(swap_pair[0])


    @classmethod
    def prep_keys_for_html(cls, dict_to_check: dict, single_quote_escape_seq: str, double_quote_escape_seq: str) -> dict:
        """Given a dictionary, ensures all keys are formatted properly. i.e. that there are no " in the key name
        :param single_quote_escape_seq An escape sequence to denote this SHOULD be a single quote.
        \n:return the properly formatted dictionary and list of keys that were changed"""
        change_lists = cls.get_keys_with_quotes(dict_to_check, single_quote_escape_seq, double_quote_escape_seq)
        keys_to_change_single, keys_to_change_double = change_lists

        # list of tuples
        # keys_to_change_single = []
        # keys_to_change_double = []
        # for key in dict_to_check.keys():
        #     has_single_quote = single_quote_escape_seq in key
        #     if has_single_quote:
        #         new_key = str(key).replace(single_quote_escape_seq, "'")
        #         keys_to_change_single.append((key, new_key))
        #     if double_quote_escape_seq in key:
        #         old_key = key
        #         if has_single_quote:
        #             # account for what the key will look like AFTER it has single quote replaced
        #             old_key = keys_to_change_single[-1][1]

        #         new_key = str(old_key).replace(double_quote_escape_seq, "'")
        #         keys_to_change_double.append((old_key, new_key))

        # swap keys with single quote and THEN double quote
        cls.swap_dict_keys(dict_to_check, keys_to_change_single)
        cls.swap_dict_keys(dict_to_check, keys_to_change_double)

        # for old_key in keys_to_change_single:
        #     dict_to_check[new_key] = dict_to_check.pop(old_key)

        #     # also update the key to get changed for double quotes (if it has both)
        #     keys_to_change_double = list(map(lambda x: x.replace(old_key, new_key), keys_to_change_double))

        # for old_key in keys_to_change_double:
        #     # make sure to escape the " so the html doesnt think a value is ending
        #     new_key = str(old_key).replace(double_quote_escape_seq, '\\"')
        #     dict_to_check[new_key] = dict_to_check.pop(old_key)

        return dict_to_check

    @classmethod
    def prep_dict_for_html(cls, raw_json_str : str,
                           single_quote_escape_seq : str,
                           double_quote_escape_seq : str) -> dict:
        """Given a json in str format from a request.args.to_dict() that WAS a json, \
            ensure it is in a valid dictionary/HTML format for the charts.
        :return The properly formatted dict"""
        raw_json_str = str(raw_json_str).replace("\'", "\"").replace("\n", " ")
        raw_json_dict = {} if raw_json_str is None else raw_json_str

        converted_dict = json.loads(raw_json_dict)

        final_converted_dict = Utils.prep_keys_for_html(
            converted_dict, single_quote_escape_seq, double_quote_escape_seq)

        return final_converted_dict


    @classmethod
    def calc_end_time(cls, start_time : datetime, time_diff_sec : float) -> datetime:
        """Given a start time and time difference in seconds,
            calculates the end datetime in %m/%d/%Y %H:%M:%S notation"""

        datetime_delta = timedelta(seconds=time_diff_sec)
        end_time = (start_time + datetime_delta).strftime(constants.TIME_FORMAT_STR)
        return end_time

    @classmethod
    def get_keys_with_quotes(cls, dict_to_check: dict,
                             single_quote_escape_seq: str,
                             double_quote_escape_seq: str
                             ) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """:return (keys_with_single_quotes, keys_with_double_quotes)
        where each of those is a LIST of Tuples -> (old_key, new_key)"""
        # list of tuples
        keys_to_change_single = []
        keys_to_change_double = []
        for key in dict_to_check.keys():
            has_single_quote = single_quote_escape_seq in key
            if has_single_quote:
                new_key = str(key).replace(single_quote_escape_seq, "'")
                keys_to_change_single.append((key, new_key))
            if double_quote_escape_seq in key:
                old_key = key
                if has_single_quote:
                    # account for what the key will look like AFTER it has single quote replaced
                    old_key = keys_to_change_single[-1][1]

                new_key = str(old_key).replace(double_quote_escape_seq, "'")
                keys_to_change_double.append((old_key, new_key))
        return (keys_to_change_single, keys_to_change_double)
