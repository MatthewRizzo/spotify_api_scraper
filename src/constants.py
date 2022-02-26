"""File used to prevent the burying of constants / magic numbers"""

# File / path constants
DEFAULT_AUTH_FILENAME =         "default_app_auth.json"
EXPECTED_AUTH_FILENAME =        "app_auth.json"
EXPECTED_USER_DATA_FILENAME =   "user_info.json"
DATA_DIR_NAME =                 "data"
FRONTEND_DIR_NAME =             "frontend"
STATIC_DIR_NAME =               "static"
TEMPLATE_DIR_NAME = "templates"


# Web Page / Display Constants
PLAYLIST_TABLE_GENRE_COLUMN =   "Analyze Playlist By Genres"
PLAYLIST_TABLE_ARTIST_COLUMN =  "Analyze Playlist By Artists and Albums"

# URL/URI Related constants
BASE_SPOTIFY_URI =              "https://api.spotify.com"
BASE_SPOTIFY_ACCOUNTS_URI =     "https://accounts.spotify.com"


# HTML Related Constants
HTML_CHAR_ESCAPE_TABLE = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    "\"": '\\"'
}
