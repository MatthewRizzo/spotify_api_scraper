"""File used to prevent the burying of constants / magic numbers"""
# Overall Project constants
PROJECT_NAME = "Spotify API Scraper Parser"

# File / path constants
DEFAULT_AUTH_FILENAME =                 "default_app_auth.json"
EXPECTED_AUTH_FILENAME =                "app_auth.json"
EXPECTED_USER_DATA_FILENAME =           "user_info.json"
EXPECTED_ARTIST_TO_GENRE_MAP_FILENAME = "artist_genre_map.json"
DATA_DIR_NAME =                         "data"
FRONTEND_DIR_NAME =                     "frontend"
STATIC_DIR_NAME =                       "static"
TEMPLATE_DIR_NAME =                     "templates"


# FLASK RELATED CONSTANTS
REDIRECT_AFTER_AUTH_ENDPOINT =  "/redirect_after_auth"

# Web Page / Display Constants
PLAYLIST_TABLE_ANALYZE_COLUMN =         "Analyze Playlist"
PLAYLIST_TABLE_DISPLAY_SONGS_COLUMN =   "List All Songs"
DEFAULT_NO_ALBUM_NAME =                 "Album Unknown"
DEFAULT_NO_GENRE_NAME =                 "Other Genre"

# URL/URI Related constants
SPOTIFY_API_BASE_URI =          "https://api.spotify.com"
SPOTIFY_ACCOUNTS_BASE_URI =     "https://accounts.spotify.com"
SPOTIFY_AUTH_BASE_URL =         "https://accounts.spotify.com/authorize?"
SPOTIFY_TOKEN_URI =             "https://accounts.spotify.com/api/token"
SPOTIFY_GET_PLAYLIST_URI =      "https://api.spotify.com/v1/playlists" # Can get ANY Playlist
SPOTIFY_GET_USER_PLAYLISTS_URI= "https://api.spotify.com/v1/me/playlists" # Gets ALL playlists of current user
SPOTIFY_USER_PROFILE_URI =      "https://api.spotify.com/v1/me"
SPOTIFY_ARTIST_BASE_URI =       "https://api.spotify.com/v1/artists/" # ends with their id
SPOTIFY_ITEM_SEARCH_URI =       "https://api.spotify.com/v1/search"
# https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recently-played
SPOTIFY_GET_RECENT_PLAYED_URI = "https://api.spotify.com/v1/me/player/recently-played"

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

# Used when requesting an access token to get these scopes as well
SPOTIFY_SCOPES_LIST = ["user-read-recently-played"]

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


# DEFAULT AUTH FILE VALUES - before user creates their own files
DEFAULT_CLIENT_ID = "CLIENT_ID"
DEFAULT_CLIENT_SECRET = "CLIENT_SECRET"
