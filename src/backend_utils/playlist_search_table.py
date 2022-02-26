from flask_table import Table, Col
from flask_table.columns import LinkCol, ButtonCol
from typing import Optional, Dict, List

from flask import url_for, escape
from jinja2 import Markup, escape

from utils import Utils
import constants

class PlaylistSearchTable(Table):
    classes = ["table", "is-bordered", "is-striped",
               "is-hoverable", "is-fullwidth"]
    playlist_name = Col('Playlist Name')
    playlist_desc = Col('Playlist Description')

    analyze_artists = ButtonCol(
        name=constants.PLAYLIST_TABLE_ARTIST_COLUMN,
        endpoint="analyze_playlist_artists",
        url_kwargs=dict(
            playlist_id="playlist_id"
        ),
        # change class of cells
        button_attrs={"class": "button is-link"}
    )

    border = True
    no_items = f"This user has no playlists"


class PlaylistSearchCell(object):
    def __init__(self,
                 playlist_name,
                 playlist_id,
                 playlist_desc
                 ):

        self.playlist_name = playlist_name
        self.playlist_id = playlist_id
        self.playlist_desc = playlist_desc


def create_playlist_search_cells(raw_res_dict: Dict) -> List[PlaylistSearchCell]:
    """Given the raw results of a serach, generates a list of PlaylistSearchCell objects.
    Can be used to create a PlaylistSearchTable object"""
    search_res = []
    if len(raw_res_dict) is not None:
        # Keep adding to the search results list with cell objects
        # Will ad-hoc generate a table on the webpage with all the results
        for playlist_key, playlist_val in raw_res_dict.items():
            description = playlist_val['description']
            escaped_description = escape(description)
            # escaped_description = Utils.escape_html_special_char(escaped_description)
            search_res.append(
                PlaylistSearchCell(playlist_val['name'],
                                   playlist_val['id'],
                                   escaped_description)
            )

        search_res.sort(key=lambda cell: cell.playlist_name)
    return search_res
