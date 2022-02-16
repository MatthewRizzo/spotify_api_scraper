#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import flask
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
import werkzeug.serving  # needed to make production worthy app that's secure
import secrets
import logging

#------------------------------Project Imports-----------------------------#
from utils import Utils

class WebApp():
    def __init__(self, port: int, is_debug: bool, secret_key : str):
        self._title = "Spotify API Scraper Parser"
        self._app = Flask(self._title)
        # refreshes flask if html files change
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True
        self._app.config['SECRET_KEY'] = secret_key


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

    def printSites(self):
        print("Existing URLs:")
        print(f"http://localhost:{self._port}/ (home & login page)")

    def create_homepage(self):
        @self._app.route("/", methods=["GET", "POST"])
        def index():
            return render_template("homepage.html", title=self._title)
