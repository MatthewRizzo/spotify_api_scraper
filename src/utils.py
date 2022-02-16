#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib


class Utils():
    src_dir_path = pathlib.Path(__file__).parent.resolve()
    root_dir_path = src_dir_path.parent.resolve()
    path_to_data_dir = pathlib.Path(root_dir_path / "data")
    """Uility class to handle common things such as pathing"""

    @classmethod
    def get_src_dir_path(cls) -> pathlib.Path:
        return cls.src_dir_path

    @classmethod
    def get_root_dir_path(cls) -> pathlib.Path:
        return cls.root_dir_path

    @classmethod
    def get_data_dir_path(cls) -> pathlib.Path:
        return cls.path_to_data_dir
