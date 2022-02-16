#------------------------------STANDARD DEPENDENCIES-----------------------------#
import requests
from typing import Optional

class Scraper():
    def __init__(self) -> None:
        """Class responsible for sending requests to Spotify API's and building up the data files as needed
        """
        pass

    def get_playlist_info(self):
        """Sends requests to the API's to get playlist info"""

    def get_authenticate_url(self, client_id : str, redirect_uri : str) -> str:
        """Start the process of Login/authenticate the user
        \n:return The url WITHOUT the actual return url. must add that manually"""
        spotify_auth_base_url = "https://accounts.spotify.com/authorize?"
        client_id_param_str = "client_id=" +  client_id
        redirect_uri_param_str = "redirect_uri=" + redirect_uri
        response_type_param_str = "response_type=code"

        url = spotify_auth_base_url
        url += client_id_param_str
        url += "&"
        url += redirect_uri_param_str
        url += "&"
        url += response_type_param_str
        return url
