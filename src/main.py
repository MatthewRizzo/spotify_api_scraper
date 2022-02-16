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

        self.app = WebApp(
            port = cli_args['port'],
            is_debug=cli_args['debugMode'],
            secret_key = self.data_parser.get_auth_info()['client_secret'])

    def authenticate_user(self):
        """Login/authenticate the user"""
        auth_info = self.data_parser.get_auth_info()
        spotify_auth_base_url = "https://accounts.spotify.com/authorize?"
        client_id_param_str = "client_id=" + auth_info['client_id']
        redirect_uri_param_str = "redirect_uri=" + auth_info['redirect_uri']
        response_type_param_str = "response_type=code"

        url = spotify_auth_base_url
        url += client_id_param_str
        url += "&"
        url += redirect_uri_param_str
        url += "&"
        url += response_type_param_str



if __name__ == "__main__":
    cli_parser = CLIParser()
    cli_args = cli_parser.args

    main = Main(cli_args)
    main.authenticate_user()


