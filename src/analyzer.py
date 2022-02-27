#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from typing import List, Dict, Optional, Tuple

#------------------------------Project Imports-----------------------------#
import constants

class Analyzer():
    def __init__(self, is_verbose) -> None:
        """Class Used to analyze the data coming out of scraper in a form usable by WebApp"""
        self._is_verbose = is_verbose

    def analyze_raw_track_list(self, raw_track_list: List[Dict]) -> Tuple[Dict, Dict]:
        """Given a list of raw track dicts from the API call itself, grabs all relevant info and does some analytics.
        \n:return a Tuple of (chart_data_artist, chart_data_album).
        Each entry of the tuple is a Dict (with html/json safe keys).
        Each dict is readily usable for the rendering of the pie-charts.
        \n`NOTE:` before using the dictionaries to make the chart, use `Utils.validate_key_format()`
            to unescape the key names"""
        # eventual returns
        analyzed_chart_data_artist = {}
        analyzed_chart_data_album = {}

        for raw_track in raw_track_list:
            processed_track = self.parse_raw_track(raw_track)

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

        return (analyzed_chart_data_artist, analyzed_chart_data_album)

    def parse_raw_track(self, raw_track) -> dict:
        """Given a raw track from the get-track API, returns just the information we care about
        \n:param raw_track - the rest from the get-track API call
        \n:return Dict that maps track_name to other info:
            keys: {track_id: { track_name, album, artist(s) } }.
            Note: artists and genres will be lists, but will mostly be of length 1
        \n:docs https://developer.spotify.com/documentation/web-api/reference/#/operations/get-track"""
        res_dict = {}
        res_dict["track_id"] = raw_track["id"]
        # print(raw_track)
        res_dict["track_name"] = raw_track["name"]
        res_dict["album"] = raw_track["album"]["name"]
        res_dict["artists"] = []

        for artist_dict in raw_track["artists"]:
            res_dict["artists"].append(artist_dict["name"])

        return res_dict

    def _analyze_raw_track_artists(self, cur_parsed_track: Dict, cur_artist_info : Dict) -> str:
        """:brief Given a track to analyze and the current analysis dict,\
            updates `cur_artist_info` after analyzing the current track `IN PLACE`.
        \n:param `cur_parsed_track` a dict representing a parsed track
        \n:param `cur_artist_info` The current metrics on artists. `Will get updated in place`
        :return The artist of the current track
        """
        # Used to remove ' from key names until it is safe to put them back in
        # eventually the ' wrapped around key's are ALL changed to ",
        # but that will also change ' in the keys to " which is BAD for parsing.
        # change the ' to know what they are later
        single_quote_escape_seq = constants.SINGLE_QUOTE_ESCAPE_SEQ
        double_quote_escape_seq = constants.DOUBLE_QUOTE_ESCAPE_SEQ
        cur_artist = cur_parsed_track["artists"][0]
        cur_artist = cur_artist.replace("\'", single_quote_escape_seq).replace(
            '\"', double_quote_escape_seq)

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
        # Used to remove ' from key names until it is safe to put them back in
        # eventually the ' wrapped around key's are ALL changed to ",
        # but that will also change ' in the keys to " which is BAD for parsing.
        # change the ' to know what they are later
        single_quote_escape_seq = constants.SINGLE_QUOTE_ESCAPE_SEQ
        double_quote_escape_seq = constants.DOUBLE_QUOTE_ESCAPE_SEQ
        cur_album = str(cur_parsed_track["album"])
        cur_album = cur_album.replace("\'", single_quote_escape_seq).replace('\"', double_quote_escape_seq)

        cur_num_tracks_in_album = cur_album_info.get(cur_album, 0)
        cur_num_tracks_in_album += 1
        cur_album_info[cur_album] = cur_num_tracks_in_album

        return cur_album

