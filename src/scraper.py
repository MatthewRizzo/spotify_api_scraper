import requests
from typing import Optional

class Scraper():
    def __init__(self) -> None:
        """Class responsible for sending requests to Spotify API's and building up the data files as needed
        """
        pass

    def authenticate(self, username : str, pwd : str) -> bool:
        """Logs in to a user's spotify given the login info"""
        pass

    def get_playlist_info(self):
        """Sends requests to the API's to get playlist info"""
