"""
    @file Responsible for handling the individual User class
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask_login import UserMixin

#--------------------------------OUR DEPENDENCIES--------------------------------#


class User(UserMixin):
    def __init__(self, userId, access_token):
        """
            Custom user class that extends the expected class from LoginManager
            \n@Brief: Initializes a User with the most basic info needed
            \n@Param: userId - The user's unique id
            \n@Param: access_token - The fully authenticated user token
        """
        # store the user's id for use when object is accessed (via 'current_user')
        # they can use the id for more queries
        self.id = str(userId)
        self.access_token = access_token

    def has_valid_user_token(self) -> bool:
        # TODO: make a check to see if it is still valid
        return self.access_token is not None

    def get_access_token(self):
        return self.access_token


