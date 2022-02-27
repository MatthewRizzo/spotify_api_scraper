#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from typing import List, Dict, Optional, Tuple

#------------------------------Project Imports-----------------------------#
import constants
from utils import Utils
from scraper import Scraper
from data_manager import DataManager

class Analyzer():
    def __init__(self, is_verbose, data_mananger_obj : DataManager) -> None:
        """Class Used to analyze the data coming out of scraper in a form usable by WebApp"""
        self._is_verbose = is_verbose
        self._data_manager = data_mananger_obj

    def analyze_raw_track_list(self, raw_track_list: List[Dict], access_token : str) -> Tuple[Dict, Dict, Dict]:
        """Given a list of raw track dicts from the API call itself, grabs all relevant info and does some analytics.
        \n:param access_token the access token received after authentication
        \n:return a Tuple of (chart_data_artist, chart_data_album, chart_data_genre).
        Each entry of the tuple is a Dict (with html/json safe keys).
        Each dict is readily usable for the rendering of the pie-charts.
        \n`NOTE:` before using the dictionaries to make the chart, use `Utils.prep_keys_for_html()`
            to unescape the key names"""
        # eventual returns
        analyzed_chart_data_artist = {}
        analyzed_chart_data_album = {}
        analyzed_chart_data_genre = {}

        existing_artist_genre_mapping = self._data_manager.get_artist_genre_mappings()

        artist_to_url_map = {}

        for raw_track in raw_track_list:
            processed_track = self.parse_raw_track(raw_track, artist_to_url_map, existing_artist_genre_mapping)

            cur_track = processed_track["track_name"]

            # Perform metric calcs for each artist and album - functions update in place
            cur_artist = self._analyze_raw_track_artists(processed_track, analyzed_chart_data_artist)
            cur_album = self._analyze_raw_track_album(processed_track, analyzed_chart_data_album)

            if self._is_verbose:
                print("Track {} by {} from their {} album".format(
                    cur_track, cur_artist, cur_album
                ))

        self._analyze_playlist_for_genre(analyzed_chart_data_artist,
                                         analyzed_chart_data_genre,
                                         artist_to_url_map,
                                         existing_artist_genre_mapping,
                                         access_token)

        # Make sure all of the genres are put in a valid form for json keys
        # replace all keys with ' or " in them with escape sequences
        # Will get converted back later
        self._prep_keys_for_json(analyzed_chart_data_artist)
        self._prep_keys_for_json(analyzed_chart_data_album)
        self._prep_keys_for_json(analyzed_chart_data_genre)

        return (analyzed_chart_data_artist, analyzed_chart_data_album, analyzed_chart_data_genre)

    def parse_raw_track(self, raw_track, artist_url_map: dict, existing_artist_genre_mapping : dict) -> dict:
        """Given a raw track from the get-track API, returns just the information we care about
        \n:param raw_track - the rest from the get-track API call
        \n:param artist_url_map - Maps each artist's name to the url to query them. Modifies this `in place`
        \n:param existing_artist_genre_mapping - Existing map of artist_name -> genre.
            Dont add to `artist_url_map` if the genre is already known
        \n:return Dict that maps track_name to other info:
            keys: {track_id: { track_name, album, artist(s) } }.
            Note: artists will be lists, but will mostly be of length 1
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artist"""
        res_dict = {}
        res_dict["track_id"] = raw_track["id"]
        res_dict["track_name"] = raw_track["name"]
        res_dict["album"] = raw_track["album"]["name"]
        res_dict["artists"] = []

        # contains info about the artist of this track
        for artist_dict in raw_track["artists"]:
            artist_name = artist_dict["name"]
            res_dict["artists"].append(artist_name)

        # only care about the primary artist of the song for purpose of id tracking / genre
        lead_artist_dict = raw_track["artists"][0]
        lead_artist_name = lead_artist_dict["name"]

        # Only try to find the genres of this artist if it is not already known
        if lead_artist_name not in existing_artist_genre_mapping.keys():
            did_add = self._update_artist_url_map(artist_url_map, lead_artist_dict)

        return res_dict

    def _analyze_raw_track_artists(self, cur_parsed_track: Dict, cur_artist_info : Dict) -> str:
        """:brief Given a track to analyze and the current analysis dict,\
            updates `cur_artist_info` after analyzing the current track `IN PLACE`.
        \n:param `cur_parsed_track` a dict representing a parsed track
        \n:param `cur_artist_info` The current metrics on artists. `Will get updated in place`
        :return The artist of the current track
        """
        cur_artist = cur_parsed_track["artists"][0]

        # do the metric calculations and update the results
        # TODO: better handle features
        # TODO - try an abstract this to a function - for the other analyze functions too
        cur_num_tracks_by_artist = cur_artist_info.get(cur_artist, 0)
        cur_num_tracks_by_artist += 1
        cur_artist_info[cur_artist] = cur_num_tracks_by_artist

        return cur_artist

    def _analyze_raw_track_album(self, cur_parsed_track: Dict, cur_album_info: Dict) -> str:
        """:brief Given a track to analyze and the current analysis dict,\
            updates `cur_album_info` after analyzing the current track `IN PLACE`.
        \n:param `cur_parsed_track` a dict representing a parsed track
        \n:param `cur_album_info` The current metrics on albums. `Will get updated in place`
        \n:return The current album name
        """
        cur_album = str(cur_parsed_track["album"])
        if cur_album == "" or cur_album == " ":
            cur_album = constants.DEFAULT_NO_ALBUM_NAME

        cur_num_tracks_in_album = cur_album_info.get(cur_album, 0)
        cur_num_tracks_in_album += 1
        cur_album_info[cur_album] = cur_num_tracks_in_album

        return cur_album

    def _analyze_playlist_for_genre(self,
                                analyzed_artist_dict: Dict,
                                genre_info: Dict,
                                artist_to_url_map : dict,
                                existing_artist_genre_mapping : dict,
                                access_token : str) -> None:
        """:brief Given a track to analyze and the current analysis dict,\
            updates `cur_genre_info` after analyzing the current track `IN PLACE`.
        \n:param `analyzed_artist_dict` a dict representing the final analysis of artists
        \n:param `genre_info` The genre metrics. `Generated in this function`
        \n:param `artist_to_url_map` Maps a artist's name to their spotify API URI
        \n:param existing_artist_genre_mapping - Existing map of artist_name -> genre.
        \n:param `access_token` The token recieved on authentication from spotify
        \n:return None
        """
        # Used to update the local file oncne all new mappings have been discovered
        new_artist_genre_mappings = {}

        # For each artist, grab their genres from spotify and use that in metric calculations
        for artist in analyzed_artist_dict.keys():
            if artist not in artist_to_url_map.keys():
                if self._is_verbose:
                    print(f"ERROR: artist {artist} does not have a spotify url to query")
                continue
            artist_url = artist_to_url_map[artist]
            artist_genres = Scraper.get_artist_info(artist_url, access_token)

            # Update the count of a given genre in the playlist
            artist_track_count = analyzed_artist_dict[artist]
            self._update_genre_count(artist_genres, genre_info, artist_track_count)

            new_artist_genre_mappings.update({artist: artist_genres})

        # Update the count using artists whose info is already saved locally
        for artist, artist_genres in existing_artist_genre_mapping.items():
            artist_track_count = analyzed_artist_dict[artist]
            self._update_genre_count(artist_genres, genre_info, artist_track_count)

        self._data_manager.update_artist_genre_mappings(new_artist_genre_mappings)

    def _prep_keys_for_json(self, analyzed_data : dict) -> None:
        """Given a dictionary of the analyzed_data (from its respective processing function),
        makes keys valid -> replaces ' and " with escape sequences.
        \nNOTE: done `in place`"""
        unescaped_key_change_lists = Utils.get_keys_with_unescaped_quotes(analyzed_data)
        keys_to_escape_single, keys_to_escape_double = unescaped_key_change_lists

        # Used to remove ' from key names until it is safe to put them back in
        # eventually the ' wrapped around key's are ALL changed to ",
        # but that will also change ' in the keys to " which is BAD for parsing.
        # change the ' to know what they are later
        Utils.swap_dict_keys(analyzed_data, keys_to_escape_single)
        Utils.swap_dict_keys(analyzed_data, keys_to_escape_double)

    def _update_artist_url_map(self, artist_url_map: dict, lead_artist_dict : dict) -> bool:
        """Checks if the artist is in the artist->api url map. Adds it if it is not.
        \n:return True on artist url added, False if not added"""
        lead_artist_name = lead_artist_dict["name"]
        did_add = False

        if lead_artist_name not in artist_url_map.keys():

            # Can't trust the given external url for then querying info about the artist
            # Build it from base url + getting their id
            artist_id = lead_artist_dict["id"]

            # Local files aren't actual artists and so they might not have id's, skip them
            if artist_id is None and self._is_verbose:
                print(f"Skipping genre collection for Local File with artist {lead_artist_name}")
            else:
                artist_url = constants.SPOTIFY_ARTIST_BASE_URI + artist_id
                artist_url_map[lead_artist_name] = artist_url
                did_add = True

        return did_add

    def _update_genre_count(self, artist_genres : List[str], genre_info : dict, artist_track_count : int):
        """:brief Updates the genre count dictionary
        \n:param `artist_genres` The list of genres a given artist is associated with
        \n:param `artist_track_count` The number of times the artist has a track in the playlist
        \n:param `genre_info` The genre metrics used for the chart. Gets updated in this function"""
        # Update the count of a given genre in the playlist
        for cur_genre in artist_genres:
            if cur_genre == "" or cur_genre == " ":
                cur_genre = constants.DEFAULT_NO_GENRE_NAME
            cur_genre_count_in_playlist = genre_info.get(cur_genre, 0)

            # Count the genre for the number of times this artist is in the playlist
            cur_genre_count_in_playlist += artist_track_count
            genre_info[cur_genre] = cur_genre_count_in_playlist
