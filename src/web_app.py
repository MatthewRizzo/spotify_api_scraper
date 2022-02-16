#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from datetime import datetime, timedelta
import flask
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_required
import werkzeug.serving  # needed to make production worthy app that's secure
import secrets
import logging
import requests
import base64

#------------------------------Project Imports-----------------------------#
from utils import Utils
from scraper import Scraper
from user_manager import UserManager
from data_manager import DataManager
from user import User


class WebApp(Scraper, UserManager):
    def __init__(self, port: int, is_debug: bool, data_manager: DataManager):

        self._title = "Spotify API Scraper Parser"
        self._app = Flask(self._title)
        self._data_manager = data_manager

        # Create the user manager with a link to the app itself
        UserManager.__init__(self, self._app)

        self._auth_info = self._data_manager.get_auth_info()

        # refreshes flask if html files change
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True
        self._app.config['SECRET_KEY'] = self._auth_info['client_secret']

        # user_auth_code - An authorization code that can be exchanged for an Access Token.
        # https: // developer.spotify.com/documentation/general/guides/authorization/code-flow/
        self.user_auth_code = None # set during authorization
        self.current_user = None

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

        # Display some of the routes before starting the server
        self.printSites()

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

    def generateRoutes(self):
        self.create_homepage()
        self.create_api_routes()
        self.create_response_uri_pages()

        self.base_route = f"http://localhost:{self._port}"

    def printSites(self):
        print("Existing URLs:")
        print(f"{self.base_route}/ (home & login page)")

    def create_homepage(self):
        @self._app.route("/", methods=["GET"])
        def index():
            # TODO: use current user to get access_token
            have_token = 0
            if self.current_user is not None:
                have_token = 1 if self.current_user.has_valid_user_token() else 0
            return render_template("homepage.html", title=self._title, have_access_token=have_token)

    def create_response_uri_pages(self):
        """Used to make all routes REQUIRED by spotify to receive responses"""
        @self._app.route("/redirect_after_auth", methods=["GET"])
        def redirect_after_auth():
            self._auth_redirect_uri = self.base_route + url_for('redirect_after_auth')

            # part of this auth flow:
            # https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
            self.user_auth_code = request.args.get('code')
            state = request.args.get('state')

            # TODO: get this to work
            # Stop the flow if the state does not match the input state
            # if self._auth_state_input == state:

            # else:
            #     print("State variable's do not match....XCF in progress. Ending it.")
            # Can now ask for the Request Access Token
            self._access_token_dict = self.get_access_token(self.user_auth_code,
                                                      self._auth_info['client_id'],
                                                      self._auth_info['client_secret'],
                                                      self._auth_redirect_uri)
            if self._access_token_dict is None:
                print("Error getting the access token. quitting")
                exit
            access_token = self._access_token_dict['access_token']
            user_id = self.get_user_id(access_token)

            # Figure out when the token times out
            current_time = datetime.now()

            # add the time to live - given in seconds using 2nd param
            datetime_delta = timedelta(seconds=self._access_token_dict['expires_in'])
            end_valid_time = (current_time + datetime_delta).strftime("%m/%d/%Y %H:%M:%S")

            self._data_manager.save_users_access_token(
                access_token, user_id, end_valid_time)

            self.current_user = User(user_id, access_token)
            return redirect(url_for("index", title=self._title, have_access_token=1))

    def create_api_routes(self):
        @self._app.route("/spotify_authorize", methods=["GET", "POST"])
        def spotify_authorize():
            # only auth if needed
            # TODO: add OR for when token is expired
            if self.current_user is None:
                self._auth_redirect_uri = self.base_route + url_for('redirect_after_auth')

                auth_url = self.get_authenticate_url(self._auth_info['client_id'], self._auth_redirect_uri)
                return redirect(auth_url)
            else:
                return redirect(url_for("index", title=self._title, have_access_token=1))



