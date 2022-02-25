"""
    @file Responsible for handling & keeping track of multiple users to keeping their data safe and seperate
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import base64
from datetime import datetime, timedelta
import os

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
# from werkzeug.contrib.securecookie import SecureCookie
from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, logout_user
import requests

#--------------------------------OUR DEPENDENCIES--------------------------------#
from data_manager import DataManager
from user import User

class UserManager(LoginManager):
    def __init__(self, app: Flask):
        """
            \n@param: app   - The flask app
        """
        self.flaskApp = app

        # create login manager object
        LoginManager.__init__(self, self.flaskApp)
        self._data_manager = DataManager()

        self.createLoginManager()

    def createLoginManager(self):
        """
            \n@Brief: Helper function that creates all the necessary login manager attributes (callbacks)
            \n@Note: Wrapper to provide closure for `self`
        """
        @self.user_loader
        def loadUser(user_id):
            """
                \n@Brief: When Flask app is asked for "current_user", this decorator gets the current user's User object
                \n@Note: Refence current user with `current_user` (from flask_login import current_user)
                \n@Param: user_id - The user's unique token id
                \n@Return: Reference to the User class related to this userToken
            """
            possible_user = None
            if self._data_manager.does_user_exist(user_id):
                possible_user = User(user_id)


            return possible_user

        @self.unauthorized_handler
        def onNeedToLogIn():
            """
                \n@Brief: VERY important callback that redirects the user to log in if needed --
                gets triggered by "@login_required" if page is accessed without logging in
            """
            return redirect(url_for("spotify_authorize"))

        # TODO: get this to work so @fresh_login_required will call it
        # @self.needs_refresh_handler
        # def refresh_handler():
        #     """:brief Called whenever `needs_refresh()` is called.
        #         Useful for when authenticated user is stale and needs to get cleaned up."""
