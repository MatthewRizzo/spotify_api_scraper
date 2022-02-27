"""
    @file Responsible for handling the individual User class
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask_login import UserMixin

#--------------------------------OUR DEPENDENCIES--------------------------------#
from data_manager import DataManager

class User(UserMixin):
    def __init__(self, userId):
        """
            Custom user class that extends the expected class from LoginManager
            \n@Brief: Initializes a User with the most basic info needed
            \n@Param: userId - The user's unique id
            \n@Param: access_token - The fully authenticated user token
        """
        # store the user's id for use when object is accessed (via 'current_user')
        # they can use the id for more queries
        self.id = str(userId)
        self._data_manager = DataManager()
        self.access_token = self._data_manager.get_users_access_token(userId)

    def get_user_id(self) -> str:
        return self.id

    def has_valid_user_token(self) -> bool:
        is_valid = self._data_manager.is_token_valid(self.id)
        is_valid &= self.access_token is not None
        return is_valid

    def get_access_token(self):
        return self.access_token

    def is_active(self) -> bool:
        """:return True when token is not expired, False if expired"""
        valid_token = self.has_valid_user_token()
        return valid_token
