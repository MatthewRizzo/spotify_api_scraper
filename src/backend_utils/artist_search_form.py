#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, StopValidation, DataRequired
from flask import flash, Flask

from scraper import Scraper

class ArtistSearchForm(FlaskForm):
    artist_name = StringField("Artist Name", validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, access_token, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        cls = self.__class__ # get reference to cls
        cls._access_token = access_token

        # represents the full get-artist result as from
        # https://developer.spotify.com/documentation/web-api/reference/#/operations/get-an-artist
        cls.artist_info = None

        cls.artist_name = StringField('Artist Name', validators=[DataRequired(), self.validateValidArtist])

    def validateValidArtist(self, form, field) ->bool:
        cls = self.__class__

        artist = field.data
        errr_msg = f"The artist {artist} is invalid. "
        errr_msg += "The artist must exactly match the artist name according to spotify "
        errr_msg += "including captialization"

        artist_info = Scraper.check_if_artist_exists(artist, cls._access_token)
        if artist_info is not None:
            cls.artist_info = artist_info
            return True
        else:
            raise ValidationError(message=errr_msg)
