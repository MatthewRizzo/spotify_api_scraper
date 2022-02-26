"""File used to prevent the burying of constants / magic numbers"""
# Overall Project constants
PROJECT_NAME = "Spotify API Scraper Parser"

# File / path constants
DEFAULT_AUTH_FILENAME =         "default_app_auth.json"
EXPECTED_AUTH_FILENAME =        "app_auth.json"
EXPECTED_USER_DATA_FILENAME =   "user_info.json"
DATA_DIR_NAME =                 "data"
FRONTEND_DIR_NAME =             "frontend"
STATIC_DIR_NAME =               "static"
TEMPLATE_DIR_NAME =             "templates"


# Web Page / Display Constants
PLAYLIST_TABLE_GENRE_COLUMN =   "Analyze Playlist By Genres"
PLAYLIST_TABLE_ARTIST_COLUMN =  "Analyze Playlist By Artists and Albums"
DEFAULT_NO_ALBUM_NAME_MSG = "Album Unknown"

# URL/URI Related constants
SPOTIFY_API_BASE_URI =          "https://api.spotify.com"
SPOTIFY_ACCOUNTS_BASE_URI =     "https://accounts.spotify.com"
SPOTIFY_AUTH_BASE_URL =         "https://accounts.spotify.com/authorize?"
SPOTIFY_TOKEN_URI =             "https://accounts.spotify.com/api/token"
SPOTIFY_GET_PLAYLIST_URI =      "https://api.spotify.com/v1/playlists" # Can get ANY Playlist
SPOTIFY_GET_USER_PLAYLISTS_URI= "https://api.spotify.com/v1/me/playlists" # Gets ALL playlists of current user
SPOTIFY_USER_PROFILE_URI =      "https://api.spotify.com/v1/me"


# API Header formats. NOTE: FILL IN "Authorization" before using them
# Used to obtain/refresh authorizationn
SPOTIFY_GET_AUTH_HEADER_FORMAT =    {   "Content-Type": "application/x-www-form-urlencoded",
                        # auth = 'Basic ' + base64-encode(client_id:client_secret)
                                        "Authorization": None,

}

# Used after already authorized
SPOTIFY_AUTHORIZED_HEADER_FORMAT = {    "Content-Type": "application/json",
                                        # auth = "Bearer " + access_token
                                        "Authorization": None,


}

# HTML Related Constants
HTML_CHAR_ESCAPE_TABLE = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    "\"": '\\"'
}

SINGLE_QUOTE_ESCAPE_SEQ = "#$%^&*!"
DOUBLE_QUOTE_ESCAPE_SEQ = "#$%^$^&*!"

# Time Related Constants
TIME_FORMAT_STR = "%m/%d/%Y %H:%M:%S"
