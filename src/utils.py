#------------------------------STANDARD DEPENDENCIES-----------------------------#
import json
import pathlib


class Utils():
    """Uility class to handle common things such as pathing"""
    src_dir_path = pathlib.Path(__file__).parent.resolve()
    root_dir_path = src_dir_path.parent.resolve()
    path_to_data_dir = pathlib.Path(root_dir_path / "data")
    frontend_dir_path = pathlib.Path(src_dir_path / "frontend")
    static_dir_path = pathlib.Path(frontend_dir_path / "static")
    templates_dir_path = pathlib.Path(frontend_dir_path / "templates")

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
