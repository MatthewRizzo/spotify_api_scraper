#------------------------------STANDARD DEPENDENCIES-----------------------------#
import requests
from typing import List, Optional, Dict
from flask import url_for
import requests
import base64
import random


#------------------------------Project Imports-----------------------------#
from utils import Utils

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
        self._auth_state_input = random.random()

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
        url += f"&state={self._auth_state_input}"
        return url

    def get_access_token(self,
                        user_auth_code: str,
                        client_id : int,
                        client_secret: int,
                        auth_redirect_uri: str) -> Optional[Dict]:
        """Given a user_auth_token, client_id, and client_secret, gets an acccess token
        \n:return Dict on success, None on failure.
        \n  Dict corresponds to https://developer.spotify.com/documentation/general/guides/authorization/code-flow/#response-1 """
        params = {"grant_type": "authorization_code",
                  "code": user_auth_code,
                  "redirect_uri": auth_redirect_uri}

        # header param must be base64 encoded with client_id:client_secret (<base64 encoded client_id:client_secret>)
        encoded_str = f"{client_id}:{client_secret}".encode('ascii')
        encoded_auth_bytes = base64.b64encode(encoded_str)
        encoded_auth_str = encoded_auth_bytes.decode()

        header_auth_str = 'Basic ' + encoded_auth_str
        headers = {'Authorization': header_auth_str,
                   "Content-Type": "application/x-www-form-urlencoded"}
        get_access_token_uri = Utils.get_base_spotify_accounts_uri() + "/api/token"

        # Send the request and get a response
        req = requests.post(get_access_token_uri,
                            params=params, headers=headers)
        access_token_res_dict = req.json()

        # Make sure the request is successful
        if 'error' in access_token_res_dict:
            print(f"ERROR getting access token: {access_token_res_dict}")
            return None

        access_token = access_token_res_dict['access_token']
        valid_for_sec = access_token_res_dict['expires_in']
        print(f"token {access_token} is valid for {valid_for_sec} seconds")
        return access_token_res_dict

    def get_user_id(self, access_token) -> str:
        """Given an access token, get the user's id
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-current-users-profile """
        user_profile_url = "https://api.spotify.com/v1/me"
        header = {"Authorization": "Bearer " + access_token,
                  "Content-Type": "application/json"}
        get_req = requests.get(user_profile_url, headers=header)
        raw_res = get_req.json()
        return str(raw_res['id'])


    def get_users_playlists(self, access_token) -> List:
        """Given the current authenticated user, get their playlists"""
        # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-list-of-current-users-playlists
        req_url = "https://api.spotify.com/v1/me/playlists"

        # represents everything after 'items':
        playlists = {}

        # hard coded into the api
        max_num_playlists = 50
        total_num_received = 0

        params = {'limit': max_num_playlists,
                  'offset': 0}
        header = {'Authorization': "Bearer " + access_token,
                  "Content-Type": "application/json"}
        # Get the id's of the playlists owned by the user
        get_playlist_ids_res = requests.get(req_url, params=params, headers=header).json()

        keep_going = True

        # Keep requesting the max number of playlists until all have been found. keep adding to dict
        while total_num_received < get_playlist_ids_res['total']:
            num_new_playlists = 0
            for new_playlist in get_playlist_ids_res['items']:
                playlists[new_playlist['id']] = new_playlist
                num_new_playlists += 1

            # adjust the offset in the params
            total_num_received += num_new_playlists
            params['offset'] = total_num_received

            get_playlist_ids_res = requests.get(
                req_url, params=params, headers=header).json()
        return playlists

    def refresh_access_token(self):
        # TODO: not sure if it is needed in the context of this app
        pass
