#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from datetime import datetime, timedelta
from email.policy import default
import json
import flask
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user, fresh_login_required, login_fresh
import werkzeug.serving  # needed to make production worthy app that's secure
import secrets
import logging
import requests
import base64
from jinja2 import Markup, escape
from is_safe_url import is_safe_url

#------------------------------Project Imports-----------------------------#
from utils import Utils
from scraper import Scraper
from user_manager import UserManager
from data_manager import DataManager
from user import User
from backend_utils.playlist_search_table import PlaylistSearchTable, PlaylistSearchCell, create_playlist_search_cells
from backend_utils.flask_utils import FlaskUtils
import constants
from analyzer import Analyzer
from backend_utils.artist_search_form import ArtistSearchForm

class WebApp(Scraper, UserManager, FlaskUtils):
    def __init__(self, port: int, is_debug: bool, data_manager: DataManager, is_verbose: bool, redirect_localhost: bool):

        self._title = constants.PROJECT_NAME
        self._app = Flask(self._title)
        self._data_manager = data_manager
        self._is_verbose = is_verbose
        self._redirect_use_localhost = redirect_localhost

        # Create the user manager with a link to the app itself
        UserManager.__init__(self, self._app)
        FlaskUtils.__init__(self, self._app, port)
        Scraper.__init__(self, self._is_verbose)
        self.analyzer = Analyzer(self._is_verbose, self._data_manager)

        self._auth_info = self._data_manager.get_auth_info()

        # refreshes flask if html files change
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True
        self._app.config['SECRET_KEY'] = self._auth_info['client_secret']

        # user_auth_code - An authorization code that can be exchanged for an Access Token.
        # https: // developer.spotify.com/documentation/general/guides/authorization/code-flow/
        self.user_auth_code = None # set during authorization

        # Set the static and tempalte dir
        self._app.static_folder = str(Utils.get_static_dir_path())
        self._app.template_folder = str(Utils.get_templates_dir_path())

        self._logger = logging.getLogger("werkzeug")
        self._is_debug = is_debug
        self._host = '0.0.0.0'
        self._port = port
        logLevel = logging.INFO if self._is_debug == True else logging.ERROR
        self._logger.setLevel(logLevel)

        is_threaded = True

        self.generateRoutes()

        if self._is_verbose:
            self.print_routes()

        # start up a Web Server. Non-blocking because threaded
        if self._is_debug:
            self._app.run(host=self._host, port=self._port,
                          debug=self._is_debug, threaded=is_threaded)
        else:
            # FOR PRODUCTION
            werkzeug.serving.run_simple(
                hostname=self._host,
                port=self._port,
                application=self._app,
                use_debugger=self._is_debug,
                threaded=is_threaded
            )

    def does_need_refresh(self, view_func):
            """Decorator function to check if a user's login is expired and needs to be refreshed
            Add to ANY view that has @login_required.
            \nFlask has no built in way to check if a user is active without calling it in EACH view function.
            The decorator is a nice 1 line way of achieving the same task
            """
            def refresh_wrapper(*args, **kwargs):
                # Refresh the user if they are currently in active / have old tokens
                if not current_user.is_active():
                    self.refresh_view = url_for("refresh_access_token")
                    return self.needs_refresh()
                else:
                    return view_func(*args, **kwargs)
            # Prevent it getting overrided by Flask when chaining
            refresh_wrapper.__name__ = view_func.__name__
            return refresh_wrapper

    def generateRoutes(self):
        self.public_ip = FlaskUtils.get_public_ip()

        if self._redirect_use_localhost is False:
            self.base_route = FlaskUtils.get_app_base_url_str(self._port)
        else:
            # when local host is used, dont give a regular ip to start the route
            self.base_route = f"http://localhost:{self._port}"

        self._auth_redirect_uri = self.base_route + constants.REDIRECT_AFTER_AUTH_ENDPOINT

        self.create_homepage()
        self.create_api_routes()
        self.create_response_uri_pages()
        self.create_processed_data_pages()


        if self._is_verbose:
            print(f"base url = {self.base_route}")
            print(f"redirect uri = {self._auth_redirect_uri}")

    def create_homepage(self):
        @self._app.route("/", methods=["GET"])
        def index():
            return render_template("homepage.html", title=self._title)

        @self._app.route("/authenticated", methods=["GET"])
        @login_required
        @self.does_need_refresh
        def post_auth():
            """All users move from homepage to authenticated hompage (this one)"""
            return render_template("homepage.html", title=self._title)

        @self._app.route("/logout", methods=["GET"])
        @login_required
        def logout():
            # remove the refresh token from the user info
            # self._data_manager.remove_users_refresh_token(current_user.get_id())
            self._data_manager.remove_user_login_info(current_user.get_id())

            logout_user()
            return redirect(url_for("index", title=self._title))

        @self._app.route("/refresh_access_token", methods=["GET"])
        @login_required
        def refresh_access_token():
            if self._is_verbose is True:
                print("refreshing access token")
            user_id = current_user.get_user_id()

            # user_id = current_user.get_user_id()
            refresh_token = self._data_manager.get_users_refresh_token(user_id)

            # happens when user is logged out - refresh token removed
            if refresh_token is None:
                return redirect(url_for("post_auth", title=self._title))

            new_access_token, new_valid_for_sec = self.refresh_access_token(
                                                        self._auth_info['client_id'],
                                                        self._auth_info['client_secret'],
                                                        refresh_token
                                                    )
            # If the token can be refreshed, log the user back in
            if new_access_token is not None and new_valid_for_sec is not None:
                new_end_time = Utils.calc_end_time(datetime.now(), new_valid_for_sec)

                self._data_manager.save_users_access_token(
                    new_access_token, user_id, new_end_time, refresh_token)
                user = User(user_id)
                login_user(user)

            # On success redirect to the page the user was originally going to
            next = flask.request.args.get('next')
            white_list = self.get_valid_endpoints()
            is_next_url_bad = next == None or not is_safe_url(next, white_list)

            found_url = False
            for url in white_list:
                # check if the given url is part of a while list url
                if next.find(str(url)) != -1:
                    found_url = True
                    break
            is_next_url_bad = is_next_url_bad and found_url

            if is_next_url_bad:
                return redirect(url_for('post_auth'))
            else:
                preserve_code = 307 # used to keep state - get or post
                return redirect(next, code=preserve_code)

    def create_response_uri_pages(self):
        """Used to make all routes REQUIRED by spotify to receive responses"""
        @self._app.route("/redirect_after_auth", methods=["GET"], defaults={'code': None, 'state': None})
        @self._app.route("/redirect_after_auth?code=<code>&state=<state>", methods=["GET"])
        def redirect_after_auth():
            # part of this auth flow:
            # https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
            self.user_auth_code = request.args.get('code')
            state = request.args.get('state')

            # TODO: get this to work
            # Stop the flow if the state does not match the input state - there is a XCF attack
            # check if this state is within the valid state list
            if state not in self._valid_auth_state_list:
                if self._is_verbose:
                    print("State variable's do not match....XCF in progress. Ending it.")
                access_token, refresh_token, valid_for_sec = None, None, None
            else:
                # Can now ask for the Request Access Token
                access_token, refresh_token, valid_for_sec = self.get_access_token(self.user_auth_code,
                                                        self._auth_info['client_id'],
                                                        self._auth_info['client_secret'],
                                                        self._auth_redirect_uri)
                # remove this state from the valid state list
                state_idx = self._valid_auth_state_list.index(state)
                del self._valid_auth_state_list[state_idx]

            if access_token is None or refresh_token is None or valid_for_sec is None:
                print("Error getting the access token. Please try authorizing yourself again")
                logout_user()
                return redirect(url_for("index", title=self._title))

            user_id = self.get_user_id(access_token)

            # Figure out when the token times out
            current_time = datetime.now()

            # add the time to live - given in seconds using 2nd param
            end_valid_time = Utils.calc_end_time(current_time, valid_for_sec)

            self._data_manager.save_users_access_token(
                access_token, user_id, end_valid_time, refresh_token)

            user = User(user_id)
            login_user(user)
            return redirect(url_for("post_auth", title=self._title))

    def create_api_routes(self):
        @self._app.route("/spotify_authorize", methods=["GET"])
        def spotify_authorize():
            # only auth if needed
            if not current_user.is_authenticated or not current_user.is_active():

                auth_url = self.get_authenticate_url(self._auth_info['client_id'], self._auth_redirect_uri)
                return redirect(auth_url)
            else:
                return redirect(url_for("post_auth", title=self._title))

        @self._app.route("/playlist_metrics", methods=["GET"])
        @login_required
        @self.does_need_refresh
        def playlist_metrics():

            user_playlists_dict = self.get_users_playlists(current_user.get_access_token())

            playlist_search_cell_list = create_playlist_search_cells(user_playlists_dict)
            playlist_table = PlaylistSearchTable(playlist_search_cell_list)


            # Done in order to allow for special characters in the playlist descriptions
            escaped_playlist_table = Markup(playlist_table.__html__()).unescape()
            return render_template("playlistResult.html",
                                   title=self._title,
                                   playlist_table=escaped_playlist_table)

        @self._app.route("/search_artist", methods=["GET"])
        @login_required
        @self.does_need_refresh
        def search_artist():
            """Used to let users find the genre of any artist they enter"""
            access_token = current_user.get_access_token()
            return render_template("artist-search.html",
                                   title=self._title,
                                   artist_search_form = ArtistSearchForm(access_token))

        # Allow both bcause defaults to post, but when redirecting with next, use get
        @self._app.route("/analyze_playlist/<string:playlist_id>", methods=["GET", "POST"])
        @login_required
        @self.does_need_refresh
        def analyze_playlist(playlist_id: str):
            token = current_user.get_access_token()
            chart_data_artist = {}
            chart_data_album = {}
            raw_track_list, playlist_name, total_num_tracks = self.get_songs_from_playlist(playlist_id, token)

            if self._is_verbose:
                print(f"playlist name = {playlist_name}")

            analyzed_data_tuple = self.analyzer.analyze_raw_track_list(raw_track_list,
                                                                       current_user.get_access_token())
            chart_data_artist, chart_data_album, chart_data_genre = analyzed_data_tuple

            num_artists = len(list(chart_data_artist.keys()))
            num_albums = len(list(chart_data_album.keys()))
            num_genres = len(list(chart_data_genre.keys()))

            if self._is_verbose:
                print("\n\nDone processing Playlist:")
                for artist in chart_data_artist.keys():
                    print("artist {} has {} tracks in this playlist".format(
                        artist, chart_data_artist[artist]))
                for album in chart_data_album.keys():
                    print("album {} has {} tracks in this playlist".format(
                        album, chart_data_album[album]))
                print(f"\nThere are {num_genres} genres in this playlist:")
                print("\t{}".format(" ".join(chart_data_genre.keys())))

            # need to redirect because templates cannot be rendered within a post request
            # Trust me, I know this isn't ideal (especially the escaping),
            #   but things render ugly if done in response to a POST
            # See: https://stackoverflow.com/questions/70977131/flask-render-template-after-client-post-request/70983151
            return redirect(url_for("show_playlist_analysis",
                                    artist_data=chart_data_artist,
                                    album_data=chart_data_album,
                                    genre_data=chart_data_genre,
                                    playlist=playlist_name,
                                    num_tracks=total_num_tracks,
                                    num_artists=num_artists,
                                    num_albums=num_albums,
                                    num_genres=num_genres))

    def create_processed_data_pages(self):
        @self._app.route("/charts/playlist_analysis", methods=["GET"])
        @login_required
        @self.does_need_refresh
        def show_playlist_analysis():
            """:param data is a dictionary that contains the processed metrics"""

            full_data = request.args.to_dict()
            playlist = full_data["playlist"]
            num_tracks = full_data["num_tracks"]
            num_artists = full_data["num_artists"]
            num_albums = full_data["num_albums"]
            num_genres = full_data["num_genres"]

            input_data_artist = Utils.prep_dict_for_html(full_data["artist_data"])
            input_data_album = Utils.prep_dict_for_html(full_data["album_data"])
            input_data_genre = Utils.prep_dict_for_html(full_data["genre_data"])

            # Sort by value - have the top values in legend by largest %
            input_data_artist = {k: v for k, v in sorted(input_data_artist.items(), key=lambda item: item[1], reverse=True)}
            input_data_album = {k: v for k, v in sorted(input_data_album.items(), key=lambda item: item[1], reverse=True)}
            input_data_genre = {k: v for k, v in sorted(input_data_genre.items(), key=lambda item: item[1], reverse=True)}

            # First entry in dictionary MUST be the column names
            artist_data = {'Artist': 'Percentage of Playlist'}
            artist_data.update(input_data_artist)

            album_data = {'Album': 'Percentage of Playlist'}
            album_data.update(input_data_album)

            genre_data = {'Genre': 'Percentage of Playlist'}
            genre_data.update(input_data_genre)

            # TODO: add links to the pie chart
            # https: // stackoverflow.com/questions/6205621/how-to-add-links-in-google-chart-api
            return render_template("playlist-pie-chart.html",
                                   title=self._title,
                                   artist_data=artist_data,
                                   album_data=album_data,
                                   genre_data=genre_data,
                                   playlist=playlist,
                                   num_tracks=num_tracks,
                                   num_artists=num_artists,
                                   num_albums=num_albums,
                                   num_genres=num_genres)

        @self._app.route("/results/search_artist", methods=["POST"])
        @login_required
        @self.does_need_refresh
        def search_artist_results():
            """Route to get information about the artist"""
            access_token = current_user.get_access_token()
            artist_search_form = ArtistSearchForm(access_token, request.form)

            # validate the form
            if artist_search_form.validate_on_submit():
                raw_artist_genres = []
                if "genres" in artist_search_form.artist_info:
                    raw_artist_genres = artist_search_form.artist_info["genres"]
                artist_genres = ", ".join(raw_artist_genres)

                artist =  artist_search_form.artist_info["name"]

                try:
                    spotify_url = artist_search_form.artist_info["external_urls"]["spotify"]
                except:
                    spotify_url = ""

                return render_template("artist-search-result.html",
                                       title=self._title,
                                       artist = artist,
                                       artist_genres = artist_genres,
                                       artist_spotify_url=spotify_url,
                                       # pass this forward so if user goes back the form data is saved
                                       artist_search_form=artist_search_form)
            else:
                flash("Search for Arist Failed", "is-danger")
                # go back to the previous page via render to validation fail display message
                return render_template("artist-search.html",
                                       title=self._title,
                                       artist_search_form = artist_search_form)



