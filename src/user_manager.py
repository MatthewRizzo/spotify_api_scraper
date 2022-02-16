"""
    @file Responsible for handling & keeping track of multiple users to keeping their data safe and seperate
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import base64
from datetime import datetime, timedelta
import os

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
# from werkzeug.contrib.securecookie import SecureCookie
from flask import Flask, redirect, url_for
from flask_login import LoginManager

#--------------------------------OUR DEPENDENCIES--------------------------------#
from user import User
from data_manager import DataManager


class UserManager(LoginManager):
    def __init__(self, app: Flask):
        """
            \n@param: app   - The flask app
        """
        self.flaskApp = app

        # create login manager object
        LoginManager.__init__(self, self.flaskApp)
        self.data_manager = DataManager()

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
            access_token = self.data_manager.get_users_access_token(user_id)
            # If the access token is None, user is not registered, be sure to log them in
            if access_token is None or not self.data_manager._is_token_valid(user_id):
                redirect(url_for("spotify_authorize"))
            return User(user_id, access_token)


        @self.unauthorized_handler
        def onNeedToLogIn():
            """
                \n@Brief: VERY important callback that redirects the user to log in if needed --
                gets triggered by "@login_required" if page is accessed without logging in
            """
            return redirect(url_for("spotify_authorize"))
