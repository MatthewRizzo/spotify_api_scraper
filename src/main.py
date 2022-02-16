#------------------------------STANDARD DEPENDENCIES-----------------------------#
from argparse import *
import webbrowser

#------------------------------Project Imports-----------------------------#
from cli_parser import CLIParser
from scraper import Scraper
from data_parser import DataParser
from web_app import WebApp

class Main():
    def __init__(self, cli_args: dict) -> None:
        """
        Args:
            args (dict): Values after parsing the CLI inputs for this program
        """
        self.args = cli_args
        self.data_parser = DataParser()

        self.app = WebApp(cli_args['port'], cli_args['debugMode'], self.data_parser.get_auth_info())


if __name__ == "__main__":
    cli_parser = CLIParser()
    cli_args = cli_parser.args

    main = Main(cli_args)


