#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import flask
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
import werkzeug.serving  # needed to make production worthy app that's secure
import secrets
import logging

#------------------------------Project Imports-----------------------------#
from utils import Utils
from scraper import Scraper
from user_manager import UserManager


class WebApp(Scraper, UserManager):
    def __init__(self, port: int, is_debug: bool, auth_info : dict):

        self._title = "Spotify API Scraper Parser"
        self._app = Flask(self._title)

        # Create the user manager with a link to the app itself
        UserManager.__init__(self, self._app)

        self._auth_info = auth_info
        # refreshes flask if html files change
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True
        self._app.config['SECRET_KEY'] = auth_info['client_secret']

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
        @self._app.route("/", methods=["GET", "POST"])
        def index():
            return render_template("homepage.html", title=self._title)

    def create_response_uri_pages(self):
        """Used to make all routes REQUIRED by spotify to receive responses"""
        @self._app.route("/redirect_after_auth", methods=["GET", "POST"])
        def redirect_after_auth():
            # part of this auth flow:
            # https: // developer.spotify.com/documentation/general/guides/authorization/code-flow/
            self.user_auth_code = request.args.get('code')
            print(self.user_auth_code)

            # Can now ask for the Request Access Token
            return redirect(url_for("index"))

    def create_api_routes(self):
        @self._app.route("/spotify_authorize", methods=["GET", "POST"])
        def spotify_authorize():
            redirect_uri = self.base_route + url_for('redirect_after_auth')

            auth_url = self.get_authenticate_url(self._auth_info['client_id'], redirect_uri)
            return redirect(auth_url)


