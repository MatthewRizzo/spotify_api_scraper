#------------------------------STANDARD DEPENDENCIES-----------------------------#
import requests
from typing import List, Optional, Dict, Tuple
from flask import url_for
import base64
import random


#------------------------------Project Imports-----------------------------#
from utils import Utils
import constants

class Scraper():
    def __init__(self, is_verbose: bool) -> None:
        """Class responsible for sending requests to Spotify API's and building up the data files as needed
        """
        self._is_verbose = is_verbose

    def get_authenticate_url(self, client_id : str, redirect_uri : str) -> str:
        """Start the process of Login/authenticate the user
        \n:return The url WITHOUT the actual return url. must add that manually"""
        self._auth_state_input = str(random.random())

        spotify_auth_base_url = constants.SPOTIFY_AUTH_BASE_URL
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
                        auth_redirect_uri: str) -> Optional[Tuple[str, str, str]]:
        """Given a user_auth_token, client_id, and client_secret, gets an acccess token
        \n:return Tuple on success (access_token, refresh_token, valid_for_sec), None on failure.
        \n  Dict corresponds to https://developer.spotify.com/documentation/general/guides/authorization/code-flow/#response-1 """
        params = {"grant_type": "authorization_code",
                  "code": user_auth_code,
                  "redirect_uri": auth_redirect_uri}

        # header param must be base64 encoded with client_id:client_secret (<base64 encoded client_id:client_secret>)
        encoded_str = f"{client_id}:{client_secret}".encode('ascii')
        encoded_auth_bytes = base64.b64encode(encoded_str)
        encoded_auth_str = encoded_auth_bytes.decode()

        header_auth_str = 'Basic ' + encoded_auth_str

        header = constants.SPOTIFY_GET_AUTH_HEADER_FORMAT
        header["Authorization"] = header_auth_str

        get_access_token_uri = constants.SPOTIFY_TOKEN_URI

        # Send the request and get a response
        req = requests.post(get_access_token_uri,
                            params=params, headers=header)
        access_token_res_dict = req.json()

        # Make sure the request is successful
        if 'error' in access_token_res_dict:
            print(f"ERROR getting access token: {access_token_res_dict}")
            return (None, None, None)

        access_token = access_token_res_dict['access_token'] if 'access_token' in access_token_res_dict else None
        refresh_token = access_token_res_dict['refresh_token'] if 'refresh_token' in access_token_res_dict else None
        valid_for_sec = access_token_res_dict['expires_in'] if 'expires_in' in access_token_res_dict else None

        if self._is_verbose:
            print(f"Got a new access token valid for {valid_for_sec} seconds")
        return access_token, refresh_token, valid_for_sec

    def refresh_access_token(self, client_id: str, client_secret : str, refresh_token: str) -> Tuple[str, str]:
        """:return Tuple(new_access_token, new_valid_for_sec). values are Null on failure
        :docs https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
            see Request a refreshed Access Token for the format"""
        refresh_uri = constants.SPOTIFY_TOKEN_URI
        params = {"grant_type": "refresh_token",
                  "refresh_token": refresh_token,
                    }

        # header param must be base64 encoded with client_id:client_secret (<base64 encoded client_id:client_secret>)
        encoded_str = f"{client_id}:{client_secret}".encode('ascii')
        encoded_auth_bytes = base64.b64encode(encoded_str)
        encoded_auth_str = encoded_auth_bytes.decode()

        header_auth_str = 'Basic ' + encoded_auth_str
        header = constants.SPOTIFY_GET_AUTH_HEADER_FORMAT
        header["Authorization"] = header_auth_str

        req = requests.post(refresh_uri,
                            params=params, headers=header)
        refresh_access_token_res = req.json()

        # Make sure the request is successful
        if 'error' in refresh_access_token_res:
            print(f"ERROR getting access token: {refresh_access_token_res}")
            return None

        new_access_token = refresh_access_token_res['access_token'] if 'access_token' in refresh_access_token_res else None
        new_valid_for_sec = refresh_access_token_res['expires_in'] if 'expires_in' in refresh_access_token_res else None
        return new_access_token, new_valid_for_sec


    def get_user_id(self, access_token) -> str:
        """Given an access token, get the user's id
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-current-users-profile """
        header = constants.SPOTIFY_AUTHORIZED_HEADER_FORMAT
        header["Authorization"] = "Bearer " + access_token
        get_req = requests.get(constants.SPOTIFY_USER_PROFILE_URI, headers=header)
        raw_res = get_req.json()
        return str(raw_res['id'])


    def get_users_playlists(self, access_token) -> List:
        """Given the current authenticated user, get their playlists"""
        # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-a-list-of-current-users-playlists

        # represents everything after 'items':
        playlists = {}

        # hard coded into the api
        max_num_playlists = 50
        total_num_received = 0

        params = {'limit': max_num_playlists,
                  'offset': 0}
        header = constants.SPOTIFY_AUTHORIZED_HEADER_FORMAT
        header["Authorization"] = "Bearer " + access_token

        # Get the id's of the playlists owned by the user
        get_playlist_ids_res = requests.get(constants.SPOTIFY_GET_USER_PLAYLISTS_URI,
                                            params=params,
                                            headers=header).json()

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
                constants.SPOTIFY_GET_USER_PLAYLISTS_URI,
                params=params,
                headers=header).json()
        return playlists

    def get_songs_from_playlist(self, playlist_id: str, access_token : str
                                ) -> Tuple[List, str, str]:
        """Given a playlist id, grabs all of the songs from the playlist
        \n:return Tuple of (unprocessed list of tracks, playlist_name, total_num_tracks)
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-playlist
        \n:docs for return "tracks" - https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track
        """

        tracks_in_playlist = []
        playlist_name = None

        base_playlist_url = constants.SPOTIFY_GET_PLAYLIST_URI

        next_url = f"{base_playlist_url}/{playlist_id}/"
        header = constants.SPOTIFY_AUTHORIZED_HEADER_FORMAT
        header["Authorization"] = "Bearer " + access_token

        # Keep grabbing tracks from the playlist until return says there are no more
        while next_url is not None:
            req = requests.get(next_url, headers=header).json()

            # The first request will be larger than subsequent ones
            # Following ones are JUST the vlaues after "tracks" key
            track_list = []
            res_top_level = req
            if "tracks" in req:
                res_top_level = req["tracks"]
                total_num_tracks = res_top_level['total']
                playlist_name = req["name"]

            next_url = res_top_level["next"]
            track_list = res_top_level["items"]


            # see https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track
            # for description of what each track looks like
            # Note: after 1st request, response is ONLY values within "tracks"
            for track in track_list:
                tracks_in_playlist.append(track["track"])

        return (tracks_in_playlist, playlist_name, total_num_tracks)

    @classmethod
    def get_artist_info(cls, artist_url : str, access_token : str) -> Optional[List[str]]:
        """Given the spotify url to request, returns info about the artist
        \n: return List of genres
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artist """
        header = constants.SPOTIFY_AUTHORIZED_HEADER_FORMAT
        header["Authorization"] = "Bearer " + access_token
        raw_artist_res = requests.get(artist_url, headers=header)

        if (
            raw_artist_res.status_code != 204 and
            raw_artist_res.headers["content-type"].strip().startswith("application/json")
        ):
            artist_req = raw_artist_res.json()
            return artist_req["genres"]
        else:
            return None
