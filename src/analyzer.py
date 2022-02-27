#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from typing import List, Dict, Optional, Tuple

#------------------------------Project Imports-----------------------------#
import constants
from utils import Utils

class Analyzer():
    def __init__(self, is_verbose) -> None:
        """Class Used to analyze the data coming out of scraper in a form usable by WebApp"""
        self._is_verbose = is_verbose

    def analyze_raw_track_list(self, raw_track_list: List[Dict]) -> Tuple[Dict, Dict, Dict]:
        """Given a list of raw track dicts from the API call itself, grabs all relevant info and does some analytics.
        \n:return a Tuple of (chart_data_artist, chart_data_album, chart_data_genre).
        Each entry of the tuple is a Dict (with html/json safe keys).
        Each dict is readily usable for the rendering of the pie-charts.
        \n`NOTE:` before using the dictionaries to make the chart, use `Utils.prep_keys_for_html()`
            to unescape the key names"""
        # eventual returns
        analyzed_chart_data_artist = {}
        analyzed_chart_data_album = {}
        analyzed_chart_data_genre = {}

        artist_to_url = {}

        for raw_track in raw_track_list:
            processed_track = self.parse_raw_track(raw_track, artist_to_url)

            cur_track = processed_track["track_name"]

            # Perform metric calcs for each artist and album - functions update in place
            cur_artist = self._analyze_raw_track_artists(processed_track, analyzed_chart_data_artist)
            cur_album = self._analyze_raw_track_album(processed_track, analyzed_chart_data_album)


            if cur_album == " " or cur_album == '':
                cur_album = constants.DEFAULT_NO_ALBUM_NAME_MSG

            if self._is_verbose:
                print("Track {} by {} from their {} album".format(
                    cur_track, cur_artist, cur_album
                ))

        # self._analyze_playlist_for_genre(analyzed_chart_data_artist, analyzed_chart_data_genre)


        # Make sure all of the genres are put in a valid form for json keys
        # replace all keys with ' or " in them with escape sequences
        # Will get converted back later
        self._prep_keys_for_json(analyzed_chart_data_artist)
        self._prep_keys_for_json(analyzed_chart_data_album)
        # self._prep_keys_for_json(analyzed_chart_data_genre)

        return (analyzed_chart_data_artist, analyzed_chart_data_album, analyzed_chart_data_genre)

    def parse_raw_track(self, raw_track, artist_url_map: dict) -> dict:
        """Given a raw track from the get-track API, returns just the information we care about
        \n:param raw_track - the rest from the get-track API call
        \n:param artist_url_map - Maps each artist's name to the url to query them
        \n:return Dict that maps track_name to other info:
            keys: {track_id: { track_name, album, artist(s), genre(s) } }.
            Note: artists and genres will be lists, but will mostly be of length 1
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track"""
        res_dict = {}
        res_dict["track_id"] = raw_track["id"]
        res_dict["track_name"] = raw_track["name"]
        res_dict["album"] = raw_track["album"]["name"]
        res_dict["artists"] = []

        print("artists = {}".format(raw_track["artists"]))

        # contains info about the artist of this track
        for artist_dict in raw_track["artists"]:
            artist_name = artist_dict["name"]
            res_dict["artists"].append()

            if artist_name not in artist_url_map.keys():
                artist_url = raw_track["artists"]["external_urls"]["spotify"]
                artist_url_map[artist_name] = artist_url
                print(f"artist_url = {artist_url}")

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

        cur_num_tracks_in_album = cur_album_info.get(cur_album, 0)
        cur_num_tracks_in_album += 1
        cur_album_info[cur_album] = cur_num_tracks_in_album

        return cur_album

    def _analyze_playlist_for_genre(self, analyzed_artist_dict: Dict, genre_info: Dict) -> None:
        """:brief Given a track to analyze and the current analysis dict,\
            updates `cur_genre_info` after analyzing the current track `IN PLACE`.
        \n:param `analyzed_artist_dict` a dict representing the final analysis of artists
        \n:param `genre_info` The genre metrics.
        \n:return None
        """
        # for each artist in analyzed_artist_dict query for their genre(s)
        # Hvae to get the artist id's
        # sum all the times a genre appears (mult by number of songs by that artist)

        # NOTE: artists will be in the preformatted form for json, have to temporarily convert them back
        pass


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