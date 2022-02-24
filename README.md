# spotify_api_scraper
Utilizes Spotify's API for devs to analyze playlists and viewing habits. Personal / for fun project because I use spotify so much

## Running the program
* Note: before running, please ensure the virtual environment is created as described in [Setup Guide](#setup-guide)
    * Whenever the program is run, it should be from the virtual environment python within [Spotify-api-scrapper-venv/bin/python](Spotify-api-scrapper-venv/bin/python)
  * This is automatically handled by the [start script](start.sh)

## Userflow & Example Running

1. Follow [Setup Guide](#setup-guide)
2. Run [start script](start.sh)
3. Go to [Homepage](<http://localhost:8080/>) - <http://localhost:8080/>
4. Follow authorization prompts - sign into spotify
  1. ![auth_example](docs/images/authorization.png)
  2. Click Agree
5. Click **Playlist Metrics**
   1. ![Playlist-Metrics-Image](docs/images/top_bar_after_auth.jpg)
6. See a list of all public Playlists
   1. ![Playlist-Table](docs/images/example_playlist_table.jpg)
   2. **Bonus:** You get to see my taste in Music *wink face*
7. Select **"Analyze Playlist By Artists and Albums"**
   1. ![Breakdown of Playlist By Artist](docs/images/example_artist_breakdown.jpg)
   2. ![Breakdown of Playlist By Album](docs/images/example_album_breakdown.jpg)
8. Select **"Analyze Playlist By Genre"**
   1. Currently not implemented / debating if possible
   2. Spotify lists multiple genres for each song, so analyzing genre's in a playlist requires judgment calls

## Setup Guide

1. This scrapper requires your Spotify account to have access to the Developer API's

* To do this, sign up for an app as directed here: <https://developer.spotify.com/documentation/general/guides/authorization/app-settings/>
* **Create an application** - <https://developer.spotify.com/dashboard/applications>
* *Maybe*: Add a user to your application - your user

2. Copy the template provided by [data/default_app_auth.json](data/default_app_auth.json) into `data/app_auth.json`
   1. **THIS IS IMPORTANT**. The application will search for this file. If it does not exist, you will be prompted to create it.
   2. Replace the default values with those associated with your Application
      1. see: <https://developer.spotify.com/documentation/general/guides/authorization/code-flow/>
      2. client_id = client id of your new registered application
3. Run the install script at [install/install.sh](install/install.sh)

## TODO

* get % genre in playlist
* BETTER way to timeout token for user
* Add the image of each playlist to the playlist table
* better handle when track has feat artists
* have clicking on pie chart link to the artist/album itself
* make end url's not show the long params
