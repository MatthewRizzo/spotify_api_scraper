#------------------------------STANDARD DEPENDENCIES-----------------------------#
from argparse import *
import webbrowser

#------------------------------Project Imports-----------------------------#
from parse_manager import ParseManager
from scraper import Scraper
from data_parser import DataParser

class Main():
    def __init__(self, args: dict) -> None:
        """
        Args:
            args (dict): Values after parsing the CLI inputs for this program
        """
        self.data_parser = DataParser()

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
        auth_page = webbrowser.open(url)



if __name__ == "__main__":
    parser = ParseManager()
    args = parser.args

    main = Main(args)
    main.authenticate_user()


